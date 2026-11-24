#!/usr/bin/env python3
"""Offline academic citation & numeric-reference auditor for academic-assistant skill."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def audit_citations(text: str) -> dict:
    parts = re.split(r"(?im)^##\s+References\b", text, maxsplit=1)
    body = parts[0]
    refs_section = parts[1] if len(parts) > 1 else ""
    cited = sorted(set(re.findall(r"\[(\d+)\]", body)), key=int)
    defined = sorted(set(re.findall(r"(?m)^\s*(?:\[(\d+)\]|(\d+)\.)\s+\S", refs_section)), key=lambda m: int(m[0] or m[1]))
    defined_ids = sorted({m[0] or m[1] for m in defined}, key=int)

    missing_refs = [c for c in cited if c not in defined_ids]
    uncited_refs = [d for d in defined_ids if d not in cited]
    return {
        "cited_count": len(cited),
        "defined_count": len(defined_ids),
        "missing_references": missing_refs,
        "uncited_references": uncited_refs,
        "ok": not missing_refs and not uncited_refs,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify numeric inline citations [1] match a ## References section.")
    parser.add_argument("draft", type=Path, help="Markdown academic draft file.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.draft.is_file():
        print(f"ERROR: File not found: {args.draft}", file=sys.stderr)
        return 2

    res = audit_citations(args.draft.read_text(encoding="utf-8"))
    if args.as_json:
        print(json.dumps(res, indent=2))
    elif res["ok"]:
        print(f"OK: All {res['cited_count']} inline citation(s) match ## References.")
    else:
        if res["missing_references"]:
            print(f"ERROR: Missing reference entries for citations: {res['missing_references']}")
        if res["uncited_references"]:
            print(f"WARNING: Uncited entries in ## References: {res['uncited_references']}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
