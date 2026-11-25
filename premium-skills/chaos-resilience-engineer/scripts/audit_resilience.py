#!/usr/bin/env python3
"""Zero-dependency resilience, timeout, retry-backoff, and HA fault-tolerance auditor."""
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


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(part in SKIP_DIRS for part in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def audit_code_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "/*", "*")):
            continue
        if re.search(r"\brequests\.(?:get|post|put|delete|patch|head|request)\s*\(", line) and "timeout=" not in line:
            snippet = "\n".join(lines[idx - 1 : min(len(lines), idx + 4)])
            if "timeout=" not in snippet:
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "HIGH",
                    "rule": "resilience-python-requests-no-timeout",
                    "message": "Python requests call omits explicit timeout=; unbounded socket hangs cascade across workers.",
                })
        if re.search(r"\bhttpx\.(?:get|post|put|delete|patch|head|request)\s*\(", line):
            snippet = "\n".join(lines[idx - 1 : min(len(lines), idx + 4)])
            if "timeout=" not in snippet:
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "HIGH",
                    "rule": "resilience-python-httpx-no-timeout",
                    "message": "Python httpx call omits explicit timeout= parameter.",
                })
        if re.search(r"\burllib\.request\.urlopen\s*\(", line) and "timeout=" not in line:
            snippet = "\n".join(lines[idx - 1 : min(len(lines), idx + 4)])
            if "timeout=" not in snippet:
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "HIGH",
                    "rule": "resilience-urlopen-no-timeout",
                    "message": "urllib.request.urlopen omits explicit timeout= parameter.",
                })
        if path.suffix == ".py" and re.search(r"\bwhile\s+True\s*:", line):
            window = "\n".join(lines[idx - 1 : min(len(lines), idx + 10)])
            if re.search(r"\b(?:except|retry)\b", window) and not re.search(r"\b(?:sleep|backoff|wait|break)\b", window):
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "MEDIUM",
                    "rule": "resilience-tight-retry-loop",
                    "message": "Unbounded 'while True:' retry/except block lacks sleep/backoff or loop exit.",
                })
        if path.suffix in {".ts", ".js", ".tsx", ".jsx"} and re.search(r"\bfetch\s*\(", line):
            snippet = "\n".join(lines[idx - 1 : min(len(lines), idx + 5)])
            if "signal" not in snippet and "AbortSignal" not in snippet:
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "MEDIUM",
                    "rule": "resilience-js-fetch-no-abort-signal",
                    "message": "fetch() call lacks AbortSignal.timeout(...) for bounded latency.",
                })
    return findings


def split_yaml_docs(text: str) -> list[tuple[int, str]]:
    docs: list[tuple[int, str]] = []
    start = 1
    buf: list[str] = []
    for idx, line in enumerate(text.splitlines(), 1):
        if line.strip() == "---":
            if any(ln.strip() and not ln.strip().startswith("#") for ln in buf):
                docs.append((start, "\n".join(buf)))
            buf = []
            start = idx + 1
        else:
            buf.append(line)
    if any(ln.strip() and not ln.strip().startswith("#") for ln in buf):
        docs.append((start, "\n".join(buf)))
    return docs


def audit_k8s_ha(path: Path) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    has_pdb_anywhere = bool(re.search(r"(?m)^kind:\s*PodDisruptionBudget\b", text))
    for start_line, doc in split_yaml_docs(text):
        if re.search(r"(?m)^kind:\s*Deployment\b", doc):
            rep_m = re.search(r"(?m)^\s*replicas:\s*(\d+)\b", doc)
            if rep_m and int(rep_m.group(1)) < 2:
                ln = start_line + doc[: rep_m.start()].count("\n")
                findings.append({
                    "file": path.as_posix(),
                    "line": ln,
                    "severity": "HIGH",
                    "rule": "resilience-single-replica",
                    "message": "Deployment specifies replicas < 2 (single point of failure during node drain/upgrade).",
                })
            if not has_pdb_anywhere:
                findings.append({
                    "file": path.as_posix(),
                    "line": start_line,
                    "severity": "LOW",
                    "rule": "resilience-missing-pdb",
                    "message": "Consider pairing production Deployment with a PodDisruptionBudget.",
                })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit services and K8s manifests for missing timeouts and single points of failure.")
    parser.add_argument("target", type=Path, help="Source/config file or directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    files = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*")
        if p.is_file() and p.suffix.lower() in {".py", ".ts", ".js", ".tsx", ".jsx", ".yaml", ".yml"}
        and not should_skip(p, args.target)
    )
    findings: list[dict] = []
    for fp in files:
        if fp.suffix.lower() in {".yaml", ".yml"}:
            findings.extend(audit_k8s_ha(fp))
        else:
            findings.extend(audit_code_file(fp))

    if args.as_json:
        print(json.dumps({"files_scanned": len(files), "count": len(findings), "findings": findings}, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {len(files)} file(s) for resilience flaws, 0 findings.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
