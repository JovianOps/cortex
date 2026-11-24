#!/usr/bin/env python3
"""Zero-dependency Go production reliability and concurrency auditor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {"vendor", ".git", "node_modules"}


def audit_go_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    is_test = path.name.endswith("_test.go")
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue

        if not is_test and re.search(r"\bhttp\.ListenAndServe(?:TLS)?\s*\(", line):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "HIGH",
                "rule": "go-http-no-timeouts",
                "message": "http.ListenAndServe omits ReadHeaderTimeout/ReadTimeout/WriteTimeout; construct an explicit &http.Server{}.",
            })
        if not is_test and re.search(r"\bhttp\.(?:Get|Post|Head)\s*\(", line):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "HIGH",
                "rule": "go-default-http-client",
                "message": "Default http.Get/Post has no timeout; use http.NewRequestWithContext and a client with explicit Timeout.",
            })
        if not is_test and re.search(r"\b_\s*=\s*\w+(?:\.\w+)*\s*\(", line):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "MEDIUM",
                "rule": "go-ignored-return-value",
                "message": "Explicitly handle returned error instead of discarding with '_ = ...'.",
            })
        if not is_test and re.search(r"\bpanic\s*\(", line):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "HIGH",
                "rule": "go-panic-in-runtime",
                "message": "Return an explicit error instead of calling panic() in production code.",
            })
        if "InsecureSkipVerify: true" in line:
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "CRITICAL",
                "rule": "go-tls-insecure-skip-verify",
                "message": "TLS InsecureSkipVerify: true disables certificate verification.",
            })
        if re.search(r"\bcontext\.TODO\s*\(", line):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "LOW",
                "rule": "go-context-todo",
                "message": "Replace context.TODO() with a propagated caller context.",
            })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Go source files for timeouts, error handling, and TLS safety.")
    parser.add_argument("target", type=Path, help="Go .go file or module directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    files = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*.go") if not any(part in SKIP_DIRS for part in p.parts)
    )
    findings: list[dict] = []
    for fp in files:
        findings.extend(audit_go_file(fp))

    if args.as_json:
        print(json.dumps({"files_scanned": len(files), "count": len(findings), "findings": findings}, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {len(files)} Go file(s), 0 issues found.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
