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

    # 6. Sync index.html chrome version, script paths, and all 24 SKILL.md + ZIP SHA-256 digests
    checksums = json.loads((ROOT / "checksums.json").read_text(encoding="utf-8"))
    html_path = ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")
    for pattern in (
        f"v{old_version}",
        f'<span class="kv-v">{old_version}</span>',
    ):
        html = html.replace(pattern, pattern.replace(old_version, new_version))

    for slug, meta in checksums["skills"].items():
        script_files = [f for f in meta["files"] if f != "SKILL.md"]
        script_val = json.dumps(script_files[0]) if script_files else "null"
        pat = re.compile(
            r'("slug"\s*:\s*"' + re.escape(slug) + r'"[\s\S]*?"script"\s*:\s*)(null|"[^"]*")([\s\S]*?"sha256"\s*:\s*")([0-9a-f]{64})("[\s\S]*?"zipSha256"\s*:\s*")([0-9a-f]{64})(")'
        )
        m = pat.search(html)
        if not m:
            raise RuntimeError(f"Missing skill entry in index.html: {slug}")
        html = (
            html[: m.start(2)]
            + script_val
            + html[m.end(2) : m.start(4)]
            + meta["files"]["SKILL.md"]
            + html[m.end(4) : m.start(6)]
            + meta["zip_sha256"]
            + html[m.end(6) :]
        )
    html_path.write_text(html, encoding="utf-8")
    print(f"Bumped Cortex {old_version} -> {new_version} across all skills, manifests, ZIPs, checksums.json, and index.html.")


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
