---
name: anti-hallucination
description: Verify AI claims and code with deterministic audit gates.
version: 3.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [anti-hallucination, validation, verification, fact-checking]
    related_skills: [academic-assistant, code-review-assistant, python-coding-assistant]
---

# Anti-Hallucination Verification Framework

Systematically audit AI-generated code, technical answers, data summaries, and citations to eliminate fabricated APIs, phantom files, arithmetic errors, and unsupported claims.

## When to Use

- Auditing AI-generated code before committing or running in production
- Fact-checking technical documentation, benchmarks, or numerical reports
- Verifying that referenced libraries, CLI flags, file paths, and symbols actually exist
- Enforcing strict evidence provenance on high-stakes outputs

### When Not to Use

- Purely subjective creative writing or fiction where factual grounding is not expected

## How to Run

> **Bundled Helper Script (`v1.0.0`):** Run `python skills/anti-hallucination/scripts/verify_claims.py report.md --repo .` to verify every backticked relative file path actually exists in the repository.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/anti-hallucination --yes
hermes chat -q "Audit this code and explanation for hallucinated APIs, math errors, or unverified claims"
```

## Mandatory Verification Pipeline

Execute these 5 layers in sequence. Skip a layer only if inapplicable, and explicitly mark skipped layers as `NOT_RUN (reason)`.

### Layer 1 — Claim & Artifact Extraction

Extract every concrete, falsifiable claim from the target text or code into an inventory:

- **Code symbols**: imports, package names, function/method names, kwargs, CLI flags, environment variables
- **File & repo references**: file paths, line numbers, config keys, URLs
- **Quantitative claims**: totals, percentages, Big-O claims, benchmark numbers, dates, versions
- **Factual assertions**: CVE IDs, RFC numbers, standard behavior, compatibility guarantees

### Layer 2 — Deterministic Code & Syntax Checks

When code is present, run real parsers/checkers instead of visual inspection alone:

```bash
# Python syntax + AST + import existence check
python3 -m py_compile <file.py>
python3 -c "import ast, pathlib; ast.parse(pathlib.Path('<file.py>').read_text())"

# Verify imported modules and attributes actually exist in the environment
python3 -c "import <pkg>; print(hasattr(<pkg>, '<symbol>'))"

# Type / static checks when installed
ruff check <file.py>
mypy <file.py>
```

For JavaScript/TypeScript, run `node --check <file.js>` or `tsc --noEmit`. For JSON/YAML, parse with `json.loads` / `yaml.safe_load`.

### Layer 3 — Arithmetic & Data Reconciliation

- **Zero mental math**: Recompute every sum, average, delta, percentage, and unit conversion via Python.
- Compare claimed values against recomputed values and flag any mismatch (even rounding discrepancies).

### Layer 4 — Grounding & Provenance Classification

Assign **exactly one** verification tag to every extracted claim:

| Tag | Meaning | Allowed in Final Output? |
| :--- | :--- | :--- |
| `[VERIFIED-TOOL]` | Confirmed by executing a command, parser, test, or script | Yes (cite command & output) |
| `[VERIFIED-FILE]` | Confirmed directly in a local file read during this session | Yes (cite `path:line`) |
| `[INFERRED]` | Logical deduction strictly entailed by verified facts | Yes (label explicitly as inference) |
| `[UNVERIFIED]` | No tool output or source file confirms the claim | Must be flagged or removed |
| `[CONTRADICTED]` | Disproved by tool output, source code, or math recomputation | Must be corrected with evidence |

### Layer 5 — Abstention & Correction Rule

- If an API, CLI flag, CVE, version number, or statistic cannot be confirmed via tools or inspected files, **do not guess or smooth it over** — mark it `[UNVERIFIED]` and state exactly what check is needed to verify it.
- Never invent tool output, line numbers, or benchmark measurements.

## Strict Output Format

```markdown
## Audit Verdict: PASS | PASS_WITH_WARNINGS | FAIL

### Summary
- Claims checked: <N>
- Verified: <N> | Inferred: <N> | Unverified: <N> | Contradicted: <N>

### Verification Matrix
| # | Claim / Artifact | Tag | Evidence / Command Output | Required Fix |
| - | ---------------- | --- | ------------------------- | ------------ |

### Corrected Output
<Only if CONTRADICTED or UNVERIFIED items exist — provide the clean, strictly grounded replacement>
```

## High-Value Failure Modes to Catch

- **Phantom kwargs / methods**: Methods that sound plausible (e.g., `requests.get(..., retries=3)` or `Path.read_lines()`) but do not exist in the actual library.
- **Version drift**: Deprecated or removed flags/APIs (e.g., `asyncio.get_event_loop()` warnings, `pydantic` v1 vs v2 `.dict()` vs `.model_dump()`).
- **Silent math drift**: Percentages that do not sum to 100%, miscalculated speedups (`2x faster` vs `50% slower`), off-by-one counts.
- **Plausible-looking CVEs / RFCs**: Any CVE/RFC number not backed by a real database lookup or local advisory must be flagged `[UNVERIFIED]`.
