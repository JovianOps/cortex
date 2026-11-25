#!/usr/bin/env python3
"""Cortex Unified CLI (v3.0.0) — detect agents, diagnose installs, search skills, install packs, and scaffold new skills.

Zero external dependencies (Python 3 stdlib only). Works on Linux, macOS, and Windows.

Usage:
  python scripts/cortex.py detect
  python scripts/cortex.py doctor
  python scripts/cortex.py search [query] [--tier core|extended] [--has-script]
  python scripts/cortex.py packs
  python scripts/cortex.py install --agent claude-code --pack fullstack
  python scripts/cortex.py graph [--format json|mermaid|dot] [--check]
  python scripts/cortex.py bundle --pack cloud-native --out dist/cortex.zip
  python scripts/cortex.py guard check [--json]
  python scripts/cortex.py new <slug> [--tier core|extended] [--with-script]
  python scripts/cortex.py status|upgrade|uninstall|audit|eval|package|verify
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VERSION = "3.0.0"

AGENT_PROBES: tuple[tuple[str, str, str, str, tuple[str, ...]], ...] = (
    ("claude-code", "Claude Code", ".claude", ".claude", ("claude",)),
    ("codex", "OpenAI Codex CLI", ".codex", ".agents", ("codex",)),
    ("gemini-cli", "Gemini CLI", ".gemini", ".gemini", ("gemini",)),
    ("cursor", "Cursor", ".cursor", ".cursor", ("cursor",)),
    ("vscode", "Visual Studio Code", ".vscode", ".vscode", ("code", "code-insiders")),
    ("copilot", "GitHub Copilot", ".copilot", ".github", ("copilot",)),
    ("opencode", "OpenCode", ".config/opencode", ".opencode", ("opencode",)),
    ("openclaw", "OpenClaw", ".openclaw", ".openclaw", ("openclaw",)),
    ("goose", "Goose", ".config/goose", ".goose", ("goose",)),
    ("cline", "Cline", ".cline", ".cline", ()),
    ("aider", "Aider", ".aider", ".aider", ("aider",)),
    ("hermes", "Hermes Agent", ".hermes", ".hermes", ("hermes",)),
)


def load_script(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_cortex_{name}", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"_cortex_{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


def parse_skill_frontmatter(skill_md: Path) -> dict[str, object]:
    text = skill_md.read_text(encoding="utf-8")
    meta: dict[str, object] = {"name": skill_md.parent.name, "description": "", "version": VERSION, "tags": []}
    if not text.startswith("---\n"):
        return meta
    parts = text.split("---", 2)
    if len(parts) < 3:
        return meta
    fm = parts[1]
    for line in fm.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip("'\"")
    tag_match = re.search(r"tags:\s*\[([^\]]*)\]", fm)
    if tag_match:
        meta["tags"] = [t.strip().strip("'\"") for t in tag_match.group(1).split(",") if t.strip()]
    return meta


def detect_agents(project_dir: Path) -> list[dict]:
    home = Path.home()
    found: list[dict] = []
    for key, label, home_marker, proj_marker, binaries in AGENT_PROBES:
        global_dir = home / home_marker
        project_marker_dir = project_dir / proj_marker
        found_bins = [b for b in binaries if shutil.which(b)]
        signals: list[str] = []
        if global_dir.exists():
            signals.append(f"~/{home_marker}")
        if project_marker_dir.exists():
            signals.append(f"./{proj_marker}")
        if found_bins:
            signals.append(f"cli:{','.join(found_bins)}")

        # Count locked Cortex skills if present
        locked = 0
        lock_candidates = (
            (home / ".copilot" / "skills" / ".cortex-lock.json", project_dir / ".github" / "skills" / ".cortex-lock.json")
            if key == "vscode"
            else (global_dir / "skills" / ".cortex-lock.json", project_marker_dir / "skills" / ".cortex-lock.json")
        )
        for candidate in lock_candidates:
            if candidate.is_file():
                try:
                    locked += len(json.loads(candidate.read_text(encoding="utf-8")).get("skills", {}))
                except json.JSONDecodeError:
                    pass

        found.append({
            "agent": key,
            "label": label,
            "detected": bool(signals),
            "signals": signals,
            "installed_cortex_skills": locked,
        })
    return found


def cmd_detect(args: argparse.Namespace) -> int:
    results = detect_agents(args.project_dir.resolve())
    detected = [r for r in results if r["detected"]]
    if args.as_json:
        print(json.dumps({"project_dir": args.project_dir.resolve().as_posix(), "detected_count": len(detected), "agents": results}, indent=2))
        return 0

    print(f"Cortex v{VERSION} — Agent Environment Detection ({args.project_dir.resolve()})\n")
    print(f"{'Agent':<14} {'Platform':<28} {'Status':<11} {'Locked':>6}  Signals")
    print("-" * 86)
    for r in results:
        status = "DETECTED" if r["detected"] else "not found"
        sigs = ", ".join(r["signals"]) if r["signals"] else "—"
        print(f"{r['agent']:<14} {r['label']:<28} {status:<11} {r['installed_cortex_skills']:>6}  {sigs}")

    installable = [r["agent"] for r in detected if r["agent"] != "hermes"]
    if installable:
        flags = " ".join(f"--agent {a}" for a in installable)
        print(f"\nSuggested install command for detected agents:\n  python scripts/cortex.py install {flags} --pack fullstack")
    else:
        print("\nNo agent config directories detected yet. Install for any target with:\n  python scripts/cortex.py install --agent claude-code --pack fullstack")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    project_dir = args.project_dir.resolve()
    as_json = bool(getattr(args, "as_json", False))

    def log(msg: str) -> None:
        if not as_json:
            print(msg)

    log(f"Cortex v{VERSION} — Environment & Integrity Doctor\n")
    issues = 0

    # 1. Runtime checks
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    node_bin = shutil.which("node")
    git_bin = shutil.which("git")
    log(f"[OK]   Python {py_ver} ({sys.executable})")
    log(f"[{'OK' if git_bin else 'WARN'}] {'git found at ' + git_bin if git_bin else 'git not found on PATH'}")
    log(f"[{'OK' if node_bin else 'INFO'}] {'node found at ' + node_bin if node_bin else 'node not found (optional — Python installer works without Node)'}")

    # 2. Integrity checks (full ZIP check in repo checkout; direct SHA-256 check in npm package)
    if (ROOT / "checksums.json").is_file() and (ROOT / "packs.json").is_file():
        if (ROOT / "zips").is_dir() and (ROOT / "premium-zips").is_dir():
            pkg_res = subprocess.run([sys.executable, str(SCRIPTS / "package_skills.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
            if pkg_res.returncode == 0:
                log(f"[OK]   {pkg_res.stdout.strip()}")
            else:
                issues += 1
                log(f"[FAIL] package_skills --check: {(pkg_res.stderr or pkg_res.stdout).strip()}")
        else:
            manifest = json.loads((ROOT / "checksums.json").read_text(encoding="utf-8"))
            checked_files = 0
            bad_files: list[str] = []
            for slug, meta in manifest.get("skills", {}).items():
                base_dir = ROOT / meta["dir"] / slug
                for rel, expected in meta.get("files", {}).items():
                    fp = base_dir / rel
                    if not fp.is_file():
                        bad_files.append(f"{slug}/{rel} (missing)")
                        continue
                    raw_bytes = fp.read_bytes().replace(b"\r\n", b"\n")
                    actual = hashlib.sha256(raw_bytes).hexdigest()
                    if actual != expected:
                        bad_files.append(f"{slug}/{rel} (sha256 mismatch)")
                    checked_files += 1
            if bad_files:
                issues += 1
                log(f"[FAIL] Bundled skill SHA-256 verification failed: {', '.join(bad_files)}")
            else:
                log(f"[OK]   Verified SHA-256 checksums for {len(manifest.get('skills', {}))} bundled skills ({checked_files} files).")

        man_res = subprocess.run([sys.executable, str(SCRIPTS / "validate_manifests.py")], cwd=ROOT, capture_output=True, text=True)
        if man_res.returncode == 0:
            log(f"[OK]   {man_res.stdout.strip()}")
        else:
            issues += 1
            log(f"[FAIL] validate_manifests: {(man_res.stderr or man_res.stdout).strip()}")

    # 3. Verify any installed .cortex-lock.json files in detected agent directories
    installer = load_script("install_skills")
    checked_locks = 0
    for target in installer.AGENT_TARGETS.values():
        for scope in ("project", "global"):
            dest = installer.destination_dir(target, scope, project_dir)
            if (dest / installer.LOCKFILE_NAME).is_file():
                checked_locks += 1
                if as_json:
                    res = subprocess.run(
                        [sys.executable, str(SCRIPTS / "install_skills.py"), "--status", "--agent", target, "--scope", scope, "--project-dir", str(project_dir)],
                        cwd=ROOT,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    rc = res.returncode
                else:
                    rc = installer.cmd_status([target], scope, project_dir)
                if rc != 0:
                    issues += 1

    if checked_locks == 0:
        log("[INFO] No .cortex-lock.json installations found in this workspace or home directory yet.")

    if as_json:
        print(json.dumps({
            "version": VERSION,
            "ok": issues == 0,
            "issues": issues,
            "python": py_ver,
            "git": git_bin,
            "node": node_bin,
            "checked_lockfiles": checked_locks,
        }, indent=2))
        return 1 if issues else 0

    log(f"\nDoctor finished with {issues} issue(s).")
    return 1 if issues else 0


def cmd_search(args: argparse.Namespace) -> int:
    q = (args.query or "").strip().lower()
    rows: list[dict] = []
    for folder, tier in (("skills", "core"), ("premium-skills", "extended")):
        if args.tier and args.tier != tier:
            continue
        base = ROOT / folder
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            md = entry / "SKILL.md"
            if not (entry.is_dir() and md.is_file()):
                continue
            meta = parse_skill_frontmatter(md)
            bundled = sorted(
                p.relative_to(entry).as_posix()
                for p in (entry / "scripts").glob("*.py")
            ) if (entry / "scripts").is_dir() else []
            if args.has_script and not bundled:
                continue
            haystack = " ".join([
                entry.name,
                str(meta.get("description", "")),
                " ".join(meta.get("tags", [])),  # type: ignore[arg-type]
                " ".join(bundled),
            ]).lower()
            if q and q not in haystack:
                continue
            rows.append({
                "slug": entry.name,
                "tier": tier,
                "dir": folder,
                "description": meta.get("description", ""),
                "tags": meta.get("tags", []),
                "scripts": bundled,
            })

    if args.as_json:
        print(json.dumps({"query": q, "count": len(rows), "skills": rows}, indent=2))
        return 0

    print(f"Found {len(rows)} Cortex skill(s)" + (f" matching {q!r}" if q else "") + ":\n")
    print(f"{'Skill':<26} {'Tier':<10} {'Script':<24} Description")
    print("-" * 102)
    for r in rows:
        script_col = r["scripts"][0].replace("scripts/", "") if r["scripts"] else "—"
        print(f"{r['slug']:<26} {r['tier']:<10} {script_col:<24} {r['description']}")
    return 0


def cmd_packs(args: argparse.Namespace) -> int:
    packs_data = json.loads((ROOT / "packs.json").read_text(encoding="utf-8"))
    packs = packs_data.get("packs", {})
    if args.as_json:
        print(json.dumps(packs_data, indent=2))
        return 0

    print(f"Cortex v{VERSION} — Curated Role-Based Skill Packs ({len(packs)} packs)\n")
    for key, info in packs.items():
        print(f"  {key:<20} {info['label']} ({len(info['skills'])} skills)")
        print(f"    {info['description']}")
        print(f"    Skills: {', '.join(info['skills'])}")
        print(f"    Install: python scripts/cortex.py install --agent claude-code --pack {key}\n")
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    slug = args.slug.strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,48}", slug):
        print("ERROR: Skill slug must be kebab-case (3-49 chars, lowercase letters, digits, hyphens).", file=sys.stderr)
        return 2

    target_root = args.out_dir.resolve() if args.out_dir else ROOT
    collection_dir = "skills" if args.tier == "core" else "premium-skills"
    skill_dir = target_root / collection_dir / slug
    if skill_dir.exists() and not args.force:
        print(f"ERROR: Skill directory already exists: {skill_dir} (pass --force to overwrite)", file=sys.stderr)
        return 1

    title = " ".join(part.capitalize() for part in slug.split("-"))
    desc = (args.description or f"Execute deterministic {title.lower()} checks.").strip()
    if not desc.endswith("."):
        desc += "."
    if len(desc) > 60:
        desc = desc[:59].rstrip(" .") + "."

    script_rel = f"scripts/{slug.replace('-', '_')}_check.py"
    script_note = (
        f"\n> **Bundled Helper Script (`v{VERSION}`):** Run `python {collection_dir}/{slug}/{script_rel} .` for deterministic verification.\n"
        if args.with_script
        else ""
    )

    skill_md = f"""---
