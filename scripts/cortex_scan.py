#!/usr/bin/env python3
"""Cortex Unified Policy & Multi-Tool Repository Scanner with Table, JSON, SARIF 2.1.0, and JUnit XML output."""
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "2.0.0"

SEVERITY_RANK = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
FAIL_THRESHOLD = {"none": 99, "low": 1, "medium": 2, "high": 3, "critical": 4}

# Registry of runnable repository-level verifiers: (id, skill, script_rel, default_subpath_or_none)
SCANNER_SPECS: list[tuple[str, str, str, str | None]] = [
    ("actions", "devops-pipeline", "premium-skills/devops-pipeline/scripts/lint_actions.py", ".github/workflows"),
    ("secrets", "security-auditor", "premium-skills/security-auditor/scripts/secret_scan.py", None),
    ("terraform", "terraform-generator", "premium-skills/terraform-generator/scripts/lint_terraform.py", None),
    ("kubernetes", "kubernetes-architect", "premium-skills/kubernetes-architect/scripts/lint_k8s.py", None),
    ("typescript", "typescript-architect", "premium-skills/typescript-architect/scripts/lint_ts.py", None),
    ("rust", "rust-systems-engineer", "premium-skills/rust-systems-engineer/scripts/lint_rust.py", None),
    ("go", "go-backend-engineer", "premium-skills/go-backend-engineer/scripts/lint_go.py", None),
    ("graphql", "graphql-architect", "premium-skills/graphql-architect/scripts/lint_graphql.py", None),
    ("sbom", "supply-chain-sbom", "premium-skills/supply-chain-sbom/scripts/audit_sbom.py", None),
    ("pii", "privacy-compliance-auditor", "premium-skills/privacy-compliance-auditor/scripts/scan_pii.py", None),
    ("finops", "finops-cost-optimizer", "premium-skills/finops-cost-optimizer/scripts/audit_finops.py", None),
    ("resilience", "chaos-resilience-engineer", "premium-skills/chaos-resilience-engineer/scripts/audit_resilience.py", None),
    ("llm", "llm-security-auditor", "premium-skills/llm-security-auditor/scripts/audit_prompts.py", None),
    ("git", "git-history-surgeon", "premium-skills/git-history-surgeon/scripts/audit_git_hygiene.py", None),
]


def load_policy(policy_path: Path | None, target_dir: Path) -> dict:
    candidate = policy_path or (target_dir / ".cortex-policy.json")
    if candidate and candidate.is_file():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return {"fail_on": "high", "disabled_scanners": [], "ignore_rules": [], "ignore_paths": []}


def normalize_finding(scanner_id: str, skill: str, raw: dict, target_dir: Path) -> dict:
    file_val = str(raw.get("file", raw.get("path", "")))
    try:
        fp = Path(file_val)
        if fp.is_absolute():
            file_val = fp.resolve().relative_to(target_dir.resolve()).as_posix()
    except ValueError:
        pass
    sev = str(raw.get("severity", "MEDIUM")).upper()
    if sev not in SEVERITY_RANK:
        sev = "MEDIUM"
    return {
        "scanner": scanner_id,
        "skill": skill,
        "severity": sev,
        "rule": str(raw.get("rule", raw.get("rule_id", f"{scanner_id}-finding"))),
        "file": file_val or ".",
        "line": int(raw.get("line", 1) or 1),
        "message": str(raw.get("message", raw.get("detail", "Finding reported."))),
    }


