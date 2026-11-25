#!/usr/bin/env python3
"""Validate every YAML file in the repository, including .github/workflows/."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {".git", "node_modules", ".venv", "__pycache__", ".private"}


def iter_yaml_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".yml", ".yaml"}:
            continue
        if any(part in IGNORED_DIRS for part in path.relative_to(ROOT).parts):
            continue
        files.append(path)
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON summary.")
    args = parser.parse_args(argv)

    if yaml is None:
        if args.as_json:
            print(json.dumps({"ok": False, "error": "PyYAML is not installed (run: pip install pyyaml)"}, indent=2))
        else:
            print("ERROR: PyYAML is required (install via `pip install pyyaml`).", file=sys.stderr)
        return 2

    files = iter_yaml_files()
    errors: list[tuple[Path, str]] = []
    for yaml_file in files:
        try:
            with yaml_file.open("r", encoding="utf-8") as handle:
                list(yaml.safe_load_all(handle))
        except yaml.YAMLError as exc:
            errors.append((yaml_file, str(exc)))

    if args.as_json:
        print(json.dumps({
            "ok": not errors,
            "files_checked": len(files),
            "errors": [{"file": p.relative_to(ROOT).as_posix(), "message": msg} for p, msg in errors],
        }, indent=2))
        return 1 if errors else 0

    if errors:
        for path, msg in errors:
            rel = path.relative_to(ROOT).as_posix()
            print(f"::error file={rel}::{msg}")
        return 1

    print(f"All {len(files)} YAML file(s) valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
