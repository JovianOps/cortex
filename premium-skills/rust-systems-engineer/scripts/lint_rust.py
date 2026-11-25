#!/usr/bin/env python3
"""Zero-dependency Rust safety & Cargo.toml dependency hygiene auditor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    "target", ".git", "node_modules", ".venv", "__pycache__", "dist", "build",
    ".opencode", ".claude", ".cursor", ".windsurf", ".cline", ".agents",
    ".codex", ".gemini", ".openclaw", ".goose", ".aider", "zips", "premium-zips",
}


def should_skip(fp: Path, root: Path) -> bool:
    rel = fp.relative_to(root).parts if fp != root else fp.parts
    if any(part in SKIP_DIRS for part in rel):
        return True
    for i in range(len(rel) - 1):
        if rel[i] == ".github" and rel[i + 1] == "skills":
            return True
    return False


def audit_rust_file(path: Path) -> list[dict]:
    findings: list[dict] = []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    pending_cfg_test = False
    cfg_test_depth = 0
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if "#[cfg(test)]" in stripped:
            pending_cfg_test = True
        if pending_cfg_test and "{" in stripped:
            cfg_test_depth += stripped.count("{") - stripped.count("}")
            if cfg_test_depth <= 0:
                pending_cfg_test = False
                cfg_test_depth = 0
            continue
        in_cfg_test = cfg_test_depth > 0 or pending_cfg_test
        if cfg_test_depth > 0:
            cfg_test_depth += stripped.count("{") - stripped.count("}")
            if cfg_test_depth <= 0:
                cfg_test_depth = 0
                pending_cfg_test = False
        if stripped.startswith("//"):
            continue

        if re.search(r"\bunsafe\s*\{", line):
            prev = lines[idx - 2].strip() if idx >= 2 else ""
            prev2 = lines[idx - 3].strip() if idx >= 3 else ""
            nxt = lines[idx].strip() if idx < len(lines) else ""
            if "SAFETY:" not in line and "SAFETY:" not in prev and "SAFETY:" not in prev2 and "SAFETY:" not in nxt:
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "HIGH",
                    "rule": "rust-undocumented-unsafe",
                    "message": "unsafe block lacks an adjacent '// SAFETY:' invariant comment.",
                })

        if not in_cfg_test and not path.name.endswith("_test.rs"):
            if ".unwrap()" in line:
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "MEDIUM",
                    "rule": "rust-unwrap-in-prod",
                    "message": "Avoid .unwrap() in non-test code; propagate errors with '?' or .expect('reason').",
                })
            if re.search(r"\b(?:todo!|unimplemented!)\s*\(", line):
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "HIGH",
                    "rule": "rust-unfinished-macro",
                    "message": "Remove todo!/unimplemented! macro before production release.",
                })
            if "mem::transmute" in line:
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "CRITICAL",
                    "rule": "rust-mem-transmute",
                    "message": "std::mem::transmute is highly error-prone; prefer safe conversions (From/TryFrom/bytemuck).",
                })
    return findings


def audit_cargo_toml(path: Path) -> list[dict]:
    findings: list[dict] = []
    in_deps = False
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("["):
            in_deps = stripped.startswith("[dependencies") or stripped.startswith("[workspace.dependencies")
            continue
        if in_deps and re.search(r'=\s*"\*"', stripped):
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "HIGH",
                "rule": "cargo-wildcard-version",
                "message": "Pin crate dependency to an explicit SemVer range instead of '*'.",
            })
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Rust source files and Cargo.toml for safety and hygiene issues.")
    parser.add_argument("target", type=Path, help="Rust .rs file, Cargo.toml, or workspace directory.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    rs_files: list[Path] = []
    cargo_files: list[Path] = []
    if args.target.is_file():
        if args.target.name == "Cargo.toml":
            cargo_files.append(args.target)
        else:
            rs_files.append(args.target)
    else:
        for p in sorted(args.target.rglob("*")):
            if not p.is_file() or should_skip(p, args.target):
                continue
            if p.suffix == ".rs":
                rs_files.append(p)
            elif p.name == "Cargo.toml":
                cargo_files.append(p)

    findings: list[dict] = []
    for fp in cargo_files:
        findings.extend(audit_cargo_toml(fp))
    for fp in rs_files:
        findings.extend(audit_rust_file(fp))

    if args.as_json:
        print(json.dumps({"rs_files": len(rs_files), "cargo_files": len(cargo_files), "count": len(findings), "findings": findings}, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {len(rs_files)} Rust file(s) and {len(cargo_files)} Cargo.toml file(s), 0 issues found.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
