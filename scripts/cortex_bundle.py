#!/usr/bin/env python3
"""Cortex Portable Bundles (v3.0.0) — build and verify deterministic, offline skill bundles.

A bundle is a single reproducible ZIP containing selected skills, a machine-readable
`bundle.json` manifest with a SHA-256 for every file, and a human README. Bundles can be
verified offline with `cortex bundle --verify <file.zip>` without the Cortex checkout.

Zero external dependencies (Python 3 stdlib only).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "3.0.0"
BUNDLE_SCHEMA = "1.0"
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)
IGNORED_PARTS = {"__pycache__", ".DS_Store", ".pytest_cache"}


def normalized_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".sh", ".ps1", ".toml", ".csv"}:
        return raw.replace(b"\r\n", b"\n")
    return raw


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def discover_catalog(root: Path) -> dict[str, dict]:
    catalog: dict[str, dict] = {}
    for folder, tier in (("skills", "core"), ("premium-skills", "extended")):
        base = root / folder
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            if entry.is_dir() and (entry / "SKILL.md").is_file():
                catalog[entry.name] = {
                    "slug": entry.name,
                    "tier": tier,
                    "dir": folder,
                    "path": entry,
                }
    return catalog


def resolve_selection(
    root: Path,
    *,
    packs: list[str] | None = None,
    skills: list[str] | None = None,
    collection: str | None = None,
) -> tuple[list[dict], dict]:
    catalog = discover_catalog(root)
    packs_data = json.loads((root / "packs.json").read_text(encoding="utf-8")).get("packs", {})
    chosen: list[str] = []

    for pid in packs or []:
        if pid not in packs_data:
            raise ValueError(f"Unknown pack {pid!r}. Available: {', '.join(sorted(packs_data))}")
        for slug in packs_data[pid]["skills"]:
            if slug not in chosen:
                chosen.append(slug)

    for slug in skills or []:
        if slug not in catalog:
            raise ValueError(f"Unknown skill {slug!r}")
        if slug not in chosen:
            chosen.append(slug)

    if collection:
        for slug, meta in sorted(catalog.items()):
            if collection == "all" or meta["tier"] == collection:
                if slug not in chosen:
                    chosen.append(slug)

    if not chosen:
        if "fullstack" in packs_data:
            chosen = list(packs_data["fullstack"]["skills"])
        else:
            chosen = sorted(catalog)

    resolved = [catalog[slug] for slug in chosen if slug in catalog]
    if not resolved:
        raise ValueError("No skills selected for the bundle.")
    return resolved, {"packs": list(packs or []), "skills": list(skills or []), "collection": collection}


def skill_files(skill_dir: Path) -> list[Path]:
    return [
        path
        for path in sorted(skill_dir.rglob("*"))
        if path.is_file()
        and not any(part in IGNORED_PARTS or part.endswith(".pyc") for part in path.parts)
    ]


def bundle_label(selection: dict) -> str:
    if selection.get("packs"):
        return "-".join(selection["packs"])
    if selection.get("collection"):
        return f"{selection['collection']}-collection"
    return "custom"


def render_readme(manifest: dict) -> str:
    rows = "\n".join(
        f"| `{slug}` | {meta['tier']} | `{meta['dir']}/{slug}` | {len(meta['files'])} | `{meta['sha256'][:12]}` |"
        for slug, meta in manifest["skills"].items()
    )
    pack_line = ", ".join(manifest["selection"]["packs"]) or "custom selection"
    return (
        "# Cortex Portable Bundle\n\n"
        f"- Cortex version: `{manifest['cortex_version']}`\n"
        f"- Bundle schema: `{manifest['schema_version']}`\n"
        f"- Selection: {pack_line}\n"
        f"- Skills: {manifest['skill_count']}\n"
        f"- Files: {manifest['file_count']}\n"
        f"- Manifest SHA-256: `{manifest['manifest_sha256']}`\n\n"
        "## Included skills\n\n"
        "| Skill | Tier | Source | Files | SKILL.md SHA-256 |\n"
        "| :--- | :--- | :--- | :---: | :--- |\n"
        f"{rows}\n\n"
        "## Install\n\n"
        "Unzip into any agent's skills directory (for example `~/.claude/skills/` or "
        "`.github/skills/`), or copy individual `<skill>/` directories.\n\n"
        "```bash\n"
        "unzip cortex-bundle.zip -d /tmp/cortex-bundle\n"
        "cp -r /tmp/cortex-bundle/skills/* ~/.claude/skills/\n"
        "```\n\n"
        "## Verify offline\n\n"
        "```bash\n"
        "python scripts/cortex_bundle.py --verify cortex-bundle.zip --json\n"
        "```\n\n"
        "`bundle.json` records a SHA-256 for every file; verification fails on any missing, "
        "extra, or modified file.\n"
    )


def build_bundle(
    root: Path,
    out_path: Path,
    *,
    packs: list[str] | None = None,
    skills: list[str] | None = None,
    collection: str | None = None,
) -> dict:
    selected, selection = resolve_selection(root, packs=packs, skills=skills, collection=collection)

    skills_manifest: dict[str, dict] = {}
    payload: list[tuple[str, bytes]] = []
    for meta in selected:
        skill_dir = meta["path"]
        files: dict[str, str] = {}
        for src in skill_files(skill_dir):
            rel = src.relative_to(skill_dir).as_posix()
            data = normalized_bytes(src)
            files[rel] = sha256_bytes(data)
            payload.append((f"skills/{meta['slug']}/{rel}", data))
        skills_manifest[meta["slug"]] = {
            "tier": meta["tier"],
            "dir": meta["dir"],
            "sha256": files.get("SKILL.md", ""),
            "files": files,
        }

    manifest: dict = {
        "schema_version": BUNDLE_SCHEMA,
        "cortex_version": VERSION,
        "bundle": bundle_label(selection),
        "selection": selection,
        "skill_count": len(skills_manifest),
        "file_count": len(payload),
        "skills": {slug: skills_manifest[slug] for slug in sorted(skills_manifest)},
        "manifest_sha256": "",
    }
    manifest["manifest_sha256"] = sha256_bytes(
        json.dumps({k: v for k, v in manifest.items() if k != "manifest_sha256"}, sort_keys=True, indent=2).encode("utf-8")
    )

    readme = render_readme(manifest)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        members = [
            ("bundle.json", json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"),
            ("README.md", readme.encode("utf-8")),
            *payload,
        ]
        for member_name, data in sorted(members):
            info = zipfile.ZipInfo(member_name, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)

    raw = out_path.read_bytes()
    return {
        "version": VERSION,
        "ok": True,
        "bundle": manifest["bundle"],
        "path": out_path.as_posix(),
        "sha256": sha256_bytes(raw),
        "size_bytes": len(raw),
        "skill_count": manifest["skill_count"],
        "file_count": manifest["file_count"],
        "skills": sorted(skills_manifest),
    }


def verify_bundle(path: Path) -> dict:
    problems: list[str] = []
    if not path.is_file():
        return {"version": VERSION, "ok": False, "path": path.as_posix(), "problems": ["bundle file is missing"]}
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            if "bundle.json" not in names:
                return {"version": VERSION, "ok": False, "path": path.as_posix(), "problems": ["bundle.json is missing"]}
            manifest = json.loads(archive.read("bundle.json").decode("utf-8"))
            expected: set[str] = {"bundle.json", "README.md"}
            for slug, meta in manifest.get("skills", {}).items():
                for rel, digest in meta.get("files", {}).items():
                    member = f"skills/{slug}/{rel}"
                    expected.add(member)
                    if member not in names:
                        problems.append(f"{member}: missing from archive")
                        continue
                    actual = sha256_bytes(archive.read(member).replace(b"\r\n", b"\n"))
                    if actual != digest:
                        problems.append(f"{member}: SHA-256 mismatch")
            unexpected = sorted(names - expected)
            if unexpected:
                problems.append(f"unexpected archive member(s): {', '.join(unexpected)}")
            if manifest.get("skill_count") != len(manifest.get("skills", {})):
                problems.append("bundle.json skill_count does not match its skills map")
    except (OSError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        problems.append(f"invalid bundle ({exc})")
        manifest = {}
    return {
        "version": VERSION,
        "ok": not problems,
        "path": path.as_posix(),
        "bundle": manifest.get("bundle", ""),
        "cortex_version": manifest.get("cortex_version", ""),
        "skill_count": manifest.get("skill_count", 0),
        "file_count": manifest.get("file_count", 0),
        "problems": problems,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or verify deterministic offline Cortex skill bundles (ZIP + SHA-256 manifest)."
    )
    parser.add_argument("--pack", "-p", action="append", default=[], help="Role pack ID(s) from packs.json.")
    parser.add_argument("--skill", "-s", action="append", default=[], help="Specific skill slug(s).")
    parser.add_argument("--collection", "-c", choices=("core", "extended", "all"), default=None)
    parser.add_argument("--out", "-o", type=Path, default=None, help="Output bundle path (default: dist/cortex-<selection>.zip).")
    parser.add_argument("--verify", type=Path, default=None, help="Verify an existing bundle and exit.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if args.verify:
        report = verify_bundle(args.verify.resolve())
        if args.as_json:
            print(json.dumps(report, indent=2))
        else:
            print(
                f"Cortex Bundle verify: {'OK' if report['ok'] else 'FAIL'} — {report['path']} "
                f"({report.get('skill_count', 0)} skills, {report.get('file_count', 0)} files)"
            )
            for problem in report.get("problems", []):
                print(f"  [FAIL] {problem}")
        return 0 if report["ok"] else 1

    selection = {"packs": args.pack, "skills": args.skill, "collection": args.collection}
    out_path = args.out or (Path.cwd() / "dist" / f"cortex-{bundle_label(selection)}.zip")
    try:
        report = build_bundle(
            ROOT,
            out_path.resolve(),
            packs=args.pack or None,
            skills=args.skill or None,
            collection=args.collection,
        )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(
            f"Cortex Bundle v{VERSION} — {report['bundle']} "
            f"({report['skill_count']} skills, {report['file_count']} files)"
        )
        print(f"  Wrote   : {report['path']}")
        print(f"  SHA-256 : {report['sha256']}")
        print(f"  Verify  : python scripts/cortex_bundle.py --verify {Path(report['path']).name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
