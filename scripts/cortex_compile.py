#!/usr/bin/env python3
"""Universal Agent Rule Compiler — compile Cortex SKILL.md playbooks into native IDE/agent formats."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "3.0.0"

SKILL_GLOBS: dict[str, str] = {
    "academic-assistant": "**/*.md,**/*.tex",
    "accessibility-auditor": "**/*.html,**/*.tsx,**/*.jsx,**/*.css",
    "anti-hallucination": "**/*",
    "api-designer": "**/*openapi*.yml,**/*openapi*.yaml,**/*swagger*.json",
    "architecture-decision-records": "docs/adr/**/*.md,adr/**/*.md",
    "blender-3d-modeling": "**/*.py,**/*.blend",
    "chaos-resilience-engineer": "**/*.py,**/*.ts,**/*.go,**/*.yaml,**/*.yml",
    "code-migration": "**/*",
    "code-review-assistant": "**/*",
    "college-report-card": "**/*.csv,**/*.json,**/*.py",
    "db-optimizer": "**/*.sql,**/migrations/**/*",
    "devops-pipeline": ".github/workflows/**/*.yml,.github/workflows/**/*.yaml,.gitlab-ci.yml",
    "docker-generator": "**/Dockerfile*,**/docker-compose*.yml,**/compose*.yaml",
    "documentation-generator": "**/*.md,docs/**/*",
    "finops-cost-optimizer": "**/*.tf,**/*.yaml,**/*.yml",
    "git-history-surgeon": "**/*",
    "go-backend-engineer": "**/*.go,**/go.mod",
    "graphql-architect": "**/*.graphql,**/*.gql",
    "incident-response": "**/*.md,**/*.json",
    "kubernetes-architect": "**/k8s/**/*.yaml,**/k8s/**/*.yml,**/charts/**/*.yaml",
    "llm-security-auditor": "**/*.md,**/*.prompt,**/*.py,**/*.ts",
    "memory-manager": "**/*",
    "observability-setup": "**/*.py,**/*.ts,**/*.go,**/*.yaml,**/*.yml",
    "performance-profiler": "**/*.py,**/*.ts,**/*.go,**/*.rs",
    "privacy-compliance-auditor": "**/*.py,**/*.ts,**/*.js,**/*.sql,**/*.json",
    "python-coding-assistant": "**/*.py,**/pyproject.toml",
    "refactoring-assistant": "**/*.py,**/*.ts,**/*.js,**/*.go,**/*.rs",
    "release-engineering": "CHANGELOG.md,package.json,pyproject.toml",
    "rust-systems-engineer": "**/*.rs,**/Cargo.toml",
    "security-auditor": "**/*",
    "supply-chain-sbom": "package.json,requirements*.txt,Cargo.toml,go.mod",
    "terraform-generator": "**/*.tf,**/*.tfvars",
    "testing-automation": "**/tests/**/*,**/*_test.*,**/*.test.*,**/*.spec.*",
    "typescript-architect": "**/*.ts,**/*.tsx,**/tsconfig.json",
    "unit-test-generator": "**/tests/**/*,**/*_test.*,**/*.test.*,**/*.spec.*",
    "web-scraper": "**/*.py,**/*.ts,**/robots.txt",
}

SUPPORTED_TARGETS = ("cursor", "vscode", "windsurf", "cline", "claude", "agents", "opencode", "gemini")
BEGIN_MARKER = "<!-- BEGIN CORTEX MANAGED -->"
END_MARKER = "<!-- END CORTEX MANAGED -->"


def parse_skill(md_path: Path) -> dict:
    raw = md_path.read_text(encoding="utf-8")
    norm_bytes = raw.replace("\r\n", "\n").encode("utf-8")
    sha = hashlib.sha256(norm_bytes).hexdigest()
    desc = ""
    version = VERSION
    body = raw
    m = re.match(r"^---\r?\n([\s\S]*?)\r?\n---\r?\n?", raw)
    if m:
        fm = m.group(1)
        body = raw[m.end() :].strip()
        dm = re.search(r"(?m)^description:\s*(.+)$", fm)
        vm = re.search(r"(?m)^version:\s*(.+)$", fm)
        if dm:
            desc = dm.group(1).strip().strip("\"'")
        if vm:
            version = vm.group(1).strip().strip("\"'")
    return {
        "slug": md_path.parent.name,
        "dir": md_path.parent.parent.name,
        "tier": "core" if md_path.parent.parent.name == "skills" else "extended",
        "description": desc,
        "version": version,
        "sha256": sha,
        "body": body,
        "globs": SKILL_GLOBS.get(md_path.parent.name, "**/*"),
    }


def discover_catalog(root: Path = ROOT) -> dict[str, dict]:
    catalog: dict[str, dict] = {}
    for folder in ("skills", "premium-skills"):
        base = root / folder
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            md = entry / "SKILL.md"
            if entry.is_dir() and md.is_file():
                catalog[entry.name] = parse_skill(md)
    return catalog


def resolve_skills(
    catalog: dict[str, dict],
    skills: list[str] | None = None,
    packs: list[str] | None = None,
    collection: str | None = None,
    root: Path = ROOT,
) -> list[dict]:
    chosen: list[str] = []
    if packs:
        packs_data = json.loads((root / "packs.json").read_text(encoding="utf-8"))
        pack_map = packs_data.get("packs", {})
        for pid in packs:
            if pid not in pack_map:
                raise ValueError(f"Unknown pack {pid!r}. Available: {', '.join(sorted(pack_map))}")
            for s in pack_map[pid]["skills"]:
                if s not in chosen:
                    chosen.append(s)
    if skills:
        for s in skills:
            if s not in catalog:
                raise ValueError(f"Unknown skill {s!r}")
            if s not in chosen:
                chosen.append(s)
    if collection:
        for slug, meta in sorted(catalog.items()):
            if collection == "all" or meta["tier"] == collection:
                if slug not in chosen:
                    chosen.append(slug)
    if not chosen:
        # Default to fullstack pack if nothing specified
        packs_data = json.loads((root / "packs.json").read_text(encoding="utf-8"))
        chosen = list(packs_data["packs"]["fullstack"]["skills"])
    return [catalog[s] for s in chosen if s in catalog]


def render_cursor_mdc(skill: dict) -> str:
    return (
        "---\n"
        f"description: {json.dumps(skill['description'])}\n"
        f"globs: {json.dumps(skill['globs'])}\n"
        "alwaysApply: false\n"
        "---\n\n"
        f"<!-- Compiled by Cortex v{VERSION} | skill={skill['slug']}@{skill['version']} | sha256={skill['sha256']} -->\n\n"
        f"{skill['body']}\n"
    )


def render_vscode_instruction(skill: dict) -> str:
    return (
        "---\n"
        f"applyTo: {json.dumps(skill['globs'])}\n"
        "---\n\n"
        f"<!-- Compiled by Cortex v{VERSION} | skill={skill['slug']}@{skill['version']} | sha256={skill['sha256']} -->\n\n"
        f"{skill['body']}\n"
    )


def render_plain_rule(skill: dict, target_label: str) -> str:
    return (
        f"<!-- Compiled by Cortex v{VERSION} for {target_label} | skill={skill['slug']}@{skill['version']} | sha256={skill['sha256']} -->\n\n"
        f"{skill['body']}\n"
    )


def render_managed_section(skills: list[dict], heading: str) -> str:
    lines = [
        BEGIN_MARKER,
        f"## {heading} (Cortex v{VERSION})",
        "",
        "| Skill | Tier | Applies To | Description | SHA-256 (prefix) |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for s in skills:
        lines.append(
            f"| `{s['slug']}` | {s['tier']} | `{s['globs']}` | {s['description']} | `{s['sha256'][:12]}` |"
        )
    lines.extend(["", END_MARKER])
    return "\n".join(lines) + "\n"


def upsert_managed_file(path: Path, section: str, title: str) -> str:
    if path.is_file():
        existing = path.read_text(encoding="utf-8")
        pattern = re.compile(re.escape(BEGIN_MARKER) + r"[\s\S]*?" + re.escape(END_MARKER) + r"\n?")
        if pattern.search(existing):
            return pattern.sub(section, existing, count=1)
        sep = "\n\n" if existing.strip() else ""
        return existing.rstrip() + sep + section
    return f"# {title}\n\n{section}"


def compile_rules(
    project_dir: Path,
    targets: list[str],
    skills: list[dict],
    *,
    dry_run: bool = False,
    check: bool = False,
) -> dict:
    resolved_targets = list(SUPPORTED_TARGETS) if "all" in targets else targets
    planned: list[tuple[Path, str]] = []

    for tgt in resolved_targets:
        if tgt == "cursor":
            for s in skills:
                planned.append((project_dir / ".cursor/rules" / f"cortex-{s['slug']}.mdc", render_cursor_mdc(s)))
        elif tgt == "vscode":
            for s in skills:
                planned.append((project_dir / ".github/instructions" / f"cortex-{s['slug']}.instructions.md", render_vscode_instruction(s)))
        elif tgt == "windsurf":
            for s in skills:
                planned.append((project_dir / ".windsurf/rules" / f"cortex-{s['slug']}.md", render_plain_rule(s, "Windsurf")))
        elif tgt == "cline":
            for s in skills:
                planned.append((project_dir / ".clinerules" / f"cortex-{s['slug']}.md", render_plain_rule(s, "Cline")))
        elif tgt == "claude":
            out = project_dir / "CLAUDE.md"
            sec = render_managed_section(skills, "Cortex Skills Index")
            planned.append((out, upsert_managed_file(out, sec, "CLAUDE.md")))
        elif tgt in {"agents", "opencode"}:
            out = project_dir / "AGENTS.md"
            sec = render_managed_section(skills, "Cortex Skills Index")
            planned.append((out, upsert_managed_file(out, sec, "AGENTS.md")))
        elif tgt == "gemini":
            out = project_dir / "GEMINI.md"
            sec = render_managed_section(skills, "Cortex Skills Index")
            planned.append((out, upsert_managed_file(out, sec, "GEMINI.md")))
        else:
            raise ValueError(f"Unsupported compile target: {tgt!r}")

    deduped: list[tuple[Path, str]] = []
    seen_paths: dict[Path, int] = {}
    for path, content in planned:
        resolved_out = path.resolve()
        if resolved_out in seen_paths:
            deduped[seen_paths[resolved_out]] = (path, content)
        else:
            seen_paths[resolved_out] = len(deduped)
            deduped.append((path, content))

    results: list[dict] = []
    drift_count = 0
    for path, content in deduped:
        rel = path.relative_to(project_dir).as_posix()
        existing = path.read_text(encoding="utf-8") if path.is_file() else None
        changed = existing != content
        if check:
            status = "drift" if changed else "ok"
            if changed:
                drift_count += 1
        elif dry_run:
            status = "would-write" if changed else "unchanged"
        else:
            if changed:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8", newline="\n")
                status = "written"
            else:
                status = "unchanged"
        results.append({"file": rel, "status": status, "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]})

    return {
        "version": VERSION,
        "project_dir": project_dir.as_posix(),
        "targets": resolved_targets,
        "skills": [s["slug"] for s in skills],
        "file_count": len(results),
        "drift_count": drift_count,
        "ok": drift_count == 0,
        "files": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compile Cortex SKILL.md playbooks into native Cursor, VS Code, Windsurf, Cline, Claude, AGENTS, and Gemini rules.")
    parser.add_argument("--target", "-t", action="append", choices=(*SUPPORTED_TARGETS, "all"), default=[], help="Output rule format(s).")
    parser.add_argument("--pack", "-p", action="append", default=[], help="Role pack ID(s) from packs.json.")
    parser.add_argument("--skill", "-s", action="append", default=[], help="Specific skill slug(s).")
    parser.add_argument("--collection", "-c", choices=("core", "extended", "all"), default=None)
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check", action="store_true", help="Exit 1 if compiled files differ from disk.")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    targets = args.target or ["cursor", "vscode"]
    try:
        catalog = discover_catalog(ROOT)
        skills = resolve_skills(catalog, skills=args.skill, packs=args.pack, collection=args.collection, root=ROOT)
        report = compile_rules(args.project_dir.resolve(), targets, skills, dry_run=args.dry_run, check=args.check)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Cortex Compiler v{VERSION} — {len(report['skills'])} skill(s) -> {', '.join(report['targets'])}")
        for f in report["files"]:
            print(f"  [{f['status']:<11}] {f['file']}")
        if args.check:
            print(f"\nCheck complete: {report['drift_count']} file(s) with drift.")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
