#!/usr/bin/env python3
"""Deterministic Dockerfile security & hardening linter for docker-generator skill.

Zero external dependencies (Python 3 stdlib only).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECRET_ENV_RE = re.compile(r"^\s*ENV\s+.*?(?:PASSWORD|SECRET|TOKEN|API_KEY|PRIVATE_KEY)\s*[=\s]+\S+", re.IGNORECASE)
PIPE_SHELL_RE = re.compile(r"(?:curl|wget)[^|\n]+\|\s*(?:sh|bash)\b", re.IGNORECASE)


def lint_dockerfile(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    findings: list[dict] = []
    from_lines: list[tuple[int, str]] = []
    has_non_root_user = False
    has_healthcheck = False

    for lineno, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        upper = line.upper()
        if upper.startswith("FROM "):
            from_lines.append((lineno, line))
            parts = [tok for tok in line.split()[1:] if not tok.startswith("--")]
            image = parts[0] if parts else ""
            if image and image.lower() != "scratch":
                if ":latest" in image or (":" not in image and "@sha256:" not in image):
                    findings.append({
                        "severity": "HIGH",
                        "rule": "pin-base-image",
                        "line": lineno,
                        "message": f"Unpinned base image {image!r}; pin an explicit version tag or @sha256 digest.",
                    })
        elif upper.startswith("USER "):
            user_val = line.split(None, 1)[1].strip()
            if user_val not in {"root", "0", "0:0"}:
                has_non_root_user = True
        elif upper.startswith("HEALTHCHECK "):
            has_healthcheck = True
        elif upper.startswith("ADD "):
            src = line.split()[1] if len(line.split()) > 1 else ""
            if not src.startswith(("http://", "https://")) and not src.endswith((".tar", ".tar.gz", ".tgz")):
                findings.append({
                    "severity": "MEDIUM",
                    "rule": "prefer-copy-over-add",
                    "line": lineno,
                    "message": "Use COPY instead of ADD for local files unless auto-extraction is explicitly required.",
                })

        if SECRET_ENV_RE.search(line):
            findings.append({
                "severity": "CRITICAL",
                "rule": "no-secret-in-env",
                "line": lineno,
                "message": "Potential secret baked into ENV instruction; pass secrets at runtime or via BuildKit --mount=type=secret.",
            })
        if PIPE_SHELL_RE.search(line):
            findings.append({
                "severity": "HIGH",
                "rule": "no-curl-pipe-shell",
                "line": lineno,
                "message": "Avoid piping remote scripts directly into sh/bash; download and verify SHA-256 first.",
            })

    if not from_lines:
        findings.append({"severity": "CRITICAL", "rule": "missing-from", "line": 1, "message": "Dockerfile has no FROM instruction."})
    if not has_non_root_user:
        findings.append({
            "severity": "HIGH",
            "rule": "require-non-root-user",
            "line": len(lines) or 1,
            "message": "Container runs as root; add a dedicated non-root USER instruction in the final stage.",
        })
    if not has_healthcheck:
        findings.append({
            "severity": "MEDIUM",
            "rule": "add-healthcheck",
            "line": len(lines) or 1,
            "message": "No HEALTHCHECK instruction defined for runtime liveness monitoring.",
        })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint a Dockerfile for security & hardening best practices.")
    parser.add_argument("dockerfile", type=Path, help="Path to Dockerfile.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON output.")
    args = parser.parse_args(argv)
    if not args.dockerfile.is_file():
        print(f"ERROR: File not found: {args.dockerfile}", file=sys.stderr)
        return 2
    findings = lint_dockerfile(args.dockerfile)
    critical_or_high = [f for f in findings if f["severity"] in {"CRITICAL", "HIGH"}]
    if args.as_json:
        print(json.dumps({"file": args.dockerfile.as_posix(), "count": len(findings), "findings": findings}, indent=2))
    else:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {args.dockerfile}:{f['line']} — {f['message']}")
        if not findings:
            print(f"OK: {args.dockerfile} passed all hardening checks.")
    return 1 if critical_or_high else 0


if __name__ == "__main__":
    raise SystemExit(main())
