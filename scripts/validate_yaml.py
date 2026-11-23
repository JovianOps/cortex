#!/usr/bin/env python3
"""Validate every YAML file in the repository, including .github/workflows/."""
from __future__ import annotations

from pathlib import Path

import yaml

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


def main() -> int:
    files = iter_yaml_files()
    errors: list[tuple[Path, str]] = []
    for yaml_file in files:
        try:
            with yaml_file.open("r", encoding="utf-8") as handle:
                list(yaml.safe_load_all(handle))
        except yaml.YAMLError as exc:
            errors.append((yaml_file, str(exc)))

    if errors:
        for path, msg in errors:
            rel = path.relative_to(ROOT).as_posix()
            print(f"::error file={rel}::{msg}")
        return 1

    print(f"All {len(files)} YAML file(s) valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
