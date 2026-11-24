#!/usr/bin/env python3
"""Zero-dependency Kubernetes & Helm manifest security and reliability auditor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WORKLOAD_KINDS = {"Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "Pod", "ReplicaSet"}


def split_documents(text: str) -> list[tuple[int, str]]:
    docs: list[tuple[int, str]] = []
    start_line = 1
    buf: list[str] = []
    for idx, line in enumerate(text.splitlines(), 1):
        if line.strip() == "---":
            if any(l.strip() and not l.strip().startswith("#") for l in buf):
                docs.append((start_line, "\n".join(buf)))
            buf = []
            start_line = idx + 1
        else:
            buf.append(line)
    if any(l.strip() and not l.strip().startswith("#") for l in buf):
        docs.append((start_line, "\n".join(buf)))
    return docs


def audit_k8s_text(path_str: str, text: str) -> list[dict]:
    findings: list[dict] = []
    for start_line, doc in split_documents(text):
        kind_m = re.search(r"(?m)^kind:\s*([A-Za-z0-9_]+)", doc)
        kind = kind_m.group(1) if kind_m else ""
        if kind not in WORKLOAD_KINDS:
            continue

        def add(severity: str, rule: str, msg: str, line: int = start_line) -> None:
            findings.append({
                "file": path_str,
                "line": line,
                "kind": kind,
                "severity": severity,
                "rule": rule,
                "message": msg,
            })

        # Privileged containers
        for m in re.finditer(r"(?m)^\s*privileged:\s*true\b", doc):
            ln = start_line + doc[: m.start()].count("\n")
            add("CRITICAL", "k8s-privileged-container", "Container runs with privileged: true; drop privileges.", ln)

        # Host namespaces
        for flag in ("hostNetwork", "hostPID", "hostIPC"):
            for m in re.finditer(rf"(?m)^\s*{flag}:\s*true\b", doc):
                ln = start_line + doc[: m.start()].count("\n")
                add("HIGH", f"k8s-{flag.lower()}", f"Workload enables {flag}: true, breaking pod isolation.", ln)

        # Unpinned or :latest images
        for m in re.finditer(r"(?m)^\s*-?\s*image:\s*['\"]?([^\s'\"]+)['\"]?", doc):
            img = m.group(1)
            ln = start_line + doc[: m.start()].count("\n")
            if img.endswith(":latest") or (":" not in img and "@" not in img):
                add("HIGH", "k8s-unpinned-image", f"Image '{img}' uses :latest or omits an immutable tag/digest.", ln)

        # SecurityContext checks
        if not re.search(r"(?m)^\s*runAsNonRoot:\s*true\b", doc):
            add("HIGH", "k8s-run-as-non-root", f"{kind} does not enforce securityContext.runAsNonRoot: true.")
        if not re.search(r"(?m)^\s*readOnlyRootFilesystem:\s*true\b", doc):
            add("MEDIUM", "k8s-readonly-root-fs", f"{kind} does not set readOnlyRootFilesystem: true.")
        if not re.search(r"(?m)^\s*allowPrivilegeEscalation:\s*false\b", doc):
            add("HIGH", "k8s-allow-priv-escalation", f"{kind} does not set allowPrivilegeEscalation: false.")

        # Resource limits & requests
        if not re.search(r"(?m)^\s*limits:\s*$", doc):
            add("MEDIUM", "k8s-missing-resource-limits", f"{kind} does not define container resources.limits.")
        if not re.search(r"(?m)^\s*requests:\s*$", doc):
            add("MEDIUM", "k8s-missing-resource-requests", f"{kind} does not define container resources.requests.")

        # Probes for long-running workloads
        if kind in {"Deployment", "StatefulSet", "DaemonSet"}:
            if "readinessProbe:" not in doc:
                add("MEDIUM", "k8s-missing-readiness-probe", f"{kind} is missing readinessProbe.")
            if "livenessProbe:" not in doc:
                add("LOW", "k8s-missing-liveness-probe", f"{kind} is missing livenessProbe.")

        # allow ALL capabilities or missing drop ALL
        if not re.search(r"(?is)drop:\s*\n?\s*-\s*ALL\b", doc):
            add("MEDIUM", "k8s-drop-all-capabilities", f"{kind} does not drop ALL Linux capabilities.")

    return findings


def collect_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*") if p.is_file() and p.suffix.lower() in {".yml", ".yaml"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Kubernetes YAML manifests for security and reliability issues.")
    parser.add_argument("target", type=Path, help="Kubernetes YAML file or directory.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON report.")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    files = collect_files(args.target)
    findings: list[dict] = []
    for fp in files:
        findings.extend(audit_k8s_text(fp.as_posix(), fp.read_text(encoding="utf-8", errors="replace")))

    if args.as_json:
        print(json.dumps({"files_scanned": len(files), "count": len(findings), "findings": findings}, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {len(files)} Kubernetes manifest file(s), 0 issues found.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
