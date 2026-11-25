---
name: llm-security-auditor
description: Audit AI agents and prompts against OWASP LLM Top 10.
version: 2.0.1
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [llm, ai-security, owasp, prompt-injection, red-team, agents]
    related_skills: [security-auditor, anti-hallucination, privacy-compliance-auditor]
---

# LLM & AI Agent Security Auditor

Audit LLM applications, RAG pipelines, MCP servers, and agent `SKILL.md` playbooks against the **OWASP Top 10 for LLM Applications** — isolating untrusted input, enforcing least-privilege tool execution, and blocking prompt-injection and data-exfiltration paths.

## When to Use

- Security reviewing LLM prompts, RAG retrieval flows, MCP tool servers, or autonomous agent workflows
- Auditing third-party `SKILL.md` files or plugins for hidden Unicode/indirect prompt injection
- Designing tool allowlists, human-in-the-loop approval gates, and output validators for AI agents

### When Not to Use

- Traditional web/infrastructure-only vulnerability reviews without LLM components (use `security-auditor`)

## How to Run

> **Bundled Helper Script (`v2.0.0`):** Run `python premium-skills/llm-security-auditor/scripts/audit_prompts.py .` to scan prompts, skills, and source files for instruction-override payloads, hidden Unicode/BiDi obfuscation, `curl | sh` agent commands, untrusted system-prompt interpolation, and unrestricted auto-approve flags.

```bash
npx @jovianops/cortex install --agent vscode --skill llm-security-auditor --scope project
python premium-skills/llm-security-auditor/scripts/audit_prompts.py . --json
```

## Mandatory LLM Security Audit Protocol

### Step 1 — Map Trust Boundaries & Tool Blast Radius

Enumerate every data source entering the context window (system prompt, user prompt, retrieved RAG chunks, web pages, tool outputs) and every side-effecting tool (filesystem write, shell exec, HTTP egress, DB mutation, credential access).

### Step 2 — Non-Negotiable OWASP LLM Controls

1. **Prompt & Data Separation (LLM01)**: Never interpolate untrusted user/RAG text into the system prompt; wrap untrusted content in explicit structural delimiters and treat retrieved content strictly as data, never instructions.
2. **Unicode & Skill Supply-Chain Hygiene**: Reject zero-width/BiDi hidden characters (`U+200B`, `U+202E`), verify skill/plugin SHA-256 checksums, and prohibit piping remote URLs into shells.
3. **Least-Privilege Tool Execution (LLM06 / Excessive Agency)**: Require strict JSON Schema argument validation, path-traversal confinement, command allowlists, and mandatory human confirmation for destructive or external-egress actions.
4. **Output & PII Guardrails (LLM02 / LLM05)**: Never pass raw LLM output into `eval()`, SQL concatenation, shell interpolation, or unsanitized HTML; redact secrets/PII before sending context to external model providers.

### Step 3 — Mandatory Verification Gate

Run both the LLM prompt auditor and secret scanner across the repository:

```bash
python premium-skills/llm-security-auditor/scripts/audit_prompts.py .
python premium-skills/security-auditor/scripts/secret_scan.py .
```

Stop and remediate all CRITICAL and HIGH findings before deploying any agent or prompt.

## Output Contract

Deliver:
1. **Threat Model & Trust-Boundary Map** — Untrusted inputs vs. privileged tools and blast radius.
2. **OWASP LLM Findings Table** — Severity, OWASP LLM ID, exact file:line evidence, and concrete remediation diff.
3. **Hardened Guardrail Config** — Tool allowlist, confirmation gates, and verification output from `audit_prompts.py`.
