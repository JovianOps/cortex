#!/usr/bin/env python3
"""Verify index.html integrity: inline JS syntax, checksums.json/packs.json parity, and WCAG 2.2 AA."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "index.html"
CHECKSUMS_JSON = ROOT / "checksums.json"
PACKS_JSON = ROOT / "packs.json"
A11Y_SCAN = ROOT / "premium-skills" / "accessibility-auditor" / "scripts" / "a11y_scan.py"


def check_inline_js(html: str) -> None:
    scripts = re.findall(r"<script>([\s\S]*?)</script>", html)
    if not scripts:
        raise RuntimeError("No inline <script> blocks found in index.html")
    for idx, body in enumerate(scripts, 1):
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tf:
            tf.write(body)
            tmp_path = Path(tf.name)
        try:
            res = subprocess.run(["node", "--check", str(tmp_path)], check=False, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"index.html script #{idx} failed node --check:\n{res.stderr}")
        finally:
            tmp_path.unlink(missing_ok=True)


def check_data_parity(html: str) -> tuple[int, int]:
    checksums = json.loads(CHECKSUMS_JSON.read_text(encoding="utf-8"))
    packs = json.loads(PACKS_JSON.read_text(encoding="utf-8"))

    missing: list[str] = []
    for slug, meta in checksums.get("skills", {}).items():
        skill_sha = meta["files"]["SKILL.md"]
        zip_sha = meta["zip_sha256"]
        if f'"{slug}"' not in html:
            missing.append(f"skill slug {slug}")
        if skill_sha not in html:
            missing.append(f"{slug} SKILL.md SHA-256 ({skill_sha[:12]}...)")
        if zip_sha not in html:
            missing.append(f"{slug} ZIP SHA-256 ({zip_sha[:12]}...)")

    for pack_id in packs.get("packs", {}):
        if f'"{pack_id}"' not in html:
            missing.append(f"pack id {pack_id}")

    if missing:
        raise RuntimeError("index.html out of sync with checksums.json/packs.json:\n  - " + "\n  - ".join(missing))

    return len(checksums.get("skills", {})), len(packs.get("packs", {}))


def check_accessibility() -> None:
    res = subprocess.run([sys.executable, str(A11Y_SCAN), str(INDEX_HTML)], check=False, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Accessibility scan failed:\n{res.stdout}\n{res.stderr}")


def main() -> int:
    html = INDEX_HTML.read_text(encoding="utf-8")
    check_inline_js(html)
    skill_count, pack_count = check_data_parity(html)
    check_accessibility()
    print(f"Verified index.html: inline JS syntax OK, {skill_count} skills & {pack_count} packs in sync with checksums.json, WCAG 2.2 AA OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
