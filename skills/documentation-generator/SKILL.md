---
name: documentation-generator
description: Generate code-verified docs, API specs, and diagrams.
version: 0.3.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [documentation, generation, markdown, api-docs, validation]
    related_skills: [api-designer, python-coding-assistant, anti-hallucination]
---

# Documentation Generator

Generate accurate, code-verified READMEs, API references, architecture diagrams, and changelogs derived strictly from real source files rather than guesswork.

## When to Use

- Writing or updating a project `README.md`, module API reference, or architecture guide
- Documenting CLI tools, environment variables, HTTP endpoints, or configuration schemas
- Creating Mermaid system diagrams grounded in actual module imports and data flows
- Generating changelogs from `git log` history

### When Not to Use

- Designing a brand-new API contract before code exists (use `api-designer`)

## How to Run

> **Bundled Helper Script (`v0.3.0`):** Run `python skills/documentation-generator/scripts/check_docs.py README.md` to verify every relative Markdown link and `#heading` anchor exists.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/documentation-generator --yes
hermes chat -q "Generate a code-verified README and API reference for this repository"
```

## Mandatory Code-Truth Protocol

### Step 1 — Extract Real Interfaces From Source First

Before drafting a single sentence of documentation, inspect the actual codebase to inventory:

1. **Entry points & manifests**: `package.json`, `pyproject.toml`, `Cargo.toml`, `Makefile`, `Dockerfile`, CI workflows (`.github/workflows/`).
2. **Public API surface**: exported functions/classes, HTTP routes & status codes, CLI flags (`argparse`/`click`/`commander`), and environment variables (`os.getenv` / `process.env`).
3. **Actual directory layout**: list real files on disk — **never document folders or scripts that do not exist**.
4. **Real examples & tests**: read existing tests to capture valid, working usage patterns.

### Step 2 — Author Structured, High-Signal Docs

Apply these structural rules based on document type:

- **README**: Value proposition (1–2 sentences) → Prerequisites (exact versions from manifest) → Quick Start (copy-pasteable, verified commands) → Configuration/Env table (name, required, default, description) → Architecture/Structure → Development & Testing → License.
- **API Reference**: Endpoint/signature → Parameter table (name, type, required, constraints, default) → Concrete request & response examples (both `2xx` success and error payloads) → Auth & rate-limit notes.
- **Architecture Diagrams (Mermaid)**: Every node and edge must correspond to a real module, service, or data store in the repo; keep diagrams under 15 nodes for readability.
- **Changelogs**: Follow Keep a Changelog (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`) backed by actual `git log` commits.

### Step 3 — Documentation Drift & Link Verification Gate

Before delivering generated docs, run deterministic checks:

```bash
# Verify every relative Markdown link resolves to an existing file
python3 -c "import re, pathlib; p=pathlib.Path('README.md'); missing=[m for m in re.findall(r'\]\(([^)#]+)\)', p.read_text()) if not m.startswith(('http://','https://','mailto:')) and not pathlib.Path(m).exists()]; assert not missing, f'Broken links: {missing}'; print('Links OK')"
```

1. **Symbol & path check**: Verify every file path, script command, CLI flag, and env var mentioned in the doc exists in the repository.
2. **Relative link check**: Verify all Markdown relative links (`[text](path)`) resolve to existing files.
3. **Markdown & syntax check**: Ensure all fenced code blocks specify a language tag and valid syntax (JSON/YAML/Mermaid/shell).
4. **Runnable snippet check**: Execute quickstart/CLI help commands when safe in the local workspace to confirm output matches docs.

## Output Contract

When writing or updating documentation, always report:

1. **Files Created / Updated** — Exact paths.
2. **Source Inventory Used** — Files parsed to derive commands, flags, env vars, and endpoints.
3. **Drift / Gaps Discovered** — Any undocumented env vars, broken links, or discrepancies found between existing docs and actual code.
4. **Verification Results** — Link check and command/lint verification status.

## Failure-Mode Guards

- **No phantom commands**: Never write `npm run dev` or `pytest` without verifying the script/dependency exists in `package.json` or `pyproject.toml`.
- **No fabricated defaults**: If an environment variable has no default in code, mark it `Required (no default)` instead of inventing one.
- **No stale copy-paste**: Remove references to deleted modules, old branches, or non-existent `docs/` folders.
