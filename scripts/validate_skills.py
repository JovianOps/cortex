#!/usr/bin/env python3
"""Validate Cortex skill metadata, required sections, and ZIP distributions."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS = (("skills", "zips"), ("premium-skills", "premium-zips"))
REQUIRED_FIELDS = ("name", "description", "version", "author", "license", "platforms")
REQUIRED_SECTIONS = ("When to Use", "How to Run")
VALID_PLATFORMS = {"linux", "macos", "windows"}


def _fallback_parse_frontmatter(frontmatter: str) -> dict:
    """Minimal stdlib YAML frontmatter parser used when PyYAML is not installed."""
    data: dict = {}
    in_metadata = False
    in_hermes = False
    for raw in frontmatter.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        stripped = raw.strip()
        if indent == 0:
            in_metadata = False
            in_hermes = False
            if ":" not in stripped:
                raise ValueError(f"Malformed frontmatter line: {raw!r}")
            k, _, v = stripped.partition(":")
            key = k.strip()
            val = v.strip()
            if key == "metadata" and not val:
                data["metadata"] = {}
                in_metadata = True
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                data[key] = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()] if inner else []
            else:
                data[key] = val.strip("\"'")
        elif in_metadata and indent == 2 and stripped.startswith("hermes:"):
            in_hermes = True
            data.setdefault("metadata", {})["hermes"] = {}
        elif in_hermes and indent >= 4 and ":" in stripped:
            k, _, v = stripped.partition(":")
            key = k.strip()
            val = v.strip()
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                data["metadata"]["hermes"][key] = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()] if inner else []
            else:
                data["metadata"]["hermes"][key] = val.strip("\"'")
    if "tags" not in data.get("metadata", {}).get("hermes", {}):
        m = re.search(r"(?m)^\s+tags:\s*\[([^\]]*)\]", frontmatter)
        if m:
            data.setdefault("metadata", {}).setdefault("hermes", {})["tags"] = [
                x.strip().strip("\"'") for x in m.group(1).split(",") if x.strip()
            ]
    return data


def _parse_frontmatter(frontmatter: str) -> object:
    if yaml is not None:
        return yaml.safe_load(frontmatter)
    return _fallback_parse_frontmatter(frontmatter)


def report_annotation(level: str, file: Path, message: str) -> None:
    relative = file.relative_to(ROOT).as_posix()
    print(f"::{level} file={relative}::{message}")


def validate_all(*, skip_archives: bool = False, quiet: bool = False) -> dict:
    errors: list[tuple[Path, str]] = []
    warnings: list[tuple[Path, str]] = []
    skills_checked = 0

    for source_dir, _archive_dir in COLLECTIONS:
        directory = ROOT / source_dir
        if not directory.is_dir():
            errors.append((ROOT / source_dir, "Skill collection directory is missing"))
            continue
        skill_dirs = sorted(path for path in directory.iterdir() if path.is_dir())
        if not skill_dirs:
            errors.append((directory, "No skill directories found"))
        for skill_dir in skill_dirs:
            skill_file = skill_dir / "SKILL.md"
            skills_checked += 1
            if not quiet:
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
                metadata = _parse_frontmatter(frontmatter)
            except Exception as exc:
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

    archives_checked = 0
    if not skip_archives:
        from package_skills import skill_sources, verify_archive

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
                archives_checked += 1
                errors.extend(
                    (output / f"{name}.zip", issue.split(": ", 1)[-1])
                    for issue in verify_archive(output / f"{name}.zip", name, source)
                )

    return {
        "ok": not errors,
        "skills_checked": skills_checked,
        "archives_checked": archives_checked,
        "archives_skipped": skip_archives,
        "yaml_parser": "pyyaml" if yaml is not None else "stdlib",
        "errors": [{"file": f.relative_to(ROOT).as_posix(), "message": m} for f, m in errors],
        "warnings": [{"file": f.relative_to(ROOT).as_posix(), "message": m} for f, m in warnings],
        "_raw_errors": errors,
        "_raw_warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-archives", action="store_true", help="Validate SKILL.md metadata without requiring zips/ archives.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON summary.")
    args = parser.parse_args(argv)

    result = validate_all(skip_archives=args.skip_archives, quiet=args.as_json)
    if args.as_json:
        payload = {k: v for k, v in result.items() if not k.startswith("_")}
        print(json.dumps(payload, indent=2))
        return 0 if result["ok"] else 1

    for file, message in result["_raw_warnings"]:
        report_annotation("warning", file, message)
    for file, message in result["_raw_errors"]:
        report_annotation("error", file, message)
    if not result["ok"]:
        return 1
    msg = (
        f"All {result['skills_checked']} skills validated successfully (archives skipped)!"
        if args.skip_archives
        else "All core and premium skills and archives validated successfully!"
    )
    print(msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
