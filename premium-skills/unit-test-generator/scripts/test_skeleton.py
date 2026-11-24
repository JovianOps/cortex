#!/usr/bin/env python3
"""AST-based unit test case & branch checklist generator for unit-test-generator skill."""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def inspect_module(source_path: Path) -> list[dict]:
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=source_path.as_posix())
    items: list[dict] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            branches = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler, ast.Match)) for n in ast.walk(node))
            raises = [
                ast.unparse(n.exc) if n.exc is not None else "re-raise"
                for n in ast.walk(node)
                if isinstance(n, ast.Raise)
            ]
            items.append({
                "name": node.name,
                "line": node.lineno,
                "args": [a.arg for a in node.args.args],
                "branch_count": branches,
                "raises": raises,
                "recommended_cases": [
                    f"test_{node.name}_happy_path",
                    f"test_{node.name}_boundary_inputs",
                    *( [f"test_{node.name}_raises_on_invalid_input"] if raises else [] ),
                ],
            })
    return items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze a Python module and emit a unit-test branch checklist.")
    parser.add_argument("source", type=Path, help="Python source file to analyze.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.source.is_file():
        print(f"ERROR: File not found: {args.source}", file=sys.stderr)
        return 2

    items = inspect_module(args.source)
    if args.as_json:
        print(json.dumps({"file": args.source.as_posix(), "functions": items}, indent=2))
    else:
        print(f"Unit-test checklist for {args.source} ({len(items)} public function(s)):")
        for it in items:
            print(f"  - {it['name']}({', '.join(it['args'])}) [branches={it['branch_count']}]: {', '.join(it['recommended_cases'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
