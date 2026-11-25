#!/usr/bin/env python3
"""Zero-dependency supply-chain, SBOM (npm/PyPI/Cargo/Go), and lockfile integrity auditor."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", "target",
    "vendor", ".opencode", ".claude", ".cursor", ".windsurf", ".cline", ".agents",
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


def audit_pyproject(path: Path) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"(?s)\bdependencies\s*=\s*\[(.*?)\]", text)
    if not m:
        return findings
    block = m.group(1)
    for item_m in re.finditer(r'["\']([^"\']+)["\']', block):
        dep = item_m.group(1).strip()
        ln = text[: m.start() + item_m.start()].count("\n") + 1
        if "http://" in dep:
            findings.append({
                "file": path.as_posix(),
                "line": ln,
                "severity": "CRITICAL",
                "rule": "sbom-insecure-http-dep",
                "message": f"Insecure http:// dependency URL in pyproject.toml: {dep}",
            })
        elif not re.search(r"(?:==|>=|<=|~=|!=|<|>|@)", dep):
            findings.append({
                "file": path.as_posix(),
                "line": ln,
                "severity": "MEDIUM",
                "rule": "sbom-unconstrained-pyproject-dep",
                "message": f"pyproject.toml dependency '{dep}' has no version constraint.",
            })
    return findings


def audit_cargo_lock_and_toml(path: Path) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    in_deps = False
    has_deps = False
    for idx, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("["):
            in_deps = stripped.startswith("[dependencies") or stripped.startswith("[workspace.dependencies")
            continue
        if in_deps and "=" in stripped and not stripped.startswith("#"):
            has_deps = True
            if re.search(r'=\s*"\*"', stripped):
                findings.append({
                    "file": path.as_posix(),
                    "line": idx,
                    "severity": "HIGH",
                    "rule": "sbom-cargo-wildcard-dep",
                    "message": "Cargo.toml dependency uses wildcard '*'; pin an explicit SemVer range.",
                })
    if has_deps and not (path.parent / "Cargo.lock").is_file() and (path.parent / "src").is_dir():
        findings.append({
            "file": path.as_posix(),
            "line": 1,
            "severity": "MEDIUM",
            "rule": "sbom-missing-cargo-lockfile",
            "message": "Binary/workspace Cargo crate has dependencies without a committed Cargo.lock.",
        })
    return findings


def audit_go_mod(path: Path) -> list[dict]:
    findings: list[dict] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    has_requires = bool(re.search(r"(?m)^\s*require\b", text))
    if has_requires and not (path.parent / "go.sum").is_file():
        findings.append({
            "file": path.as_posix(),
            "line": 1,
            "severity": "HIGH",
            "rule": "sbom-missing-go-sum",
            "message": "go.mod declares external requirements without a committed go.sum checksum file.",
        })
    return findings


def generate_cyclonedx_summary(candidates: list[Path]) -> dict:
    components: list[dict] = []
    for p in candidates:
        text = p.read_text(encoding="utf-8", errors="replace")
        if p.name == "package.json":
            try:
                d = json.loads(text)
            except json.JSONDecodeError:
                continue
            for sec in ("dependencies", "devDependencies"):
                for name, ver in (d.get(sec) or {}).items():
                    components.append({
                        "type": "library",
                        "ecosystem": "npm",
                        "name": name,
                        "version": str(ver),
                        "purl": f"pkg:npm/{name}@{ver}",
                        "scope": sec,
                    })
        elif p.name.startswith("requirements") and p.suffix == ".txt":
            for raw in text.splitlines():
                line = raw.strip()
                if not line or line.startswith(("#", "-")):
                    continue
                name, _, ver = re.split(r"(==|>=|<=|~=|@)", line, maxsplit=1) if re.search(r"(==|>=|<=|~=|@)", line) else (line, "", "*")
                clean_name = name.strip()
                clean_ver = ver.strip() or "*"
                components.append({
                    "type": "library",
                    "ecosystem": "pypi",
                    "name": clean_name,
                    "version": clean_ver,
                    "purl": f"pkg:pypi/{clean_name}@{clean_ver}",
                })
        elif p.name == "go.mod":
            for m in re.finditer(r"(?m)^\s*(?:require\s+)?([a-zA-Z0-9._-]+/[a-zA-Z0-9._/-]+)\s+(v[0-9A-Za-z.+-]+)", text):
                components.append({
                    "type": "library",
                    "ecosystem": "golang",
                    "name": m.group(1),
                    "version": m.group(2),
                    "purl": f"pkg:golang/{m.group(1)}@{m.group(2)}",
                })
    return {"bomFormat": "CycloneDX", "specVersion": "1.6", "componentCount": len(components), "components": components}


def collect_manifests(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    return sorted(
        p for p in target.rglob("*")
        if p.is_file() and not should_skip(p, target)
        and (
            p.name in {"package.json", "pyproject.toml", "Cargo.toml", "go.mod"}
            or (p.name.startswith("requirements") and p.suffix == ".txt")
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit dependency manifests (npm, PyPI, Cargo, Go) for supply-chain risks and emit CycloneDX summary.")
    parser.add_argument("target", type=Path, help="Manifest file or repository directory.")
    parser.add_argument("--sbom", action="store_true", help="Include lightweight CycloneDX component summary.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    if not args.target.exists():
        print(f"ERROR: Target not found: {args.target}", file=sys.stderr)
        return 2

    candidates = collect_manifests(args.target)
    findings: list[dict] = []
    for fp in candidates:
        if fp.name == "package.json":
            findings.extend(audit_package_json(fp))
        elif fp.name == "pyproject.toml":
            findings.extend(audit_pyproject(fp))
        elif fp.name == "Cargo.toml":
            findings.extend(audit_cargo_lock_and_toml(fp))
        elif fp.name == "go.mod":
            findings.extend(audit_go_mod(fp))
        else:
            findings.extend(audit_requirements(fp))

    payload: dict = {"manifests_scanned": len(candidates), "count": len(findings), "findings": findings}
    if args.sbom:
        payload["sbom"] = generate_cyclonedx_summary(candidates)

    if args.as_json:
        print(json.dumps(payload, indent=2))
    elif findings:
        for f in findings:
            print(f"[{f['severity']}] ({f['rule']}) {f['file']}:{f['line']} — {f['message']}")
    else:
        print(f"OK: Audited {len(candidates)} dependency manifest(s), 0 supply-chain issues found.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
