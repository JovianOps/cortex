#!/usr/bin/env python3
"""Atomic, versioned JSON session memory store with staleness checks for memory-manager skill.

Zero external dependencies (Python 3 stdlib only).
Commands: init, add-decision, add-task, complete-task, check-stale, summary
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def load_store(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"Memory store not found: {path}. Run `init` first.")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "schema_version" not in data:
        raise ValueError(f"Malformed memory store at {path}")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Atomic versioned session memory store.")
    parser.add_argument("--file", "-f", type=Path, default=Path("context.json"), help="Path to context.json.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit structured JSON output.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize a new versioned context.json.")
    p_init.add_argument("--project", required=True, help="Project name.")
    p_init.add_argument("--json", action="store_true", dest="sub_json", help="Emit JSON output.")

    p_dec = sub.add_parser("add-decision", help="Record an architectural or workflow decision.")
    p_dec.add_argument("summary", help="Decision text.")
    p_dec.add_argument("--rationale", default="", help="Why this decision was made.")
    p_dec.add_argument("--json", action="store_true", dest="sub_json", help="Emit JSON output.")

    p_task = sub.add_parser("add-task", help="Add an open task.")
    p_task.add_argument("title", help="Task description.")
    p_task.add_argument("--json", action="store_true", dest="sub_json", help="Emit JSON output.")

    p_done = sub.add_parser("complete-task", help="Mark an open task completed by ID.")
    p_done.add_argument("task_id", type=int, help="Numeric task ID.")
    p_done.add_argument("--json", action="store_true", dest="sub_json", help="Emit JSON output.")

    p_stale = sub.add_parser("check-stale", help="Check whether memory has exceeded max age.")
    p_stale.add_argument("--max-hours", type=float, default=24.0, help="Staleness threshold in hours.")
    p_stale.add_argument("--json", action="store_true", dest="sub_json", help="Emit JSON output.")

    p_sum = sub.add_parser("summary", help="Print a concise summary of current memory.")
    p_sum.add_argument("--json", action="store_true", dest="sub_json", help="Emit JSON output.")

    args = parser.parse_args(argv)
    want_json = bool(args.as_json or getattr(args, "sub_json", False))

    if args.cmd == "init":
        data = {
            "schema_version": SCHEMA_VERSION,
            "project": args.project,
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "decisions": [],
            "open_tasks": [],
            "completed_tasks": [],
        }
        atomic_write_json(args.file, data)
        if want_json:
            print(json.dumps({"ok": True, "action": "init", "file": args.file.as_posix(), "data": data}, indent=2))
        else:
            print(f"Initialized memory store at {args.file}")
        return 0

    try:
        data = load_store(args.file)
    except (FileNotFoundError, ValueError) as exc:
        if want_json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.cmd == "add-decision":
        entry = {
            "id": len(data["decisions"]) + 1,
            "summary": args.summary,
            "rationale": args.rationale,
            "recorded_at": utc_now(),
        }
        data["decisions"].append(entry)
        data["updated_at"] = utc_now()
        atomic_write_json(args.file, data)
        if want_json:
            print(json.dumps({"ok": True, "action": "add-decision", "decision": entry}, indent=2))
        else:
            print(f"Recorded decision #{len(data['decisions'])}")
        return 0

    if args.cmd == "add-task":
        next_id = max([t["id"] for t in data["open_tasks"] + data["completed_tasks"]], default=0) + 1
        task = {"id": next_id, "title": args.title, "created_at": utc_now()}
        data["open_tasks"].append(task)
        data["updated_at"] = utc_now()
        atomic_write_json(args.file, data)
        if want_json:
            print(json.dumps({"ok": True, "action": "add-task", "task": task}, indent=2))
        else:
            print(f"Added task #{next_id}")
        return 0

    if args.cmd == "complete-task":
        match = next((t for t in data["open_tasks"] if t["id"] == args.task_id), None)
        if not match:
            msg = f"Open task #{args.task_id} not found."
            if want_json:
                print(json.dumps({"ok": False, "error": msg}, indent=2))
            else:
                print(f"ERROR: {msg}", file=sys.stderr)
            return 1
        data["open_tasks"] = [t for t in data["open_tasks"] if t["id"] != args.task_id]
        match["completed_at"] = utc_now()
        data["completed_tasks"].append(match)
        data["updated_at"] = utc_now()
        atomic_write_json(args.file, data)
        if want_json:
            print(json.dumps({"ok": True, "action": "complete-task", "task": match}, indent=2))
        else:
            print(f"Completed task #{args.task_id}")
        return 0

    if args.cmd == "check-stale":
        updated = datetime.fromisoformat(data["updated_at"])
        age = datetime.now(timezone.utc) - updated
        is_stale = age > timedelta(hours=args.max_hours)
        print(json.dumps({
            "file": args.file.as_posix(),
            "updated_at": data["updated_at"],
            "age_hours": round(age.total_seconds() / 3600.0, 2),
            "max_hours": args.max_hours,
            "stale": is_stale,
        }, indent=2))
        return 1 if is_stale else 0

    if args.cmd == "summary":
        if want_json:
            print(json.dumps({
                "ok": True,
                "file": args.file.as_posix(),
                "project": data["project"],
                "schema_version": data["schema_version"],
                "updated_at": data["updated_at"],
                "decision_count": len(data["decisions"]),
                "open_task_count": len(data["open_tasks"]),
                "completed_task_count": len(data["completed_tasks"]),
                "open_tasks": data["open_tasks"],
            }, indent=2))
        else:
            print(f"# Session Memory: {data['project']} (v{data['schema_version']})")
            print(f"- Updated: {data['updated_at']}")
            print(f"- Decisions: {len(data['decisions'])} | Open tasks: {len(data['open_tasks'])} | Completed: {len(data['completed_tasks'])}")
            for t in data["open_tasks"]:
                print(f"  - [ ] #{t['id']}: {t['title']}")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
