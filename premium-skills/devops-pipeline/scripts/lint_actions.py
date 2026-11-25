#!/usr/bin/env python3
"""Deterministic GitHub Actions workflow security linter for devops-pipeline skill.

Zero external dependencies (Python 3 stdlib only).
Checks:
  1. Third-party `uses:` references pinned to full 40-char commit SHAs (not mutable tags like @v4 or @master).
  2. Explicit `permissions:` block defined (and not `write-all`) to enforce least-privilege GITHUB_TOKEN.
  3. Dangerous untrusted expression interpolation (`github.head_ref`, `github.event.issue.title`, `pull_request.title`, etc.) in `run:` blocks.
  4. High-risk `pull_request_target` workflows checking out untrusted PR head refs/SHAs.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

USES_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")
FULL_SHA_RE = re.compile(r"@[0-9a-fA-F]{40}$")
UNTRUSTED_EXPR_RE = re.compile(
    r"\$\{\{\s*(?:github\.head_ref|github\.event\.(?:issue\.title|issue\.body|pull_request\.title|pull_request\.body|pull_request\.head\.ref|pull_request\.head\.label|discussion\.title|discussion\.body|review\.body|comment\.body|head_commit\.message|workflow_run\.head_branch))\s*\}\}"
)


def lint_workflow(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    findings: list[dict] = []
    has_permissions = any(re.match(r"^\s*permissions\s*:", ln) for ln in lines)
    if not has_permissions:
        findings.append({
            "severity": "HIGH",
            "rule": "least-privilege-permissions",
            "file": path.as_posix(),
            "line": 1,
            "message": "Missing explicit `permissions:` block; restrict GITHUB_TOKEN to minimum needed scopes.",
        })
    elif re.search(r"(?m)^\s*permissions\s*:\s*write-all\b", text):
        findings.append({
            "severity": "HIGH",
            "rule": "overbroad-permissions",
            "file": path.as_posix(),
            "line": 1,
            "message": "Avoid `permissions: write-all`; grant explicit least-privilege scopes.",
        })

    uses_prt = bool(re.search(r"(?m)^\s*pull_request_target\b", text))
    if uses_prt and re.search(r"github\.event\.pull_request\.head\.(?:sha|ref)", text):
        findings.append({
            "severity": "CRITICAL",
            "rule": "pull-request-target-pwn",
            "file": path.as_posix(),
            "line": 1,
            "message": "pull_request_target workflow references untrusted PR head SHA/ref (pwn-request risk).",
        })

    for lineno, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        m = USES_RE.match(line)
        if m:
            ref = m.group(1).strip("'\"")
            if not ref.startswith("./") and not ref.startswith("docker://") and not FULL_SHA_RE.search(ref):
                findings.append({
                    "severity": "HIGH",
                    "rule": "pin-action-sha",
                    "file": path.as_posix(),
                    "line": lineno,
                    "message": f"Action {ref!r} is not pinned to a 40-character commit SHA.",
                })
        if UNTRUSTED_EXPR_RE.search(line):
            findings.append({
                "severity": "CRITICAL",
                "rule": "no-script-injection",
                "file": path.as_posix(),
                "line": lineno,
                "message": "Untrusted github.* expression interpolated directly; pass via an env: variable instead.",
            })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint GitHub Actions workflow YAML files for supply-chain & injection risks.")
    parser.add_argument("target", type=Path, help="Workflow file or .github/workflows directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    files = [args.target] if args.target.is_file() else sorted(
        list(args.target.glob("*.yml")) + list(args.target.glob("*.yaml"))
    )
    if not files:
        print(f"ERROR: No workflow YAML files found at {args.target}", file=sys.stderr)
        return 2

    findings: list[dict] = []
    for wf in files:
        findings.extend(lint_workflow(wf))

    severe = [f for f in findings if f["severity"] in {"CRITICAL", "HIGH"}]
    if args.as_json:
        print(json.dumps({"files_checked": len(files), "count": len(findings), "findings": findings}, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
        if not findings:
            print(f"OK: {len(files)} workflow file(s) passed all security checks.")
    return 1 if severe else 0


if __name__ == "__main__":
    raise SystemExit(main())
