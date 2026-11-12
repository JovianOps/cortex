---
name: unit-test-generator
description: Generate comprehensive unit tests from source code with coverage analysis.
version: 0.1.0
author: Athalla Jovian Maharsa
license: MIT
platforms: [linux, macos, windows]
---

# Unit Test Generator

Generate comprehensive unit tests from source code with coverage analysis.

## When to Use
- Adding tests to untested code
- Increasing test coverage
- Generating edge case tests
- Creating regression tests for bug fixes
- Setting up test infrastructure for new projects

## How to Run
```bash
hermes skills install JovianOps/cortex/premium-skills/unit-test-generator
hermes chat -q "Generate unit tests for this Python module"
```

## Core Capabilities
1. **Test generation** — Generate tests from source code analysis
4. **Edge case detection** — Identify boundary conditions and error paths
4. **Coverage analysis** — Identify untested code paths
5. **Framework support** — pytest, Jest, JUnit, Go test, etc.
6. **Mock generation** — Generate mocks for dependencies

## Anti-Hallucination Measures
- Analyze actual code structure, not guesses
- No invented function signatures
- Tests must pass before delivery
- Deterministic test generation from AST