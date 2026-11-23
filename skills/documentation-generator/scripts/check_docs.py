#!/usr/bin/env python3
"""Deterministic local Markdown link & anchor verifier for documentation-generator skill.

Zero external dependencies (Python 3 stdlib only).
Checks that relative file links and intra-document #heading anchors actually exist.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+)$", re.MULTILINE)


def slugify_heading(text: str) -> str:
    cleaned = re.sub(r"`([^`]*)`", r"\1", text.strip().lower())
    cleaned = re.sub(r"[^\w\s-]", "", cleaned)
    return re.sub(r"\s+", "-", cleaned).strip("-")


def extract_anchors(markdown: str) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    for m in HEADING_RE.finditer(markdown):
        base = slugify_heading(m.group(1))
        if base in counts:
            counts[base] += 1
            anchors.add(f"{base}-{counts[base]}")
        else:
            counts[base] = 0
            anchors.add(base)
    return anchors


def strip_fenced_code(markdown: str) -> list[tuple[int, str]]:
    in_fence = False
    out: list[tuple[int, str]] = []
    for lineno, line in enumerate(markdown.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((lineno, line))
    return out


def check_file(md_path: Path) -> list[dict]:
    content = md_path.read_text(encoding="utf-8")
    anchors = extract_anchors(content)
    broken: list[dict] = []

    for lineno, line in strip_fenced_code(content):
        for match in LINK_RE.finditer(line):
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "tel:", "data:")):
                continue
            if target.startswith("#"):
                anchor = target[1:].lower()
                if anchor not in anchors:
                    broken.append({
                        "file": md_path.as_posix(),
                        "line": lineno,
                        "target": target,
                        "reason": f"Anchor #{anchor} not found in document",
                    })
                continue
            path_part, _, frag = target.partition("#")
            resolved = (md_path.parent / path_part).resolve()
            if not resolved.exists():
                broken.append({
                    "file": md_path.as_posix(),
                    "line": lineno,
                    "target": target,
                    "reason": f"Relative target does not exist: {path_part}",
                })
            elif frag and resolved.is_file() and resolved.suffix.lower() == ".md":
                other_anchors = extract_anchors(resolved.read_text(encoding="utf-8"))
                if frag.lower() not in other_anchors:
                    broken.append({
                        "file": md_path.as_posix(),
                        "line": lineno,
                        "target": target,
                        "reason": f"Anchor #{frag} not found in {path_part}",
                    })
    return broken


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify local Markdown links and heading anchors.")
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown file(s) or directories to check.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output JSON.")
    args = parser.parse_args(argv)

    md_files: list[Path] = []
    for p in args.paths:
        if p.is_file():
            md_files.append(p)
        elif p.is_dir():
            md_files.extend(sorted(p.rglob("*.md")))
        else:
            print(f"ERROR: Path not found: {p}", file=sys.stderr)
            return 2

    all_broken: list[dict] = []
    for mf in md_files:
        all_broken.extend(check_file(mf))

    if args.as_json:
        print(json.dumps({"files_checked": len(md_files), "broken_count": len(all_broken), "broken": all_broken}, indent=2))
    else:
        for item in all_broken:
            print(f"[BROKEN] {item['file']}:{item['line']} -> {item['target']} ({item['reason']})")
        if not all_broken:
            print(f"OK: Checked {len(md_files)} Markdown file(s), 0 broken local links or anchors.")
    return 1 if all_broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
