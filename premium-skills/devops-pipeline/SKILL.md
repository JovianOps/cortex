---
name: devops-pipeline
description: Generate and validate CI/CD pipelines for GitHub Actions, GitLab CI, and CircleCI.
version: 0.1.0
author: Athalla Jovian Maharsa
license: MIT
platforms: [linux, macos, windows]
---

# DevOps Pipeline Generator

Generate, validate, and optimize CI/CD pipelines across platforms.

## When to Use
- Setting up a new CI/CD pipeline
- Migrating between CI platforms (GitHub Actions → GitLab CI)
- Optimizing slow pipelines
- Adding security scanning to pipelines
- Generating deployment workflows

## How to Run
```bash
hermes skills install JovianOps/cortex/premium-skills/devops-pipeline
hermes chat -q "Create a GitHub Actions pipeline for a Node.js project with tests and deploy"
```

## Core Capabilities
1. **Pipeline generation** — Generate platform-specific YAML configs
4. **Cross-platform conversion** — Convert between GitHub Actions, GitLab CI, CircleCI
4. **Optimization** — Reduce build times, cache dependencies
5. **Security integration** — Add SAST, dependency scanning, secret detection
6. **Validation** — Validate YAML syntax and schema compliance

## Anti-Hallucination Measures
- Schema validation against official platform schemas
- No invented actions or runners
- Deterministic generation from project structure
- Explicit error reporting on invalid configs