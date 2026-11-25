---
name: architecture-decision-records
description: Author and validate MADR Architecture Decision Records.
version: 3.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [adr, architecture, madr, documentation, governance]
    related_skills: [documentation-generator, code-migration, refactoring-assistant]
---

# Architecture Decision Records (MADR) Architect

Author crisp, immutable, MADR-compliant Architecture Decision Records capturing engineering context, considered alternatives, explicit trade-offs, and reversible vs. irreversible consequences.

## When to Use

- Recording a significant architecture, database, protocol, security, or framework decision in `docs/adr/`
- Superseding a legacy architectural choice cleanly without rewriting historical decisions
- Auditing an ADR directory for numbering collisions, missing trade-off sections, or invalid status values

### When Not to Use

- General API reference docs or README tutorials (use `documentation-generator`) or incident postmortems (use `incident-response`)

## How to Run

> **Bundled Helper Script (`v3.0.0`):** Run `python premium-skills/architecture-decision-records/scripts/check_adrs.py docs/adr/` to validate `NNNN-kebab-title.md` naming, monotonic sequence numbers, required sections (`Status`, `Context`, `Decision`, `Consequences`), and valid status values.

```bash
npx @jovianops/cortex install --agent vscode --skill architecture-decision-records --scope project
python premium-skills/architecture-decision-records/scripts/check_adrs.py docs/adr/ --json
```

## Mandatory ADR Authoring Protocol

### Step 1 — Confirm Scope, Stakeholders & Numbering

1. Check existing `docs/adr/NNNN-*.md` files to assign the next strictly increasing 4-digit sequence number.
2. Never edit an `Accepted` ADR's decision retroactively — instead create a new ADR that marks the prior record `Superseded by NNNN`.

### Step 2 — Non-Negotiable MADR Quality Rules

Every ADR MUST include:
1. **Clear Filename & Title**: `NNNN-concise-kebab-title.md` with `# NNNN. <Decision Title>`.
2. **Valid `## Status`**: One of `Proposed`, `Accepted`, `Rejected`, `Deprecated`, or `Superseded by NNNN` (with ISO-8601 date).
3. **Objective `## Context`**: Concrete problem statement, scale/latency/security constraints, and decision drivers — zero hand-waving.
4. **Explicit `## Decision` & Considered Alternatives**: Compare at least 2 concrete options (pros/cons/cost) before stating the chosen option.
5. **Honest `## Consequences`**: List positive outcomes, negative trade-offs/operational costs, and clear revisit triggers.

### Step 3 — Mandatory Verification Gate

Validate all ADRs with Cortex's bundled MADR checker and documentation link verifier:

```bash
python premium-skills/architecture-decision-records/scripts/check_adrs.py docs/adr/
python skills/documentation-generator/scripts/check_docs.py docs/adr/
```

Stop and fix any missing sections, duplicate numbers, or broken cross-links.

## Output Contract

Deliver:
1. **MADR Markdown File** — Ready-to-commit `docs/adr/NNNN-<slug>.md` with full alternatives and trade-offs.
2. **Supersession & Index Updates** — Any status link updates to superseded ADRs or `docs/adr/README.md`.
3. **Verification Results** — Exact output from `check_adrs.py`.
