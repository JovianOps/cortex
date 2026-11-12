---
name: security-auditor
description: Audit code for security vulnerabilities, secrets, and compliance issues.
version: 0.1.0
author: Athalla Jovian Maharsa
license: MIT
platforms: [linux, macos, windows]
---

# Security Auditor

Audit code for security vulnerabilities, hardcoded secrets, and compliance issues.

## When to Use
- Pre-release security check
- Detecting hardcoded API keys, tokens, passwords
- OWASP Top 10 vulnerability scanning
- Dependency vulnerability auditing
- Compliance checks (SOC 2, GDPR, HIPAA)

## How to Run
```bash
hermes skills install JovianOps/cortex/premium-skills/security-auditor
hermes chat -q "Audit this codebase for security issues"
```

## Core Capabilities
1. **Secret detection** — Find API keys, tokens, passwords, private keys
4. **Vulnerability scanning** — SQL injection, XSS, CSRF, SSRF patterns
4. **Dependency audit** — Check package.json/requirements.txt for known CVEs
5. **Compliance mapping** — Map findings to OWASP/SOC2/GDPR controls
6. **Remediation** — Provide specific fixes for each finding

## Anti-Hallucination Measures
- Pattern-based detection, not speculation
- No invented CVEs or vulnerabilities
- Explicit file:line references for every finding
- Redacted previews only (never expose full secrets)