# Cortex Skill & Helper Script Authoring Standard

Every skill in Cortex is engineered to achieve a **100/100** structural audit score and bundle a real, executable, zero-dependency Python 3 verification tool.

## Required Directory Layout

```text
premium-skills/<kebab-slug>/
├── SKILL.md
└── scripts/
    └── <tool_name>.py
```

## Frontmatter Contract

```yaml
---
name: my-skill-slug
description: Concise <=60-char action sentence ending in a period.
version: 3.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [domain, security, verification]
    related_skills: [security-auditor, code-review-assistant]
---
```

## Required Sections in `SKILL.md`

1. `## When to Use` + `### When Not to Use` (clear trigger boundary)
2. `## How to Run` (including a `> **Bundled Helper Script (\`v3.0.0\`):**` callout)
3. Numbered `## Mandatory ... Protocol` steps with explicit stop gates
4. `## Output Contract` defining concrete deliverables

## Bundled Helper Script Contract

Every script under `scripts/`:
- Must use **Python 3 standard library only** (no `pip` packages)
- Must support `--json` for machine-readable integration with `cortex mcp`, `cortex studio`, and `cortex scan`
- Must use deterministic exit codes: `0` (clean), `1` (findings detected), `2` (invalid usage / missing target)
- Must be covered by automated unit tests in `tests/`

## Scaffolding & Verification

```bash
# Scaffold a 100/100 audit-ready skill with a starter helper script
python3 scripts/cortex.py new my-skill --tier extended --with-script

# Rebuild all ZIPs, checksums.json, and index.html
python3 scripts/package_skills.py

# Run complete audit, evals, manifest validation, and tests
npm test
```
