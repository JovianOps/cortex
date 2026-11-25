"""End-to-end tests for Cortex v3.0.0: capability graph, portable bundles, guard gate, and MCP/Studio integration."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
PKG_VERSION = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]


def load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def write_skill(root: Path, tier: str, slug: str, related: str = "") -> None:
    skill_dir = root / tier / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    related_line = f"\n  hermes:\n    related_skills: [{related}]\n" if related else ""
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        f"name: {slug}\n"
        f"description: Fixture skill {slug}.\n"
        "version: 3.0.0\n"
        "author: test\n"
        "license: MIT\n"
        "platforms: [linux]\n"
        f"metadata:{related_line}---\n\n# {slug}\n",
        encoding="utf-8",
    )


class TestCapabilityGraph(unittest.TestCase):
    def test_real_catalog_graph_and_renderers(self) -> None:
        graph_mod = load_mod("cortex_graph_real", SCRIPTS / "cortex_graph.py")
        graph = graph_mod.build_graph(ROOT)
        self.assertEqual(graph["skill_count"], 36)
        self.assertEqual(graph["pack_count"], 10)
        self.assertGreater(graph["edge_count"], 100)
        self.assertTrue(graph["ok"])
        self.assertEqual(graph["dangling_references"], [])
        self.assertEqual(len(graph["hubs"]), 5)
        for slug, meta in graph["skills"].items():
            self.assertIn(slug, graph["metrics"])
            self.assertEqual(len(meta["sha256"]), 64)
            self.assertGreaterEqual(graph["metrics"][slug]["packs"], 0)

        mermaid = graph_mod.to_mermaid(graph)
        self.assertTrue(mermaid.startswith("graph LR"))
        self.assertIn("P_fullstack", mermaid)
        self.assertIn("S_security_auditor", mermaid)
        dot = graph_mod.to_dot(graph)
        self.assertTrue(dot.startswith("digraph cortex"))
        self.assertIn('"pack:fullstack" -> "skill:security-auditor"', dot)

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "graph.mmd"
            rc = graph_mod.main(["--format", "mermaid", "--out", str(out)])
            self.assertEqual(rc, 0)
            self.assertTrue(out.read_text(encoding="utf-8").startswith("graph LR"))

    def test_check_rejects_dangling_and_reports_orphans(self) -> None:
        graph_mod = load_mod("cortex_graph_fixture", SCRIPTS / "cortex_graph.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(root, "skills", "alpha", related="ghost-skill")
            write_skill(root, "premium-skills", "beta")
            (root / "packs.json").write_text(
                json.dumps({"packs": {"only-beta": {"label": "Only Beta", "description": "x", "skills": ["beta"]}}}),
                encoding="utf-8",
            )
            graph = graph_mod.build_graph(root)
            self.assertFalse(graph["ok"])
            self.assertEqual(graph["orphans"], ["alpha"])
            self.assertEqual(len(graph["dangling_references"]), 1)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(graph_mod.main(["--check", "--project-dir", str(root)]), 1)
                self.assertEqual(graph_mod.main(["--check", "--strict", "--project-dir", str(root)]), 1)

    def test_cli_graph_dispatches(self) -> None:
        cli = SCRIPTS / "cortex.py"
        res = subprocess.run(
            [sys.executable, str(cli), "graph", "--format", "json", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stdout + res.stderr)
        self.assertEqual(json.loads(res.stdout)["skill_count"], 36)


class TestPortableBundles(unittest.TestCase):
    def test_build_verify_and_deterministic_bytes(self) -> None:
        bundle_mod = load_mod("cortex_bundle_real", SCRIPTS / "cortex_bundle.py")
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "a.zip"
            second = Path(tmp) / "b.zip"
            built = bundle_mod.build_bundle(ROOT, first, packs=["cloud-native"])
            self.assertTrue(built["ok"])
            self.assertEqual(built["skill_count"], 6)
            self.assertGreaterEqual(built["file_count"], 12)
            built2 = bundle_mod.build_bundle(ROOT, second, packs=["cloud-native"])
            self.assertEqual(built["sha256"], built2["sha256"], msg="bundle bytes must be deterministic")

            report = bundle_mod.verify_bundle(first)
            self.assertTrue(report["ok"], msg=report["problems"])
            self.assertEqual(report["cortex_version"], PKG_VERSION)

            with zipfile.ZipFile(first) as archive:
                manifest = json.loads(archive.read("bundle.json"))
                self.assertIn("README.md", archive.namelist())
                self.assertEqual(manifest["selection"]["packs"], ["cloud-native"])
                for slug, meta in manifest["skills"].items():
                    self.assertIn(f"skills/{slug}/SKILL.md", archive.namelist())

    def test_verify_detects_tampering(self) -> None:
        bundle_mod = load_mod("cortex_bundle_tamper", SCRIPTS / "cortex_bundle.py")
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.zip"
            bad = Path(tmp) / "bad.zip"
            bundle_mod.build_bundle(ROOT, good, skills=["security-auditor"])
            with zipfile.ZipFile(good) as src, zipfile.ZipFile(bad, "w") as dst:
                for info in src.infolist():
                    data = src.read(info.filename)
                    if info.filename.endswith("SKILL.md"):
                        data = data.replace(b"# ", b"# TAMPERED ", 1)
                    dst.writestr(info, data)
            report = bundle_mod.verify_bundle(bad)
            self.assertFalse(report["ok"])
            self.assertTrue(any("SHA-256 mismatch" in p for p in report["problems"]))

    def test_cli_bundle_build_and_verify(self) -> None:
        cli = SCRIPTS / "cortex.py"
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "bundle.zip"
            build = subprocess.run(
                [sys.executable, str(cli), "bundle", "--pack", "polyglot-systems", "--out", str(out), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, msg=build.stdout + build.stderr)
            self.assertEqual(json.loads(build.stdout)["skill_count"], 6)
            verify = subprocess.run(
                [sys.executable, str(cli), "bundle", "--verify", str(out), "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(verify.returncode, 0, msg=verify.stdout + verify.stderr)
            self.assertTrue(json.loads(verify.stdout)["ok"])


class TestGuardGate(unittest.TestCase):
    def test_guard_check_runs_selected_gates(self) -> None:
        res = subprocess.run(
            [sys.executable, str(SCRIPTS / "cortex_guard.py"), "check", "--only", "package", "--only", "graph", "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stdout + res.stderr)
        report = json.loads(res.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual(report["checks_run"], 2)
        self.assertEqual({c["name"] for c in report["checks"]}, {"package", "graph"})

    def test_guard_workflow_is_pinned_and_lint_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp) / "cortex-guard.yml"
            printed = subprocess.run(
                [sys.executable, str(SCRIPTS / "cortex_guard.py"), "--print-workflow"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(printed.returncode, 0, msg=printed.stderr)
            text = printed.stdout
            self.assertIn("permissions:\n  contents: read", text)
            self.assertIn("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1", text)
            self.assertNotIn("github.event", text)
            workflow.write_text(text, encoding="utf-8")

            lint = subprocess.run(
                [sys.executable, str(ROOT / "premium-skills/devops-pipeline/scripts/lint_actions.py"), str(workflow)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(lint.returncode, 0, msg=lint.stdout + lint.stderr)

    def test_guard_pre_commit_and_hook_install(self) -> None:
        guard_mod = load_mod("cortex_guard_unit", SCRIPTS / "cortex_guard.py")
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            payload = guard_mod.install_hooks(project)
            self.assertTrue(payload["ok"])
            hook = project / ".githooks" / "pre-commit"
            self.assertTrue(hook.is_file())
            body = hook.read_text(encoding="utf-8")
            self.assertIn("cortex.py verify", body)
            self.assertIn("scan . --fail-on high", body)
            self.assertIn("npx -y @jovianops/cortex verify", body)

            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(guard_mod.main(["install", "--project-dir", str(project), "--json"]), 0)

    def test_guard_write_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            res = subprocess.run(
                [sys.executable, str(SCRIPTS / "cortex_guard.py"), "--write-workflow", "--project-dir", tmp, "--json"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            dest = Path(tmp) / ".github/workflows/cortex-guard.yml"
            self.assertTrue(dest.is_file())
            self.assertIn("Cortex Guard", dest.read_text(encoding="utf-8"))


class TestV3McpAndStudio(unittest.TestCase):
    def test_mcp_exposes_graph_bundle_and_gate(self) -> None:
        mcp_mod = load_mod("cortex_mcp_v3", SCRIPTS / "cortex_mcp.py")
        with tempfile.TemporaryDirectory() as tmp:
            server = mcp_mod.CortexMCPServer(Path(tmp))
            tools = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
            assert tools is not None
            names = {t["name"] for t in tools["result"]["tools"]}
            self.assertEqual(len(names), 11)
            self.assertTrue({"cortex_skill_graph", "cortex_build_bundle", "cortex_release_gate"}.issubset(names))

            graph_call = server.handle_request({
                "jsonrpc": "2.0", "id": 2, "method": "tools/call",
                "params": {"name": "cortex_skill_graph", "arguments": {"format": "json"}},
            })
            assert graph_call is not None
            graph = json.loads(graph_call["result"]["content"][0]["text"])
            self.assertEqual(graph["skill_count"], 36)

            gate_call = server.handle_request({
                "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "cortex_release_gate", "arguments": {"only": ["graph"]}},
            })
            assert gate_call is not None
            gate = json.loads(gate_call["result"]["content"][0]["text"])
            self.assertTrue(gate["ok"])

            resources = server.handle_request({"jsonrpc": "2.0", "id": 4, "method": "resources/list", "params": {}})
            assert resources is not None
            uris = {r["uri"] for r in resources["result"]["resources"]}
            self.assertEqual(len(uris), 39)
            self.assertIn("cortex://graph", uris)

            read = server.handle_request({"jsonrpc": "2.0", "id": 5, "method": "resources/read", "params": {"uri": "cortex://graph"}})
            assert read is not None
            self.assertEqual(json.loads(read["result"]["contents"][0]["text"])["skill_count"], 36)

    def test_studio_graph_and_guard_endpoints(self) -> None:
        studio_mod = load_mod("cortex_studio_v3", SCRIPTS / "cortex_studio.py")
        with tempfile.TemporaryDirectory() as tmp:
            server = studio_mod.create_server("127.0.0.1", 0, Path(tmp))
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = f"http://127.0.0.1:{port}"
                with urllib.request.urlopen(f"{base}/api/overview", timeout=10) as resp:
                    overview = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(overview["mcp_tool_count"], 11)
                self.assertGreater(overview["graph_edge_count"], 100)

                with urllib.request.urlopen(f"{base}/api/graph", timeout=15) as resp:
                    graph = json.loads(resp.read().decode("utf-8"))
                self.assertEqual(graph["skill_count"], 36)

                with urllib.request.urlopen(f"{base}/api/graph?format=mermaid", timeout=15) as resp:
                    mermaid = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(mermaid["graph"].startswith("graph LR"))

                req = urllib.request.Request(
                    f"{base}/api/guard",
                    data=json.dumps({"only": ["graph"], "fail_fast": False}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    guard = json.loads(resp.read().decode("utf-8"))
                self.assertTrue(guard["ok"])
                self.assertEqual(guard["checks_run"], 1)
            finally:
                server.shutdown()
                server.server_close()

    def test_cli_version_is_v3(self) -> None:
        res = subprocess.run([sys.executable, str(SCRIPTS / "cortex.py"), "--version"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertEqual(res.stdout.strip(), f"cortex {PKG_VERSION}")
        self.assertTrue(PKG_VERSION.startswith("3."))


if __name__ == "__main__":
    unittest.main()
