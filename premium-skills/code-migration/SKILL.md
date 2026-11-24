---
name: code-migration
description: Migrate languages and frameworks with parity tests.
version: 0.4.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [migration, modernization, upgrade, parity-testing]
    related_skills: [refactoring-assistant, unit-test-generator, code-review-assistant]
---

# Code Migration

Migrate code between languages, frameworks, or major runtime/library versions with strict behavioral equivalence verified by golden-master characterization tests before and after translation.

## When to Use

- Upgrading major runtimes or frameworks (Python 2 → 3, Node 16 → 22, Pydantic v1 → v2, React Router/Next.js major upgrades, Express → Fastify)
- Converting JavaScript codebases to strict TypeScript
- Porting modules across languages (Python → Go/Rust, Java → Kotlin)
- Auditing breaking API changes and subtle semantic traps before upgrading dependencies

### When Not to Use

- Internal cleanup within the same language and framework version (use `refactoring-assistant`)

## How to Run

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/code-migration --yes
hermes chat -q "Migrate this Python 2 module to Python 3.12 with golden-master parity tests"
```

## Mandatory Migration Protocol

### Step 1 — Inventory & Freeze Behavior First (Characterization Gate)

**Never rewrite code before capturing current observable behavior:**

1. Read the full source module, dependencies, config files, and existing tests.
2. Inventory all external contracts: public signatures, return shapes, exception types, exit codes, file formats, and side effects.
3. Write or run **golden-master / characterization tests** capturing exact input → output pairs (including edge cases and error inputs) against the legacy implementation first.

### Step 2 — Separate Mechanical vs. Semantic Changes

Classify every change before editing:

- **Mechanical syntax changes** (safe for automated transforms/codemods): import paths, type annotations, print syntax, ESM/CJS exports.
- **Semantic traps** (MUST be audited line-by-line — these cause silent production bugs):

| Migration Pair | High-Risk Semantic Traps to Audit Explicitly |
| :--- | :--- |
| **Python 2 → 3** | Integer `/` vs `//` division, `bytes` vs `str` encoding, `dict.keys()`/`map`/`filter` returning iterators instead of lists, `round()` banker's rounding, exception scoping |
| **JavaScript → TypeScript** | Implicit `any`, `null` vs `undefined` narrowing, `catch (err: unknown)`, JSON parsing returning `unknown`, `this` binding, enum vs `as const` unions |
| **Pydantic v1 → v2** | `.dict()` → `.model_dump()`, `.parse_obj()` → `.model_validate()`, `@validator` → `@field_validator`, `orm_mode` → `from_attributes`, strict coercion changes |
| **Express → Fastify** | Async handler return vs `reply.send()`, middleware execution lifecycle hooks, JSON schema validation & serialization stripping unknown fields |
| **Language Ports (e.g., Py → Rust/Go)** | Integer overflow/wrapping, float NaN/precision, UTF-8 byte vs char indexing, error propagation vs exceptions, timezone/regex dialect differences |

### Step 3 — Incremental Migration & Scope Discipline

- **No speculative feature additions** during migration — keep migrated code functionally identical first; defer redesigns to a separate follow-up PR.
- Migrate leaf modules first (no internal dependents), then work up the dependency graph.
- Preserve rollback safety (keep original untouched until target passes parity, or isolate behind feature flag / adapter).

### Step 4 — Side-by-Side Parity Verification

Verify migrated code with real execution:

```bash
# Python target verification
python3 -m py_compile <migrated_file.py> && ruff check . && mypy . && pytest -q

# TypeScript / Go / Rust targets
npx tsc --noEmit && npm test    # TypeScript
go vet ./... && go test ./...   # Go
cargo check && cargo test       # Rust
```

1. Run compiler / typechecker / linter for the target runtime.
2. Run the golden-master parity tests against the migrated code and assert identical outputs, status codes, and error classes.
3. Document any intentional behavioral delta (e.g., fixing a legacy security flaw or deprecated format) explicitly in a **Behavioral Deltas** table.

## Output Contract

Deliver:

1. **Migration Inventory & Risk Map** — Dependencies mapped old → new and semantic traps audited.
2. **Migrated Code** — Clean, idiomatic target-language code without unrequested feature creep.
3. **Parity Verification Results** — Commands run, golden-master test pass/fail counts, and any intentional behavioral deltas documented explicitly.
4. **Rollback & Cutover Checklist** — Steps to deploy safely and revert if regressions appear.
