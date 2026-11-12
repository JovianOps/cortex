---
name: refactoring-assistant
description: Refactor code with behavior preservation, complexity reduction, and pattern application.
version: 0.1.0
author: Athalla Jovian Maharsa
license: MIT
platforms: [linux, macos, windows]
---

# Refactoring Assistant

Refactor code while preserving behavior, reducing complexity, and applying design patterns.

## When to Use
- Code is hard to read or maintain
- Functions are too long or complex
- Duplicated code needs consolidation
- Applying design patterns (Strategy, Factory, Observer, etc.)
- Pre-release code cleanup

## How to Run
```bash
hermes skills install JovianOps/cortex/premium-skills/refactoring-assistant
hermes chat -q "Refactor this function to reduce complexity"
```

## Core Capabilities
1. **Code smell detection** — Long functions, duplicated code, complex conditionals
4. **Pattern application** — Suggest and apply appropriate design patterns
4. **Complexity reduction** — Simplify nested logic, extract methods
5. **Behavior preservation** — Ensure refactored code produces identical outputs
6. **Incremental refactoring** — Safe, step-by-step refactoring with validation

## Anti-Hallucination Measures
- AST-based analysis, not pattern matching guesses
- Test-based validation (old and new code must produce same results)
- No speculative pattern application
- Explicit before/after comparison