def run_scan(
    target_dir: Path,
    *,
    only: list[str] | None = None,
    policy: dict | None = None,
    fail_on_override: str | None = None,
) -> dict:
    pol = policy or {}
    enabled = set(only) if only else (set(pol["enabled_scanners"]) if pol.get("enabled_scanners") else {s[0] for s in SCANNER_SPECS})
    disabled = set(pol.get("disabled_scanners", []))
    ignore_rules = set(pol.get("ignore_rules", []))
    ignore_paths = list(pol.get("ignore_paths", []))
    fail_on = (fail_on_override or pol.get("fail_on") or "high").lower()

    findings: list[dict] = []
    scanners_run: list[dict] = []

    for scanner_id, skill, script_rel, sub in SCANNER_SPECS:
        if scanner_id not in enabled or scanner_id in disabled:
            continue
        script_path = ROOT / script_rel
        if not script_path.is_file():
            continue
        scan_target = (target_dir / sub) if sub else target_dir
        if not scan_target.exists():
            continue

        cmd = [sys.executable, str(script_path), str(scan_target), "--json"]
        res = subprocess.run(cmd, cwd=target_dir, check=False, capture_output=True, text=True, timeout=60)
        raw_findings: list[dict] = []
        if res.stdout.strip():
            try:
                parsed = json.loads(res.stdout)
                if isinstance(parsed, dict) and isinstance(parsed.get("findings"), list):
                    raw_findings = parsed["findings"]
                elif isinstance(parsed, list):
                    raw_findings = parsed
            except json.JSONDecodeError:
                pass

        kept = 0
        for rf in raw_findings:
            if not isinstance(rf, dict):
                continue
            nf = normalize_finding(scanner_id, skill, rf, target_dir)
            if nf["rule"] in ignore_rules:
                continue
            if any(fnmatch.fnmatch(nf["file"], pat) for pat in ignore_paths):
                continue
            findings.append(nf)
            kept += 1

        scanners_run.append({
            "scanner": scanner_id,
            "skill": skill,
            "findings": kept,
            "exit_code": res.returncode,
        })

    counts = {k: 0 for k in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    threshold = FAIL_THRESHOLD.get(fail_on, 3)
    blocking = [f for f in findings if SEVERITY_RANK.get(f["severity"], 0) >= threshold]

    return {
        "version": VERSION,
        "target": target_dir.resolve().as_posix(),
        "fail_on": fail_on,
        "scanners_run": scanners_run,
        "summary": counts,
        "total_findings": len(findings),
        "blocking_findings": len(blocking),
        "passed": len(blocking) == 0,
        "findings": findings,
    }


def to_sarif(report: dict) -> dict:
    sarif_level = {"CRITICAL": "error", "HIGH": "error", "MEDIUM": "warning", "LOW": "note", "INFO": "note"}
    rules_map: dict[str, dict] = {}
    results: list[dict] = []
    for f in report["findings"]:
        rid = f["rule"]
        if rid not in rules_map:
            rules_map[rid] = {
                "id": rid,
                "shortDescription": {"text": f"[{f['skill']}] {rid}"},
                "properties": {"tags": ["cortex", f["scanner"], f["severity"].lower()]},
            }
        results.append({
            "ruleId": rid,
            "level": sarif_level.get(f["severity"], "warning"),
            "message": {"text": f["message"]},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f["file"]},
                    "region": {"startLine": max(1, int(f["line"]))},
                }
            }],
        })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "Cortex",
                    "version": VERSION,
                    "informationUri": "https://github.com/JovianOps/cortex",
                    "rules": list(rules_map.values()),
                }
            },
            "results": results,
        }],
    }


def to_junit_xml(report: dict) -> str:
    suite = ET.Element("testsuite", {
        "name": "cortex-scan",
        "tests": str(max(1, len(report["scanners_run"]))),
        "failures": str(report["blocking_findings"]),
    })
    by_scanner: dict[str, list[dict]] = {}
    for f in report["findings"]:
        by_scanner.setdefault(f["scanner"], []).append(f)
    for sc in report["scanners_run"]:
        tc = ET.SubElement(suite, "testcase", {"classname": f"cortex.{sc['skill']}", "name": sc["scanner"]})
        for f in by_scanner.get(sc["scanner"], []):
            fail = ET.SubElement(tc, "failure", {"type": f["severity"], "message": f"({f['rule']}) {f['file']}:{f['line']}"})
            fail.text = f["message"]
    return ET.tostring(suite, encoding="unicode", xml_declaration=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Cortex unified multi-tool security & quality scan with Table, JSON, SARIF 2.1.0, or JUnit XML output.")
    parser.add_argument("target", type=Path, nargs="?", default=Path.cwd(), help="Target repository directory.")
    parser.add_argument("--only", action="append", default=[], help="Run only specific scanner(s), e.g., --only actions --only sbom.")
    parser.add_argument("--policy", type=Path, default=None, help="Path to .cortex-policy.json.")
    parser.add_argument("--fail-on", choices=("none", "low", "medium", "high", "critical"), default=None)
    parser.add_argument("--format", "-f", choices=("table", "json", "sarif", "junit"), default="table")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Optional file path to write report.")
    args = parser.parse_args(argv)

    target = args.target.resolve()
    if not target.exists():
        print(f"ERROR: Target not found: {target}", file=sys.stderr)
        return 2

    pol = load_policy(args.policy, target)
    report = run_scan(target, only=args.only or None, policy=pol, fail_on_override=args.fail_on)

    if args.format == "json":
        rendered = json.dumps(report, indent=2) + "\n"
    elif args.format == "sarif":
        rendered = json.dumps(to_sarif(report), indent=2) + "\n"
    elif args.format == "junit":
        rendered = to_junit_xml(report)
    else:
        lines = [
            f"Cortex Unified Scan v{VERSION} — {report['target']}",
            f"Scanners run: {len(report['scanners_run'])} | Findings: {report['total_findings']} "
            f"(CRIT={report['summary']['CRITICAL']} HIGH={report['summary']['HIGH']} MED={report['summary']['MEDIUM']} LOW={report['summary']['LOW']}) | "
            f"Gate (fail-on={report['fail_on']}): {'PASS' if report['passed'] else 'FAIL'}",
            "",
        ]
        for f in report["findings"]:
            lines.append(f"  [{f['severity']:<8}] ({f['scanner']}/{f['rule']}) {f['file']}:{f['line']} — {f['message']}")
        if not report["findings"]:
            lines.append("  No findings reported.")
        rendered = "\n".join(lines) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
