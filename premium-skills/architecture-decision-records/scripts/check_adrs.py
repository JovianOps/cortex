#!/usr/bin/env python3
"""Zero-dependency MADR Architecture Decision Record (ADR) validator."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALID_STATUSES = {"proposed", "accepted", "rejected", "deprecated", "superseded"}
REQUIRED_SECTIONS = ("status", "context", "decision", "consequences")


def audit_adr_dir(target: Path) -> dict:
    files = [target] if target.is_file() else sorted(
        p for p in target.glob("*.md") if p.name.lower() not in {"readme.md", "template.md", "index.md"}
    )
    findings: list[dict] = []
    seen_nums: list[int] = []

    for fp in files:
        m = re.match(r"^(\d{4})-[a-z0-9-]+\.md$", fp.name)
        if not m:
            findings.append({
                "file": fp.as_posix(),
                "severity": "MEDIUM",
                "rule": "adr-filename-format",
                "message": "ADR filename must match NNNN-kebab-title.md (e.g., 0001-use-postgresql.md).",
            })
        else:
            num = int(m.group(1))
            if num in seen_nums:
                findings.append({
                    "file": fp.as_posix(),
                    "severity": "HIGH",
                    "rule": "adr-duplicate-number",
                    "message": f"Duplicate ADR sequence number {num:04d}.",
                })
            seen_nums.append(num)

        text = fp.read_text(encoding="utf-8", errors="replace")
        headings = [h.strip().lower() for h in re.findall(r"(?m)^##\s+(.+)$", text)]
        for req in REQUIRED_SECTIONS:
            if not any(req in h for h in headings):
                findings.append({
                    "file": fp.as_posix(),
                    "severity": "HIGH",
                    "rule": f"adr-missing-{req}",
                    "message": f"ADR is missing required '## {req.title()}' section.",
                })

        status_m = re.search(r"(?im)^##\s+Status\s*\n+([^\n#]+)", text)
        if status_m:
            raw_status = status_m.group(1).strip().lower()
            if not any(valid in raw_status for valid in VALID_STATUSES):
                findings.append({
                    "file": fp.as_posix(),
                    "severity": "HIGH",
                    "rule": "adr-invalid-status",
                    "message": f"Unrecognized ADR status '{status_m.group(1).strip()}'; expected one of {sorted(VALID_STATUSES)}.",
                })

    if seen_nums and seen_nums != sorted(seen_nums):
        findings.append({
            "file": target.as_posix(),
            "severity": "LOW",
            "rule": "adr-non-monotonic",
            "message": "ADR sequence numbers are not strictly increasing.",
        })

    return {"adrs_scanned": len(files), "count": len(findings), "findings": findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MADR Architecture Decision Records (numbering, sections, status).")
    parser.add_argument("target", type=Path, help="ADR markdown file or docs/adr directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    res = audit_adr_dir(args.target)
    if args.as_json:
        print(json.dumps(res, indent=2))
    elif res["findings"]:
        for f in res["findings"]:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']} — {f['message']}")
    else:
        print(f"OK: Validated {res['adrs_scanned']} ADR file(s), 0 issues found.")
    return 1 if res["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
