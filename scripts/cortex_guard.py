#!/usr/bin/env python3
"""Cortex Guard (v3.0.0) — one release gate plus hardened CI and pre-commit enforcement.

`cortex guard check` runs every deterministic Cortex gate in one pass (packaging,
manifests, skill validation, 100-point audit, capability graph, and the policy/SARIF
scanner) and exits non-zero on the first blocking failure. `cortex guard` can also emit
a SHA-pinned GitHub Actions workflow and a Git pre-commit hook so the same gate runs
locally and in CI.

Zero external dependencies (Python 3 stdlib only).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VERSION = "3.0.0"

# SHA-pinned actions (same pins used by Cortex CI).
CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"  # v7.0.1
SETUP_PYTHON_SHA = "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0"  # v7.1.0
SETUP_NODE_SHA = "949feb2413d6458794dcd2491c4babbbce0c15c1"  # v7.1.0
UPLOAD_SARIF_SHA = "1bd86f2fdb4b86187fa4059f16f31a3202acc9ea"  # v4

WORKFLOW_TEMPLATE = f"""name: Cortex Guard

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

concurrency:
  group: ${{{{ github.workflow }}}}-${{{{ github.ref }}}}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  guard:
    name: Cortex Release Gate
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - name: Checkout repository
        uses: actions/checkout@{CHECKOUT_SHA} # v7.0.1

      - name: Setup Node.js
        uses: actions/setup-node@{SETUP_NODE_SHA} # v7.1.0
        with:
          node-version: '24'
          package-manager-cache: false

      - name: Setup Python
        uses: actions/setup-python@{SETUP_PYTHON_SHA} # v7.1.0
        with:
          python-version: '3.12'

      - name: Install validation dependencies
        run: python -m pip install --upgrade pip pyyaml ruff

      - name: Cortex integrity, audit & graph gate
        run: npx -y @jovianops/cortex@3 verify --json

      - name: Cortex policy & SARIF gate
        run: npx -y @jovianops/cortex@3 scan . --format sarif --output cortex.sarif --fail-on high

      - name: Upload Cortex SARIF to GitHub Security
        if: always() && hashFiles('cortex.sarif') != ''
        uses: github/codeql-action/upload-sarif@{UPLOAD_SARIF_SHA} # v4
        with:
          sarif_file: 'cortex.sarif'
          category: 'cortex'
"""
PRE_COMMIT_TEMPLATE = """#!/bin/sh
set -eu
echo "[cortex] verifying skill integrity and policy gates..."
if [ -f scripts/cortex.py ]; then
  python scripts/cortex.py verify
  python scripts/cortex.py scan . --fail-on high
else
  npx -y @jovianops/cortex verify
  npx -y @jovianops/cortex scan . --fail-on high
