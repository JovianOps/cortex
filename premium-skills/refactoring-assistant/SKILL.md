---
name: refactoring-assistant
description: Refactor complex code safely with parity verification.
version: 2.0.1
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [refactoring, clean-code, design-patterns, complexity, maintainability]
    related_skills: [code-review-assistant, unit-test-generator, code-migration, python-coding-assistant]
---

# Refactoring Assistant

Simplify complex, duplicated, or brittle code through small, measurable, behavior-preserving refactoring steps verified by green tests before and after every change.

## When to Use

- Breaking down deeply nested or overly long functions and God classes
- Consolidating copy-pasted business logic without introducing leaky abstractions
- Replacing brittle conditional chains with clean lookup tables, guard clauses, or Strategy/State patterns
- Preparing messy modules for upcoming feature work without changing external behavior

### When Not to Use

- Changing language/framework versions (use `code-migration`)
- Performance tuning hot paths (use `performance-profiler`)

## How to Run

> **Bundled Helper Script (`v1.0.0`):** Run `python premium-skills/refactoring-assistant/scripts/complexity_scan.py src/` to locate Python cyclomatic complexity and function-length hotspots before refactoring.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/refactoring-assistant --yes
hermes chat -q "Refactor src/order_processor.py to reduce nesting and complexity while preserving all behavior"
```

## Mandatory Safe-Refactoring Protocol

### Step 1 — Measure Smells & Lock Behavior First

1. Read the full target module AND all callers referencing its public functions/classes.
2. Quantify the concrete structural problems before editing:
   - Max nesting depth, function line counts, branching/cyclomatic complexity, duplicated blocks, mixed I/O + pure logic.
3. **Green-Test Precondition**: Run the existing test suite first. If no tests cover the target module, write characterization tests locking current inputs, outputs, and edge-case exceptions **before** changing production code.

### Step 2 — Apply Minimal, High-Leverage Refactors (Anti-Over-Engineering)

Apply transformations in order of lowest risk to highest structural impact:

1. **Flatten Nesting with Guard Clauses**: Invert preconditions and return/raise early to cut indentation depth.
2. **Separate Pure Logic from Side Effects**: Extract pure calculation/validation helpers from file/DB/HTTP orchestration so logic becomes clear and testable.
3. **Decompose by Cohesion (Not Arbitrary Line Count)**: Extract helpers with clear, domain-meaningful names and narrow parameter lists (group 4+ co-traveling args into a typed `dataclass` / interface).
4. **Replace Brittle Conditionals Appropriately**:
   - Use a simple dispatch dictionary / lookup table for static mappings.
   - Apply Strategy/Factory/State patterns **only** when there are `>= 3` concrete variants or an active extension seam — **never introduce abstract base classes or factories for 1–2 simple branches**.
5. **Preserve Public Contracts**: Keep exported function names, parameter defaults, return types, and exception classes backward-compatible unless explicitly asked to change them.

### Step 3 — Verify Parity & Structural Improvement

After refactoring, execute static checks and full regression tests:

```bash
# Python verification
python3 -m py_compile <file.py> && ruff check . && mypy . && pytest -q

# TypeScript / JS verification
npx tsc --noEmit && npm test
```

Report concrete before-vs-after structural metrics (max nesting depth, longest function length, branching count, duplicated blocks removed) alongside the real test pass output.

## Output Contract

Deliver:

1. **Structural Diagnosis (Before)** — Measured complexity/smell inventory with exact `file:line` pointers.
2. **Refactoring Steps Applied** — Concise summary of each transformation and why it was chosen (plus any patterns intentionally avoided to prevent over-engineering).
3. **Before vs. After Metrics** — Table comparing function lengths, max nesting depth, and test/lint results.
4. **Verification Proof** — Exact test and static-check commands run and their real pass output.
