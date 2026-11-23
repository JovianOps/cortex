#!/usr/bin/env python3
"""Install Cortex SKILL.md playbooks into any supported AI coding agent.

Zero external dependencies (Python 3 stdlib only). Works on Linux, macOS, and Windows.

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
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLLECTIONS: dict[str, Path] = {
    "core": ROOT / "skills",
    "extended": ROOT / "premium-skills",
}


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
        label="GitHub Copilot & VS Code",
        global_rel=".copilot/skills",
        project_rel=".github/skills",
        note="Commit .github/skills/ to share skills with VS Code Copilot and Copilot coding agent.",
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
    "vscode": "copilot",
}


def discover_skills() -> dict[str, tuple[str, Path]]:
    """Return mapping of skill_slug -> (collection_name, skill_dir)."""
    found: dict[str, tuple[str, Path]] = {}
    for collection, base in COLLECTIONS.items():
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            if entry.is_dir() and (entry / "SKILL.md").is_file():
                found[entry.name] = (collection, entry)
    return found


def resolve_agents(raw_agents: list[str]) -> list[AgentTarget]:
    if not raw_agents:
        return []
    resolved: list[AgentTarget] = []
    seen: set[str] = set()
    for item in raw_agents:
        token = item.strip().lower()
        if token == "all":
            for key, target in AGENT_TARGETS.items():
                if key not in seen:
                    resolved.append(target)
                    seen.add(key)
            continue
        canonical = AGENT_ALIASES.get(token, token)
        if canonical not in AGENT_TARGETS:
            valid = ", ".join(sorted(AGENT_TARGETS.keys()) + ["all"])
            raise SystemExit(f"ERROR: Unknown agent {item!r}. Supported: {valid}")
        if canonical not in seen:
            resolved.append(AGENT_TARGETS[canonical])
            seen.add(canonical)
    return resolved


def select_skills(
    catalog: dict[str, tuple[str, Path]],
    collection: str,
    requested: list[str],
) -> list[tuple[str, str, Path]]:
    if requested:
        chosen: list[tuple[str, str, Path]] = []
        missing: list[str] = []
        for slug in requested:
            if slug in catalog:
                col, path = catalog[slug]
                chosen.append((slug, col, path))
            else:
                missing.append(slug)
        if missing:
            raise SystemExit(
                f"ERROR: Unknown skill(s): {', '.join(missing)}. Run --list to view available skills."
            )
        return chosen

    selected: list[tuple[str, str, Path]] = []
    for slug, (col, path) in catalog.items():
        if collection == "all" or col == collection:
            selected.append((slug, col, path))
    return selected


def destination_dir(target: AgentTarget, scope: str, project_root: Path) -> Path:
    if scope == "global":
        return Path.home() / target.global_rel
    return project_root / target.project_rel


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
        print(f"Aider config already references all selected skills: {conf_path}")
        return

    if dry_run:
        print(f"[dry-run] Would append {len(to_add)} read entries to {conf_path}")
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
    print(f"Updated {conf_path} with {len(to_add)} Cortex skill(s).")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install Cortex SKILL.md playbooks for Claude Code, Codex, Gemini CLI, Cursor, Copilot/VS Code, OpenCode, OpenClaw, Goose, Cline, Aider, and .agents/skills."
    )
    parser.add_argument(
        "--agent",
        "-a",
        action="append",
        default=[],
        help="Target agent(s): claude-code, codex, gemini-cli, cursor, copilot, opencode, openclaw, goose, cline, aider, agents, or all. Repeat for multiple.",
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
        help="Specific skill slug to install (repeatable). Overrides --collection.",
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
        "--write-aider-conf",
        action="store_true",
        help="When installing for aider, append installed SKILL.md paths to .aider.conf.yml in --project-dir.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be installed without writing files.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all supported agents and available Cortex skills, then exit.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    catalog = discover_skills()

    if args.list:
        print("Supported Agents:")
        for target in AGENT_TARGETS.values():
            print(
                f"  {target.key:<12} {target.label:<38} global: ~/{target.global_rel}   project: {target.project_rel}"
            )
        print("\nAvailable Cortex Skills:")
        for slug, (col, _) in catalog.items():
            print(f"  {slug:<26} ({col})")
        return 0

    if not args.agent:
        print("ERROR: Specify at least one --agent (or --agent all). Run --list for options.", file=sys.stderr)
        return 2

    agents = resolve_agents(args.agent)
    skills = select_skills(catalog, args.collection, args.skill)
    project_root = args.project_dir.resolve()

    for target in agents:
        dest_base = destination_dir(target, args.scope, project_root)
        installed_md: list[Path] = []
        print(f"\n==> {target.label} ({args.scope}: {dest_base})")
        for slug, _, src_dir in skills:
            dest_skill_dir = dest_base / slug
            dest_md = dest_skill_dir / "SKILL.md"
            if args.dry_run:
                print(f"  [dry-run] {src_dir / 'SKILL.md'} -> {dest_md}")
            else:
                dest_skill_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_dir / "SKILL.md", dest_md)
                print(f"  installed {slug} -> {dest_md}")
            installed_md.append(dest_md)

        if target.key == "aider":
            sample_flags = " ".join(f'--read "{p}"' for p in installed_md[:3])
            suffix = " ..." if len(installed_md) > 3 else ""
            print(f"  Aider usage: aider {sample_flags}{suffix}")
            if args.write_aider_conf:
                update_aider_conf(project_root, installed_md, args.dry_run)
        if target.note:
            print(f"  Note: {target.note}")

    print(f"\nDone! Installed {len(skills)} skill(s) across {len(agents)} agent target(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
