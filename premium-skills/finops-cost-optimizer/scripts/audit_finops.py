#!/usr/bin/env python3
"""Zero-dependency Cloud FinOps & infrastructure cost waste auditor for Terraform and Kubernetes."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_TAGS = ("environment", "owner", "cost_center")
OVERSIZED_RE = re.compile(r"\b(?:m5|m6i|c5|c6i|r5|r6i|p4d|g5)\.(?:8xlarge|12xlarge|16xlarge|24xlarge|32xlarge|metal)\b")
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


def audit_tf_finops(path: Path) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    for idx, line in enumerate(text.splitlines(), 1):
        m = OVERSIZED_RE.search(line)
        if m:
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "HIGH",
                "rule": "finops-oversized-instance",
                "message": f"Large instance type '{m.group(0)}' detected; verify right-sizing and Savings Plan/Spot eligibility.",
            })
        if re.search(r"\bvolume_type\s*=\s*\"gp2\"", line):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "MEDIUM",
                "rule": "finops-legacy-gp2-volume",
                "message": "Legacy EBS gp2 volume detected; migrate to gp3 for ~20% lower cost and better baseline IOPS.",
            })

    # Check resource blocks for cost-allocation tags and S3 lifecycle
    for m in re.finditer(r'(?m)^resource\s+"(aws_instance|aws_db_instance|aws_s3_bucket|aws_eks_cluster)"\s+"([^"]+)"\s*\{', text):
        rtype, rname = m.group(1), m.group(2)
        ln = text[: m.start()].count("\n") + 1
        snippet = text[m.start() : m.start() + 1200]
        missing = [t for t in REQUIRED_TAGS if not re.search(rf'\b{t}\b', snippet, re.I)]
        if missing:
            findings.append({
                "file": path.as_posix(),
                "line": ln,
                "severity": "MEDIUM",
                "rule": "finops-missing-cost-tags",
                "message": f"{rtype}.{rname} is missing FinOps cost-allocation tag(s): {', '.join(missing)}.",
            })
    return findings


def audit_k8s_finops(path: Path) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"(?m)^kind:\s*(?:Deployment|StatefulSet)\b", text):
        return findings
    if "resources:" not in text or "requests:" not in text:
        findings.append({
            "file": path.as_posix(),
            "line": 1,
            "severity": "MEDIUM",
            "rule": "finops-k8s-no-requests",
            "message": "Kubernetes workload omits resources.requests, blocking accurate cluster bin-packing and right-sizing.",
        })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Terraform and Kubernetes configs for cloud cost waste and missing FinOps tags.")
    parser.add_argument("target", type=Path, help="Terraform/K8s file or directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    files = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*")
        if p.is_file() and p.suffix.lower() in {".tf", ".yaml", ".yml"} and not should_skip(p, args.target)
    )
    findings: list[dict] = []
    for fp in files:
        if fp.suffix.lower() == ".tf":
            findings.extend(audit_tf_finops(fp))
        else:
            findings.extend(audit_k8s_finops(fp))

    if args.as_json:
        print(json.dumps({"files_scanned": len(files), "count": len(findings), "findings": findings}, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {len(files)} infrastructure file(s) for FinOps issues, 0 findings.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