fi
"""

CHECKS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("package", "package_skills.py", ("--check",)),
    ("skills", "validate_skills.py", ()),
    ("manifests", "validate_manifests.py", ()),
    ("audit", "eval_skills.py", ()),
    ("graph", "cortex_graph.py", ("--check", "--strict")),
    ("scan", "cortex_scan.py", ("--fail-on", "high", "--format", "json")),
)


def run_check(name: str, script: str, extra: tuple[str, ...], project_dir: Path) -> dict:
    started = time.monotonic()
    if name == "package" and not (
        (ROOT / "zips").is_dir() and (ROOT / "premium-zips").is_dir()
    ):
        return {
            "name": name,
            "ok": True,
            "skipped": True,
            "detail": "Not a source checkout with ZIP archives; SHA-256 files were verified by cortex verify.",
            "duration_ms": 0,
        }

    cmd = [sys.executable, str(SCRIPTS / script), *extra]
    if name == "scan":
        cmd.append(str(project_dir))
    try:
        res = subprocess.run(
            cmd,
            cwd=project_dir if name == "scan" else ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "name": name,
            "ok": False,
            "skipped": False,
            "detail": f"could not run {script}: {exc}",
            "duration_ms": int((time.monotonic() - started) * 1000),
        }

    detail = ""
    if name == "graph" and res.stderr.strip():
        detail = res.stderr.strip().splitlines()[-1]
    if name == "scan" and res.stdout.strip().startswith("{"):
        try:
            report = json.loads(res.stdout)
            detail = (
                f"{len(report.get('scanners_run', []))} scanners, "
                f"{report.get('total_findings', 0)} findings, "
                f"{report.get('blocking_findings', 0)} blocking"
            )
        except json.JSONDecodeError:
            pass
    if not detail:
        output = (res.stdout.strip() or res.stderr.strip()).splitlines()
        detail = output[-1] if output else ""
    return {
        "name": name,
        "ok": res.returncode == 0,
        "skipped": False,
        "detail": detail[:400],
        "duration_ms": int((time.monotonic() - started) * 1000),
    }


def guard_check(project_dir: Path, *, only: list[str] | None, fail_fast: bool) -> dict:
    selected = set(only) if only else {spec[0] for spec in CHECKS}
    unknown = sorted(selected - {spec[0] for spec in CHECKS})
    if unknown:
        raise ValueError(f"Unknown guard check(s): {', '.join(unknown)}")

    results: list[dict] = []
    all_ok = True
    for name, script, extra in CHECKS:
        if name not in selected:
            continue
        result = run_check(name, script, extra, project_dir)
        results.append(result)
        if not result["ok"]:
            all_ok = False
            if fail_fast:
                break

    return {
        "version": VERSION,
        "project_dir": project_dir.as_posix(),
        "ok": all_ok,
        "checks_run": len(results),
        "checks_passed": sum(1 for r in results if r["ok"]),
        "checks_skipped": sum(1 for r in results if r["skipped"]),
        "checks": results,
    }


def install_hooks(project_dir: Path) -> dict:
    hook_dir = project_dir / ".githooks"
    hook_path = hook_dir / "pre-commit"
    hook_dir.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(PRE_COMMIT_TEMPLATE, encoding="utf-8", newline="\n")
    try:
        hook_path.chmod(0o755)
    except OSError:
        pass

    git_configured = False
    detail = "Run `git config core.hooksPath .githooks` to activate the hook."
    git_bin = shutil.which("git")
    if git_bin and (project_dir / ".git").exists():
        res = subprocess.run(
            [git_bin, "config", "core.hooksPath", ".githooks"],
            cwd=project_dir,
            check=False,
            capture_output=True,
            text=True,
        )
        git_configured = res.returncode == 0
        detail = (
            "Installed pre-commit hook and set core.hooksPath=.githooks."
            if git_configured
            else f"Hook written, but git config failed: {res.stderr.strip()}"
        )
    return {
        "version": VERSION,
        "ok": hook_path.is_file(),
        "hook": hook_path.as_posix(),
        "git_hooks_path_configured": git_configured,
        "detail": detail,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Cortex's full release gate or generate hardened CI / pre-commit enforcement."
    )
    parser.add_argument("action", nargs="?", choices=("check", "install"), default="check")
    parser.add_argument("--project-dir", type=Path, default=Path.cwd(), help="Workspace to scan and install hooks into.")
    parser.add_argument("--only", action="append", default=[], help="Run only specific checks (package, skills, manifests, audit, graph, scan).")
    parser.add_argument("--fail-fast", action="store_true", help="Stop at the first failing check.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--print-workflow", action="store_true", help="Print a SHA-pinned Cortex Guard GitHub Actions workflow and exit.")
    parser.add_argument("--write-workflow", action="store_true", help="Write .github/workflows/cortex-guard.yml in the project directory.")
    parser.add_argument("--print-pre-commit", action="store_true", help="Print a Git pre-commit hook and exit.")
    args = parser.parse_args(argv)

    if args.print_workflow:
        sys.stdout.write(WORKFLOW_TEMPLATE)
        return 0
    if args.print_pre_commit:
        sys.stdout.write(PRE_COMMIT_TEMPLATE)
        return 0
    if args.write_workflow:
        dest = args.project_dir.resolve() / ".github" / "workflows" / "cortex-guard.yml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(WORKFLOW_TEMPLATE, encoding="utf-8", newline="\n")
        payload = {"version": VERSION, "ok": True, "workflow": dest.as_posix()}
        print(json.dumps(payload, indent=2) if args.as_json else f"Wrote Cortex Guard workflow to {dest}")
        return 0
    if args.action == "install":
        payload = install_hooks(args.project_dir.resolve())
        print(json.dumps(payload, indent=2) if args.as_json else payload["detail"])
        return 0 if payload["ok"] else 1

    try:
        report = guard_check(args.project_dir.resolve(), only=args.only, fail_fast=args.fail_fast)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Cortex Guard v{VERSION} — {report['project_dir']}")
        for check in report["checks"]:
            tag = "SKIP" if check["skipped"] else ("OK" if check["ok"] else "FAIL")
            print(f"  [{tag:<4}] {check['name']:<10} {check['duration_ms']:>5} ms  {check['detail']}")
        print(
            f"\nGate: {'PASS' if report['ok'] else 'FAIL'} — "
            f"{report['checks_passed']}/{report['checks_run']} checks passed"
            + (f", {report['checks_skipped']} skipped" if report["checks_skipped"] else "")
        )
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
