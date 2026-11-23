#!/usr/bin/env python3
"""Validate all multi-agent plugin, marketplace, and extension manifests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/JovianOps/cortex"

PLUGIN_MANIFESTS = (
    ".claude-plugin/plugin.json",
    "plugin.json",
    ".cursor-plugin/plugin.json",
)
MARKETPLACE_MANIFESTS = (
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
    ".cursor-plugin/marketplace.json",
)
GEMINI_MANIFEST = "gemini-extension.json"


def all_skill_paths() -> list[str]:
    paths: list[str] = []
    for folder in ("skills", "premium-skills"):
        base = ROOT / folder
        if base.is_dir():
            for entry in sorted(base.iterdir()):
                if entry.is_dir() and (entry / "SKILL.md").is_file():
                    paths.append(f"./{folder}/{entry.name}")
    return paths


def load_json(rel: str, errors: list[str]) -> dict | None:
    path = ROOT / rel
    if not path.is_file():
        errors.append(f"{rel}: manifest file is missing")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel}: invalid JSON ({exc})")
        return None
    if not isinstance(data, dict):
        errors.append(f"{rel}: top-level JSON must be an object")
        return None
    return data


def validate_skill_list(rel: str, skills: object, expected_all: set[str], require_all: bool, errors: list[str]) -> None:
    if not isinstance(skills, list) or not skills:
        errors.append(f"{rel}: skills must be a non-empty list")
        return
    for item in skills:
        if not isinstance(item, str) or not item.startswith("./"):
            errors.append(f"{rel}: skill path {item!r} must start with './'")
            continue
        skill_md = ROOT / item.removeprefix("./") / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{rel}: skill path {item!r} does not contain SKILL.md")
    if require_all and set(skills) != expected_all:
        missing = sorted(expected_all - set(skills))
        extra = sorted(set(skills) - expected_all)
        errors.append(f"{rel}: skill list mismatch (missing={missing}, extra={extra})")


def main() -> int:
    errors: list[str] = []
    expected_all = set(all_skill_paths())
    versions: dict[str, str] = {}

    for rel in PLUGIN_MANIFESTS:
        data = load_json(rel, errors)
        if data is None:
            continue
        for req in ("name", "version", "description", "skills"):
            if not data.get(req):
                errors.append(f"{rel}: missing required field {req!r}")
        if isinstance(data.get("version"), str):
            versions[rel] = data["version"]
        if data.get("repository") and data["repository"] != REPO_URL:
            errors.append(f"{rel}: repository must be {REPO_URL!r}, found {data['repository']!r}")
        validate_skill_list(rel, data.get("skills"), expected_all, require_all=True, errors=errors)

    for rel in MARKETPLACE_MANIFESTS:
        data = load_json(rel, errors)
        if data is None:
            continue
        for req in ("name", "owner", "plugins"):
            if not data.get(req):
                errors.append(f"{rel}: missing required field {req!r}")
        plugins = data.get("plugins")
        if not isinstance(plugins, list) or not plugins:
            errors.append(f"{rel}: plugins must be a non-empty list")
            continue
        for entry in plugins:
            if not isinstance(entry, dict):
                errors.append(f"{rel}: plugin entry must be an object")
                continue
            pname = entry.get("name", "<unnamed>")
            if not entry.get("source") or not str(entry["source"]).startswith("./"):
                errors.append(f"{rel} ({pname}): source must start with './'")
            if isinstance(entry.get("version"), str):
                versions[f"{rel}:{pname}"] = entry["version"]
            require_all = pname == "cortex"
            validate_skill_list(f"{rel} ({pname})", entry.get("skills"), expected_all, require_all=require_all, errors=errors)

    gem = load_json(GEMINI_MANIFEST, errors)
    if gem is not None:
        for req in ("name", "version", "description"):
            if not gem.get(req):
                errors.append(f"{GEMINI_MANIFEST}: missing required field {req!r}")
        if isinstance(gem.get("version"), str):
            versions[GEMINI_MANIFEST] = gem["version"]
        ctx = gem.get("contextFileName")
        if isinstance(ctx, str) and not (ROOT / ctx).is_file():
            errors.append(f"{GEMINI_MANIFEST}: contextFileName {ctx!r} does not exist")

    if len(set(versions.values())) > 1:
        errors.append(f"Version mismatch across manifests: {versions}")

    if errors:
        for err in errors:
            print(f"::error::{err}", file=sys.stderr)
        return 1

    print(
        f"Validated {len(PLUGIN_MANIFESTS) + len(MARKETPLACE_MANIFESTS) + 1} multi-agent manifests "
        f"(all {len(expected_all)} skills verified at v{next(iter(versions.values()))})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
