---
name: code-review-assistant
description: Run evidence-backed code reviews with severity rubrics.
version: 0.4.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, validation, anti-hallucination, quality]
    related_skills: [python-coding-assistant, anti-hallucination, security-auditor, refactoring-assistant]
---

# Code Review Assistant

Perform rigorous, evidence-backed code and PR reviews that prioritize real correctness, security, and maintainability defects over noisy style nitpicks.

## When to Use

- Reviewing pull requests, git diffs, or individual modules before merge
- Auditing changed code for regressions, edge-case bugs, concurrency races, or security flaws
- Enforcing deterministic static-analysis gates alongside human-readable review feedback

### When Not to Use

- Full-repository compliance/penetration audits (use `security-auditor`)
- Large architectural rewrites (use `refactoring-assistant`)

## How to Run

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/code-review-assistant --yes
hermes chat -q "Review the staged git diff for bugs, security risks, and missing edge cases"
```

## Mandatory Review Protocol

### Step 1 — Inspect the Actual Scope & Context

1. Read the full diff (`git diff` / `git diff main...HEAD`) **and** the surrounding functions/callers of modified lines — never review diff hunks in isolation without checking callers and invariants.
2. Identify the intent of the change before flagging issues.

### Step 2 — Run Deterministic Checkers First

Run whatever linters, typecheckers, or test suites exist in the repository before writing prose feedback:

```bash
# Python projects
ruff check . && mypy . && pytest -q

# JS/TS projects
npx tsc --noEmit && npm test

# Security quick-scan when available
bandit -r src/ -ll
```

Record exact tool commands and pass/fail output. If a tool is not installed, note it as `not available` — never pretend it ran.

### Step 3 — Targeted Defect Pass (High-Signal Checklist)

Inspect modified code specifically for bugs LLMs and humans frequently miss:

1. **Boundary & null/empty handling**: empty collections, `0`, negative numbers, `None`/`null`/`undefined`, off-by-one slices, timezone-naive datetimes.
2. **Error handling & resource leaks**: swallowed exceptions (`except: pass`), unclosed files/sockets/transactions, partial writes on failure.
3. **State & concurrency**: shared mutable defaults (`def f(x=[])`), TOCTOU file races, missing locks/transactions, non-idempotent retries.
4. **Security at trust boundaries**: unvalidated input reaching SQL, shell (`shell=True`), file paths (path traversal), HTML (XSS), or SSRF URLs; leaked secrets in logs.
5. **API & backward compatibility**: breaking signature changes, altered JSON fields, silent behavior changes for existing callers.
6. **Test coverage of changed branches**: do tests actually exercise the new failure paths, or only the happy path?

### Step 4 — Strict Severity & Evidence Rubric

Every single finding MUST include a severity level, exact `file:line`, concrete failure scenario, and minimal fix. **Drop any speculative or ungrounded nitpick.**

| Severity | Definition | Merge Action |
| :--- | :--- | :--- |
| **`P0` Blocker** | Data loss, security vulnerability, crash in common path, broken build/tests | Must fix before merge |
| **`P1` High** | Real edge-case bug, race condition, resource leak, breaking contract | Should fix before merge |
| **`P2` Medium** | Maintainability trap, missing error context, weak test coverage | Fix now or track explicitly |
| **`P3` Nit** | Minor clarity/naming improvement (limit to at most 3 nits per review) | Optional |

## Strict Output Contract

```markdown
## Review Verdict: APPROVE | REQUEST_CHANGES | COMMENT

### Automated Checks
- `<command>`: PASS | FAIL | NOT_AVAILABLE

### Findings

#### [P0/P1/P2/P3] Short Title — `path/to/file.py:42`
- **Why it fails:** Concrete input or sequence that triggers the defect.
- **Evidence:** Exact offending snippet or tool output.
- **Suggested fix:** Minimal, copy-pasteable patch.

### Missing Test Cases
- Bullet list of specific untested branches or regression cases to add.
```

## Anti-Hallucination Rules

- **Line-number fidelity**: Only cite `file:line` numbers read directly from files during this session.
- **Zero phantom defects**: Verify that a variable isn't already checked by an upstream caller or middleware before flagging a missing null check.
- **No linter-duplication spam**: Don't manually list 20 formatting issues if a formatter/linter handles them — flag the formatter command once.
