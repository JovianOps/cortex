#!/usr/bin/env python3
"""Zero-dependency GraphQL SDL schema contract & pagination auditor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def audit_graphql(path: Path) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    current_block = ""
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        block_m = re.match(r"^(?:extend\s+)?(type|input|interface|enum)\s+([A-Za-z_][A-Za-z0-9_]*)", stripped)
        if block_m:
            current_block = f"{block_m.group(1)}:{block_m.group(2)}"
            continue
        if stripped == "}":
            current_block = ""
            continue

        # 1. @deprecated without reason
        if re.search(r"@deprecated(?!\s*\(\s*reason\s*:)", stripped):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "MEDIUM",
                "rule": "gql-deprecated-missing-reason",
                "message": "@deprecated directive must specify a clear reason and migration path.",
            })

        # 2. Unbounded list queries on Query root without pagination arguments
        if current_block == "type:Query":
            list_m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*(\([^)]*\))?\s*:\s*\[", stripped)
            if list_m:
                field_name = list_m.group(1)
                args_str = list_m.group(2) or ""
                if not re.search(r"\b(?:first|last|limit|after|before|page|pageSize)\b", args_str):
                    findings.append({
                        "file": path.as_posix(),
                        "line": idx,
                        "severity": "HIGH",
                        "rule": "gql-unbounded-list-query",
                        "message": f"Query.{field_name} returns an unbounded list without pagination args (e.g., Relay Connection first/after).",
                    })

        # 3. Mutations with >2 scalar args instead of an Input object
        if current_block == "type:Mutation":
            mut_m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]+)\)\s*:", stripped)
            if mut_m:
                mut_name = mut_m.group(1)
                arg_list = [a.strip() for a in mut_m.group(2).split(",") if a.strip()]
                if len(arg_list) > 1 and not any("input:" in a.lower() for a in arg_list):
                    findings.append({
                        "file": path.as_posix(),
                        "line": idx,
                        "severity": "MEDIUM",
                        "rule": "gql-mutation-missing-input-type",
                        "message": f"Mutation.{mut_name} takes {len(arg_list)} raw arguments; wrap in a dedicated Input object type.",
                    })

        # 4. Nullable id field on object types
        if current_block.startswith("type:") and current_block not in {"type:Query", "type:Mutation", "type:Subscription"}:
            if re.match(r"^id\s*:\s*ID\s*(?:#.*)?$", stripped):
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "MEDIUM",
                    "rule": "gql-nullable-id",
                    "message": f"{current_block} declares nullable 'id: ID'; use non-null 'id: ID!'.",
                })

    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit GraphQL SDL schemas for pagination, input types, and deprecation hygiene.")
    parser.add_argument("target", type=Path, help="GraphQL .graphql/.gql file or directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    files = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*") if p.is_file() and p.suffix.lower() in {".graphql", ".gql"}
    )
    findings: list[dict] = []
    for fp in files:
        findings.extend(audit_graphql(fp))

    if args.as_json:
        print(json.dumps({"files_scanned": len(files), "count": len(findings), "findings": findings}, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {len(files)} GraphQL schema file(s), 0 issues found.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
