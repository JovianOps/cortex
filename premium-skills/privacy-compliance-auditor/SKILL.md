---
name: privacy-compliance-auditor
description: Audit code and logs for GDPR, CCPA, and raw PII leaks.
version: 2.0.1
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [privacy, gdpr, ccpa, pii, compliance, security]
    related_skills: [security-auditor, db-optimizer, observability-setup]
---

# Privacy & PII Compliance Auditor

Audit source code, test fixtures, telemetry pipelines, and database schemas for GDPR/CCPA data minimization, retention TTLs, erasure workflows, and raw PII leaks in logs or repositories.

## When to Use

- Auditing application code, telemetry/log statements, CSV/JSON fixtures, or schemas for raw PII
- Designing GDPR right-to-erasure (DSAR), consent tracking, retention TTLs, and pseudonymization
- Preparing privacy impact checklists before launching analytics or AI data pipelines

### When Not to Use

- Credential/API-key secret scanning only (use `security-auditor`) or formal legal counsel (note clearly that technical controls do not replace legal review)

## How to Run

> **Bundled Helper Script (`v2.0.0`):** Run `python premium-skills/privacy-compliance-auditor/scripts/scan_pii.py .` to detect raw SSNs, Luhn-validated payment card numbers, unmasked PII in logger/print calls, and optional non-example email addresses (`--check-emails`).

```bash
npx @jovianops/cortex install --agent vscode --skill privacy-compliance-auditor --scope project
python premium-skills/privacy-compliance-auditor/scripts/scan_pii.py . --json
```

## Mandatory Privacy Engineering Protocol

### Step 1 — Classify Data Flows & Legal Basis

Map every personal-data field collected (direct identifiers, quasi-identifiers, sensitive/special-category data), its storage location, retention TTL, third-party processors, and deletion path.

### Step 2 — Non-Negotiable Privacy & Data Minimization Rules

1. **Zero Raw PII in Logs & Traces**: Never pass SSNs, payment card PANs, passwords, DOBs, or raw emails into `logger.*`, `console.log`, or OpenTelemetry span attributes; use an allowlist serializer with deterministic redaction.
2. **Synthetic Fixtures Only**: Never commit production database dumps or real user records into tests; use RFC 2606 `@example.com` emails and non-Luhn synthetic fixtures.
3. **Encryption & Pseudonymization**: Separate identity tables from behavioral analytics via keyed HMAC/tokenization so right-to-erasure (`DELETE` / crypto-shredding) completes atomically without breaking referential integrity.
4. **Explicit Retention & DSAR Paths**: Every PII table/bucket MUST document a retention TTL and automated purge job.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled PII scanner across source files, fixtures, and sample logs:

```bash
python premium-skills/privacy-compliance-auditor/scripts/scan_pii.py .
```

Stop and redact or replace every CRITICAL and HIGH PII finding immediately.

## Output Contract

Deliver:
1. **Data Inventory & Flow Map** — PII categories, storage systems, retention TTLs, and processors.
2. **PII Leak & Compliance Findings** — Severity, redacted file:line evidence, and concrete redaction/schema fixes.
3. **Verification Results** — Exact output from `scan_pii.py`.
