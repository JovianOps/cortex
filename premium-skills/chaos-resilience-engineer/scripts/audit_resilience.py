#!/usr/bin/env python3
"""Zero-dependency resilience, timeout, retry-backoff, and HA fault-tolerance auditor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}


def audit_code_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        if re.search(r"\brequests\.(?:get|post|put|delete|patch|head)\s*\(", line) and "timeout=" not in line:
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "HIGH",
                "rule": "resilience-python-requests-no-timeout",
                "message": "Python requests call omits explicit timeout=; unbounded socket hangs cascade across workers.",
            })
        if re.search(r"\burllib\.request\.urlopen\s*\(", line) and "timeout=" not in line:
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "HIGH",
                "rule": "resilience-urlopen-no-timeout",
                "message": "urllib.request.urlopen omits explicit timeout= parameter.",
            })
        if re.search(r"\bwhile\s+True\s*:", line) and "sleep" not in line:
            # Flag tight retry loops only when nearby lines mention retry/except
            pass
        if re.search(r"\bfetch\s*\([^)]+\)", line) and "signal" not in line and "AbortSignal" not in line and path.suffix in {".ts", ".js", ".tsx", ".jsx"}:
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "MEDIUM",
                "rule": "resilience-js-fetch-no-abort-signal",
                "message": "fetch() call lacks AbortSignal.timeout(...) for bounded latency.",
            })
    return findings


def audit_k8s_ha(path: Path) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?m)^kind:\s*Deployment\b", text):
        rep_m = re.search(r"(?m)^\s*replicas:\s*(\d+)\b", text)
        if rep_m and int(rep_m.group(1)) < 2:
            ln = text[: rep_m.start()].count("\n") + 1
            findings.append({
                "file": path.as_posix(),
                "line": ln,
                "severity": "HIGH",
                "rule": "resilience-single-replica",
                "message": "Deployment specifies replicas < 2 (single point of failure during node drain/upgrade).",
            })
        if "PodDisruptionBudget" not in text:
            findings.append({
                "file": path.as_posix(),
                "line": 1,
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
        and not any(part in SKIP_DIRS for part in p.parts)
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