name: {slug}
description: {desc}
version: {VERSION}
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [{slug}, automation, validation]
    related_skills: [anti-hallucination, code-review-assistant]
---

# {title}

Deliver verifiable, repeatable {title.lower()} results using mandatory stop gates, concrete tool verification, and a strict output contract.

## When to Use

- Running structured {title.lower()} workflows where silent assumptions are unacceptable
- Requiring reproducible verification commands and evidence-backed findings

### When Not to Use

- Unrelated tasks outside the {title.lower()} domain

## How to Run
{script_note}
```bash
# Universal CLI
npx skills add JovianOps/cortex --skill {slug} -g -y

# Hermes Agent
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/{collection_dir}/{slug} --yes
```

## Mandatory {title} Protocol

### Step 1 — Gather Inputs & Verify Preconditions (Stop Gate)

Inspect all relevant files before making changes. Stop and ask for clarification if required inputs are missing or contradictory.

### Step 2 — Execute Deterministic Checks

Run real local verification commands and record exact output (never fabricate tool results):

```bash
# Replace with concrete project checks
python --version
```

### Step 3 — Apply Minimal Verified Changes & Re-Verify

Implement minimal targeted changes, re-run verification checks, and report any residual risks explicitly.

## Strict Output Contract

```markdown
## {title} Summary
- **Scope:** Files inspected and commands executed.
- **Status:** PASS / FAIL

## Findings & Actions
- Evidence-backed items with exact `file:line` references.

## Verification Evidence
- Exact commands executed and observed exit codes.
```
"""

    as_json = bool(getattr(args, "as_json", False))
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
    if not as_json:
        print(f"Created {skill_dir / 'SKILL.md'}")

    created_script: str | None = None
    if args.with_script:
        script_path = skill_dir / script_rel
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(
            f'#!/usr/bin/env python3\n'
            f'"""Deterministic helper tool for the {slug} Cortex skill."""\n'
            f'from __future__ import annotations\n\n'
            f'import argparse\n'
            f'import json\n'
            f'from pathlib import Path\n\n\n'
            f'def main() -> int:\n'
            f'    parser = argparse.ArgumentParser(description="{title} verification helper.")\n'
            f'    parser.add_argument("target", type=Path, help="Target file or directory.")\n'
            f'    args = parser.parse_args()\n'
            f'    print(json.dumps({{"skill": "{slug}", "target": args.target.as_posix(), "status": "ok"}}, indent=2))\n'
            f'    return 0\n\n\n'
            f'if __name__ == "__main__":\n'
            f'    raise SystemExit(main())\n',
            encoding="utf-8",
        )
        created_script = script_path.as_posix()
        if not as_json:
            print(f"Created {script_path}")

    if as_json:
        print(json.dumps({
            "slug": slug,
            "tier": args.tier,
            "skill_md": (skill_dir / "SKILL.md").as_posix(),
            "script": created_script,
            "version": VERSION,
        }, indent=2))
        return 0

    print("\nNext steps:")
    print(f"  1. Add a 100-point A/B rubric for `{slug}` in evals/skill_evals.json")
    print("  2. Rebuild ZIPs & checksums.json: python scripts/package_skills.py")
    print("  3. Update manifests & run tests: npm test")
    return 0


def detect_project_stack(project_dir: Path) -> tuple[str, list[str]]:
    """Recommend a Cortex role pack based on files present in project_dir."""
    signals: list[str] = []
    has_tf = any(project_dir.glob("*.tf")) or (project_dir / "terraform").is_dir()
    has_docker = (project_dir / "Dockerfile").is_file() or (project_dir / "docker-compose.yml").is_file()
    has_ci = (project_dir / ".github" / "workflows").is_dir()
    has_node = (project_dir / "package.json").is_file()
    has_py = (project_dir / "pyproject.toml").is_file() or (project_dir / "requirements.txt").is_file() or (project_dir / "setup.py").is_file()

    if has_tf:
        signals.append("terraform")
    if has_docker:
        signals.append("docker")
    if has_ci:
        signals.append("github-actions")
    if has_node:
        signals.append("node/web")
    if has_py:
        signals.append("python")

    if has_tf or (has_docker and has_ci and not has_node):
        return "devops-sre", signals
    if has_py and not has_node:
        return "python-pro", signals
    return "fullstack", signals


def cmd_init(args: argparse.Namespace) -> int:
    project_dir = args.project_dir.resolve()
    detected = detect_agents(project_dir)
    recommended_pack, stack_signals = detect_project_stack(project_dir)
    pack = args.pack or recommended_pack

    if args.agent:
        chosen_agents = list(args.agent)
    else:
        installer = load_script("install_skills")
        supported = set(installer.AGENT_TARGETS.keys())
        chosen_agents = [a["agent"] for a in detected if a["detected"] and a["agent"] in supported]
        if not chosen_agents:
            chosen_agents = ["vscode"]

    install_argv: list[str] = []
    for ag in chosen_agents:
        install_argv.extend(["--agent", ag])
    install_argv.extend(["--pack", pack, "--scope", args.scope, "--project-dir", str(project_dir)])
    if "vscode" in chosen_agents:
        install_argv.append("--write-vscode-settings")
    if "aider" in chosen_agents:
        install_argv.append("--write-aider-conf")
    if args.dry_run:
        install_argv.append("--dry-run")

    if args.as_json:
        buf_res = subprocess.run(
            [sys.executable, str(SCRIPTS / "install_skills.py"), *install_argv],
            cwd=project_dir,
            check=False,
            capture_output=True,
            text=True,
        )
        print(json.dumps({
            "version": VERSION,
            "project_dir": project_dir.as_posix(),
            "stack_signals": stack_signals,
            "pack": pack,
            "agents": chosen_agents,
            "scope": args.scope,
            "dry_run": args.dry_run,
            "ok": buf_res.returncode == 0,
            "output": buf_res.stdout.strip(),
            "error": buf_res.stderr.strip(),
        }, indent=2))
        return buf_res.returncode

    print(f"Cortex v{VERSION} — Project Initialization ({project_dir})")
    print(f"  Stack signals : {', '.join(stack_signals) or 'generic'}")
    print(f"  Selected pack : {pack}")
    print(f"  Target agents : {', '.join(chosen_agents)}")
    return delegate("install_skills", install_argv)


def cmd_info(args: argparse.Namespace) -> int:
    slug = args.slug.strip().lower()
    skill_dir: Path | None = None
    tier = ""
    folder_name = ""
    for folder, t in (("skills", "core"), ("premium-skills", "extended")):
        candidate = ROOT / folder / slug
        if (candidate / "SKILL.md").is_file():
            skill_dir = candidate
            tier = t
            folder_name = folder
            break

    if skill_dir is None:
        print(f"ERROR: Unknown skill {args.slug!r}. Run `cortex search` to list all skills.", file=sys.stderr)
        return 2

    meta = parse_skill_frontmatter(skill_dir / "SKILL.md")
    scripts = sorted(
        p.relative_to(skill_dir).as_posix()
        for p in (skill_dir / "scripts").glob("*.py")
    ) if (skill_dir / "scripts").is_dir() else []

    checksums = json.loads((ROOT / "checksums.json").read_text(encoding="utf-8")) if (ROOT / "checksums.json").is_file() else {}
    c_entry = checksums.get("skills", {}).get(slug, {})
    packs_data = json.loads((ROOT / "packs.json").read_text(encoding="utf-8")) if (ROOT / "packs.json").is_file() else {}
    member_packs = [pid for pid, pinfo in packs_data.get("packs", {}).items() if slug in pinfo.get("skills", [])]

    info = {
        "slug": slug,
        "tier": tier,
        "dir": folder_name,
        "version": meta.get("version", VERSION),
        "description": meta.get("description", ""),
        "tags": meta.get("tags", []),
        "scripts": scripts,
        "packs": member_packs,
        "skill_sha256": c_entry.get("files", {}).get("SKILL.md", ""),
        "zip_sha256": c_entry.get("zip_sha256", ""),
        "install_cmd": f"npx @jovianops/cortex install --agent vscode --skill {slug} --scope project",
    }

    if args.as_json:
        print(json.dumps(info, indent=2))
        return 0

    print(f"{info['slug']}  (v{info['version']} · {info['tier']})")
    print(f"  Description : {info['description']}")
    print(f"  Path        : {info['dir']}/{info['slug']}/SKILL.md")
    print(f"  Script      : {', '.join(info['scripts']) or 'none'}")
    print(f"  Role packs  : {', '.join(info['packs']) or 'none'}")
    if info["skill_sha256"]:
        print(f"  SKILL SHA256: {info['skill_sha256']}")
    if info["zip_sha256"]:
        print(f"  ZIP SHA256  : {info['zip_sha256']}")
    print(f"  Install     : {info['install_cmd']}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    project_dir = args.project_dir.resolve()
    checks: list[dict] = []

    def run_check(name: str, script_name: str, extra: list[str]) -> bool:
        res = subprocess.run(
            [sys.executable, str(SCRIPTS / f"{script_name}.py"), *extra],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        checks.append({
            "name": name,
            "ok": res.returncode == 0,
            "detail": (res.stdout.strip() or res.stderr.strip()).splitlines()[-1] if (res.stdout.strip() or res.stderr.strip()) else "",
        })
        return res.returncode == 0

    all_ok = True
    if (ROOT / "zips").is_dir() and (ROOT / "premium-zips").is_dir():
        all_ok &= run_check("package_checksums", "package_skills", ["--check"])
    elif (ROOT / "checksums.json").is_file():
        manifest = json.loads((ROOT / "checksums.json").read_text(encoding="utf-8"))
        bad: list[str] = []
        for slug, meta in manifest.get("skills", {}).items():
            base_dir = ROOT / meta["dir"] / slug
            for rel, expected in meta.get("files", {}).items():
                fp = base_dir / rel
                if not fp.is_file() or hashlib.sha256(fp.read_bytes().replace(b"\r\n", b"\n")).hexdigest() != expected:
                    bad.append(f"{slug}/{rel}")
        ok = not bad
        all_ok &= ok
        checks.append({
            "name": "bundled_checksums",
            "ok": ok,
            "detail": f"Verified {len(manifest.get('skills', {}))} bundled skills." if ok else f"Mismatch: {', '.join(bad)}",
        })

    all_ok &= run_check("manifests", "validate_manifests", [])
    all_ok &= run_check("evals_and_audit", "eval_skills", [])

    # Check installed lockfiles under project_dir
    installer = load_script("install_skills")
    lock_issues = 0
    locks_checked = 0
    seen_dests: set[Path] = set()
    for target in installer.AGENT_TARGETS.values():
        dest = installer.destination_dir(target, "project", project_dir)
        if dest in seen_dests:
            continue
        seen_dests.add(dest)
        if (dest / installer.LOCKFILE_NAME).is_file():
            locks_checked += 1
            if installer.cmd_status([target], "project", project_dir) != 0:
                lock_issues += 1
    if locks_checked:
        ok = lock_issues == 0
        all_ok &= ok
        checks.append({
            "name": "project_lockfiles",
            "ok": ok,
            "detail": f"Checked {locks_checked} project lockfile(s), {lock_issues} issue(s).",
        })

    if args.as_json:
        print(json.dumps({"version": VERSION, "ok": all_ok, "checks": checks}, indent=2))
    else:
        for c in checks:
            tag = "OK" if c["ok"] else "FAIL"
            print(f"[{tag:<4}] {c['name']}: {c['detail']}")
    return 0 if all_ok else 1


def delegate(script_name: str, extra_args: list[str], *, use_root_cwd: bool = False) -> int:
    run_cwd = ROOT if use_root_cwd else Path.cwd()
    res = subprocess.run([sys.executable, str(SCRIPTS / f"{script_name}.py"), *extra_args], check=False, cwd=run_cwd)
    return res.returncode


def main(argv: list[str] | None = None) -> int:
    raw = argv if argv is not None else sys.argv[1:]
    if raw and raw[0] in {"-V", "--version"}:
        print(f"cortex {VERSION}")
        return 0
    if not raw or raw[0] in {"-h", "--help"}:
        print(
            f"Cortex CLI v{VERSION} — Multi-Agent Skill & Runtime Platform\n\n"
            "Commands:\n"
            "  init         Auto-detect stack & agents, install recommended pack with SHA-256 checks\n"
            "  mcp          Start zero-dependency MCP 2025-03-26 stdio server (--print-config)\n"
            "  studio       Launch local Light/Dark Swiss web workbench (cortex studio --port 4310)\n"
            "  compile      Compile SKILL.md playbooks to Cursor .mdc, VS Code, Windsurf, Cline & more\n"
            "  scan         Run unified multi-tool repo scan (Table, JSON, SARIF 2.1.0, JUnit XML)\n"
            "  graph        Build the skill/pack capability graph (JSON, Mermaid, Graphviz DOT)\n"
            "  bundle       Build or --verify a deterministic offline skill bundle (ZIP + SHA-256)\n"
            "  guard        Run the full release gate or emit hardened CI / pre-commit hooks\n"
            "  detect       Auto-detect installed AI agents & locked Cortex skills\n"
            "  doctor       Run environment, lockfile SHA-256, checksum & manifest diagnostics\n"
            "  info <slug>  Inspect a skill's metadata, bundled script, packs, and SHA-256 hashes\n"
            "  search       Search all 36 skills by keyword, tier, or bundled script\n"
            "  packs        List all 10 curated role-based skill packs (packs.json)\n"
            f"  new <slug>   Scaffold a 100/100 audit-ready v{VERSION} skill (+ optional script)\n"
            "  install      Install skills/packs locally or --remote (SHA-256 verified)\n"
            "  status       Verify installed skills against .cortex-lock.json\n"
            "  upgrade      Upgrade installed skills to latest catalog\n"
            "  uninstall    Remove installed Cortex skills and update lockfile\n"
            "  audit        Run 100-point structural quality audit on all skills\n"
            "  eval         Validate or --run live A/B benchmarks\n"
            "  package      Rebuild or --check reproducible ZIPs and checksums.json\n"
            "  verify       Run full checksum, manifest, eval & lockfile verification (--json)\n"
        )
        return 0

    cmd, rest = raw[0], raw[1:]

    if cmd == "mcp":
        return delegate("cortex_mcp", rest)
    if cmd == "studio":
        return delegate("cortex_studio", rest)
    if cmd == "compile":
        return delegate("cortex_compile", rest)
    if cmd == "scan":
        return delegate("cortex_scan", rest)
    if cmd == "graph":
        return delegate("cortex_graph", rest, use_root_cwd=True)
    if cmd == "bundle":
        return delegate("cortex_bundle", rest, use_root_cwd=True)
    if cmd == "guard":
        return delegate("cortex_guard", rest)

    if cmd == "init":
        p = argparse.ArgumentParser(prog="cortex init")
        p.add_argument("--project-dir", type=Path, default=Path.cwd())
        p.add_argument("--agent", "-a", action="append", default=[])
        p.add_argument("--pack", "-p", default=None)
        p.add_argument("--scope", choices=("project", "global"), default="project")
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--json", action="store_true", dest="as_json")
        return cmd_init(p.parse_args(rest))

    if cmd == "info":
        p = argparse.ArgumentParser(prog="cortex info")
        p.add_argument("slug", help="Skill slug (e.g., security-auditor).")
        p.add_argument("--json", action="store_true", dest="as_json")
        return cmd_info(p.parse_args(rest))

    if cmd == "detect":
        p = argparse.ArgumentParser(prog="cortex detect")
        p.add_argument("--project-dir", type=Path, default=Path.cwd())
        p.add_argument("--json", action="store_true", dest="as_json")
        return cmd_detect(p.parse_args(rest))

    if cmd == "doctor":
        p = argparse.ArgumentParser(prog="cortex doctor")
        p.add_argument("--project-dir", type=Path, default=Path.cwd())
        p.add_argument("--json", action="store_true", dest="as_json")
        return cmd_doctor(p.parse_args(rest))

    if cmd == "search":
        p = argparse.ArgumentParser(prog="cortex search")
        p.add_argument("query", nargs="?", default="")
        p.add_argument("--tier", choices=("core", "extended"), default=None)
        p.add_argument("--has-script", action="store_true")
        p.add_argument("--json", action="store_true", dest="as_json")
        return cmd_search(p.parse_args(rest))

    if cmd == "packs":
        p = argparse.ArgumentParser(prog="cortex packs")
        p.add_argument("--json", action="store_true", dest="as_json")
        return cmd_packs(p.parse_args(rest))

    if cmd == "new":
        p = argparse.ArgumentParser(prog="cortex new")
        p.add_argument("slug", help="Kebab-case skill slug (e.g., graph-debugger).")
        p.add_argument("--tier", choices=("core", "extended"), default="extended")
        p.add_argument("--description", default="", help="Concise <=60-char description.")
        p.add_argument("--with-script", action="store_true", help="Include starter Python helper script.")
        p.add_argument("--out-dir", type=Path, default=None, help="Optional root directory override.")
        p.add_argument("--force", action="store_true")
        p.add_argument("--json", action="store_true", dest="as_json")
        return cmd_new(p.parse_args(rest))

    if cmd == "install":
        return delegate("install_skills", rest)
    if cmd == "status":
        return delegate("install_skills", ["--status", *rest])
    if cmd == "upgrade":
        return delegate("install_skills", ["--upgrade", *rest])
    if cmd == "uninstall":
        return delegate("install_skills", ["--uninstall", *rest])
    if cmd == "audit":
        return delegate("eval_skills", ["--audit-skills", *rest], use_root_cwd=True)
    if cmd == "eval":
        return delegate("eval_skills", rest, use_root_cwd=True)
    if cmd == "package":
        return delegate("package_skills", rest, use_root_cwd=True)
    if cmd == "verify":
        p = argparse.ArgumentParser(prog="cortex verify")
        p.add_argument("--project-dir", type=Path, default=Path.cwd())
        p.add_argument("--json", action="store_true", dest="as_json")
        return cmd_verify(p.parse_args(rest))

    print(f"ERROR: Unknown cortex subcommand {cmd!r}. Run `cortex --help`.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
