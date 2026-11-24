---
name: python-coding-assistant
description: Write typed, linted, and tested Python code reliably.
version: 2.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [coding, python, validation, anti-hallucination]
    related_skills: [testing-automation, code-review-assistant, anti-hallucination, refactoring-assistant]
---

# Python Coding Assistant

Write production-grade, strictly typed, cross-platform Python code with mandatory syntax, static-analysis, and execution verification before delivery.

## When to Use

- Writing new Python scripts, CLIs, libraries, or data-processing pipelines
- Debugging Python tracebacks, type errors, subtle edge cases, or performance issues
- Adding type hints, input validation, and structured error handling to existing Python modules

### When Not to Use

- Porting legacy Python 2 codebases at scale (use `code-migration`)
- Deep CPU/memory flamegraph profiling (use `performance-profiler`)

## How to Run

> **Bundled Helper Script (`v1.0.0`):** Run `python skills/python-coding-assistant/scripts/check_python_ast.py src/` to audit Python ASTs for mutable default args, bare `except:`, and missing return annotations.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/python-coding-assistant --yes
hermes chat -q "Write a typed Python CLI to validate and summarize sales.csv with unit tests"
```

## Mandatory Engineering Workflow

### Step 1 — Inspect Environment & Project Conventions First

Before writing code, check:

1. Target Python version (`python3 --version`, `pyproject.toml`, `requires-python`).
2. Installed dependencies (`pyproject.toml`, `requirements.txt`) — **never import third-party packages not present in the project without stating the dependency explicitly**.
3. Existing code style, test framework, and linter config (`ruff.toml`, `mypy.ini`, `pytest.ini`).

### Step 2 — Non-Negotiable Python Quality Standards

Apply every rule below unless project conventions explicitly dictate otherwise:

1. **Strict Type Hints**: Use `from __future__ import annotations`, annotate all function parameters and return types, and avoid untyped `Any` unless genuinely dynamic.
2. **Safe I/O & Paths**: Use `pathlib.Path` with explicit `encoding="utf-8"`; use context managers (`with`) for all files, locks, and network connections.
3. **Defensive Validation at Boundaries**: Validate external inputs (CLI args, CSV/JSON rows, env vars) immediately and raise specific exceptions (`ValueError`, `TypeError`, `FileNotFoundError`) with actionable messages.
4. **Zero Dangerous Defaults & Anti-Patterns**:
   - Never use mutable default arguments (`def f(items: list[str] = [])`).
   - Never use bare `except:` or silent `except Exception: pass`.
   - Never call `subprocess.run(..., shell=True)` with interpolated user input — always pass argument lists (`["cmd", arg]`) with `check=True` and explicit `timeout=`.
   - Never use `eval()`, `exec()`, `pickle.loads()`, or `yaml.load()` (always `yaml.safe_load()`).
   - Use `decimal.Decimal` for currency/grading math instead of binary `float`.
5. **Clean Architecture**: Keep pure business logic separate from CLI/file I/O so core functions are trivially unit-testable.

### Step 3 — Mandatory Verification Gate Before Delivery

Run these checks locally before declaring code complete:

```bash
# 1. Syntax & bytecode compile check (always available)
python3 -m py_compile <file.py>

# 2. Static lint & type checks (run whichever are installed)
ruff check <file.py>
mypy <file.py>

# 3. Execute tests or a concrete smoke test with boundary inputs
pytest -q
```

If `ruff` or `mypy` is unavailable in the environment, state that explicitly and still run `py_compile` + a real execution test covering both happy-path and error-path inputs.

## Output Contract

Every coding deliverable must include:

1. **Implementation** — Clean, typed Python code with clear docstrings on public functions.
2. **Edge Cases Handled** — Explicit list of boundary/failure cases guarded against (empty input, missing files, invalid types, encoding).
3. **Verification Proof** — Exact commands executed (`py_compile`, `pytest`, `ruff`, `mypy`) and their real exit status / results.
