#!/usr/bin/env python3
"""Zero-dependency supply-chain, SBOM, and lockfile integrity auditor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build", "target"}


def audit_package_json(path: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError as exc:
        return [{"file": path.as_posix(), "line": 1, "severity": "HIGH", "rule": "sbom-invalid-package-json", "message": str(exc)}]

    parent = path.parent
    has_deps = bool(data.get("dependencies") or data.get("devDependencies"))
    has_lock = any((parent / lf).is_file() for lf in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock"))
    if has_deps and not has_lock:
        findings.append({
            "file": path.as_posix(),
            "line": 1,
            "severity": "HIGH",
            "rule": "sbom-missing-npm-lockfile",
            "message": "package.json declares dependencies without a committed lockfile.",
        })

    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        deps = data.get(section, {})
        if not isinstance(deps, dict):
            continue
        for pkg, spec in deps.items():
            s = str(spec).strip()
            if s in {"*", "latest"} or s.startswith("http://"):
                findings.append({
                    "file": path.as_posix(),
                    "line": 1,
                    "severity": "CRITICAL" if s.startswith("http://") else "HIGH",
                    "rule": "sbom-unpinned-npm-dep",
                    "message": f"{section}.{pkg} uses unsafe spec '{s}'; pin an explicit SemVer range or HTTPS commit.",
                })

    scripts = data.get("scripts", {})
    if isinstance(scripts, dict):
        for hook in ("preinstall", "install", "postinstall"):
            cmd = str(scripts.get(hook, ""))
            if re.search(r"\b(?:curl|wget|powershell|iwr)\b", cmd, re.I):
                findings.append({
                    "file": path.as_posix(),
                    "line": 1,
                    "severity": "CRITICAL",
                    "rule": "sbom-suspicious-lifecycle-hook",
                    "message": f"Lifecycle hook '{hook}' executes remote download command.",
                })
    return findings


def audit_requirements(path: Path) -> list[dict]:
    findings: list[dict] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("-r "):
            continue
        if "http://" in stripped:
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "CRITICAL",
                "rule": "sbom-insecure-http-dep",
                "message": "Insecure http:// dependency URL detected.",
            })
        elif not stripped.startswith("-") and "==" not in stripped and "@" not in stripped:
            findings.append({
                "file": path.as_posix(),
                "line": idx,
                "severity": "MEDIUM",
                "rule": "sbom-unpinned-python-req",
                "message": f"Requirement '{stripped}' is not pinned with '==' for reproducible builds.",
            })
    return findings


def generate_cyclonedx_summary(target: Path) -> dict:
    components: list[dict] = []
    for p in sorted(target.rglob("package.json")) if target.is_dir() else ([target] if target.name == "package.json" else []):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        for sec in ("dependencies", "devDependencies"):
            for name, ver in (d.get(sec) or {}).items():
                components.append({"type": "library", "ecosystem": "npm", "name": name, "version": str(ver), "scope": sec})
    return {"bomFormat": "CycloneDX", "specVersion": "1.6", "componentCount": len(components), "components": components}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit dependency manifests for supply-chain risks and emit CycloneDX summary.")
    parser.add_argument("target", type=Path, help="Manifest file or repository directory.")
    parser.add_argument("--sbom", action="store_true", help="Include lightweight CycloneDX component summary.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    findings: list[dict] = []
    manifests = 0
    candidates = [args.target] if args.target.is_file() else sorted(
        p for p in args.target.rglob("*")
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts)
        and (p.name == "package.json" or p.name.startswith("requirements") and p.suffix == ".txt")
    )
    for fp in candidates:
        manifests += 1
        if fp.name == "package.json":
            findings.extend(audit_package_json(fp))
        else:
            findings.extend(audit_requirements(fp))

    payload: dict = {"manifests_scanned": manifests, "count": len(findings), "findings": findings}
    if args.sbom:
        payload["sbom"] = generate_cyclonedx_summary(args.target)

    if args.as_json:
        print(json.dumps(payload, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {manifests} dependency manifest(s), 0 supply-chain issues found.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
