#!/usr/bin/env python3
"""Zero-dependency GDPR/CCPA raw PII & unmasked logging scanner with Luhn validation."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    "coverage", ".next", "target", "vendor", ".terraform", ".pytest_cache",
    ".opencode", ".claude", ".cursor", ".windsurf", ".cline", ".agents",
    ".codex", ".gemini", ".openclaw", ".goose", ".aider", ".githooks",
    "zips", "premium-zips",
}
SSN_RE = re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")
CC_RE = re.compile(r"\b(?:\d[ -]*?){13,16}\b")
LOG_PII_RE = re.compile(
    r"(?i)\b(?:logger\.\w+|logging\.\w+|console\.(?:log|info|warn|error|debug)|print)\s*\([^)]*\b"
    r"(?:ssn|social_security|credit_card|card_number|password|passport_no|dob|tax_id|national_id|drivers_license|bank_account|iban|api_key|access_token|refresh_token)\b"
)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@(?!example\.com\b|example\.org\b|users\.noreply\.github\.com\b|test\.local\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(part in SKIP_DIRS for part in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def luhn_valid(digits: str) -> bool:
    if not digits.isdigit() or not (13 <= len(digits) <= 19):
        return False
    total = 0
    rev = digits[::-1]
    for i, ch in enumerate(rev):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def redact(val: str) -> str:
    if len(val) <= 6:
        return "***"
    return val[:2] + "*" * (len(val) - 4) + val[-2:]


def scan_file(path: Path, check_emails: bool = False) -> list[dict]:
    findings: list[dict] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.lstrip()
        if stripped.startswith(("#", "//", "/*", "*")):
            continue
        for m in SSN_RE.finditer(line):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "CRITICAL",
                "rule": "pii-raw-ssn",
                "message": f"Possible raw US SSN detected ({redact(m.group(0))}); tokenize or replace with synthetic fixture.",
            })
        for m in CC_RE.finditer(line):
            digits = re.sub(r"\D", "", m.group(0))
            if luhn_valid(digits) and len(set(digits)) > 2:
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "CRITICAL",
                    "rule": "pii-luhn-payment-card",
                    "message": f"Possible Luhn-valid payment card number detected ({redact(digits)}).",
                })
        if "re.compile(" not in line and LOG_PII_RE.search(line):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "HIGH",
                "rule": "pii-logged-sensitive-field",
                "message": "Sensitive PII/credential field appears inside a log/print statement; redact before emitting logs.",
            })
        if check_emails:
            for m in EMAIL_RE.finditer(line):
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "LOW",
                    "rule": "pii-personal-email",
                    "message": f"Non-example email address found ({redact(m.group(0))}).",
                })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan source files, fixtures, and logs for raw PII and unmasked PII logging.")
    parser.add_argument("target", type=Path, help="File or directory to scan.")
    parser.add_argument("--check-emails", action="store_true", help="Also flag non-example email addresses.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    exts = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".json", ".yaml", ".yml", ".csv", ".log", ".sql", ".txt"}
    files = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*")
        if p.is_file() and p.suffix.lower() in exts and not should_skip(p, args.target)
    )
    findings: list[dict] = []
    for fp in files:
        findings.extend(scan_file(fp, check_emails=args.check_emails))

    if args.as_json:
        print(json.dumps({"files_scanned": len(files), "count": len(findings), "findings": findings}, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Scanned {len(files)} file(s) for raw PII, 0 findings.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
