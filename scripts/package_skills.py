#!/usr/bin/env python3
"""Build or verify deterministic ZIP distributions and checksums.json for every Cortex skill.

Supports multi-file skill packages (SKILL.md plus optional bundled scripts/, references/, templates/).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = (("skills", "zips"), ("premium-skills", "premium-zips"))
CHECKSUMS_FILE = ROOT / "checksums.json"
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)
IGNORED_PARTS = {"__pycache__", ".DS_Store", ".pytest_cache"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".sh", ".ps1", ".toml", ".csv"}:
        return raw.replace(b"\r\n", b"\n")
    return raw


def skill_sources(directory: Path) -> dict[str, Path]:
    return {
        skill_dir.name: skill_dir / "SKILL.md"
        for skill_dir in sorted(directory.iterdir())
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").is_file()
    }


def skill_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(skill_dir.rglob("*")):
        if any(part in IGNORED_PARTS or part.endswith(".pyc") for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def expected_members(skill_dir: Path) -> dict[str, Path]:
    name = skill_dir.name
    return {
        f"{name}/{path.relative_to(skill_dir).as_posix()}": path
        for path in skill_files(skill_dir)
    }


def verify_archive(path: Path, name: str, source: Path) -> list[str]:
    problems: list[str] = []
    skill_dir = source.parent
    if not path.is_file():
        return [f"{path.relative_to(ROOT)}: archive is missing"]
    try:
        expected = expected_members(skill_dir)
        with zipfile.ZipFile(path) as archive:
            bad_member = archive.testzip()
            if bad_member:
                problems.append(f"{path.relative_to(ROOT)}: corrupt member {bad_member}")
            actual_names = sorted(archive.namelist())
            expected_names = sorted(expected.keys())
            if actual_names != expected_names:
                problems.append(
                    f"{path.relative_to(ROOT)}: expected members {expected_names}, found {actual_names}"
                )
            else:
                for member_name, src_path in expected.items():
                    archive_content = archive.read(member_name).replace(b"\r\n", b"\n")
                    source_content = normalized_bytes(src_path)
                    if archive_content != source_content:
                        problems.append(
                            f"{path.relative_to(ROOT)}: member {member_name} differs from {src_path.relative_to(ROOT)}"
                        )
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        problems.append(f"{path.relative_to(ROOT)}: invalid ZIP archive ({exc})")
    return problems


def build_checksums_manifest() -> dict:
    pkg_version = json.loads((ROOT / "package.json").read_text(encoding="utf-8")).get("version", "0.4.0")
    skills_index: dict[str, dict] = {}
    for source_dir, archive_dir in COLLECTIONS:
        sources = skill_sources(ROOT / source_dir)
        for name, source_md in sources.items():
            skill_dir = source_md.parent
            file_hashes: dict[str, str] = {}
            for src_path in skill_files(skill_dir):
                rel_inside = src_path.relative_to(skill_dir).as_posix()
                file_hashes[rel_inside] = sha256_bytes(normalized_bytes(src_path))
            zip_path = ROOT / archive_dir / f"{name}.zip"
            zip_hash = sha256_bytes(zip_path.read_bytes()) if zip_path.is_file() else ""
            skills_index[name] = {
                "collection": "core" if source_dir == "skills" else "extended",
                "dir": source_dir,
                "zip": f"{archive_dir}/{name}.zip",
                "zip_sha256": zip_hash,
                "files": file_hashes,
            }
    return {
        "schema_version": "1.0.0",
        "release_version": pkg_version,
        "skill_count": len(skills_index),
        "skills": skills_index,
    }


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
                members = expected_members(source.parent)
                with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                    for member_name, src_path in sorted(members.items()):
                        info = zipfile.ZipInfo(member_name, date_time=FIXED_ZIP_TIME)
                        info.compress_type = zipfile.ZIP_DEFLATED
                        info.external_attr = 0o644 << 16
                        archive.writestr(info, normalized_bytes(src_path))
                print(f"Created {destination.relative_to(ROOT)} ({len(members)} file(s))")

    expected_manifest = build_checksums_manifest()
    if check:
        if not CHECKSUMS_FILE.is_file():
            problems.append("checksums.json: file is missing (run python scripts/package_skills.py)")
        else:
            try:
                actual_manifest = json.loads(CHECKSUMS_FILE.read_text(encoding="utf-8"))
                if actual_manifest != expected_manifest:
                    problems.append("checksums.json: out of sync with skills/ or zips/ (run python scripts/package_skills.py)")
            except json.JSONDecodeError as exc:
                problems.append(f"checksums.json: invalid JSON ({exc})")
    else:
        CHECKSUMS_FILE.write_text(json.dumps(expected_manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {CHECKSUMS_FILE.relative_to(ROOT)} ({expected_manifest['skill_count']} skills)")

    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    if check:
        print(f"All {expected_manifest['skill_count']} skill ZIP archives and checksums.json are valid.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify archives and checksums without writing")
    return package(parser.parse_args().check)


if __name__ == "__main__":
    raise SystemExit(main())
