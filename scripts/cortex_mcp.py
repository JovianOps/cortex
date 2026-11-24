#!/usr/bin/env python3
"""Zero-dependency Model Context Protocol (MCP 2025-03-26) JSON-RPC 2.0 server for Cortex v2.0.0."""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VERSION = "2.0.0"
PROTOCOL_VERSION = "2025-03-26"


def load_local_module(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"cortex_mcp_{name}", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def discover_skills_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    checksums = json.loads((ROOT / "checksums.json").read_text(encoding="utf-8")) if (ROOT / "checksums.json").is_file() else {}
    c_skills = checksums.get("skills", {})
    for folder, tier in (("skills", "core"), ("premium-skills", "extended")):
        base = ROOT / folder
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            md = entry / "SKILL.md"
            if not (entry.is_dir() and md.is_file()):
                continue
            scripts = sorted(p.relative_to(entry).as_posix() for p in (entry / "scripts").glob("*.py")) if (entry / "scripts").is_dir() else []
            text = md.read_text(encoding="utf-8")
            desc = ""
            for line in text.splitlines():
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip().strip("\"'")
                    break
            c_meta = c_skills.get(entry.name, {})
            index[entry.name] = {
                "slug": entry.name,
                "tier": tier,
                "dir": folder,
                "description": desc,
                "scripts": scripts,
                "skill_path": md.as_posix(),
                "sha256": c_meta.get("files", {}).get("SKILL.md", ""),
                "zip_sha256": c_meta.get("zip_sha256", ""),
            }
    return index


class CortexMCPServer:
    """In-process and stdio MCP 2025-03-26 server exposing Cortex skills, verifiers, compiler, and scanner."""

    def __init__(self, workspace_dir: Path | None = None) -> None:
        self.workspace_dir = (workspace_dir or Path.cwd()).resolve()
        self.skills = discover_skills_index()

    def _safe_workspace_path(self, raw_path: str | None) -> Path:
        if not raw_path:
            return self.workspace_dir
        candidate = (self.workspace_dir / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path).resolve()
        try:
            candidate.relative_to(self.workspace_dir)
        except ValueError as exc:
            raise ValueError(f"Path '{raw_path}' escapes workspace root '{self.workspace_dir}'.") from exc
        return candidate

    def tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "cortex_list_skills",
                "description": "List all Cortex skills with tier, description, bundled script path, and SHA-256 hash.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "tier": {"type": "string", "enum": ["core", "extended"]},
                    },
                },
            },
            {
                "name": "cortex_get_skill",
                "description": "Retrieve full SKILL.md instructions and metadata for a specific Cortex skill slug.",
                "inputSchema": {
                    "type": "object",
                    "required": ["slug"],
                    "properties": {
                        "slug": {"type": "string", "description": "Skill slug (e.g., security-auditor)."},
                    },
                },
            },
            {
                "name": "cortex_search_skills",
                "description": "Search Cortex skills by keyword across slug, description, and bundled script name.",
                "inputSchema": {
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string"},
                    },
                },
            },
            {
                "name": "cortex_list_packs",
                "description": "List all curated Cortex role-based skill packs from packs.json.",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "cortex_verify_workspace",
                "description": "Run Cortex supply-chain verification (checksums, manifests, evals, and project lockfiles).",
                "inputSchema": {"type": "object", "properties": {}},
            },
            {
                "name": "cortex_run_verifier",
                "description": "Execute a skill's bundled zero-dependency Python verifier against a path inside the workspace.",
                "inputSchema": {
                    "type": "object",
                    "required": ["slug"],
                    "properties": {
                        "slug": {"type": "string", "description": "Skill slug whose bundled script should run."},
                        "target": {"type": "string", "description": "Relative file or directory inside the workspace."},
                        "extra_args": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            {
                "name": "cortex_compile_rules",
                "description": "Compile Cortex skills/packs into native Cursor (.mdc), VS Code (.instructions.md), Windsurf, Cline, CLAUDE.md, AGENTS.md, or GEMINI.md rules.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "targets": {"type": "array", "items": {"type": "string"}},
                        "pack": {"type": "string"},
                        "skills": {"type": "array", "items": {"type": "string"}},
                        "dry_run": {"type": "boolean", "default": True},
                    },
                },
            },
            {
                "name": "cortex_scan_repo",
                "description": "Run Cortex unified multi-tool security, IaC, PII, SBOM, and code hygiene scanner across the workspace.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "only": {"type": "array", "items": {"type": "string"}},
                        "fail_on": {"type": "string", "enum": ["none", "low", "medium", "high", "critical"]},
                    },
                },
            },
        ]

    def call_tool(self, name: str, args: dict[str, Any]) -> dict:
        if name == "cortex_list_skills":
            tier = args.get("tier")
            rows = [s for s in self.skills.values() if not tier or s["tier"] == tier]
            return {"count": len(rows), "skills": rows}

        if name == "cortex_get_skill":
            slug = str(args.get("slug", "")).strip().lower()
            if slug not in self.skills:
                raise ValueError(f"Unknown skill slug: {slug!r}")
            meta = dict(self.skills[slug])
            meta["content"] = Path(meta["skill_path"]).read_text(encoding="utf-8")
            return meta

        if name == "cortex_search_skills":
            q = str(args.get("query", "")).strip().lower()
            matches = [
                s for s in self.skills.values()
                if q in s["slug"].lower() or q in s["description"].lower() or any(q in sc.lower() for sc in s["scripts"])
            ]
            return {"query": q, "count": len(matches), "skills": matches}

        if name == "cortex_list_packs":
            return json.loads((ROOT / "packs.json").read_text(encoding="utf-8"))

        if name == "cortex_verify_workspace":
            res = subprocess.run(
                [sys.executable, str(SCRIPTS / "cortex.py"), "verify", "--project-dir", str(self.workspace_dir), "--json"],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return json.loads(res.stdout) if res.stdout.strip().startswith("{") else {"ok": res.returncode == 0, "stdout": res.stdout, "stderr": res.stderr}

        if name == "cortex_run_verifier":
            slug = str(args.get("slug", "")).strip().lower()
            if slug not in self.skills:
                raise ValueError(f"Unknown skill slug: {slug!r}")
            scripts = self.skills[slug]["scripts"]
            if not scripts:
                raise ValueError(f"Skill {slug!r} has no bundled helper script.")
            script_path = ROOT / self.skills[slug]["dir"] / slug / scripts[0]
            cmd = [sys.executable, str(script_path)]
            if args.get("target"):
                safe_t = self._safe_workspace_path(str(args["target"]))
                cmd.append(str(safe_t))
            extra = args.get("extra_args") or []
            if isinstance(extra, list):
                cmd.extend(str(a) for a in extra)
            if "--json" not in cmd:
                cmd.append("--json")
            res = subprocess.run(cmd, cwd=self.workspace_dir, check=False, capture_output=True, text=True, timeout=60)
            parsed: Any = res.stdout.strip()
            try:
                parsed = json.loads(res.stdout)
            except json.JSONDecodeError:
                pass
            return {"skill": slug, "script": scripts[0], "exit_code": res.returncode, "result": parsed, "stderr": res.stderr.strip()}

        if name == "cortex_compile_rules":
            compiler = load_local_module("cortex_compile")
            catalog = compiler.discover_catalog(ROOT)
            packs = [str(args["pack"])] if args.get("pack") else None
            skill_list = [str(s) for s in args["skills"]] if args.get("skills") else None
            targets = [str(t) for t in args.get("targets") or ["cursor", "vscode"]]
            selected = compiler.resolve_skills(catalog, skills=skill_list, packs=packs, root=ROOT)
            return compiler.compile_rules(self.workspace_dir, targets, selected, dry_run=bool(args.get("dry_run", True)))

        if name == "cortex_scan_repo":
            scanner = load_local_module("cortex_scan")
            pol = scanner.load_policy(None, self.workspace_dir)
            only = [str(x) for x in args["only"]] if args.get("only") else None
            return scanner.run_scan(self.workspace_dir, only=only, policy=pol, fail_on_override=args.get("fail_on"))

        raise ValueError(f"Unknown MCP tool: {name!r}")

    def handle_request(self, req: dict[str, Any]) -> dict[str, Any] | None:
        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params") or {}

        # Notifications have no id and expect no response
        if req_id is None and method.startswith("notifications/"):
            return None

        try:
            if method == "initialize":
                result: Any = {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                        "prompts": {"listChanged": False},
                    },
                    "serverInfo": {"name": "cortex-mcp", "version": VERSION},
                }
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": self.tool_definitions()}
            elif method == "tools/call":
                tool_name = str(params.get("name", ""))
                tool_args = params.get("arguments") or {}
                out = self.call_tool(tool_name, tool_args)
                result = {"content": [{"type": "text", "text": json.dumps(out, indent=2)}], "isError": False}
            elif method == "resources/list":
                resources = [
                    {
                        "uri": f"cortex://skills/{slug}",
                        "name": slug,
                        "description": meta["description"],
                        "mimeType": "text/markdown",
                    }
                    for slug, meta in self.skills.items()
                ]
                resources.extend([
                    {"uri": "cortex://packs", "name": "packs.json", "description": "Curated Cortex role-based skill packs", "mimeType": "application/json"},
                    {"uri": "cortex://checksums", "name": "checksums.json", "description": "SHA-256 supply-chain checksums", "mimeType": "application/json"},
                ])
                result = {"resources": resources}
            elif method == "resources/read":
                uri = str(params.get("uri", ""))
                if uri == "cortex://packs":
                    result = {"contents": [{"uri": uri, "mimeType": "application/json", "text": (ROOT / "packs.json").read_text(encoding="utf-8")}]}
                elif uri == "cortex://checksums":
                    result = {"contents": [{"uri": uri, "mimeType": "application/json", "text": (ROOT / "checksums.json").read_text(encoding="utf-8")}]}
                elif uri.startswith("cortex://skills/"):
                    slug = uri.removeprefix("cortex://skills/")
                    if slug not in self.skills:
                        raise ValueError(f"Resource not found: {uri}")
                    result = {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": Path(self.skills[slug]["skill_path"]).read_text(encoding="utf-8")}]}
                else:
                    raise ValueError(f"Unknown resource URI: {uri}")
            elif method == "prompts/list":
                result = {
                    "prompts": [
                        {
                            "name": f"cortex/{slug}",
                            "description": meta["description"],
                            "arguments": [{"name": "task", "description": "Task or target context for this skill", "required": False}],
                        }
                        for slug, meta in self.skills.items()
                    ]
                }
            elif method == "prompts/get":
                pname = str(params.get("name", ""))
                slug = pname.removeprefix("cortex/")
                if slug not in self.skills:
                    raise ValueError(f"Unknown prompt: {pname}")
                skill_md = Path(self.skills[slug]["skill_path"]).read_text(encoding="utf-8")
                task = str((params.get("arguments") or {}).get("task", "")).strip()
                user_msg = f"{skill_md}\n\n---\nTask: {task}" if task else skill_md
                result = {
                    "description": self.skills[slug]["description"],
                    "messages": [{"role": "user", "content": {"type": "text", "text": user_msg}}],
                }
            else:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

            return {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as exc:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(exc)}}


