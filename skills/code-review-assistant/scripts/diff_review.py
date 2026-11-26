#!/usr/bin/env python3
"""Deterministic unified-diff risk & hygiene pre-reviewer for code-review-assistant skill."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

DEBUG_PATTERNS = [
    (re.compile(r"\bconsole\.log\s*\("), "Leftover console.log()"),
    (re.compile(r"\bdebugger\b"), "Leftover debugger statement"),
    (re.compile(r"\b(pdb\.set_trace|breakpoint)\s*\("), "Leftover Python debugger breakpoint"),
    (re.compile(r"\bTODO\b|\bFIXME\b"), "Unresolved TODO/FIXME added in diff"),
]
CODE_EXTS = (".py", ".js", ".mjs", ".cjs", ".ts", ".mts", ".cts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".php", ".kt", ".swift")


def analyze_diff(diff_text: str) -> dict:
    files: list[str] = []
    added_lines = 0
    removed_lines = 0
    findings: list[dict] = []
    current_file = "<unknown>"

    for line in diff_text.splitlines():
        if line.startswith("+++ b/"):
            current_file = line[6:].split("\t", 1)[0].strip()
            if current_file not in files:
                files.append(current_file)
            continue
        if line.startswith("+") and not line.startswith("+++"):
            added_lines += 1
            body = line[1:]
            for rx, msg in DEBUG_PATTERNS:
                if rx.search(body):
                    findings.append({"severity": "MEDIUM", "file": current_file, "message": msg})
        elif line.startswith("-") and not line.startswith("---"):
            removed_lines += 1

    code_files = [f for f in files if f.endswith(CODE_EXTS) and "test" not in f.lower() and "spec" not in f.lower()]
    test_files = [f for f in files if "test" in f.lower() or "spec" in f.lower()]
    if code_files and not test_files:
        findings.append({
            "severity": "MEDIUM",
            "file": ", ".join(code_files[:3]),
            "message": "Production source files changed with no companion test file edits.",
        })

    return {
        "files_changed": len(files),
        "added_lines": added_lines,
        "removed_lines": removed_lines,
        "findings": findings,
    }


def _read_dir_git_diff(repo_dir: Path) -> str:
    res = subprocess.run(["git", "diff", "HEAD"], cwd=repo_dir, capture_output=True, text=True, check=False)
    if res.returncode != 0:
        res = subprocess.run(["git", "diff"], cwd=repo_dir, capture_output=True, text=True, check=False)
    return res.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze a unified diff file (or git directory) for review risks and debug leftovers.")
    parser.add_argument("diff_file", type=Path, help="Path to unified diff file, git directory, or '-' for stdin.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if str(args.diff_file) == "-":
        text = sys.stdin.read()
    elif args.diff_file.is_dir():
        text = _read_dir_git_diff(args.diff_file)
    elif args.diff_file.is_file():
        text = args.diff_file.read_text(encoding="utf-8", errors="replace")
    else:
        print(f"ERROR: Diff path not found: {args.diff_file}", file=sys.stderr)
        return 2

    report = analyze_diff(text)
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Diff summary: {report['files_changed']} file(s), +{report['added_lines']}/-{report['removed_lines']}, {len(report['findings'])} finding(s)")
        for f in report["findings"]:
            print(f"[{f['severity']}] {f['file']} — {f['message']}")
    return 1 if report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
