#!/usr/bin/env python3
"""Deterministic offline secret & dangerous-sink scanner for security-auditor skill.

Zero external dependencies (Python 3 stdlib only).
Always redacts detected secret values (never echoes raw credentials).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".private"}
TEXT_SUFFIXES = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".mjs", ".cjs", ".go", ".rs", ".java",
    ".rb", ".php", ".sh", ".ps1", ".yml", ".yaml", ".json", ".toml", ".env", ".ini", ".cfg",
}

SECRET_RULES: tuple[tuple[str, str, str, re.Pattern[str]], ...] = (
    ("CRITICAL", "CWE-798", "AWS Access Key ID", re.compile(r"\b(AKIA[0-9A-Z]{16})\b")),
    ("CRITICAL", "CWE-798", "GitHub Personal Access Token", re.compile(r"\b(gh[pousr]_[A-Za-z0-9_]{36,})\b")),
    ("CRITICAL", "CWE-798", "OpenAI / Stripe Secret Key", re.compile(r"\b(sk-(?:live-|proj-)?[A-Za-z0-9_-]{20,})\b")),
    ("CRITICAL", "CWE-798", "Private Key Material", re.compile(r"(-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----)")),
)

SINK_RULES: tuple[tuple[str, str, str, re.Pattern[str]], ...] = (
    ("HIGH", "CWE-78", "Shell injection risk (shell=True)", re.compile(r"subprocess\.\w+\([^)]*shell\s*=\s*True")),
    ("HIGH", "CWE-94", "Dynamic code execution (eval/exec)", re.compile(r"(?<![.\w])(?:eval|exec)\s*\(")),
    ("HIGH", "CWE-502", "Unsafe YAML deserialization (yaml.load without SafeLoader)", re.compile(r"yaml\.load\s*\((?![^)]*SafeLoader)")),
    ("HIGH", "CWE-502", "Unsafe pickle deserialization", re.compile(r"pickle\.loads?\s*\(")),
    ("MEDIUM", "CWE-327", "Weak cryptographic hash (MD5/SHA1)", re.compile(r"hashlib\.(?:md5|sha1)\s*\(")),
    ("MEDIUM", "CWE-79", "Raw HTML injection sink", re.compile(r"dangerouslySetInnerHTML|\.innerHTML\s*=")),
)


def redact(secret: str) -> str:
    if len(secret) <= 8:
        return "****"
    return f"{secret[:4]}****...{secret[-4:]}"


def iter_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    files: list[Path] = []
    for path in sorted(target.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file() and (path.suffix.lower() in TEXT_SUFFIXES or path.name.startswith(".env")):
            files.append(path)
    return files


def scan_path(target: Path) -> list[dict]:
    findings: list[dict] = []
    for file_path in iter_files(target):
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, start=1):
            for severity, cwe, title, pattern in SECRET_RULES:
                match = pattern.search(line)
                if match:
                    findings.append({
                        "severity": severity,
                        "cwe": cwe,
                        "title": title,
                        "file": file_path.as_posix(),
                        "line": lineno,
                        "evidence": redact(match.group(1)),
                    })
            for severity, cwe, title, pattern in SINK_RULES:
                if pattern.search(line):
                    findings.append({
                        "severity": severity,
                        "cwe": cwe,
                        "title": title,
                        "file": file_path.as_posix(),
                        "line": lineno,
                        "evidence": line.strip()[:120],
                    })
    return findings


def sanitize_findings_for_output(findings: list[dict]) -> list[dict]:
    sanitized: list[dict] = []
    for finding in findings:
        sanitized_finding = dict(finding)
        if "evidence" in sanitized_finding:
            sanitized_finding["evidence"] = "[REDACTED]"
        sanitized.append(sanitized_finding)
    return sanitized


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline secret & dangerous-sink scanner (CWE-mapped, auto-redacted).")
    parser.add_argument("target", type=Path, help="File or directory to scan.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args(argv)
    if not args.target.exists():
        print(f"ERROR: Path not found: {args.target}", file=sys.stderr)
        return 2
    findings = scan_path(args.target)
    findings_for_output = sanitize_findings_for_output(findings)
    for f in findings_for_output:
        f["severity"] = str(f.get("severity", "UNKNOWN"))
        f["cwe"] = str(f.get("cwe", "N/A"))
        f["title"] = str(f.get("title", "Unknown finding"))[:200]
        f["file"] = str(f.get("file", ""))[:500]
        f["line"] = int(f.get("line", 0))
    if args.format == "json":
        print(json.dumps({"target": args.target.as_posix(), "count": len(findings_for_output), "findings": findings_for_output}, indent=2))
    else:
        print(f"# Security Scan Summary ({len(findings_for_output)} finding(s))\n")
        for f in findings_for_output:
            print(f"- **[{f['severity']}] {f['title']} ({f['cwe']})** — `{f['file']}:{f['line']}` (`{f['evidence']}`)")
        if not findings_for_output:
            print("No hardcoded secrets or high-risk sink patterns detected.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
