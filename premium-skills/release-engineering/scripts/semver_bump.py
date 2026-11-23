#!/usr/bin/env python3
"""Deterministic SemVer bump & Keep-a-Changelog generator from Conventional Commits.

Zero external dependencies (Python 3 stdlib only).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
CONVENTIONAL_RE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<desc>.+)$")


def parse_version(raw: str) -> tuple[int, int, int]:
    m = SEMVER_RE.match(raw.strip())
    if not m:
        raise ValueError(f"Invalid SemVer version: {raw!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def compute_bump(current: str, commits: list[str]) -> dict:
    major, minor, patch = parse_version(current)
    level = "patch"
    grouped: dict[str, list[str]] = {"Breaking Changes": [], "Added": [], "Fixed": [], "Changed": []}

    for msg in commits:
        first_line = msg.splitlines()[0].strip()
        if not first_line:
            continue
        is_breaking = "BREAKING CHANGE:" in msg
        m = CONVENTIONAL_RE.match(first_line)
        if m:
            ctype = m.group("type")
            desc = m.group("desc")
            if m.group("breaking") or is_breaking:
                level = "major"
                grouped["Breaking Changes"].append(first_line)
            elif ctype == "feat":
                if level != "major":
                    level = "minor"
                grouped["Added"].append(desc)
            elif ctype in {"fix", "security"}:
                grouped["Fixed"].append(desc)
            else:
                grouped["Changed"].append(desc)
        elif is_breaking:
            level = "major"
            grouped["Breaking Changes"].append(first_line)
        else:
            grouped["Changed"].append(first_line)

    if level == "major":
        next_ver = f"{major + 1}.0.0"
    elif level == "minor":
        next_ver = f"{major}.{minor + 1}.0"
    else:
        next_ver = f"{major}.{minor}.{patch + 1}"

    return {"current": f"{major}.{minor}.{patch}", "bump": level, "next": next_ver, "sections": grouped}


def read_git_commits(since_ref: str | None) -> list[str]:
    rev = f"{since_ref}..HEAD" if since_ref else "HEAD"
    res = subprocess.run(
        ["git", "log", rev, "--format=%s%n%b%x1e"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [chunk.strip() for chunk in res.stdout.split("\x1e") if chunk.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute next SemVer release & changelog from Conventional Commits.")
    parser.add_argument("--current", required=True, help="Current SemVer version (e.g., 0.2.0).")
    parser.add_argument("--since", default=None, help="Git ref/tag to read commits from (default: all commits).")
    parser.add_argument("--commits-file", type=Path, default=None, help="Optional file of commit messages (one per line).")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON output.")
    args = parser.parse_args(argv)

    if args.commits_file:
        commits = [ln for ln in args.commits_file.read_text(encoding="utf-8").splitlines() if ln.strip()]
    else:
        commits = read_git_commits(args.since)

    result = compute_bump(args.current, commits)
    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"## [{result['next']}] ({result['bump']} bump from {result['current']})\n")
        for heading, items in result["sections"].items():
            if items:
                print(f"### {heading}")
                for item in items:
                    print(f"- {item}")
                print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
