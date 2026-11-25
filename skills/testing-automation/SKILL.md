---
name: testing-automation
description: Build branch-tested pytest suites with CI coverage gates.
version: 3.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [testing, automation, pytest, ci-cd, coverage]
    related_skills: [python-coding-assistant, unit-test-generator, devops-pipeline]
---

# Testing Automation

Design, implement, and wire deterministic `pytest` test suites with branch coverage gates, isolated fixtures, property-based edge-case discovery, and CI enforcement.

## When to Use

- Bootstrapping a `pytest` suite, `conftest.py` fixtures, and coverage configuration
- Hardening flaky or shallow test suites into deterministic, branch-covering suites
- Enforcing coverage thresholds and test matrices in GitHub Actions / GitLab CI
- Adding property-based (`hypothesis`) or contract tests for critical parsers and calculators

### When Not to Use

- Generating quick unit tests for a single isolated module in JS/Go/Java (use `unit-test-generator`)

## How to Run

> **Bundled Helper Script (`v1.0.0`):** Run `python skills/testing-automation/scripts/check_test_coverage_map.py tests/` to detect assertion-free test functions across a Python test suite.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/testing-automation --yes
hermes chat -q "Set up a deterministic pytest suite with branch coverage and CI workflow for this repo"
```

## Mandatory Test Engineering Protocol

### Step 1 — Audit Source Branches & Existing Test Setup

1. Inspect `pyproject.toml`, `pytest.ini`, `tests/`, and `.github/workflows/`.
2. Read the target source modules and enumerate **every conditional branch, error raise, boundary value, and external I/O touchpoint** before writing a single test.

### Step 2 — Enforce High-Signal Test Design Rules

1. **Arrange–Act–Assert (AAA)** clarity with one logical behavior per test and descriptive test names (`test_<unit>_<condition>_<expected_outcome>`).
2. **Parametrized Boundary Matrix**: Use `@pytest.mark.parametrize` to cover empty inputs, single-item inputs, exact boundaries (`0`, `-1`, `max`), malformed inputs, Unicode, and expected exceptions (`pytest.raises(ValueError, match=...)`).
3. **Strict Isolation (Zero Flakiness)**:
   - Use `tmp_path` for filesystem I/O — never write to hardcoded `/tmp` paths or mutate repo files.
   - Use `monkeypatch` for environment variables, globals, and clocks — never depend on real wall-clock time, live network calls, or random unseeded state.
   - Clean up or scope fixtures tightly (`scope="function"` by default).
4. **Anti-Tautology Rule (Mutation Thinking)**:
   - Assert observable outputs, state transitions, and exact exception types/messages — **never write tests that only assert a mock returned what the test told it to return**.
   - Never weaken assertions (`assert result is not None`) when an exact value or structural invariant can be verified.
5. **Property-Based Testing (When Applicable)**: For parsers, serializers, or math functions, add round-trip / invariant tests (`decode(encode(x)) == x`, monotonicity, idempotency).

### Step 3 — Coverage & CI Configuration

Configure branch coverage in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers --strict-config"

[tool.coverage.run]
branch = true
source = ["src"]

[tool.coverage.report]
show_missing = true
fail_under = 85
```

### Step 4 — Mandatory Execution Proof

Run the full test suite and inspect real pass/fail and uncovered lines:

```bash
pytest -q
pytest --cov=src --cov-branch --cov-report=term-missing
```

Fix every failing test (distinguishing real source bugs from test setup mistakes — never silence a real bug just to make tests green).

## Output Contract

Deliver:

1. **Test Files & Fixtures Added/Updated** — Exact paths.
2. **Branch & Edge-Case Matrix** — Summary of happy paths, boundaries, and failure paths verified.
3. **Execution & Coverage Output** — Exact `pytest` command run, passed/failed/skipped counts, and branch coverage percentage (or uncovered line numbers).
4. **Defects Surfaced** — Any real source bugs discovered while testing.
