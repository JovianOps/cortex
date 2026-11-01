---
name: security-audit
description: Security auditing with vulnerability scanning, dependency checking, and compliance.
version: 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, audit, vulnerability, compliance]
    related_skills: [code-review-assistant, api-development, ci-cd-pipeline]
---
# Security Audit Skill

Security auditing with vulnerability scanning, dependency checking, and compliance.

## When to Use
- Dependency vulnerability scanning
- Static code analysis
- Compliance checking (OWASP, etc.)
- Secrets detection

## Prerequisites
- Bandit, Safety, Semgrep, TruffleHog

## How to Run
```bash
hermes skills install owner/repo/skills/security-audit
hermes chat -q "Run security audit on my Python project"
```

## Features
- Dependency vulnerability scanning (Safety)
- Static analysis (Bandit, Semgrep)
- Secrets detection (TruffleHog)
- License compliance
- SBOM generation