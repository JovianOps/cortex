#!/usr/bin/env python3
"""Test-suite completeness & assertion-free test detector for testing-automation skill."""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def has_assertion(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for node in ast.walk(func):
        if isinstance(node, ast.Assert):
            return True
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and (
                node.func.attr.startswith("assert") or node.func.attr in {"raises", "warns", "fail"}
            ):
                return True
            if isinstance(node.func, ast.Name) and node.func.id in {"assert_called", "raises"}:
                return True
    return False


def scan_tests(test_dir: Path) -> list[dict]:
    findings: list[dict] = []
    for fp in sorted(test_dir.rglob("test_*.py")):
        tree = ast.parse(fp.read_text(encoding="utf-8"), filename=fp.as_posix())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                if not has_assertion(node):
                    findings.append({
                        "severity": "HIGH",
                        "rule": "assertion-free-test",
                        "file": fp.as_posix(),
                        "line": node.lineno,
                        "test": node.name,
                        "message": f"Test '{node.name}' contains no assert / assertEqual / pytest.raises call.",
                    })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Python test suites for assertion-free tests.")
    parser.add_argument("test_dir", type=Path, help="Directory containing test_*.py files.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.test_dir.exists():
        print(f"ERROR: Directory not found: {args.test_dir}", file=sys.stderr)
        return 2

    findings = scan_tests(args.test_dir)
    if args.as_json:
        print(json.dumps({"count": len(findings), "findings": findings}, indent=2))
    elif not findings:
        print(f"OK: All test functions under {args.test_dir} contain explicit assertions.")
    else:
        for f in findings:
            print(f"[{f['severity']}] {f['file']}:{f['line']} — {f['message']}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
