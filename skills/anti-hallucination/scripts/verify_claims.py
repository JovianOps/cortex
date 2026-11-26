#!/usr/bin/env python3
"""Offline claim verifier for anti-hallucination skill — checks cited file paths exist in a repository."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PATH_RX = re.compile(r"`([A-Za-z0-9_.\-/]+\.[A-Za-z0-9]{1,8})`")


def verify_claims(doc_text: str, repo_root: Path) -> tuple[list[str], list[str]]:
    cited = sorted(set(PATH_RX.findall(doc_text)))
    verified: list[str] = []
    missing: list[str] = []
    for rel in cited:
        if rel.startswith(("http://", "https://")) or "/" not in rel:
            continue
        candidate = (repo_root / rel).resolve()
        try:
            candidate.relative_to(repo_root.resolve())
        except ValueError:
            missing.append(rel)
            continue
        if candidate.exists():
            verified.append(rel)
        else:
            missing.append(rel)
    return verified, missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify backticked relative file path claims against a repository.")
    parser.add_argument("document", type=Path, help="Markdown/text response to audit.")
    parser.add_argument("--repo", type=Path, default=Path("."), help="Repository root directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    if not args.document.is_file():
        print(f"ERROR: Document not found: {args.document}", file=sys.stderr)
        return 2

    verified, missing = verify_claims(args.document.read_text(encoding="utf-8", errors="replace"), args.repo)
    if args.as_json:
        print(json.dumps({"verified": verified, "missing": missing, "ok": not missing}, indent=2))
    elif not missing:
        print(f"OK: Verified {len(verified)} cited path(s); 0 hallucinated paths.")
    else:
        print(f"FAIL: {len(missing)} cited path(s) do not exist in {args.repo}:")
        for m in missing:
            print(f"  - {m}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
