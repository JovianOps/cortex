#!/usr/bin/env python3
"""Zero-dependency Git repository hygiene, conflict-marker, large-file, and Conventional Commits auditor."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    "coverage", ".next", "target", "vendor", ".pytest_cache",
    ".opencode", ".claude", ".cursor", ".windsurf", ".cline", ".agents",
    ".codex", ".gemini", ".openclaw", ".goose", ".aider", "zips", "premium-zips",
}
CONVENTIONAL_RE = re.compile(r"^(?:feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|release)(?:\([a-z0-9._/-]+\))?!?: .+")
CONFLICT_RE = re.compile(r"^(?:<{7}\s|={7}$|>{7}\s)")


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(part in SKIP_DIRS for part in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def audit_repo(repo: Path, max_file_kb: int = 1024, commits_to_check: int = 10) -> dict:
    findings: list[dict] = []
    scanned_files = 0

    for p in sorted(repo.rglob("*")):
        if not p.is_file() or should_skip(p, repo):
            continue
        scanned_files += 1
        size_kb = p.stat().st_size / 1024
        if size_kb > max_file_kb:
            findings.append({
                "file": p.relative_to(repo).as_posix(),
                "line": 1,
                "severity": "MEDIUM",
                "rule": "git-large-file",
                "message": f"File size {size_kb:.1f} KB exceeds threshold ({max_file_kb} KB); consider Git LFS or artifact storage.",
            })
        if p.suffix.lower() in {".py", ".ts", ".tsx", ".js", ".md", ".json", ".yml", ".yaml", ".txt", ".html", ".css", ".rs", ".go"}:
            for idx, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if CONFLICT_RE.match(line):
                    findings.append({
                        "file": p.relative_to(repo).as_posix(),
                        "line": idx,
                        "severity": "CRITICAL",
                        "rule": "git-conflict-marker",
                        "message": "Unresolved Git merge conflict marker detected.",
                    })

    commits_checked = 0
    if (repo / ".git").exists():
        res = subprocess.run(
            ["git", "log", f"-n{commits_to_check}", "--no-merges", "--pretty=format:%h%x09%s"],
            cwd=repo,
            check=False,
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and res.stdout.strip():
            for row in res.stdout.strip().splitlines():
                if "\t" not in row:
                    continue
                sha, subj = row.split("\t", 1)
                commits_checked += 1
                if not CONVENTIONAL_RE.match(subj):
                    findings.append({
                        "file": f"commit:{sha}",
                        "line": 1,
                        "severity": "LOW",
                        "rule": "git-non-conventional-commit",
                        "message": f"Commit subject '{subj}' does not follow Conventional Commits.",
                    })

    return {
        "files_scanned": scanned_files,
        "commits_checked": commits_checked,
        "count": len(findings),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Git repo for conflict markers, large files, and Conventional Commits.")
    parser.add_argument("target", type=Path, nargs="?", default=Path.cwd(), help="Repository directory.")
    parser.add_argument("--max-file-kb", type=int, default=1024)
    parser.add_argument("--commits", type=int, default=10)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.is_dir():
        print(f"ERROR: Directory not found: {args.target}", file=sys.stderr)
        return 2

    res = audit_repo(args.target, max_file_kb=args.max_file_kb, commits_to_check=args.commits)
    if args.as_json:
        print(json.dumps(res, indent=2))
    elif res["findings"]:
        for f in res["findings"]:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {res['files_scanned']} file(s) and {res['commits_checked']} commit(s), 0 hygiene issues.")
    return 1 if any(f["severity"] in {"CRITICAL", "HIGH"} for f in res["findings"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
