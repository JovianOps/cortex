---
name: code-review-assistant
description: Code review with anti-hallucination checks, style enforcement, and deterministic validation.
version: 0.1.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, validation, anti-hallucination, quality]
    related_skills: [python-coding-assistant, academic-assistant]
---
# Code Review Assistant Skill

Code review with anti-hallucination checks, style enforcement, and deterministic validation.

## When to Use
- Automate PR reviews
- Enforce code standards
- Catch security issues early
- Validate code before merge

## How to Run
```bash
hermes skills install owner/repo/skills/code-review-assistant
hermes chat -q "Review PR #42 for security issues and style violations"
```

## Features
- Style enforcement (linting)
- Security scanning (bandit, semgrep)
- Complexity analysis
- Dependency checking
- Anti-hallucination: only flag real issues

## Checks
| Check | Tool | Purpose |
|-------|------|---------|
| Style | ruff/flake8 | Consistent formatting |
| Security | bandit/semgrep | Vulnerability detection |
| Complexity | radon | Maintainability |
| Types | mypy | Type safety |
| Dead code | vulture | Unused code |

## Anti-Hallucination
- Only reports actual findings (no invented issues)
- Every finding traced to line number
- Severity scoring with evidence