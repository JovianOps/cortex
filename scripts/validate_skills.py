#!/usr/bin/env python3
"""Validate Cortex skill metadata, required sections, and ZIP distributions."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = (("skills", "zips"), ("premium-skills", "premium-zips"))
REQUIRED_FIELDS = ("name", "description", "version", "author", "license", "platforms")
REQUIRED_SECTIONS = ("When to Use", "How to Run")
VALID_PLATFORMS = {"linux", "macos", "windows"}


def report_annotation(level: str, file: Path, message: str) -> None:
    relative = file.relative_to(ROOT).as_posix()
    print(f"::{level} file={relative}::{message}")


def main() -> int:
    errors: list[tuple[Path, str]] = []
    warnings: list[tuple[Path, str]] = []
    for source_dir, archive_dir in COLLECTIONS:
        directory = ROOT / source_dir
        if not directory.is_dir():
            errors.append((ROOT / source_dir, "Skill collection directory is missing"))
            continue
        skill_dirs = sorted(path for path in directory.iterdir() if path.is_dir())
        if not skill_dirs:
            errors.append((directory, "No skill directories found"))
        for skill_dir in skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            print(f"Checking {skill_file.relative_to(ROOT).as_posix()}...")
            if not skill_file.is_file():
                errors.append((skill_dir, "Missing SKILL.md"))
                continue
            content = skill_file.read_text(encoding="utf-8")
            if not content.startswith("---\n"):
                errors.append((skill_file, "Missing YAML frontmatter (must start with ---)"))
                continue
            try:
                _, frontmatter, body = content.split("---", 2)
                metadata = yaml.safe_load(frontmatter)
            except (ValueError, yaml.YAMLError) as exc:
                errors.append((skill_file, f"Invalid YAML frontmatter: {exc}"))
                continue
            if not isinstance(metadata, dict):
                errors.append((skill_file, "Frontmatter must be a YAML mapping"))
                continue
            for field in REQUIRED_FIELDS:
                if field not in metadata:
                    errors.append((skill_file, f"Missing required field: {field}"))
            if metadata.get("name") != skill_dir.name:
                errors.append((skill_file, f"name must match directory name {skill_dir.name!r}"))
            if not isinstance(metadata.get("description"), str) or not metadata.get("description", "").strip():
                errors.append((skill_file, "description must be a non-empty string"))
            if not isinstance(metadata.get("platforms"), list):
                errors.append((skill_file, "platforms must be a list"))
            else:
                for platform in metadata["platforms"]:
                    if platform not in VALID_PLATFORMS:
                        warnings.append((skill_file, f"Unknown platform: {platform}"))
            for section in REQUIRED_SECTIONS:
                if f"## {section}" not in body:
                    errors.append((skill_file, f"Missing required section: {section}"))
            hermes = metadata.get("metadata", {}).get("hermes", {}) if isinstance(metadata.get("metadata", {}), dict) else {}
            if hermes and "tags" not in hermes:
                warnings.append((skill_file, "Missing hermes.tags"))
            description = metadata.get("description")
            if isinstance(description, str):
                if len(description) > 60:
                    warnings.append((skill_file, f"Description > 60 chars ({len(description)} chars)"))
                if not description.endswith("."):
                    warnings.append((skill_file, "Description should end with period"))

    # Reuse the package script's integrity check so validation and packaging agree.
    from package_skills import verify_archive, skill_sources

    for source_dir, archive_dir in COLLECTIONS:
        sources = skill_sources(ROOT / source_dir)
        output = ROOT / archive_dir
        if not output.is_dir():
            errors.append((ROOT / archive_dir, "Archive directory is missing"))
            continue
        expected = {f"{name}.zip" for name in sources}
        actual = {path.name for path in output.glob("*.zip")}
        if actual != expected:
            errors.append((output, f"Expected archives {sorted(expected)}, found {sorted(actual)}"))
        for name, source in sources.items():
            errors.extend((output / f"{name}.zip", issue.split(": ", 1)[-1]) for issue in verify_archive(output / f"{name}.zip", name, source))

    for file, message in warnings:
        report_annotation("warning", file, message)
    for file, message in errors:
        report_annotation("error", file, message)
    if errors:
        return 1
    print("All core and premium skills and archives validated successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