def read_stdio_message(stream) -> tuple[dict[str, Any] | None, str]:
    """Read either Content-Length framed or newline-delimited JSON-RPC message."""
    first_line = stream.readline()
    if not first_line:
        return None, "jsonl"
    stripped = first_line.strip()
    if not stripped:
        return None, "jsonl"
    if stripped.lower().startswith(b"content-length:"):
        length = int(stripped.split(b":", 1)[1].strip())
        while True:
            hdr = stream.readline()
            if not hdr or hdr in (b"\r\n", b"\n"):
                break
        body = stream.read(length)
        return json.loads(body.decode("utf-8")), "lsp"
    return json.loads(stripped.decode("utf-8")), "jsonl"


def write_stdio_message(stream, payload: dict[str, Any], mode: str) -> None:
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    if mode == "lsp":
        stream.write(f"Content-Length: {len(encoded)}\r\n\r\n".encode("ascii") + encoded)
    else:
        stream.write(encoded + b"\n")
    stream.flush()


def client_mcp_config(client: str, project_dir: Path) -> dict:
    base_entry = {
        "command": "npx",
        "args": ["-y", "@jovianops/cortex", "mcp", "--project-dir", project_dir.as_posix()],
    }
    if client == "vscode":
        return {"servers": {"cortex": {"type": "stdio", **base_entry}}}
    return {"mcpServers": {"cortex": base_entry}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Cortex zero-dependency MCP (Model Context Protocol) JSON-RPC stdio server.")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd(), help="Workspace root directory for tool confinement.")
    parser.add_argument("--print-config", choices=("vscode", "claude-code", "cursor", "codex", "windsurf"), default=None, help="Print copy-paste MCP client JSON configuration and exit.")
    args = parser.parse_args(argv)

    if args.print_config:
        print(json.dumps(client_mcp_config(args.print_config, args.project_dir.resolve()), indent=2))
        return 0

    server = CortexMCPServer(args.project_dir.resolve())
    stdin = sys.stdin.buffer
    stdout = sys.stdout.buffer
    while True:
        try:
            msg, mode = read_stdio_message(stdin)
        except Exception as exc:
            write_stdio_message(stdout, {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}}, "jsonl")
            continue
        if msg is None:
            break
        resp = server.handle_request(msg)
        if resp is not None:
            write_stdio_message(stdout, resp, mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
