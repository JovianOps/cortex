---
name: code-review-assistant
description: Automated code review with style checks, security scans, and best practices.
version: 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, automation, quality]
    related_skills: []
---
# Code Review Assistant Skill

Automated code review with style checks, security scans, and best practice enforcement.

## When to Use
- Automate PR reviews
- Enforce code standards
- Catch security issues early

## Prerequisites
- Language-specific linters (eslint, flake8, etc.)
- Security scanners (semgrep, bandit, etc.)

## How to Run
```bash
hermes skills install owner/repo/skills/code-review-assistant
hermes chat -q "Review the latest PR for security issues and style violations"
```

## Commands
| Command | Description |
|---------|-------------|
| `review-pr` | Full automated PR review |
| `lint-check` | Run all configured linters |
| `security-scan` | Run security scanners |
| `style-check` | Check code style compliance |

## Usage Examples
- "Review PR #42 for security issues"
- "Check code style for the latest commit"
- "Run all linters on the feature branch"