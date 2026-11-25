#!/usr/bin/env python3
"""Deterministic SQL query & migration anti-pattern linter for db-optimizer skill."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    "coverage", ".next", "target", "vendor", ".pytest_cache",
    ".opencode", ".claude", ".cursor", ".windsurf", ".cline", ".agents",
    ".codex", ".gemini", ".openclaw", ".goose", ".aider", "zips", "premium-zips",
}


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(part in SKIP_DIRS for part in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def lint_sql_text(text: str, filename: str) -> list[dict]:
    findings: list[dict] = []
    lines = text.splitlines()
    for idx, raw in enumerate(lines, 1):
        code = raw.split("--", 1)[0].strip()
        if not code:
            continue

        if re.search(r"(?i)\bSELECT\s+\*", code):
            findings.append({
                "severity": "MEDIUM",
                "rule": "select-star",
                "file": filename,
                "line": idx,
                "message": "Avoid SELECT *; project explicit columns to enable index-only scans.",
            })

        if re.search(r"(?i)\bLIKE\s+'%", code):
            findings.append({
                "severity": "HIGH",
                "rule": "leading-wildcard-like",
                "file": filename,
                "line": idx,
                "message": "Leading wildcard LIKE '%...' prevents B-tree index usage; consider trigram/FTS index.",
            })

        if re.search(r"(?i)\bOFFSET\s+[1-9]\d{2,}\b", code):
            findings.append({
                "severity": "MEDIUM",
                "rule": "deep-offset-pagination",
                "file": filename,
                "line": idx,
                "message": "Large OFFSET scans and discards rows; prefer keyset/cursor pagination.",
            })

        if re.search(r"(?i)\bORDER\s+BY\s+RANDOM\s*\(\s*\)", code):
            findings.append({
                "severity": "HIGH",
                "rule": "order-by-random",
                "file": filename,
                "line": idx,
                "message": "ORDER BY RANDOM() forces a full-table sort.",
            })

    # Statement-level check for DELETE/UPDATE without WHERE (with accurate start line)
    offset = 0
    for stmt in re.split(r";", text):
        cleaned = re.sub(r"--[^\n]*", "", stmt).strip()
        if cleaned:
            stmt_ln = text[:offset].count("\n") + 1
            if re.match(r"(?i)^(DELETE\s+FROM|UPDATE)\b", cleaned) and not re.search(r"(?i)\bWHERE\b", cleaned):
                findings.append({
                    "severity": "CRITICAL",
                    "rule": "dml-without-where",
                    "file": filename,
                    "line": stmt_ln,
                    "message": "DELETE/UPDATE statement has no WHERE clause and will mutate every row.",
                })
        offset += len(stmt) + 1

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint SQL files for common performance and safety anti-patterns.")
    parser.add_argument("target", type=Path, help="Path to a .sql file or directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.target.exists():
        print(f"ERROR: Path not found: {args.target}", file=sys.stderr)
        return 2

    files = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*.sql") if p.is_file() and not should_skip(p, args.target)
    )
    findings: list[dict] = []
    for fp in files:
        findings.extend(lint_sql_text(fp.read_text(encoding="utf-8", errors="replace"), fp.as_posix()))

    if args.as_json:
        print(json.dumps({"files_checked": len(files), "count": len(findings), "findings": findings}, indent=2))
    elif not findings:
        print(f"OK: {len(files)} SQL file(s) passed all checks.")
    else:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
