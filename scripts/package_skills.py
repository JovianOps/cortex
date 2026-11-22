#!/usr/bin/env python3
"""Build or verify one-file ZIP distributions for every Cortex skill."""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = (("skills", "zips"), ("premium-skills", "premium-zips"))


def skill_sources(directory: Path) -> dict[str, Path]:
    return {
        skill_dir.name: skill_dir / "SKILL.md"
        for skill_dir in sorted(directory.iterdir())
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file()
    }


def expected_member(name: str) -> str:
    return f"{name}/SKILL.md"


def verify_archive(path: Path, name: str, source: Path) -> list[str]:
    problems: list[str] = []
    if not path.is_file():
        return [f"{path.relative_to(ROOT)}: archive is missing"]
    try:
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                problems.append(f"{path.relative_to(ROOT)}: corrupt member {bad_member}")
            expected = expected_member(name)
            if archive.namelist() != [expected]:
                problems.append(
                    f"{path.relative_to(ROOT)}: expected only {expected}, found {archive.namelist()}"
                )
            else:
                archive_content = archive.read(expected).replace(b"\r\n", b"\n")
                source_content = source.read_bytes().replace(b"\r\n", b"\n")
                if archive_content != source_content:
                    problems.append(
                        f"{path.relative_to(ROOT)}: content differs from {source.relative_to(ROOT)}"
                    )
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        problems.append(f"{path.relative_to(ROOT)}: invalid ZIP archive ({exc})")
    return problems


def package(check: bool) -> int:
    problems: list[str] = []
    for source_dir, archive_dir in COLLECTIONS:
        sources = skill_sources(ROOT / source_dir)
        output = ROOT / archive_dir
        if not sources:
            problems.append(f"{source_dir}: no skills found")
            continue
        if check:
            expected_files = {f"{name}.zip" for name in sources}
            actual_files = {p.name for p in output.glob("*.zip")} if output.is_dir() else set()
            if actual_files != expected_files:
                problems.append(
                    f"{archive_dir}: expected archives {sorted(expected_files)}, found {sorted(actual_files)}"
                )
            for name, source in sources.items():
                problems.extend(verify_archive(output / f"{name}.zip", name, source))
        else:
            output.mkdir(parents=True, exist_ok=True)
            for name, source in sources.items():
                destination = output / f"{name}.zip"
                with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                    normalized = source.read_bytes().replace(b"\r\n", b"\n")
                    archive.writestr(expected_member(name), normalized)
                print(f"Created {destination.relative_to(ROOT)}")
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    if check:
        print("All skill ZIP archives are valid and match their source files.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify archives without writing them")
    return package(parser.parse_args().check)


if __name__ == "__main__":
    raise SystemExit(main())
