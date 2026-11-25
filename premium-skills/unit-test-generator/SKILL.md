---
name: unit-test-generator
description: Generate branch-covering unit tests from source code.
version: 3.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, unit-tests, coverage, edge-cases, tdd]
    related_skills: [testing-automation, python-coding-assistant, refactoring-assistant, code-review-assistant]
---

# Unit Test Generator

Generate high-signal, branch-covering unit tests from real source code across Python (`pytest`), JS/TS (`vitest`/`jest`), Go (`testing`), and Java (`JUnit 5`) with mandatory execution and anti-tautology checks.

## When to Use

- Adding unit tests to untested or under-tested functions, classes, and modules
- Closing branch-coverage gaps and catching boundary/error-path bugs
- Writing minimal regression tests that reproduce a reported bug before fixing it
- Building deterministic mocks/fakes at I/O boundaries without mocking away the logic under test

### When Not to Use

- Setting up full repository CI pipelines and multi-stage coverage infrastructure (use `testing-automation` / `devops-pipeline`)

## How to Run

> **Bundled Helper Script (`v1.0.0`):** Run `python premium-skills/unit-test-generator/scripts/test_skeleton.py module.py` to generate an AST-derived branch and edge-case test checklist for every public function.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/unit-test-generator --yes
hermes chat -q "Generate branch-covering unit tests for src/pricing.py and verify they pass"
```

## Mandatory Test Generation Protocol

### Step 1 — Read Source & Build a Branch Inventory First

**Never write tests from guessed function signatures.** Read the exact target source file and existing test conventions first, then list:

1. Exact exported function/method signatures, parameter types, defaults, and return types.
2. Every control-flow branch (`if`/`elif`/`else`, `match`/`switch`, loop 0/1/N iterations, short-circuit boolean ops).
3. Every exception/error return path and guard clause.
4. External side-effect boundaries (filesystem, clock, RNG, HTTP/DB clients) that require isolation.

### Step 2 — Cover the 5 Mandatory Test Categories

For each public unit, generate focused tests covering:

1. **Happy Path**: Representative valid inputs verifying exact return values and state changes.
2. **Boundary Conditions**: Empty (`""`, `[]`, `{}`), single element, zero, negative, `min`/`max` thresholds, exact off-by-one cutoffs.
3. **Invalid & Malformed Inputs**: `None`/`null`, wrong types, missing required keys, malformed strings, Unicode/whitespace edge cases — asserting exact error types and message patterns.
4. **Failure & Edge Branches**: Downstream dependency failure (timeout, I/O error, empty result) verifying graceful handling or explicit propagation.
5. **Regression / Invariant Cases**: Idempotency, commutativity, or exact bug-reproduction cases when fixing a defect.

### Step 3 — Anti-Tautology & Mocking Hygiene

- **Mock ONLY external boundaries** (network, DB, clock, filesystem), never the core module's own internal pure logic.
- **Ban mock-echo tests**: Every test must break if the production code's logic is mutated (e.g., flipping `<` to `<=` or removing a guard clause).
- **Zero shared mutable state**: Tests must pass in any execution order and in parallel (`pytest -n auto` / `jest --runInBand` or default parallel).
- **Use fixed timestamps and seeds**: Inject clocks (`datetime(2026, 1, 1, tzinfo=timezone.utc)`) instead of `datetime.now()`.

### Step 4 — Mandatory Execution Verification

Run the generated test suite locally before delivering:

```bash
# Python
pytest -q <test_file>
pytest --cov=<module> --cov-branch --cov-report=term-missing <test_file>

# JS/TS
npx vitest run <test_file>   # or npx jest <test_file>

# Go
go test -v -cover ./...
```

- If a test fails because the **source code has a real bug**, report the bug with exact input/expected/actual instead of altering the test to assert buggy behavior.

## Output Contract

Deliver:

1. **Test File(s)** — Clean, idiomatic, runnable unit tests matching the repository's existing test framework and naming conventions.
2. **Branch Coverage Checklist** — Table mapping source branches/error paths to the specific test functions exercising them.
3. **Execution Proof** — Exact test command executed, pass/fail counts, and branch coverage percentage (when coverage tooling is available).
4. **Bugs Surfaced** — Any real source defects uncovered during test execution.
