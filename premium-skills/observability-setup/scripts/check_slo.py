#!/usr/bin/env python3
"""Deterministic SLO error-budget calculator & metric cardinality auditor for observability-setup skill."""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

HIGH_CARDINALITY_LABELS = {
    "user_id", "userid", "request_id", "requestid", "trace_id", "span_id",
    "email", "ip", "client_ip", "session_id", "uuid", "order_id", "timestamp",
}


def compute_error_budget(slo_percent: Decimal, window_days: int) -> dict:
    if not (Decimal("0") < slo_percent < Decimal("100")):
        raise ValueError("SLO must be strictly between 0 and 100 (e.g., 99.9).")
    total_minutes = Decimal(window_days) * Decimal(24 * 60)
    error_ratio = (Decimal("100") - slo_percent) / Decimal("100")
    budget_minutes = (total_minutes * error_ratio).quantize(Decimal("0.01"))
    return {
        "slo_percent": str(slo_percent),
        "window_days": window_days,
        "error_budget_minutes": str(budget_minutes),
        "error_budget_ratio": f"{error_ratio:.6f}",
        "multi_window_burn_alerts": {
            "page_fast_2pct_1h_5m": {"burn_rate": 14.4, "error_rate_threshold": f"{error_ratio * Decimal('14.4'):.6f}"},
            "page_slow_5pct_6h_30m": {"burn_rate": 6.0, "error_rate_threshold": f"{error_ratio * Decimal('6.0'):.6f}"},
            "ticket_10pct_3d_6h": {"burn_rate": 1.0, "error_rate_threshold": f"{error_ratio:.6f}"},
        },
    }


def scan_labels(path: Path) -> list[dict]:
    findings: list[dict] = []
    files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file() and p.suffix in {".py", ".ts", ".js", ".go", ".yml", ".yaml", ".json"})
    for fp in files:
        for idx, line in enumerate(fp.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for label in HIGH_CARDINALITY_LABELS:
                if re.search(rf'["\']{re.escape(label)}["\']', line) and re.search(r'(?i)(label|tag|metric|counter|histogram|gauge|prom)', line):
                    findings.append({
                        "severity": "HIGH",
                        "rule": "high-cardinality-label",
                        "file": fp.as_posix(),
                        "line": idx,
                        "label": label,
                        "message": f"High-cardinality label '{label}' detected on metric definition.",
                    })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compute SLO error budgets and audit metric label cardinality.")
    parser.add_argument("--slo", type=Decimal, default=Decimal("99.9"), help="SLO target percent (default: 99.9).")
    parser.add_argument("--window-days", type=int, default=30, help="Rolling SLO window in days (default: 30).")
    parser.add_argument("--scan", type=Path, help="Optional file or directory to scan for high-cardinality metric labels.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    try:
        budget = compute_error_budget(args.slo, args.window_days)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    findings = scan_labels(args.scan) if args.scan else []
    payload = {"slo": budget, "cardinality_findings": findings}
    if args.as_json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"SLO {budget['slo_percent']}% ({budget['window_days']}d window) -> Error Budget: {budget['error_budget_minutes']} min")
        for f in findings:
            print(f"[{f['severity']}] {f['file']}:{f['line']} — {f['message']}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
