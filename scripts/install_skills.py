#!/usr/bin/env python3
"""Cortex v1.0.0 Multi-Agent Skill Manager — install, verify, upgrade, and uninstall SKILL.md playbooks.

Zero external dependencies (Python 3 stdlib only). Works on Linux, macOS, and Windows.

Highlights:
  - Installs full skill packages (SKILL.md + bundled scripts/, references/, templates/).
  - Supports --remote zero-clone installation with mandatory SHA-256 checksum verification.
  - Writes .cortex-lock.json for --status integrity checks, --check-updates, --upgrade, and --uninstall.

Supported agents:
  claude-code  Claude Code (~/.claude/skills or .claude/skills)
  codex        OpenAI Codex CLI (~/.codex/skills or .agents/skills)
  gemini-cli   Gemini CLI (~/.gemini/skills or .gemini/skills)
  cursor       Cursor (~/.cursor/skills or .cursor/skills)
  copilot      GitHub Copilot & VS Code (~/.copilot/skills or .github/skills)
  opencode     OpenCode (~/.config/opencode/skills or .opencode/skills)
  openclaw     OpenClaw (~/.openclaw/skills or .openclaw/skills)
  goose        Goose (~/.config/goose/skills or .goose/skills)
  cline        Cline (~/.cline/skills or .cline/skills)
  aider        Aider (~/.aider/skills or .aider/skills + --read / .aider.conf.yml)
  agents       Universal .agents/skills/ standard (~/.agents/skills or .agents/skills)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS: dict[str, Path] = {
    "core": ROOT / "skills",
    "extended": ROOT / "premium-skills",
}
DEFAULT_REPO = "JovianOps/cortex"
DEFAULT_REF = "main"
LOCKFILE_NAME = ".cortex-lock.json"
IGNORED_PARTS = {"__pycache__", ".DS_Store", ".pytest_cache"}


@dataclass(frozen=True)
class AgentTarget:
    key: str
    label: str
    global_rel: str
    project_rel: str
    note: str = ""


AGENT_TARGETS: dict[str, AgentTarget] = {
    "claude-code": AgentTarget(
        key="claude-code",
        label="Claude Code",
        global_rel=".claude/skills",
        project_rel=".claude/skills",
        note="Start a new Claude Code session or run /reload-skills.",
    ),
    "codex": AgentTarget(
        key="codex",
        label="OpenAI Codex CLI",
        global_rel=".codex/skills",
        project_rel=".agents/skills",
        note="Restart Codex or refresh skills to load newly installed playbooks.",
    ),
    "gemini-cli": AgentTarget(
        key="gemini-cli",
        label="Gemini CLI",
        global_rel=".gemini/skills",
        project_rel=".gemini/skills",
        note="Gemini CLI auto-discovers SKILL.md under ~/.gemini/skills/ and .gemini/skills/.",
    ),
    "cursor": AgentTarget(
        key="cursor",
        label="Cursor",
        global_rel=".cursor/skills",
        project_rel=".cursor/skills",
        note="Cursor loads SKILL.md files from .cursor/skills/ and ~/.cursor/skills/.",
    ),
    "copilot": AgentTarget(
        key="copilot",
        label="GitHub Copilot",
        global_rel=".copilot/skills",
        project_rel=".github/skills",
        note="Commit .github/skills/ to share skills with GitHub Copilot and Copilot coding agent.",
    ),
    "vscode": AgentTarget(
        key="vscode",
        label="Visual Studio Code",
        global_rel=".copilot/skills",
        project_rel=".github/skills",
        note='VS Code auto-loads SKILL.md from .github/skills/ and ~/.copilot/skills/. For native plugin installs, add "JovianOps/cortex" to chat.plugins.marketplaces.',
    ),
    "opencode": AgentTarget(
        key="opencode",
        label="OpenCode",
        global_rel=".config/opencode/skills",
        project_rel=".opencode/skills",
        note="Restart OpenCode to pick up newly installed SKILL.md playbooks.",
    ),
    "openclaw": AgentTarget(
        key="openclaw",
        label="OpenClaw",
        global_rel=".openclaw/skills",
        project_rel=".openclaw/skills",
        note="Start a new OpenClaw session to activate newly installed skills.",
    ),
    "goose": AgentTarget(
        key="goose",
        label="Goose",
        global_rel=".config/goose/skills",
        project_rel=".goose/skills",
        note="Goose discovers SKILL.md playbooks in ~/.config/goose/skills/ and .goose/skills/.",
    ),
    "cline": AgentTarget(
        key="cline",
        label="Cline",
        global_rel=".cline/skills",
        project_rel=".cline/skills",
        note="Open Cline's Skills panel in VS Code or invoke skills with /<skill-name>.",
    ),
    "aider": AgentTarget(
        key="aider",
        label="Aider",
        global_rel=".aider/skills",
        project_rel=".aider/skills",
        note="Pass installed SKILL.md files via `aider --read <path>` or add them to `.aider.conf.yml`.",
    ),
    "agents": AgentTarget(
        key="agents",
        label="Universal Agent Skills (.agents/skills)",
        global_rel=".agents/skills",
        project_rel=".agents/skills",
        note="Shared canonical Agent Skills directory read by Codex, Copilot, OpenCode, and skills CLI.",
    ),
}

AGENT_ALIASES: dict[str, str] = {
    "claude": "claude-code",
    "openai": "codex",
    "gemini": "gemini-cli",
    "github-copilot": "copilot",
    "vs-code": "vscode",
    "code": "vscode",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".sh", ".ps1", ".toml", ".csv"}:
        return raw.replace(b"\r\n", b"\n")
    return raw


def raw_url(repo: str, ref: str, rel_path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{rel_path}"


def fetch_bytes(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "cortex-installer/1.0.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to download {url}: {exc}") from exc


def load_local_catalog() -> dict:
    """Build catalog manifest directly from the local repository checkout."""
    checksums_path = ROOT / "checksums.json"
    if checksums_path.is_file():
        return json.loads(checksums_path.read_text(encoding="utf-8"))

    pkg_version = "1.0.0"
    pkg_json = ROOT / "package.json"
    if pkg_json.is_file():
        pkg_version = json.loads(pkg_json.read_text(encoding="utf-8")).get("version", pkg_version)

    skills_index: dict[str, dict] = {}
    for col, base in COLLECTIONS.items():
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            if not (entry.is_dir() and (entry / "SKILL.md").is_file()):
                continue
            files_map: dict[str, str] = {}
            for fp in sorted(entry.rglob("*")):
                if any(part in IGNORED_PARTS or part.endswith(".pyc") for part in fp.parts):
                    continue
                if fp.is_file():
                    rel = fp.relative_to(entry).as_posix()
                    files_map[rel] = sha256_bytes(normalized_bytes(fp))
            skills_index[entry.name] = {
                "collection": col,
                "dir": base.name,
                "files": files_map,
            }
    return {
        "schema_version": "1.0.0",
        "release_version": pkg_version,
        "skill_count": len(skills_index),
        "skills": skills_index,
    }


def load_remote_catalog(repo: str, ref: str) -> dict:
    url = raw_url(repo, ref, "checksums.json")
    data = json.loads(fetch_bytes(url).decode("utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("skills"), dict):
        raise RuntimeError(f"Invalid checksums.json received from {url}")
    return data


def resolve_agents(raw_agents: list[str]) -> list[AgentTarget]:
    if not raw_agents:
        return []
    resolved: list[AgentTarget] = []
    seen: set[str] = set()
    seen_paths: set[tuple[str, str]] = set()
    for item in raw_agents:
        token = item.strip().lower()
        if token == "all":
            for key, target in AGENT_TARGETS.items():
                path_pair = (target.global_rel, target.project_rel)
                if key not in seen and path_pair not in seen_paths:
                    resolved.append(target)
                    seen.add(key)
                    seen_paths.add(path_pair)
            continue
        canonical = AGENT_ALIASES.get(token, token)
        if canonical not in AGENT_TARGETS:
            valid = ", ".join(sorted(AGENT_TARGETS.keys()) + ["all"])
            raise SystemExit(f"ERROR: Unknown agent {item!r}. Supported: {valid}")
        if canonical not in seen:
            target = AGENT_TARGETS[canonical]
            resolved.append(target)
            seen.add(canonical)
            seen_paths.add((target.global_rel, target.project_rel))
    return resolved


def load_packs(remote: bool = False, repo: str = DEFAULT_REPO, ref: str = DEFAULT_REF) -> dict[str, dict]:
    if remote:
        data = json.loads(fetch_bytes(raw_url(repo, ref, "packs.json")).decode("utf-8"))
        return data.get("packs", {})
    packs_path = ROOT / "packs.json"
    if packs_path.is_file():
        return json.loads(packs_path.read_text(encoding="utf-8")).get("packs", {})
    return {}


def select_skills(
    catalog: dict,
    collection: str,
    requested: list[str],
    pack_names: list[str] | None = None,
    packs: dict[str, dict] | None = None,
) -> list[tuple[str, dict]]:
    skills_map: dict[str, dict] = catalog["skills"]
    combined: list[str] = list(requested)
    if pack_names:
        available_packs = packs or {}
        for pname in pack_names:
            key = pname.strip().lower()
            if key not in available_packs:
                valid = ", ".join(sorted(available_packs.keys()))
                raise SystemExit(f"ERROR: Unknown pack {pname!r}. Available packs: {valid}")
            for slug in available_packs[key]["skills"]:
                if slug not in combined:
                    combined.append(slug)

    if combined:
        chosen: list[tuple[str, dict]] = []
        missing: list[str] = []
        for slug in combined:
            if slug in skills_map:
                chosen.append((slug, skills_map[slug]))
            else:
                missing.append(slug)
        if missing:
            raise SystemExit(
                f"ERROR: Unknown skill(s): {', '.join(missing)}. Run --list to view available skills."
            )
        return chosen
    return [
        (slug, meta)
        for slug, meta in skills_map.items()
        if collection == "all" or meta.get("collection") == collection
    ]


def destination_dir(target: AgentTarget, scope: str, project_root: Path) -> Path:
    if scope == "global":
        return Path.home() / target.global_rel
    return project_root / target.project_rel


def read_lockfile(dest_base: Path) -> dict:
    lock_path = dest_base / LOCKFILE_NAME
    if lock_path.is_file():
        try:
            data = json.loads(lock_path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("skills"), dict):
                return data
        except json.JSONDecodeError:
            pass
    return {"schema_version": "1.0.0", "skills": {}}


def write_lockfile(dest_base: Path, lock_data: dict) -> None:
    dest_base.mkdir(parents=True, exist_ok=True)
    lock_path = dest_base / LOCKFILE_NAME
    lock_path.write_text(json.dumps(lock_data, indent=2) + "\n", encoding="utf-8")


def update_aider_conf(project_root: Path, installed_files: list[Path], dry_run: bool) -> None:
    conf_path = project_root / ".aider.conf.yml"
    rel_paths: list[str] = []
    for path in installed_files:
        try:
            rel_paths.append(path.relative_to(project_root).as_posix())
        except ValueError:
            rel_paths.append(path.as_posix())

    existing_lines: list[str] = []
    if conf_path.is_file():
        existing_lines = conf_path.read_text(encoding="utf-8").splitlines()

    existing_text = "\n".join(existing_lines)
    to_add = [p for p in rel_paths if p not in existing_text]
    if not to_add:
        print(f"  Aider config already references all selected skills: {conf_path}")
        return

    if dry_run:
        print(f"  [dry-run] Would append {len(to_add)} read entries to {conf_path}")
        return

    if "read:" in existing_lines:
        idx = existing_lines.index("read:")
        insertion = [f"  - {p}" for p in to_add]
        new_lines = existing_lines[: idx + 1] + insertion + existing_lines[idx + 1 :]
    else:
        new_lines = list(existing_lines)
        if new_lines and new_lines[-1].strip():
            new_lines.append("")
        new_lines.append("read:")
        new_lines.extend(f"  - {p}" for p in to_add)

    conf_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"  Updated {conf_path} with {len(to_add)} Cortex skill(s).")


def update_vscode_settings(project_root: Path, dry_run: bool) -> None:
    """Safely enable Agent Skills in .vscode/settings.json without clobbering existing keys."""
    settings_path = project_root / ".vscode" / "settings.json"
    existing: dict = {}
    if settings_path.is_file():
        try:
            parsed = json.loads(settings_path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                existing = parsed
            else:
                print(f"  Skipped {settings_path}: expected top-level JSON object.")
                return
        except json.JSONDecodeError:
            print(f"  Skipped {settings_path}: existing file contains comments or non-strict JSON.")
            return

    if existing.get("chat.useAgentSkills") is True:
        print(f"  VS Code settings already enable chat.useAgentSkills: {settings_path}")
        return

    if dry_run:
        print(f"  [dry-run] Would set chat.useAgentSkills=true in {settings_path}")
        return

    existing["chat.useAgentSkills"] = True
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    print(f"  Updated {settings_path} with chat.useAgentSkills=true.")


def install_single_skill(
    slug: str,
    meta: dict,
    dest_base: Path,
    *,
    remote: bool,
    repo: str,
    ref: str,
    dry_run: bool,
) -> dict[str, str]:
    files_meta: dict[str, str] = meta["files"]
    src_dir_name = meta["dir"]
    dest_skill_dir = dest_base / slug
    written_hashes: dict[str, str] = {}

    for rel_file, expected_sha in files_meta.items():
        target_path = dest_skill_dir / rel_file
        if remote:
            url = raw_url(repo, ref, f"{src_dir_name}/{slug}/{rel_file}")
            if dry_run:
                print(f"  [dry-run] GET {url} -> {target_path} (sha256:{expected_sha[:12]})")
                written_hashes[rel_file] = expected_sha
                continue
            payload = fetch_bytes(url)
            if target_path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".sh", ".ps1", ".toml", ".csv"}:
                payload = payload.replace(b"\r\n", b"\n")
            actual_sha = sha256_bytes(payload)
            if actual_sha != expected_sha:
                raise RuntimeError(
                    f"SHA-256 verification FAILED for {slug}/{rel_file}: "
                    f"expected {expected_sha}, got {actual_sha}"
                )
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(payload)
            written_hashes[rel_file] = actual_sha
        else:
            src_path = ROOT / src_dir_name / slug / rel_file
            if not src_path.is_file():
                raise RuntimeError(f"Source file missing: {src_path}")
            payload = normalized_bytes(src_path)
            actual_sha = sha256_bytes(payload)
            if dry_run:
                print(f"  [dry-run] {src_path} -> {target_path}")
                written_hashes[rel_file] = actual_sha
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_bytes(payload)
            written_hashes[rel_file] = actual_sha

    if not dry_run:
        extra = f" (+{len(files_meta) - 1} bundled resource(s))" if len(files_meta) > 1 else ""
        print(f"  installed {slug} -> {dest_skill_dir / 'SKILL.md'}{extra}")
    return written_hashes


def cmd_status(agents: list[AgentTarget], scope: str, project_root: Path) -> int:
    any_issues = False
    for target in agents:
        dest_base = destination_dir(target, scope, project_root)
        lock = read_lockfile(dest_base)
        installed = lock.get("skills", {})
        print(f"\n==> {target.label} ({scope}: {dest_base})")
        if not installed:
            print("  (no Cortex skills recorded in lockfile)")
            continue
        for slug, entry in sorted(installed.items()):
            ver = entry.get("version", "?")
            files = entry.get("files", {})
            state = "OK"
            for rel_file, recorded_sha in files.items():
                fp = dest_base / slug / rel_file
                if not fp.is_file():
                    state = f"MISSING ({rel_file})"
                    any_issues = True
                    break
                if sha256_bytes(normalized_bytes(fp)) != recorded_sha:
                    state = f"MODIFIED ({rel_file})"
                    any_issues = True
                    break
            print(f"  {slug:<26} v{ver:<8} [{state}]")
    return 1 if any_issues else 0


def cmd_check_updates(
    agents: list[AgentTarget],
    scope: str,
    project_root: Path,
    catalog: dict,
    *,
    do_upgrade: bool,
    remote: bool,
    repo: str,
    ref: str,
    dry_run: bool,
) -> int:
    latest_version = catalog.get("release_version", "1.0.0")
    skills_map = catalog["skills"]
    updates_found = 0

    for target in agents:
        dest_base = destination_dir(target, scope, project_root)
        lock = read_lockfile(dest_base)
        installed = lock.get("skills", {})
        print(f"\n==> {target.label} ({scope}: {dest_base})")
        if not installed:
            print("  (no Cortex skills recorded in lockfile)")
            continue
        changed = False
        for slug, entry in sorted(installed.items()):
            if slug not in skills_map:
                print(f"  {slug:<26} [REMOVED FROM CATALOG]")
                continue
            latest_files = skills_map[slug]["files"]
            current_files = entry.get("files", {})
            if current_files == latest_files and entry.get("version") == latest_version:
                print(f"  {slug:<26} v{latest_version:<8} [UP TO DATE]")
                continue
            updates_found += 1
            if do_upgrade:
                hashes = install_single_skill(
                    slug, skills_map[slug], dest_base, remote=remote, repo=repo, ref=ref, dry_run=dry_run
                )
                if not dry_run:
                    installed[slug] = {
                        "version": latest_version,
                        "dir": skills_map[slug]["dir"],
                        "installed_at": datetime.now(timezone.utc).isoformat(),
                        "files": hashes,
                    }
                    changed = True
            else:
                print(f"  {slug:<26} v{entry.get('version', '?')} -> v{latest_version} [UPDATE AVAILABLE]")
        if changed and not dry_run:
            lock["release_version"] = latest_version
            write_lockfile(dest_base, lock)

    if not do_upgrade:
        print(f"\n{updates_found} skill update(s) available." if updates_found else "\nAll installed skills are up to date.")
    return 0


def cmd_uninstall(
    agents: list[AgentTarget],
    scope: str,
    project_root: Path,
    requested_skills: list[str],
    remove_all: bool,
    dry_run: bool,
) -> int:
    if not requested_skills and not remove_all:
        print("ERROR: --uninstall requires --skill <slug> or --all.", file=sys.stderr)
        return 2
    for target in agents:
        dest_base = destination_dir(target, scope, project_root)
        lock = read_lockfile(dest_base)
        installed = lock.get("skills", {})
        to_remove = sorted(installed.keys()) if remove_all else requested_skills
        print(f"\n==> {target.label} ({scope}: {dest_base})")
        if not to_remove:
            print("  (nothing to uninstall)")
            continue
        for slug in to_remove:
            skill_dir = dest_base / slug
            if dry_run:
                print(f"  [dry-run] Would remove {skill_dir}")
                continue
            if skill_dir.is_dir():
                shutil.rmtree(skill_dir)
                print(f"  removed {slug} ({skill_dir})")
            else:
                print(f"  skipped {slug} (not found at {skill_dir})")
            installed.pop(slug, None)
        if not dry_run:
            write_lockfile(dest_base, lock)
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install, verify, upgrade, and uninstall Cortex v1.0.0 SKILL.md playbooks across 12 AI agent & IDE targets."
    )
    parser.add_argument(
        "--agent",
        "-a",
        action="append",
        default=[],
        help="Target agent(s): claude-code, codex, gemini-cli, cursor, copilot, vscode, opencode, openclaw, goose, cline, aider, agents, or all.",
    )
    parser.add_argument(
        "--collection",
        "-c",
        choices=("all", "core", "extended"),
        default="all",
        help="Skill collection to install when --skill is omitted (default: all).",
    )
    parser.add_argument(
        "--skill",
        "-s",
        action="append",
        default=[],
        help="Specific skill slug to install/uninstall (repeatable). Overrides --collection.",
    )
    parser.add_argument(
        "--pack",
        "-p",
        action="append",
        default=[],
        help="Install a curated role-based skill pack from packs.json (e.g., fullstack, devops-sre, security-hardening, python-pro, academic, clean-migration).",
    )
    parser.add_argument(
        "--scope",
        choices=("global", "project"),
        default="global",
        help="Install into home directory (global) or current project root (project). Default: global.",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project root used when --scope project is set (default: current working directory).",
    )
    parser.add_argument(
        "--remote",
        action="store_true",
        help="Fetch skills directly from GitHub with SHA-256 verification (no git clone required).",
    )
    parser.add_argument(
        "--repo",
        default=DEFAULT_REPO,
        help=f"GitHub owner/repo used with --remote (default: {DEFAULT_REPO}).",
    )
    parser.add_argument(
        "--ref",
        default=DEFAULT_REF,
        help=f"Git branch or tag used with --remote (default: {DEFAULT_REF}).",
    )
    parser.add_argument("--status", action="store_true", help="Verify installed skills against .cortex-lock.json SHA-256 hashes.")
    parser.add_argument("--check-updates", action="store_true", help="Check whether installed skills have newer versions.")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade installed skills to match the latest catalog.")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall --skill <slug> or --all Cortex skills.")
    parser.add_argument("--all", action="store_true", dest="all_flag", help="Used with --uninstall to remove all locked Cortex skills.")
    parser.add_argument(
        "--write-aider-conf",
        action="store_true",
        help="When installing for aider, append installed SKILL.md paths to .aider.conf.yml in --project-dir.",
    )
    parser.add_argument(
        "--write-vscode-settings",
        action="store_true",
        help="When installing for vscode, ensure chat.useAgentSkills=true in .vscode/settings.json under --project-dir.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing or deleting files.")
    parser.add_argument("--list", action="store_true", help="List all supported agents and available Cortex skills.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    if args.list:
        catalog = load_remote_catalog(args.repo, args.ref) if args.remote else load_local_catalog()
        print("Supported Agents:")
        for target in AGENT_TARGETS.values():
            print(
                f"  {target.key:<12} {target.label:<38} global: ~/{target.global_rel}   project: {target.project_rel}"
            )
        print(f"\nAvailable Cortex Skills (v{catalog.get('release_version', '1.0.0')} — {len(catalog['skills'])} total):")
        for slug, meta in catalog["skills"].items():
            extras = [f for f in meta.get("files", {}) if f != "SKILL.md"]
            badge = f"  [+{len(extras)} script(s)]" if extras else ""
            print(f"  {slug:<26} ({meta.get('collection', 'core')}){badge}")
        return 0

    if not args.agent:
        print("ERROR: Specify at least one --agent (or --agent all). Run --list for options.", file=sys.stderr)
        return 2

    agents = resolve_agents(args.agent)
    project_root = args.project_dir.resolve()

    if args.status:
        return cmd_status(agents, args.scope, project_root)
    if args.uninstall:
        return cmd_uninstall(agents, args.scope, project_root, args.skill, args.all_flag, args.dry_run)

    catalog = load_remote_catalog(args.repo, args.ref) if args.remote else load_local_catalog()

    if args.check_updates or args.upgrade:
        return cmd_check_updates(
            agents,
            args.scope,
            project_root,
            catalog,
            do_upgrade=args.upgrade,
            remote=args.remote,
            repo=args.repo,
            ref=args.ref,
            dry_run=args.dry_run,
        )

    packs = load_packs(args.remote, args.repo, args.ref) if args.pack else {}
    skills = select_skills(catalog, args.collection, args.skill, args.pack, packs)
    release_ver = catalog.get("release_version", "1.0.0")

    for target in agents:
        dest_base = destination_dir(target, args.scope, project_root)
        lock = read_lockfile(dest_base)
        installed_md: list[Path] = []
        print(f"\n==> {target.label} ({args.scope}: {dest_base})")
        for slug, meta in skills:
            hashes = install_single_skill(
                slug, meta, dest_base, remote=args.remote, repo=args.repo, ref=args.ref, dry_run=args.dry_run
            )
            installed_md.append(dest_base / slug / "SKILL.md")
            if not args.dry_run:
                lock["skills"][slug] = {
                    "version": release_ver,
                    "dir": meta["dir"],
                    "installed_at": datetime.now(timezone.utc).isoformat(),
                    "files": hashes,
                }
        if not args.dry_run:
            lock["release_version"] = release_ver
            write_lockfile(dest_base, lock)

        if target.key == "aider":
            sample_flags = " ".join(f'--read "{p}"' for p in installed_md[:3])
            suffix = " ..." if len(installed_md) > 3 else ""
            print(f"  Aider usage: aider {sample_flags}{suffix}")
            if args.write_aider_conf:
                update_aider_conf(project_root, installed_md, args.dry_run)
        if target.key == "vscode" and args.write_vscode_settings:
            update_vscode_settings(project_root, args.dry_run)
        if target.note:
            print(f"  Note: {target.note}")

    source_desc = f"remote ({args.repo}@{args.ref}, SHA-256 verified)" if args.remote else "local checkout"
    print(f"\nDone! Installed {len(skills)} skill(s) from {source_desc} across {len(agents)} agent target(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
