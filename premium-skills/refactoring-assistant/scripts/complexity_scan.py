#!/usr/bin/env python3
"""Python AST cyclomatic complexity & function-length hotspot scanner for refactoring-assistant skill."""
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
BRANCH_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler, ast.With, ast.AsyncWith, ast.Assert, ast.IfExp)


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(part in SKIP_DIRS for part in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def cyclomatic_complexity(node: ast.AST) -> int:
    score = 1
    for child in ast.walk(node):
        if isinstance(child, BRANCH_NODES):
            score += 1
        elif isinstance(child, ast.BoolOp):
            score += len(child.values) - 1
    return score


def scan_file(path: Path, max_cc: int, max_lines: int) -> list[dict]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=path.as_posix())
    except SyntaxError as exc:
        return [{
            "file": path.as_posix(),
            "function": "<module>",
            "line": exc.lineno or 1,
            "complexity": 0,
            "lines": 0,
            "error": f"SyntaxError: {exc.msg}",
        }]
    hotspots: list[dict] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cc = cyclomatic_complexity(node)
            length = (getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno + 1
            if cc > max_cc or length > max_lines:
                hotspots.append({
                    "file": path.as_posix(),
                    "function": node.name,
                    "line": node.lineno,
                    "complexity": cc,
                    "lines": length,
                })
    return hotspots


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Find Python complexity & function-length refactoring hotspots.")
    parser.add_argument("target", type=Path, help="Python file or directory.")
    parser.add_argument("--max-cc", type=int, default=10, help="Cyclomatic complexity threshold (default: 10).")
    parser.add_argument("--max-lines", type=int, default=60, help="Function line-count threshold (default: 60).")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.target.exists():
        print(f"ERROR: Path not found: {args.target}", file=sys.stderr)
        return 2

    files = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*.py") if p.is_file() and not should_skip(p, args.target)
    )
    hotspots: list[dict] = []
    for fp in files:
        hotspots.extend(scan_file(fp, args.max_cc, args.max_lines))

    if args.as_json:
        print(json.dumps({"files_checked": len(files), "count": len(hotspots), "hotspots": hotspots}, indent=2))
    elif not hotspots:
        print(f"OK: No complexity hotspots exceeding CC>{args.max_cc} or lines>{args.max_lines}.")
    else:
        for h in sorted(hotspots, key=lambda x: (-x["complexity"], -x["lines"])):
            print(f"{h['file']}:{h['line']} {h['function']}() — CC={h['complexity']}, lines={h['lines']}")
    return 1 if hotspots else 0


if __name__ == "__main__":
    raise SystemExit(main())
