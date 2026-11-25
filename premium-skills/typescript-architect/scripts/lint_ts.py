#!/usr/bin/env python3
"""Zero-dependency TypeScript & React static safety and tsconfig strictness auditor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    "node_modules", "dist", "build", ".next", ".nuxt", ".output", "coverage",
    ".git", ".venv", "__pycache__", ".opencode", ".claude", ".cursor",
    ".windsurf", ".cline", ".agents", ".codex", ".gemini", ".openclaw",
    ".goose", ".aider", "zips", "premium-zips",
}

TS_RULES: list[tuple[str, str, re.Pattern[str], str]] = [
    ("CRITICAL", "ts-eval-or-new-function", re.compile(r"\b(?:eval\s*\(|new\s+Function\s*\()"), "Avoid eval() / new Function() due to code-injection risk."),
    ("HIGH", "ts-dangerous-inner-html", re.compile(r"\bdangerouslySetInnerHTML\b"), "dangerouslySetInnerHTML requires explicit HTML sanitization (e.g., DOMPurify)."),
    ("HIGH", "ts-ignore-directive", re.compile(r"//\s*@ts-(?:ignore|nocheck)\b"), "Replace @ts-ignore/@ts-nocheck with @ts-expect-error + justification or fix the type."),
    ("MEDIUM", "ts-explicit-any", re.compile(r"(?::\s*any\b|\bas\s+any\b|<any>)"), "Avoid explicit 'any'; use 'unknown' with runtime type narrowing."),
    ("MEDIUM", "ts-non-null-assertion-chain", re.compile(r"\w+!\.\w+!\."), "Chained non-null assertions (!.) hide null/undefined runtime crashes."),
    ("LOW", "ts-console-debug", re.compile(r"\bconsole\.(?:log|debug)\s*\("), "Replace console.log/debug with structured application logging."),
]


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(part in SKIP_DIRS for part in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def strip_json_comments(raw: str) -> str:
    raw = re.sub(r"/\*[\s\S]*?\*/", "", raw)
    raw = re.sub(r"(?m)^\s*//.*$", "", raw)
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    return raw


def audit_tsconfig(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        data = json.loads(strip_json_comments(path.read_text(encoding="utf-8", errors="replace")))
    except json.JSONDecodeError as exc:
        return [{"file": path.as_posix(), "line": 1, "severity": "HIGH", "rule": "tsconfig-invalid-json", "message": f"Invalid tsconfig JSON: {exc}"}]

    if isinstance(data, dict) and "extends" in data and not data.get("compilerOptions"):
        return findings

    opts = data.get("compilerOptions", {}) if isinstance(data, dict) else {}
    if opts.get("strict") is not True:
        findings.append({"file": path.as_posix(), "line": 1, "severity": "HIGH", "rule": "tsconfig-strict-disabled", "message": "Enable compilerOptions.strict = true."})
    if opts.get("noUncheckedIndexedAccess") is not True:
        findings.append({"file": path.as_posix(), "line": 1, "severity": "MEDIUM", "rule": "tsconfig-unchecked-indexed-access", "message": "Enable compilerOptions.noUncheckedIndexedAccess = true for safer array/record indexing."})
    if opts.get("noImplicitOverride") is not True:
        findings.append({"file": path.as_posix(), "line": 1, "severity": "LOW", "rule": "tsconfig-implicit-override", "message": "Enable compilerOptions.noImplicitOverride = true."})
    return findings


def audit_ts_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    is_test = bool(re.search(r"\.(?:test|spec)\.[mc]?tsx?$", path.name))
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("*") or stripped.startswith("/*"):
            continue
        is_line_comment = stripped.startswith("//")
        for sev, rule, pat, msg in TS_RULES:
            if is_line_comment and rule != "ts-ignore-directive":
                continue
            if rule == "ts-console-debug" and is_test:
                continue
            if pat.search(line):
                findings.append({"file": path.as_posix(), "line": idx, "severity": sev, "rule": rule, "message": msg})
    return findings


def collect_targets(target: Path) -> tuple[list[Path], list[Path]]:
    if target.is_file():
        if target.name == "tsconfig.json" or (target.name.startswith("tsconfig.") and target.suffix == ".json"):
            return [target], []
        return [], [target]
    tsconfigs: list[Path] = []
    ts_files: list[Path] = []
    for p in sorted(target.rglob("*")):
        if not p.is_file() or should_skip(p, target):
            continue
        if p.name == "tsconfig.json" or (p.name.startswith("tsconfig.") and p.suffix == ".json"):
            tsconfigs.append(p)
        elif p.suffix in {".ts", ".tsx", ".mts", ".cts"} and not p.name.endswith(".d.ts"):
            ts_files.append(p)
    return tsconfigs, ts_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit TypeScript source files and tsconfig.json strictness.")
    parser.add_argument("target", type=Path, help="TypeScript file, tsconfig.json, or project directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    tsconfigs, ts_files = collect_targets(args.target)
    findings: list[dict] = []
    for cfg in tsconfigs:
        findings.extend(audit_tsconfig(cfg))
    for fp in ts_files:
        findings.extend(audit_ts_file(fp))

    if args.as_json:
        print(json.dumps({"tsconfigs": len(tsconfigs), "ts_files": len(ts_files), "count": len(findings), "findings": findings}, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {len(tsconfigs)} tsconfig(s) and {len(ts_files)} TypeScript file(s), 0 issues found.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
