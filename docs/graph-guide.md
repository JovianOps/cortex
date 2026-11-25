# Capability Graph (`cortex graph`)

`cortex graph` turns the Cortex catalog into an inspectable directed graph. Skills and role packs become nodes; pack membership and `metadata.hermes.related_skills` become edges. The graph is deterministic — the same checkout always produces byte-identical JSON, Mermaid, or DOT.

## Why it exists

A skill catalog is a dependency system whether or not you model it. Packs overlap, skills cross-reference siblings, and some skills drift outside every pack. `cortex graph` makes those relationships explicit so you can answer:

- Which skills are the real hubs every pack reaches for?
- Which skills are not in any role pack (orphans)?
- Which `related_skills` or pack entries point at a slug that no longer exists?
- What does a pack actually cover before an agent installs it?

## Usage

```bash
# Full machine-readable report (nodes, edges, metrics, hubs, orphans)
python scripts/cortex_graph.py

# Human-reviewable Mermaid diagram for docs or PRs
python scripts/cortex_graph.py --format mermaid --out docs/capability-graph.mmd

# Graphviz DOT for rendering (optionally scoped to one or more packs)
python scripts/cortex_graph.py --format dot --pack cloud-native --out capability-graph.dot

# CI gate: fail on dangling pack/related references
python scripts/cortex_graph.py --check

# Stricter gate: also fail when a skill belongs to no role pack
python scripts/cortex_graph.py --check --strict
```

`--project-dir` lets you point the graph at another Cortex checkout.

## Report shape

```json
{
  "version": "3.0.0",
  "skill_count": 36,
  "pack_count": 10,
  "edge_count": 179,
  "pack_edges": 61,
  "related_edges": 118,
  "skills": { "security-auditor": { "tier": "extended", "related": ["..."], "sha256": "..." } },
  "packs": { "fullstack": { "skill_count": 6, "skills": ["..."] } },
  "edges": [{ "from": "pack:fullstack", "to": "skill:security-auditor", "type": "contains" }],
  "metrics": { "security-auditor": { "packs": 3, "related_out": 4, "related_in": 15, "degree": 22, "hub_score": 1.0 } },
  "hubs": ["security-auditor", "code-review-assistant", "devops-pipeline", "python-coding-assistant", "anti-hallucination"],
  "orphans": [],
  "dangling_references": [],
  "ok": true
}
```

`hub_score` is degree centrality normalised to the highest-degree skill (packs + inbound + outbound related edges). It is a routing signal, not a quality score.

## Exit codes

| Code | Meaning |
| :--- | :--- |
| `0` | Graph built; with `--check`, no dangling references (and no orphans under `--strict`). |
| `1` | `--check` found dangling references (or orphans with `--strict`). |
| `2` | The catalog or `packs.json` could not be read. |

## In CI

```yaml
- name: Capability graph gate
  run: python scripts/cortex_graph.py --check
```

`cortex guard check` already includes this gate. MCP clients can call `cortex_skill_graph`, and Studio exposes it at `GET /api/graph?format=json|mermaid|dot`.
