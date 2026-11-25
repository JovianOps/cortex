#!/usr/bin/env python3
"""Atomically bump Cortex release version across all skills, manifests, CLI scripts, ZIPs, checksums, and index.html."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")

JSON_FILES = (
    "package.json",
    "packs.json",
    "plugin.json",
    "gemini-extension.json",
    ".cortex-policy.json",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".github/plugin.json",
    ".github/plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
    ".cursor-plugin/plugin.json",
    ".cursor-plugin/marketplace.json",
)

TEXT_FILES = (
    "scripts/cortex.py",
    "scripts/cortex_mcp.py",
    "scripts/cortex_studio.py",
    "scripts/cortex_compile.py",
    "scripts/cortex_scan.py",
    "scripts/install_skills.py",
    "scripts/package_skills.py",
    "AGENTS.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
)


def bump_all(new_version: str) -> None:
    pkg_path = ROOT / "package.json"
    old_version = json.loads(pkg_path.read_text(encoding="utf-8"))["version"]

    # 1. Bump all SKILL.md frontmatter versions
    for folder in ("skills", "premium-skills"):
        for md in sorted((ROOT / folder).glob("*/SKILL.md")):
            text = md.read_text(encoding="utf-8")
            updated, count = re.subn(r"^version:\s*\S+$", f"version: {new_version}", text, count=1, flags=re.M)
            if count != 1:
                raise RuntimeError(f"Could not update version frontmatter in {md}")
            md.write_text(updated, encoding="utf-8")

    # 2. Bump all JSON manifests + package.json + packs.json
    for rel in JSON_FILES:
        path = ROOT / rel
        updated = path.read_text(encoding="utf-8").replace(old_version, new_version)
        json.loads(updated)
        path.write_text(updated, encoding="utf-8")

    # 3. Update evals/skill_evals.json metadata (preserving embedded release-engineering prompt fixtures)
    eval_path = ROOT / "evals/skill_evals.json"
    eval_data = json.loads(eval_path.read_text(encoding="utf-8"))
    eval_data["schema_version"] = new_version
    eval_data["description"] = eval_data["description"].replace(f"v{old_version}", f"v{new_version}")
    eval_path.write_text(json.dumps(eval_data, indent=2) + "\n", encoding="utf-8")

    # 4. Update CLI scripts and agent docs
    for rel in TEXT_FILES:
        path = ROOT / rel
        if path.is_file():
            path.write_text(path.read_text(encoding="utf-8").replace(old_version, new_version), encoding="utf-8")

    # 5. Rebuild deterministic ZIP archives & checksums.json
    subprocess.run([sys.executable, str(ROOT / "scripts" / "package_skills.py")], cwd=ROOT, check=True)

    # 6. Sync index.html chrome version, full SKILLS array (from disk + checksums.json), and PACKS array (from packs.json)
    checksums = json.loads((ROOT / "checksums.json").read_text(encoding="utf-8"))
    packs_data = json.loads((ROOT / "packs.json").read_text(encoding="utf-8"))
    html_path = ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")
    for pattern in (
        f"v{old_version}",
        f"@{old_version}",
        f"version: '{old_version}'",
        f'<span class="kv-v">{old_version}</span>',
    ):
        html = html.replace(pattern, pattern.replace(old_version, new_version))

    skills_js: list[dict] = []
    for folder, tier, zip_dir in (("skills", "core", "zips"), ("premium-skills", "extended", "premium-zips")):
        for entry in sorted((ROOT / folder).iterdir()):
            md = entry / "SKILL.md"
            if not (entry.is_dir() and md.is_file()):
                continue
            raw_md = md.read_text(encoding="utf-8")
            dm = re.search(r"(?m)^description:\s*(.+)$", raw_md)
            tm = re.search(r"(?m)^\s*tags:\s*\[([^\]]*)\]", raw_md)
            desc = dm.group(1).strip().strip("\"'") if dm else ""
            tags = [t.strip().strip("\"'") for t in tm.group(1).split(",") if t.strip()] if tm else []
            meta = checksums["skills"][entry.name]
            script_files = [f for f in meta["files"] if f != "SKILL.md"]
            skills_js.append({
                "slug": entry.name,
                "tier": tier,
                "dir": folder,
                "zipDir": zip_dir,
                "desc": desc,
                "tags": tags,
                "script": script_files[0] if script_files else None,
                "sha256": meta["files"]["SKILL.md"],
                "zipSha256": meta["zip_sha256"],
            })

    packs_js = [
        {
            "id": pid,
            "label": pinfo["label"],
            "desc": pinfo["description"],
            "skills": pinfo["skills"],
        }
        for pid, pinfo in packs_data["packs"].items()
    ]

    html, c1 = re.subn(
        r"const SKILLS = \[[\s\S]*?\];",
        f"const SKILLS = {json.dumps(skills_js, indent=2)};",
        html,
        count=1,
    )
    html, c2 = re.subn(
        r"const PACKS = \[[\s\S]*?\];",
        f"const PACKS = {json.dumps(packs_js, indent=2)};",
        html,
        count=1,
    )
    if c1 != 1 or c2 != 1:
        raise RuntimeError("Could not sync SKILLS or PACKS arrays in index.html")
    html_path.write_text(html, encoding="utf-8")
    print(f"Bumped Cortex {old_version} -> {new_version} across {len(skills_js)} skills, {len(packs_js)} packs, manifests, ZIPs, checksums.json, and index.html.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Atomically bump Cortex release version and rebuild checksums.")
    parser.add_argument("version", help="Target SemVer version (e.g., 1.0.0).")
    args = parser.parse_args(argv)
    if not SEMVER_RE.match(args.version):
        print(f"ERROR: Invalid SemVer version {args.version!r}", file=sys.stderr)
        return 2
    bump_all(args.version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
