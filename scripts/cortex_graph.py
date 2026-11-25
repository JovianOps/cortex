#!/usr/bin/env python3
"""Cortex Capability Graph (v3.0.0) — map skills, role packs, and related-skill edges.

Builds a deterministic directed graph from the on-disk catalog, `packs.json`, and
`metadata.hermes.related_skills` frontmatter, then reports centrality, pack coverage,
orphaned skills, and dangling references. Emits JSON, Mermaid, or Graphviz DOT.

Zero external dependencies (Python 3 stdlib only).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "3.0.0"
COLLECTIONS = (("skills", "core"), ("premium-skills", "extended"))


def parse_skill(skill_md: Path, checksums: dict) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    slug = skill_md.parent.name
    desc = ""
    related: list[str] = []
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            dm = re.search(r"(?m)^description:\s*(.+)$", frontmatter)
            if dm:
                desc = dm.group(1).strip().strip("\"'")
            rm = re.search(r"related_skills:\s*\[([^\]]*)\]", frontmatter)
            if rm:
                related = [
                    item.strip().strip("\"'")
                    for item in rm.group(1).split(",")
                    if item.strip()
                ]
    entry = checksums.get("skills", {}).get(slug, {})
    return {
        "slug": slug,
        "tier": "core" if skill_md.parent.parent.name == "skills" else "extended",
        "dir": skill_md.parent.parent.name,
        "description": desc,
        "related": sorted(set(related)),
        "sha256": entry.get("files", {}).get("SKILL.md", ""),
    }


def _connected_components(skills: dict[str, dict], packs: dict[str, list[str]], edges: list[dict]) -> int:
    nodes = {f"skill:{s}" for s in skills} | {f"pack:{p}" for p in packs}
    adj: dict[str, set[str]] = {n: set() for n in nodes}
    for edge in edges:
        src, dst = edge["from"], edge["to"]
        if src in adj and dst in adj:
            adj[src].add(dst)
            adj[dst].add(src)
    visited: set[str] = set()
    components = 0
    for node in nodes:
        if node in visited:
            continue
        components += 1
        stack = [node]
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            stack.extend(adj[cur] - visited)
    return components


def build_graph(root: Path = ROOT, packs_filter: list[str] | None = None) -> dict:
    checksums_path = root / "checksums.json"
    checksums = (
        json.loads(checksums_path.read_text(encoding="utf-8"))
        if checksums_path.is_file()
        else {}
    )
    all_skills: dict[str, dict] = {}
    for folder, _tier in COLLECTIONS:
        base = root / folder
        if not base.is_dir():
            continue
        for entry in sorted(base.iterdir()):
            md = entry / "SKILL.md"
            if entry.is_dir() and md.is_file():
                meta = parse_skill(md, checksums)
                all_skills[meta["slug"]] = meta

    packs_data = json.loads((root / "packs.json").read_text(encoding="utf-8"))
    all_packs: dict[str, list[str]] = {
        pid: list(info.get("skills", []))
        for pid, info in packs_data.get("packs", {}).items()
    }

    if packs_filter:
        unknown = [pid for pid in packs_filter if pid not in all_packs]
        if unknown:
            raise ValueError(f"Unknown pack(s): {', '.join(unknown)}")
        packs = {pid: all_packs[pid] for pid in packs_filter}
        selected_slugs = {slug for members in packs.values() for slug in members}
        skills = {slug: all_skills[slug] for slug in sorted(selected_slugs) if slug in all_skills}
    else:
        packs = all_packs
        skills = all_skills

    dangling: list[dict] = []
    pack_edges: list[dict] = []
    for pid, members in packs.items():
        for slug in members:
            if slug not in all_skills:
                dangling.append({"from": f"pack:{pid}", "to": f"skill:{slug}", "type": "contains"})
                continue
            pack_edges.append({"from": f"pack:{pid}", "to": f"skill:{slug}", "type": "contains"})

    related_edges: list[dict] = []
    for slug, meta in sorted(skills.items()):
        for target in meta["related"]:
            if target not in all_skills or target == slug:
                dangling.append({"from": f"skill:{slug}", "to": f"skill:{target}", "type": "related"})
                continue
            if target in skills:
                related_edges.append({"from": f"skill:{slug}", "to": f"skill:{target}", "type": "related"})

    pack_count = {slug: 0 for slug in skills}
    for edge in pack_edges:
        pack_count[edge["to"].removeprefix("skill:")] += 1
    incoming = {slug: 0 for slug in skills}
    outgoing = {slug: 0 for slug in skills}
    for edge in related_edges:
        outgoing[edge["from"].removeprefix("skill:")] += 1
        incoming[edge["to"].removeprefix("skill:")] += 1

    max_degree = max((pack_count[s] + incoming[s] + outgoing[s] for s in skills), default=0)
    metrics = {
        slug: {
            "packs": pack_count[slug],
            "related_out": outgoing[slug],
            "related_in": incoming[slug],
            "degree": pack_count[slug] + incoming[slug] + outgoing[slug],
            "hub_score": round(
                (pack_count[slug] + incoming[slug] + outgoing[slug]) / max_degree, 3
            ) if max_degree else 0.0,
        }
        for slug in sorted(skills)
    }

    orphans = sorted(slug for slug in skills if pack_count[slug] == 0)
    hubs = sorted(
        metrics,
        key=lambda s: (-metrics[s]["hub_score"], s),
    )[:5]
    edges = pack_edges + related_edges

    return {
        "version": VERSION,
        "skill_count": len(skills),
        "pack_count": len(packs),
        "edge_count": len(edges),
        "pack_edges": len(pack_edges),
        "related_edges": len(related_edges),
        "components": _connected_components(skills, packs, edges),
        "skills": {slug: skills[slug] for slug in sorted(skills)},
        "packs": {pid: {"skill_count": len(members), "skills": members} for pid, members in sorted(packs.items())},
        "edges": edges,
        "metrics": metrics,
        "hubs": hubs,
        "orphans": orphans,
        "dangling_references": dangling,
        "ok": not dangling,
    }


def to_mermaid(graph: dict) -> str:
    lines = ["graph LR", '  subgraph packs["Role Packs"]']
    for pid, info in graph["packs"].items():
        lines.append(f'    P_{pid.replace("-", "_")}["{pid} ({info["skill_count"]})"]')
    lines.append("  end")
    lines.append('  subgraph catalog["Skill Catalog"]')
    for slug in graph["skills"]:
        lines.append(f'    S_{slug.replace("-", "_")}["{slug}"]')
    lines.append("  end")
    for edge in graph["edges"]:
        src = edge["from"].replace("pack:", "P_").replace("skill:", "S_").replace("-", "_")
        dst = edge["to"].replace("pack:", "P_").replace("skill:", "S_").replace("-", "_")
        arrow = "-->" if edge["type"] == "contains" else "-. related .->"
        lines.append(f"  {src} {arrow} {dst}")
    return "\n".join(lines) + "\n"


def to_dot(graph: dict) -> str:
    lines = ["digraph cortex {", '  rankdir="LR";', '  node [shape=box, fontname="Helvetica"];']
    for pid in graph["packs"]:
        lines.append(f'  "pack:{pid}" [style=filled, fillcolor="#f1efe8"];')
    for edge in graph["edges"]:
        style = "solid" if edge["type"] == "contains" else "dashed"
        lines.append(f'  "{edge["from"]}" -> "{edge["to"]}" [style={style}, label="{edge["type"]}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the Cortex skill/pack capability graph (JSON, Mermaid, or Graphviz DOT)."
    )
    parser.add_argument("--format", "-f", choices=("json", "mermaid", "dot"), default="json")
    parser.add_argument("--pack", "-p", action="append", default=[], help="Restrict graph output to specific role pack ID(s).")
    parser.add_argument("--out", "-o", type=Path, default=None, help="Write output to a file instead of stdout.")
    parser.add_argument("--check", action="store_true", help="Exit 1 on dangling pack/related references.")
    parser.add_argument("--strict", action="store_true", help="With --check, also fail on skills that no pack includes.")
    parser.add_argument("--project-dir", type=Path, default=ROOT, help="Cortex catalog root (defaults to this checkout).")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit the full JSON report.")
    args = parser.parse_args(argv)

    try:
        graph = build_graph(args.project_dir.resolve(), packs_filter=args.pack or None)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"ERROR: could not build capability graph: {exc}", file=sys.stderr)
        return 2

    fmt = "json" if args.as_json else args.format
    if fmt == "mermaid":
        rendered = to_mermaid(graph)
    elif fmt == "dot":
        rendered = to_dot(graph)
    else:
        rendered = json.dumps(graph, indent=2) + "\n"

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
        if not args.as_json and fmt == "json":
            print(f"Wrote capability graph to {args.out}")
    else:
        sys.stdout.write(rendered)

    if not args.check:
        return 0

    failures = bool(graph["dangling_references"])
    if args.strict and graph["orphans"]:
        failures = True
    details = []
    if graph["dangling_references"]:
        details.append(f"{len(graph['dangling_references'])} dangling reference(s)")
    if args.strict and graph["orphans"]:
        details.append(f"{len(graph['orphans'])} orphaned skill(s): {', '.join(graph['orphans'])}")
    print(
        f"Capability graph: {graph['skill_count']} skills, {graph['pack_count']} packs, "
        f"{graph['edge_count']} edges - {'OK' if not failures else 'FAIL'}"
        + (f" ({'; '.join(details)})" if details else ""),
        file=sys.stderr,
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
