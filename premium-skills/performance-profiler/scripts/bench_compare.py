#!/usr/bin/env python3
"""Deterministic baseline vs. candidate latency benchmark comparator for performance-profiler skill."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    k = max(0, min(len(sorted_vals) - 1, int(round((pct / 100.0) * (len(sorted_vals) - 1)))))
    return round(sorted_vals[k], 4)


def summarize(samples: list[float]) -> dict[str, float]:
    s = sorted(float(x) for x in samples)
    return {"count": len(s), "p50": percentile(s, 50), "p95": percentile(s, 95), "p99": percentile(s, 99)}


def compare(baseline: list[float], candidate: list[float], max_regression_pct: float) -> dict:
    b = summarize(baseline)
    c = summarize(candidate)
    p95_delta_pct = round(((c["p95"] - b["p95"]) / b["p95"]) * 100.0, 2) if b["p95"] > 0 else 0.0
    regressed = p95_delta_pct > max_regression_pct
    return {
        "baseline": b,
        "candidate": c,
        "p95_delta_pct": p95_delta_pct,
        "max_regression_pct": max_regression_pct,
        "regressed": regressed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare baseline vs. candidate benchmark latency JSON arrays.")
    parser.add_argument("baseline", type=Path, help="JSON file containing a list of numeric baseline durations.")
    parser.add_argument("candidate", type=Path, help="JSON file containing a list of numeric candidate durations.")
    parser.add_argument("--max-regression-pct", type=float, default=5.0, help="Max allowed p95 regression percent (default: 5.0).")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.baseline.is_file() or not args.candidate.is_file():
        print("ERROR: Baseline or candidate file not found.", file=sys.stderr)
        return 2

    res = compare(
        json.loads(args.baseline.read_text(encoding="utf-8")),
        json.loads(args.candidate.read_text(encoding="utf-8")),
        args.max_regression_pct,
    )
    if args.as_json:
        print(json.dumps(res, indent=2))
    else:
        status = "REGRESSION" if res["regressed"] else "OK"
        print(f"[{status}] p95: {res['baseline']['p95']} -> {res['candidate']['p95']} ({res['p95_delta_pct']:+.2f}%)")
    return 1 if res["regressed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
