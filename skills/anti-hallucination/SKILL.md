---
name: anti-hallucination
description: Validation framework and anti-hallucination measures for AI outputs.
version: 0.1.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [anti-hallucination, validation, verification, fact-checking]
    related_skills: [academic-assistant, code-review-assistant, python-coding-assistant]
---
# Anti-Hallucination Framework Skill

Validation framework and anti-hallucination measures for AI outputs.

## When to Use
- Validate AI outputs before use
- Fact-check generated content
- Prevent hallucinated code/data
- Verify claims against sources

## How to Run
```bash
hermes skills install owner/repo/skills/anti-hallucination
hermes chat -q "Validate this code snippet for hallucinations"
```

## Validation Layers
| Layer | Method | Purpose |
|-------|--------|---------|
| Syntax | AST parsing | Syntax validity |
| Semantics | Type checking | Type correctness |
| Logic | Static analysis | Logical consistency |
| Facts | Source verification | Factual accuracy |
| Execution | Sandbox execution | Runtime verification |

## Validation Layers
1. **Syntax** - AST parsing, syntax validity
2. **Types** - Type checking (mypy/pyright)
3. **Logic** - Static analysis, control flow
4. **Facts** - Source verification against known data
5. **Execution** - Sandbox execution for verification

## Anti-Hallucination Measures
- Deterministic calculations only (no AI math)
- Input validation before processing
- Template-based output (no free-form)
- Explicit error reporting
- Source-cited outputs only
- Fail fast with clear messages

## Usage
```bash
hermes chat -q "Validate this Python code for hallucinations"
```