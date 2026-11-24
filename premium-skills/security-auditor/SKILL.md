---
name: security-auditor
description: Audit code for OWASP flaws, secrets, and CWE findings.
version: 0.4.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [security, owasp, audit, secrets, vulnerability-scanning]
    related_skills: [code-review-assistant, devops-pipeline, docker-generator, anti-hallucination]
---

# Security Auditor

Audit source code, configurations, and dependency manifests for OWASP Top 10 vulnerabilities, hardcoded secrets, supply-chain risks, and insecure defaults using source-to-sink evidence and mandatory secret redaction.

## When to Use

- Pre-release security review of an application, API, CLI, or infrastructure repo
- Scanning for hardcoded secrets, injection flaws, broken access control, or SSRF/path traversal
- Auditing lockfiles and containers for known vulnerable dependencies
- Mapping verified security defects to CWE IDs and concrete minimal remediation patches

### When Not to Use

- Offensive exploitation against systems you do not own or have explicit authorization to test

## How to Run

> **Bundled Helper Script (`v0.3.0`):** Run `python premium-skills/security-auditor/scripts/secret_scan.py .` for offline, auto-redacted CWE secret and dangerous-sink pre-scanning.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/security-auditor --yes
hermes chat -q "Audit this codebase for OWASP vulnerabilities, hardcoded secrets, and unsafe defaults"
```

## Mandatory Security Audit Protocol

### Step 1 — Map Attack Surface & Trust Boundaries First

Before flagging issues, identify:

- Entry points accepting untrusted input (HTTP routes, GraphQL resolvers, webhooks, CLI args, file uploads, env/config parsers)
- Authentication, session/JWT handling, and tenant/object-level authorization checks
- Sensitive sinks (SQL queries, shell commands, filesystem paths, HTML templates, outbound HTTP requests, deserializers, crypto primitives)

### Step 2 — Run Deterministic Scanners & Pattern Audits

Execute available security tools and record exact output (never fabricate scan results or CVE IDs):

```bash
# Dependency audits (run whichever match the repo)
npm audit --omit=dev
pip-audit
trivy fs . --severity HIGH,CRITICAL

# Static security scans when installed
bandit -r . -ll
semgrep --config auto .
```

### Step 3 — Source-to-Sink Vulnerability Verification (Zero False-Positive Spam)

For every suspected vulnerability, trace **both** the untrusted source and the dangerous sink before reporting:

1. **Injection (CWE-89 SQLi, CWE-78 OS Command, CWE-94 Code)**: String formatting/concatenation reaching SQL execution, `subprocess(..., shell=True)`, `eval`/`exec`, or template engines without parameterization.
2. **Broken Access Control (CWE-639 IDOR, CWE-862 Missing AuthZ)**: Endpoints loading records by user-supplied ID without verifying ownership/tenant scope; missing auth middleware on admin/mutating routes; mass assignment.
3. **Path Traversal & SSRF (CWE-22, CWE-918)**: User-controlled paths joined without canonicalization + `Path.resolve().is_relative_to(base_dir)`; outbound requests to user-supplied URLs without allowlisting/blocking link-local (`169.254.169.254`) and RFC1918 private IP ranges.
4. **XSS, CSRF & Auth Crypto (CWE-79, CWE-352, CWE-327, CWE-798)**: `dangerouslySetInnerHTML`/`innerHTML`/`|safe`, weak password hashing (`MD5`/`SHA1`/`SHA256` instead of `Argon2id`/`bcrypt`/`scrypt`), hardcoded JWT secrets, accepting `alg: none`, cookies missing `HttpOnly`/`Secure`/`SameSite`, non-constant-time token compare (`==` instead of `hmac.compare_digest`).
5. **Unsafe Deserialization & XXE (CWE-502, CWE-611)**: `pickle.loads`, `yaml.load` (without `SafeLoader`), untrusted XML parsers.
6. **Hardcoded Secrets (CWE-798)**: High-entropy tokens, AWS keys (`AKIA...`), private keys (`-----BEGIN ... PRIVATE KEY-----`), DB URIs with embedded passwords.
   - **Mandatory Redaction Rule**: ALWAYS redact detected secrets in reports (e.g., `AKIA****...WXYZ`) — never echo full secret values!
   - **Test-Fixture Filter**: Distinguish real credentials from obvious dummy test fixtures (`test_key`, `example.com`, `000000`) and label test-only placeholders separately as `Informational`.

### Step 4 — Evidence-Backed Severity Classification

Assign severity based on **exploitability × impact**:

- **Critical**: Remote unauthenticated compromise, SQLi/RCE, leaked live production credentials, auth bypass.
- **High**: Authenticated IDOR/privilege escalation, stored XSS, SSRF to metadata/internal services, path traversal.
- **Medium**: Missing rate limiting on auth, weak headers/CORS misconfiguration (`Access-Control-Allow-Origin: *` with credentials), sensitive data in logs.
- **Low / Informational**: Defense-in-depth hardening, missing optional headers, test-fixture placeholders.

## Strict Output Contract

```markdown
## Security Audit Summary
- **Scope:** Files/directories audited and automated tools run (or unavailable).
- **Counts:** Critical: <N> | High: <N> | Medium: <N> | Low: <N>

## Verified Findings

### [CRITICAL/HIGH/MEDIUM/LOW] Title (CWE-XXX) — `path/to/file:line`
- **Source → Sink Trace:** Untrusted input origin and exact path to dangerous operation.
- **Exploit Scenario:** Concrete payload or request demonstrating impact.
- **Remediation Patch:** Minimal secure replacement code.

## Dependency & Configuration Notes
- Verified tool findings only (zero invented CVE IDs).
```
