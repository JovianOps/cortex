#!/usr/bin/env python3
"""Deterministic UTC incident timeline & MTTR/MTTD validator for incident-response skill."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def parse_utc(ts: str) -> datetime:
    if not ts.endswith("Z"):
        raise ValueError(f"Timestamp must be UTC ISO-8601 ending in 'Z': {ts!r}")
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def validate_incident(data: dict) -> tuple[list[str], dict]:
    errors: list[str] = []
    events = data.get("timeline")
    if not isinstance(events, list) or not events:
        return ["'timeline' must be a non-empty list of UTC events."], {}

    parsed: list[tuple[datetime, str]] = []
    for idx, ev in enumerate(events):
        if not isinstance(ev, dict) or "timestamp" not in ev or "event" not in ev:
            errors.append(f"Event #{idx + 1} missing 'timestamp' or 'event'.")
            continue
        try:
            dt = parse_utc(str(ev["timestamp"]))
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if parsed and dt < parsed[-1][0]:
            errors.append(f"Out-of-order timestamp at event #{idx + 1}: {ev['timestamp']}")
        parsed.append((dt, str(ev.get("phase", "")).lower()))

    by_phase = {phase: dt for dt, phase in parsed if phase}
    metrics: dict[str, float | None] = {"mttd_minutes": None, "mttr_minutes": None}
    if "impact_start" in by_phase and "detected" in by_phase:
        metrics["mttd_minutes"] = round((by_phase["detected"] - by_phase["impact_start"]).total_seconds() / 60.0, 2)
    if "impact_start" in by_phase and "resolved" in by_phase:
        metrics["mttr_minutes"] = round((by_phase["resolved"] - by_phase["impact_start"]).total_seconds() / 60.0, 2)

    actions = data.get("action_items", [])
    if not isinstance(actions, list) or not actions:
        errors.append("Postmortem must include at least one corrective 'action_items' entry.")
    else:
        for idx, item in enumerate(actions, 1):
            if not isinstance(item, dict) or not item.get("owner") or not item.get("due_date"):
                errors.append(f"Action item #{idx} missing required 'owner' or 'due_date'.")

    return errors, metrics


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate an incident timeline JSON and compute MTTD/MTTR.")
    parser.add_argument("file", type=Path, help="Path to incident timeline JSON file.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.file.is_file():
        print(f"ERROR: File not found: {args.file}", file=sys.stderr)
        return 2

    data = json.loads(args.file.read_text(encoding="utf-8"))
    errors, metrics = validate_incident(data)
    if args.as_json:
        print(json.dumps({"valid": not errors, "metrics": metrics, "errors": errors}, indent=2))
    elif not errors:
        print(f"OK: Timeline valid (MTTD={metrics['mttd_minutes']}m, MTTR={metrics['mttr_minutes']}m).")
    else:
        for e in errors:
            print(f"ERROR: {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
