# Cortex v3.0.0 Architecture

Cortex `v3.0.0` is a **zero-dependency Agent OS**: a `SKILL.md` catalog with deterministic Python 3 verifiers, a native MCP 2025-03-26 server, a local web workbench, a universal agent-rule compiler, a unified policy/SARIF scanner, a capability graph, deterministic portable bundles, and a single release gate that generates its own CI and Git hooks.

## System Topology

```text
                        +--------------------------------------------+
                        |         Cortex Canonical Catalog           |
                        |  36 SKILL.md Playbooks + 36 Python Tools   |
                        |  10 Role Packs (packs.json)                |
                        |  36 Eval Rubrics (evals/skill_evals.json)  |
                        |  72 SHA-256 Digests (checksums.json)       |
                        +---------------------+----------------------+
                                              |
        +-------------------+-----------------+-----------------+-------------------+
        |                   |                                   |                   |
        v                   v                                   v                   v
+---------------+   +---------------+                   +---------------+   +---------------+
|  cortex mcp   |   | cortex studio |                   | cortex compile|   |  cortex scan  |
|  JSON-RPC 2.0 |   | Local Swiss   |                   | 8 IDE/Agent   |   | Policy + SARIF|
|  stdio server |   | Web Workbench |                   | Rule Formats  |   | + JUnit XML   |
+---------------+   +---------------+                   +---------------+   +---------------+
        |                   |                                   |                   |
        +-------------------+-----------------+-----------------+-------------------+
                                              |
                                              v
                            +-----------------------------------+
                            |  cortex graph / bundle / guard   |
                            |  Capability Graph + SHA-256      |
                            |  Bundles + Release Gate + Hooks  |
                            +-----------------------------------+
```

## Core Design Principles

1. **Zero Runtime Dependencies**: All 36 helper scripts, the unified CLI (`scripts/cortex.py`), the MCP server (`scripts/cortex_mcp.py`), the local web workbench (`scripts/cortex_studio.py`), the universal rule compiler (`scripts/cortex_compile.py`), the policy/SARIF scanner (`scripts/cortex_scan.py`), the capability graph (`scripts/cortex_graph.py`), the bundle engine (`scripts/cortex_bundle.py`), and the guard gate (`scripts/cortex_guard.py`) run strictly on the **Python 3 standard library**.
2. **Cryptographic Supply-Chain Integrity**:
   - Every `SKILL.md`, bundled script, and deterministic `.zip` archive is hashed in `checksums.json` (72 verified files across 36 skills).
   - Remote installations verify every byte against `checksums.json` before writing to disk and record installations in `.cortex-lock.json`.
   - npm releases publish with **SLSA v1 Provenance** via GitHub Actions OIDC.
3. **Workspace Path Confinement**:
   - Both `cortex mcp` (`cortex_run_verifier`) and `cortex studio` (`/api/run-tool`) resolve every target path against `--project-dir` and reject any path-traversal attempts escaping the workspace root.
4. **Deterministic Quality Gates**:
   - All 36 skills are audited to **100.0/100** by `scripts/eval_skills.py` and verified across **Linux, macOS, and Windows** in CI.
5. **Closed-Loop Release Gate**:
   - `cortex guard check` runs packaging, validation, audit, graph and scanner gates together; `cortex guard --write-workflow` / `guard install` emit SHA-pinned CI and a versionable pre-commit hook.
   - `cortex graph` models pack memberships and `related_skills` edges, exposing hubs, orphans and dangling references as JSON, Mermaid or DOT.
   - `cortex bundle` ships a deterministic ZIP with a per-file SHA-256 manifest and offline `--verify`.
6. **Formal JSON Schemas (`schemas/`)**:
   - `schemas/checksums.schema.json`
   - `schemas/packs.schema.json`
   - `schemas/cortex-lock.schema.json`
   - `schemas/policy.schema.json`

## Component Inventory

| Module | CLI Command | Responsibility |
| :--- | :--- | :--- |
| `scripts/cortex.py` | `cortex <cmd>` | Unified CLI entrypoint (`init`, `mcp`, `studio`, `compile`, `scan`, `graph`, `bundle`, `guard`, `detect`, `doctor`, `info`, `search`, `packs`, `new`, `install`, `verify`) |
| `scripts/cortex_mcp.py` | `cortex mcp` | MCP 2025-03-26 JSON-RPC 2.0 server (11 tools, 39 resources, 36 prompts) |
| `scripts/cortex_studio.py` | `cortex studio` | Local Light/Dark Swiss web UI + 12 REST endpoints across 7 panels |
| `scripts/cortex_graph.py` | `cortex graph` | Skill/pack capability graph with centrality, hubs, orphans, and dangling references (JSON, Mermaid, DOT) |
| `scripts/cortex_bundle.py` | `cortex bundle` | Deterministic offline skill bundles (ZIP + per-file SHA-256 manifest) with `--verify` |
| `scripts/cortex_guard.py` | `cortex guard` | Six-check release gate plus SHA-pinned CI workflow and pre-commit hook generation |
| `scripts/cortex_compile.py` | `cortex compile` | Compiles `SKILL.md` into Cursor `.mdc`, VS Code `.instructions.md`, Windsurf, Cline, `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` |
| `scripts/cortex_scan.py` | `cortex scan` | Unified multi-tool repository scanner with `.cortex-policy.json`, SARIF 2.1.0, and JUnit XML |
| `scripts/install_skills.py` | `cortex install` | Multi-agent skill installer & `.cortex-lock.json` manager across 12 agent targets |
| `scripts/bump_version.py` | `python scripts/bump_version.py <ver>` | Atomic release bumper for all 36 skills, 9 manifests, ZIPs, `checksums.json`, and `index.html` |
