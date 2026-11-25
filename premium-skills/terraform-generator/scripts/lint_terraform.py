#!/usr/bin/env python3
"""Deterministic offline Terraform (.tf) security & best-practice linter for terraform-generator skill."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SENSITIVE_PORTS = {"22", "3389", "5432", "3306", "6379", "27017"}
IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".terraform", "dist", "build",
    "coverage", ".next", "target", "vendor",
    ".opencode", ".claude", ".cursor", ".windsurf", ".cline", ".agents",
    ".codex", ".gemini", ".openclaw", ".goose", ".aider", ".githooks",
    "zips", "premium-zips",
}


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(p in IGNORE_DIRS for p in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def lint_tf_text(text: str, filename: str) -> list[dict]:
    findings: list[dict] = []
    lines = text.splitlines()

    if "required_providers" in text and not re.search(r'version\s*=\s*"[^"]+"', text):
        findings.append({
            "severity": "HIGH",
            "rule": "pin-provider-version",
            "file": filename,
            "line": 1,
            "message": "required_providers block has no pinned version constraint.",
        })

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("#", "//")):
            continue

        if re.search(r'0\.0\.0\.0/0|::/0', stripped):
            window = "\n".join(lines[max(0, idx - 8) : min(len(lines), idx + 5)])
            if any(re.search(rf'\b(from_port|to_port|port)\s*=\s*{p}\b', window) for p in SENSITIVE_PORTS):
                findings.append({
                    "severity": "CRITICAL",
                    "rule": "open-admin-port",
                    "file": filename,
                    "line": idx,
                    "message": "Security group exposes administrative/database port to 0.0.0.0/0 or ::/0.",
                })

        if re.search(r'(?i)\b(password|secret_key|access_key|api_key|token)\s*=\s*"[^"$]{6,}"', stripped):
            findings.append({
                "severity": "CRITICAL",
                "rule": "hardcoded-secret",
                "file": filename,
                "line": idx,
                "message": "Possible hardcoded credential in Terraform config; use variables/secrets manager.",
            })

        if re.search(r'(?i)\b(encrypted|storage_encrypted)\s*=\s*false\b', stripped):
            findings.append({
                "severity": "HIGH",
                "rule": "encryption-disabled",
                "file": filename,
                "line": idx,
                "message": "Storage encryption is explicitly disabled.",
            })

        if re.search(r'(?i)\bpublicly_accessible\s*=\s*true\b', stripped):
            findings.append({
                "severity": "HIGH",
                "rule": "public-database",
                "file": filename,
                "line": idx,
                "message": "Resource is marked publicly_accessible = true.",
            })

        if re.search(r'source\s*=\s*"(git::|github\.com/)', stripped) and "ref=" not in stripped:
            findings.append({
                "severity": "MEDIUM",
                "rule": "unpinned-module-ref",
                "file": filename,
                "line": idx,
                "message": "Remote Git module source lacks a pinned ?ref=<tag|sha>.",
            })

    return findings


def scan_target(target: Path) -> tuple[int, list[dict]]:
    files = [target] if target.is_file() else sorted(p for p in target.rglob("*.tf") if not should_skip(p, target))
    findings: list[dict] = []
    for fp in files:
        findings.extend(lint_tf_text(fp.read_text(encoding="utf-8", errors="ignore"), fp.as_posix()))
    return len(files), findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint Terraform (.tf) files for security and version pinning.")
    parser.add_argument("target", type=Path, help="Path to a .tf file or directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.target.exists():
        print(f"ERROR: Path not found: {args.target}", file=sys.stderr)
        return 2

    count, findings = scan_target(args.target)
    if args.as_json:
        print(json.dumps({"files_checked": count, "count": len(findings), "findings": findings}, indent=2))
    elif not findings:
        print(f"OK: {count} Terraform file(s) passed all checks.")
    else:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
