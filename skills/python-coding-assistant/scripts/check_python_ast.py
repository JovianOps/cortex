#!/usr/bin/env python3
"""Deterministic Python AST quality & safety auditor for python-coding-assistant skill."""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".tox",
    ".opencode", ".claude", ".cursor", ".windsurf", ".cline", ".agents",
    ".codex", ".gemini", ".openclaw", ".goose", ".aider", "zips", "premium-zips",
}


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(part in SKIP_DIRS for part in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def audit_python_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=path.as_posix())
    except SyntaxError as exc:
        return [{"severity": "CRITICAL", "rule": "syntax-error", "file": path.as_posix(), "line": exc.lineno or 1, "message": str(exc)}]

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for default in list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    findings.append({
                        "severity": "HIGH",
                        "rule": "mutable-default-arg",
                        "file": path.as_posix(),
                        "line": node.lineno,
                        "message": f"Function '{node.name}' uses a mutable default argument; use None instead.",
                    })
            if not node.name.startswith("_") and node.returns is None:
                findings.append({
                    "severity": "LOW",
                    "rule": "missing-return-annotation",
                    "file": path.as_posix(),
                    "line": node.lineno,
                    "message": f"Public function '{node.name}' is missing a return type annotation.",
                })
        elif isinstance(node, ast.ExceptHandler) and node.type is None:
            findings.append({
                "severity": "HIGH",
                "rule": "bare-except",
                "file": path.as_posix(),
                "line": node.lineno,
                "message": "Bare 'except:' catches SystemExit/KeyboardInterrupt; catch a specific exception.",
            })

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Python files via AST for mutable defaults, bare excepts, and missing return types.")
    parser.add_argument("target", type=Path, help="Python file or directory.")
    parser.add_argument("--strict", action="store_true", help="Also fail on LOW severity findings.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.target.exists():
        print(f"ERROR: Path not found: {args.target}", file=sys.stderr)
        return 2

    files = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*.py") if p.is_file() and not should_skip(p, args.target)
    )
    findings: list[dict] = []
    for fp in files:
        findings.extend(audit_python_file(fp))

    blocking = [f for f in findings if args.strict or f["severity"] in {"CRITICAL", "HIGH"}]
    if args.as_json:
        print(json.dumps({"files_checked": len(files), "count": len(findings), "findings": findings}, indent=2))
    elif not findings:
        print(f"OK: {len(files)} Python file(s) passed AST audit.")
    else:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
