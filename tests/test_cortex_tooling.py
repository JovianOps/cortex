"""Comprehensive test suite for Cortex v0.3.0 tooling, manifests, installer, and bundled helper scripts."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TestPackagingAndManifests(unittest.TestCase):
    def test_package_check_passes(self) -> None:
        res = subprocess.run(
            [sys.executable, str(SCRIPTS / "package_skills.py"), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stderr + res.stdout)
        self.assertIn("24 skill ZIP archives", res.stdout)

    def test_validate_manifests_passes(self) -> None:
        res = subprocess.run(
            [sys.executable, str(SCRIPTS / "validate_manifests.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stderr + res.stdout)
        self.assertIn("24 skills verified at v0.3.0", res.stdout)

    def test_eval_suite_and_audit_pass(self) -> None:
        res = subprocess.run(
            [sys.executable, str(SCRIPTS / "eval_skills.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stderr + res.stdout)
        self.assertIn("100.0/100", res.stdout)
        self.assertIn("24 tasks covering all 24 skills", res.stdout)


class TestMultiAgentInstaller(unittest.TestCase):
    def setUp(self) -> None:
        self.installer = load_module("cortex_installer_test", SCRIPTS / "install_skills.py")

    def test_full_lifecycle_local_install_status_tamper_upgrade_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            # Install 2 skills (one core with script, one extended with script) into claude-code & aider
            rc = self.installer.main([
                "--agent", "claude-code",
                "--agent", "aider",
                "--skill", "college-report-card",
                "--skill", "security-auditor",
                "--scope", "project",
                "--project-dir", str(project),
                "--write-aider-conf",
            ])
            self.assertEqual(rc, 0)

            # Verify bundled helper scripts were copied too
            self.assertTrue((project / ".claude/skills/college-report-card/SKILL.md").is_file())
            self.assertTrue((project / ".claude/skills/college-report-card/scripts/grade_calc.py").is_file())
            self.assertTrue((project / ".claude/skills/security-auditor/scripts/secret_scan.py").is_file())
            self.assertTrue((project / ".claude/skills/.cortex-lock.json").is_file())

            # Verify .aider.conf.yml was written cleanly
            aider_conf = (project / ".aider.conf.yml").read_text(encoding="utf-8")
            self.assertIn(".aider/skills/college-report-card/SKILL.md", aider_conf)
            self.assertIn(".aider/skills/security-auditor/SKILL.md", aider_conf)

            # Status should pass cleanly
            self.assertEqual(
                self.installer.main(["--agent", "claude-code", "--scope", "project", "--project-dir", str(project), "--status"]),
                0,
            )

            # Tamper with an installed file -> --status must fail (exit 1)
            tampered = project / ".claude/skills/security-auditor/SKILL.md"
            tampered.write_text("# tampered\n", encoding="utf-8")
            self.assertEqual(
                self.installer.main(["--agent", "claude-code", "--scope", "project", "--project-dir", str(project), "--status"]),
                1,
            )

            # Simulate outdated lockfile entry -> --upgrade restores clean file
            lock_path = project / ".claude/skills/.cortex-lock.json"
            lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
            lock_data["skills"]["security-auditor"]["version"] = "0.2.0"
            lock_path.write_text(json.dumps(lock_data), encoding="utf-8")
            self.assertEqual(
                self.installer.main(["--agent", "claude-code", "--scope", "project", "--project-dir", str(project), "--upgrade"]),
                0,
            )
            self.assertEqual(
                self.installer.main(["--agent", "claude-code", "--scope", "project", "--project-dir", str(project), "--status"]),
                0,
            )

            # Uninstall one skill
            self.assertEqual(
                self.installer.main([
                    "--agent", "claude-code",
                    "--scope", "project",
                    "--project-dir", str(project),
                    "--uninstall",
                    "--skill", "security-auditor",
                ]),
                0,
            )
            self.assertFalse((project / ".claude/skills/security-auditor").exists())
            self.assertTrue((project / ".claude/skills/college-report-card/SKILL.md").is_file())

    def test_remote_install_verifies_sha256_and_rejects_tampering(self) -> None:
        checksums_bytes = (ROOT / "checksums.json").read_bytes()
        skill_bytes = (ROOT / "skills/anti-hallucination/SKILL.md").read_bytes()

        def fake_fetch_ok(url: str, timeout: int = 20) -> bytes:
            if url.endswith("/checksums.json"):
                return checksums_bytes
            if url.endswith("/skills/anti-hallucination/SKILL.md"):
                return skill_bytes
            raise AssertionError(f"Unexpected URL: {url}")

        def fake_fetch_tampered(url: str, timeout: int = 20) -> bytes:
            if url.endswith("/checksums.json"):
                return checksums_bytes
            return b"MALICIOUS TAMPERED PAYLOAD"

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            with mock.patch.object(self.installer, "fetch_bytes", side_effect=fake_fetch_ok):
                rc = self.installer.main([
                    "--agent", "cursor",
                    "--skill", "anti-hallucination",
                    "--scope", "project",
                    "--project-dir", str(project),
                    "--remote",
                ])
                self.assertEqual(rc, 0)
                self.assertTrue((project / ".cursor/skills/anti-hallucination/SKILL.md").is_file())

            with mock.patch.object(self.installer, "fetch_bytes", side_effect=fake_fetch_tampered):
                with self.assertRaises(RuntimeError) as ctx:
                    self.installer.main([
                        "--agent", "gemini-cli",
                        "--skill", "anti-hallucination",
                        "--scope", "project",
                        "--project-dir", str(project),
                        "--remote",
                    ])
                self.assertIn("SHA-256 verification FAILED", str(ctx.exception))
                self.assertFalse((project / ".gemini/skills/anti-hallucination/SKILL.md").exists())


class TestBundledSkillScripts(unittest.TestCase):
    def test_grade_calc_exact_decimal_and_stop_gates(self) -> None:
        script = ROOT / "skills/college-report-card/scripts/grade_calc.py"
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            good_syl = p / "syllabus.json"
            good_syl.write_text(json.dumps({"weights": {"labs": 0.30, "midterm": 0.30, "final": 0.40}}), encoding="utf-8")
            bad_syl = p / "bad_syllabus.json"
            bad_syl.write_text(json.dumps({"weights": {"labs": 0.30, "midterm": 0.30, "final": 0.45}}), encoding="utf-8")

            grades = p / "grades.csv"
            grades.write_text(
                "student_id,name,labs,midterm,final\n"
                "S001,Alice,95,90,92\n"
                "S002,Bob,80,,88\n",
                encoding="utf-8",
            )

            # Bad weight sum must trigger stop gate (exit 1)
            bad_res = subprocess.run([sys.executable, str(script), str(grades), str(bad_syl)], capture_output=True, text=True)
            self.assertEqual(bad_res.returncode, 1)
            self.assertIn("STOP GATE", bad_res.stderr)

            # Good syllabus computes exact Decimal score and flags incomplete Bob
            good_res = subprocess.run(
                [sys.executable, str(script), str(grades), str(good_syl), "--format", "json"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(good_res.returncode, 0, msg=good_res.stderr)
            report = json.loads(good_res.stdout)
            self.assertEqual(report["graded_count"], 1)
            self.assertEqual(report["incomplete_count"], 1)
            self.assertEqual(report["students"][0]["final_score"], "92.30")
            self.assertEqual(report["students"][0]["letter"], "A-")

    def test_secret_scan_detects_and_redacts(self) -> None:
        script = ROOT / "premium-skills/security-auditor/scripts/secret_scan.py"
        fake_key = "AKIA" + "IOSFODNN7EXAMPLE"
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "unsafe.py"
            sample.write_text(
                f'AWS_KEY = "{fake_key}"\n'
                'import subprocess\n'
                'subprocess.run(cmd, shell=True)\n',
                encoding="utf-8",
            )
            res = subprocess.run([sys.executable, str(script), str(sample), "--format", "json"], capture_output=True, text=True)
            self.assertEqual(res.returncode, 1)
            self.assertNotIn(fake_key, res.stdout)  # Mandatory redaction!
            payload = json.loads(res.stdout)
            cwes = {f["cwe"] for f in payload["findings"]}
            self.assertIn("CWE-798", cwes)
            self.assertIn("CWE-78", cwes)

    def test_lint_openapi_catches_errors_and_passes_valid(self) -> None:
        script = ROOT / "premium-skills/api-designer/scripts/lint_openapi.py"
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps({"openapi": "3.1.0", "info": {"title": "API", "version": "1.0.0"}, "paths": {"/items": {"get": {"responses": {"200": {"description": "ok"}}}}}}), encoding="utf-8")
            res_bad = subprocess.run([sys.executable, str(script), str(bad), "--json"], capture_output=True, text=True)
            self.assertEqual(res_bad.returncode, 1)

            good = Path(tmp) / "good.json"
            good.write_text(json.dumps({
                "openapi": "3.1.0",
                "info": {"title": "API", "version": "1.0.0"},
                "components": {"securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}}},
                "paths": {"/items": {"get": {"operationId": "listItems", "responses": {"200": {"description": "ok"}, "400": {"description": "bad"}}}}},
            }), encoding="utf-8")
            res_good = subprocess.run([sys.executable, str(script), str(good)], capture_output=True, text=True)
            self.assertEqual(res_good.returncode, 0, msg=res_good.stdout)

    def test_a11y_scan_catches_flaws_and_passes_clean_html(self) -> None:
        script = ROOT / "premium-skills/accessibility-auditor/scripts/a11y_scan.py"
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.html"
            bad.write_text(
                "<html><head><style>button:focus { outline: none; }</style></head>"
                "<body><div onclick='go()'>Go</div><input placeholder='Email' tabindex='5'><img src='a.png'></body></html>",
                encoding="utf-8",
            )
            res_bad = subprocess.run([sys.executable, str(script), str(bad), "--json"], capture_output=True, text=True)
            self.assertEqual(res_bad.returncode, 1)
            rules = {f["rule"] for f in json.loads(res_bad.stdout)["findings"]}
            self.assertTrue({"html-lang", "document-title", "non-semantic-click", "form-label", "positive-tabindex", "img-alt", "focus-outline"}.issubset(rules))

            good = Path(tmp) / "good.html"
            good.write_text(
                "<!doctype html><html lang='en'><head><title>Clean</title></head>"
                "<body><h1>Hello</h1><label for='em'>Email</label><input id='em' type='email'>"
                "<button type='button'>Save</button><img src='a.png' alt='Logo'></body></html>",
                encoding="utf-8",
            )
            res_good = subprocess.run([sys.executable, str(script), str(good)], capture_output=True, text=True)
            self.assertEqual(res_good.returncode, 0, msg=res_good.stdout)

    def test_memory_store_lifecycle(self) -> None:
        script = ROOT / "skills/memory-manager/scripts/memory_store.py"
        with tempfile.TemporaryDirectory() as tmp:
            ctx = Path(tmp) / "context.json"
            self.assertEqual(subprocess.run([sys.executable, str(script), "-f", str(ctx), "init", "--project", "demo"]).returncode, 0)
            self.assertEqual(subprocess.run([sys.executable, str(script), "-f", str(ctx), "add-decision", "Use Decimal"]).returncode, 0)
            self.assertEqual(subprocess.run([sys.executable, str(script), "-f", str(ctx), "add-task", "Ship v0.3.0"]).returncode, 0)
            self.assertEqual(subprocess.run([sys.executable, str(script), "-f", str(ctx), "complete-task", "1"]).returncode, 0)
            stale = subprocess.run([sys.executable, str(script), "-f", str(ctx), "check-stale", "--max-hours", "1"], capture_output=True, text=True)
            self.assertEqual(stale.returncode, 0, msg=stale.stdout)
            self.assertFalse(json.loads(stale.stdout)["stale"])

    def test_check_docs_catches_broken_links_and_passes_readme(self) -> None:
        script = ROOT / "skills/documentation-generator/scripts/check_docs.py"
        res_ok = subprocess.run([sys.executable, str(script), str(ROOT / "AGENTS.md")], capture_output=True, text=True)
        self.assertEqual(res_ok.returncode, 0, msg=res_ok.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "BAD.md"
            bad.write_text("# Title\n\nSee [missing](./does-not-exist.md) and [bad anchor](#nope).\n", encoding="utf-8")
            res_bad = subprocess.run([sys.executable, str(script), str(bad), "--json"], capture_output=True, text=True)
            self.assertEqual(res_bad.returncode, 1)
            self.assertEqual(json.loads(res_bad.stdout)["broken_count"], 2)

    def test_lint_dockerfile_catches_risks_and_passes_hardened(self) -> None:
        script = ROOT / "premium-skills/docker-generator/scripts/lint_dockerfile.py"
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "Dockerfile.bad"
            bad.write_text("FROM python:latest\nENV API_KEY=supersecret\nRUN curl https://x.test/i.sh | sh\n", encoding="utf-8")
            res_bad = subprocess.run([sys.executable, str(script), str(bad), "--json"], capture_output=True, text=True)
            self.assertEqual(res_bad.returncode, 1)
            rules = {f["rule"] for f in json.loads(res_bad.stdout)["findings"]}
            self.assertTrue({"pin-base-image", "no-secret-in-env", "no-curl-pipe-shell", "require-non-root-user"}.issubset(rules))

            good = Path(tmp) / "Dockerfile.good"
            good.write_text("FROM python:3.12-slim\nUSER 10001:10001\nHEALTHCHECK CMD true\n", encoding="utf-8")
            res_good = subprocess.run([sys.executable, str(script), str(good)], capture_output=True, text=True)
            self.assertEqual(res_good.returncode, 0, msg=res_good.stdout)

    def test_lint_actions_catches_unpinned_and_injection(self) -> None:
        script = ROOT / "premium-skills/devops-pipeline/scripts/lint_actions.py"
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "ci.yml"
            bad.write_text("jobs:\n  t:\n    steps:\n      - uses: actions/checkout@v4\n      - run: echo ${{ github.event.issue.title }}\n", encoding="utf-8")
            res_bad = subprocess.run([sys.executable, str(script), str(bad), "--json"], capture_output=True, text=True)
            self.assertEqual(res_bad.returncode, 1)
            rules = {f["rule"] for f in json.loads(res_bad.stdout)["findings"]}
            self.assertTrue({"least-privilege-permissions", "pin-action-sha", "no-script-injection"}.issubset(rules))

            good = Path(tmp) / "good.yml"
            good.write_text("permissions:\n  contents: read\njobs:\n  t:\n    steps:\n      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683\n", encoding="utf-8")
            res_good = subprocess.run([sys.executable, str(script), str(good)], capture_output=True, text=True)
            self.assertEqual(res_good.returncode, 0, msg=res_good.stdout)

    def test_semver_bump_computes_major_minor_patch(self) -> None:
        script = ROOT / "premium-skills/release-engineering/scripts/semver_bump.py"
        with tempfile.TemporaryDirectory() as tmp:
            commits = Path(tmp) / "commits.txt"
            commits.write_text("feat(cli): add cortex doctor\nfix(zip): normalize line endings\n", encoding="utf-8")
            res = subprocess.run([sys.executable, str(script), "--current", "0.2.0", "--commits-file", str(commits), "--json"], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, msg=res.stderr)
            out = json.loads(res.stdout)
            self.assertEqual(out["bump"], "minor")
            self.assertEqual(out["next"], "0.3.0")


class TestUnifiedCortexCLI(unittest.TestCase):
    def test_cortex_detect_doctor_search_packs(self) -> None:
        cli = SCRIPTS / "cortex.py"
        det = subprocess.run([sys.executable, str(cli), "detect", "--json"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(det.returncode, 0, msg=det.stderr)
        self.assertGreaterEqual(json.loads(det.stdout)["detected_count"], 1)

        doc = subprocess.run([sys.executable, str(cli), "doctor"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(doc.returncode, 0, msg=doc.stdout + doc.stderr)

        srch = subprocess.run([sys.executable, str(cli), "search", "--has-script", "--json"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(srch.returncode, 0, msg=srch.stderr)
        self.assertEqual(json.loads(srch.stdout)["count"], 10)

        pks = subprocess.run([sys.executable, str(cli), "packs", "--json"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(pks.returncode, 0, msg=pks.stderr)
        self.assertEqual(len(json.loads(pks.stdout)["packs"]), 6)

    def test_cortex_pack_install_and_new_skill_scaffolder_scores_100(self) -> None:
        cli = SCRIPTS / "cortex.py"
        eval_mod = load_module("cortex_eval_scaffold_test", SCRIPTS / "eval_skills.py")
        with tempfile.TemporaryDirectory() as tmp:
            proj = Path(tmp)
            # Install fullstack pack into claude-code
            inst = subprocess.run(
                [sys.executable, str(cli), "install", "--agent", "claude-code", "--pack", "fullstack", "--scope", "project", "--project-dir", str(proj)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(inst.returncode, 0, msg=inst.stdout + inst.stderr)
            self.assertTrue((proj / ".claude/skills/accessibility-auditor/scripts/a11y_scan.py").is_file())
            self.assertTrue((proj / ".claude/skills/security-auditor/scripts/secret_scan.py").is_file())

            # Scaffold a brand-new skill and verify it passes Cortex's 100/100 structural quality audit!
            scaf = subprocess.run(
                [sys.executable, str(cli), "new", "graph-debugger", "--tier", "extended", "--with-script", "--out-dir", str(proj)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(scaf.returncode, 0, msg=scaf.stdout + scaf.stderr)
            new_md = proj / "premium-skills/graph-debugger/SKILL.md"
            self.assertTrue(new_md.is_file())
            self.assertTrue((proj / "premium-skills/graph-debugger/scripts/graph_debugger_check.py").is_file())

            score, issues = eval_mod.audit_skill("graph-debugger", new_md, set(eval_mod.discover_skills()) | {"graph-debugger"})
            self.assertEqual(score, 100, msg=f"Scaffolded skill scored {score}/100: {issues}")


if __name__ == "__main__":
    unittest.main()
