#!/usr/bin/env python3
"""Zero-dependency OWASP LLM Top 10 prompt-injection and agent-config security auditor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", "dist", "build", ".venv", "venv",
    "coverage", ".next", "target", "vendor", ".pytest_cache",
    ".opencode", ".claude", ".cursor", ".windsurf", ".cline", ".agents",
    ".codex", ".gemini", ".openclaw", ".goose", ".aider", ".githooks",
    "zips", "premium-zips",
}

INJECTION_PATTERNS: list[tuple[str, str, re.Pattern[str], str]] = [
    ("CRITICAL", "llm-override-instructions", re.compile(r"(?i)\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions\b"), "Prompt contains classic instruction-override phrase."),
    ("CRITICAL", "llm-exfil-shell-pipe", re.compile(r"(?i)\b(?:curl|wget)\b[^\n|]*\|\s*(?:sh|bash|zsh)\b"), "Agent instruction pipes remote content directly into a shell."),
    ("HIGH", "llm-secret-exfil-prompt", re.compile(r"(?i)\b(?:print|reveal|exfiltrate|send)\s+(?:all\s+)?(?:system\s+prompt|env(?:ironment)?\s+variables|api\s+keys?)\b"), "Potential system-prompt or credential exfiltration instruction."),
    ("HIGH", "llm-zero-width-obfuscation", re.compile(r"[\u200b-\u200f\u202a-\u202e\ufeff]"), "Hidden Unicode zero-width or BiDi control characters detected (possible hidden prompt injection)."),
    ("HIGH", "llm-untrusted-fstring-prompt", re.compile(r"(?:system_prompt|SYSTEM_PROMPT)\s*=\s*f['\"]"), "System prompt built with Python f-string interpolation; separate untrusted user input into user messages."),
    ("MEDIUM", "llm-unrestricted-auto-approve", re.compile(r"(?i)(?:[\"']?(?:auto_approve|autoApprove|dangerouslySkipPermissions|dangerouslyAllowAll|skip_confirmation)[\"']?\s*[:=]\s*true|permission_mode[\"']?\s*[:=]\s*[\"']bypassPermissions[\"'])"), "Unrestricted auto-approval bypasses human-in-the-loop safety gates."),
]

INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(part in SKIP_DIRS for part in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def audit_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    is_markdown = path.suffix.lower() in {".md", ".mdx"}
    fence_char: str | None = None
    for idx, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        if is_markdown and (stripped.startswith("```") or stripped.startswith("~~~")):
            marker = stripped[:3]
            if fence_char is None:
                fence_char = marker
                continue
            if fence_char == marker:
                fence_char = None
                continue
        if is_markdown and fence_char is not None:
            continue
        for sev, rule, pat, msg in INJECTION_PATTERNS:
            target_line = line
            if rule == "llm-exfil-shell-pipe" and is_markdown:
                target_line = INLINE_CODE_RE.sub("", line)
            if pat.search(target_line):
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": sev,
                    "rule": rule,
                    "message": msg,
                })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit prompts, skills, and LLM integration files for prompt-injection and agent security risks.")
    parser.add_argument("target", type=Path, help="Prompt/config/source file or directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    exts = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".ts", ".js", ".prompt"}
    files = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*")
        if p.is_file() and p.suffix.lower() in exts and not should_skip(p, args.target)
    )
    findings: list[dict] = []
    for fp in files:
        findings.extend(audit_file(fp))

    if args.as_json:
        print(json.dumps({"files_scanned": len(files), "count": len(findings), "findings": findings}, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {len(files)} file(s) for OWASP LLM security risks, 0 findings.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
