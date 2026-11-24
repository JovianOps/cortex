#!/usr/bin/env python3
"""Deterministic codebase migration inventory builder for code-migration skill."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

IGNORED = {".git", "node_modules", ".venv", "__pycache__", "dist", "build"}
MANIFEST_NAMES = {"package.json", "pyproject.toml", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "Gemfile"}


def build_inventory(root: Path) -> dict:
    ext_files: Counter[str] = Counter()
    ext_lines: Counter[str] = Counter()
    manifests: list[str] = []

    for fp in sorted(root.rglob("*")):
        if not fp.is_file() or any(part in IGNORED for part in fp.relative_to(root).parts):
            continue
        if fp.name in MANIFEST_NAMES:
            manifests.append(fp.relative_to(root).as_posix())
        ext = fp.suffix.lower() or "<no-ext>"
        ext_files[ext] += 1
        try:
            ext_lines[ext] += sum(1 for _ in fp.open("r", encoding="utf-8", errors="ignore"))
        except OSError:
            pass

    return {
        "root": root.as_posix(),
        "total_files": sum(ext_files.values()),
        "total_lines": sum(ext_lines.values()),
        "manifests": manifests,
        "by_extension": {ext: {"files": ext_files[ext], "lines": ext_lines[ext]} for ext, _ in ext_lines.most_common(15)},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a deterministic file/LOC/manifest inventory for migration planning.")
    parser.add_argument("target", type=Path, default=Path("."), nargs="?", help="Directory to inventory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.target.is_dir():
        print(f"ERROR: Directory not found: {args.target}", file=sys.stderr)
        return 2

    inv = build_inventory(args.target)
    if args.as_json:
        print(json.dumps(inv, indent=2))
    else:
        print(f"Migration inventory for {inv['root']}: {inv['total_files']} file(s), {inv['total_lines']} lines")
        print(f"Manifests: {', '.join(inv['manifests']) or 'none'}")
        for ext, stats in inv["by_extension"].items():
            print(f"  {ext:<10} {stats['files']:>5} files   {stats['lines']:>8} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
