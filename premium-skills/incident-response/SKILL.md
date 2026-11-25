---
name: incident-response
description: Triage outages, contain blast radius, and write postmortems.
version: 2.0.1
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [incident-response, sre, ops, postmortem, triage]
    related_skills: [observability-setup, devops-pipeline, performance-profiler, security-auditor]
---

# Incident Response

Run calm, deterministic incident triage and recovery: classify severity, stabilize production first (rollback/feature-flag before root-cause debugging), preserve forensic evidence, communicate on a fixed cadence, and produce a blameless postmortem with verifiable action items.

## When to Use

- Active production outage, elevated 5xx rate, latency spike, data pipeline stall, or security incident
- Reconstructing an incident timeline from logs, metrics, deploy history, and alert transcripts
- Drafting internal/external status updates and blameless postmortems with concrete follow-up actions
- Preparing rollback or traffic-shifting runbooks under time pressure

### When Not to Use

- Routine bug fixes or non-urgent local development debugging with zero production impact
- Speculative architecture redesigns unrelated to stabilizing or preventing an incident

## How to Run

> **Bundled Helper Script (`v1.0.0`):** Run `python premium-skills/incident-response/scripts/incident_timeline.py timeline.json` to validate monotonic UTC ISO-8601 timelines, action-item owners/dates, and compute MTTD/MTTR.

```bash
# Universal CLI (Claude Code, Codex, Gemini CLI, Cursor, Copilot, OpenCode, OpenClaw, Goose, Cline)
npx skills add JovianOps/cortex --skill incident-response -g -y

# Hermes Agent
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/incident-response --yes
```

## Mandatory Incident Response Protocol

### Step 1 — Classify Severity & Protect Blast Radius (Stop Gate)

Before proposing any code edit or restart, establish ground truth:

1. **Severity Level**:
   - **SEV-1**: Complete outage, data loss/corruption, or active security breach affecting all/most users.
   - **SEV-2**: Major feature degraded, elevated error rate exceeding SLO burn budget, or partial regional failure.
   - **SEV-3**: Minor degradation with clean workaround; no data integrity risk.
2. **Evidence Preservation Stop Gate**: Never wipe logs, rotate crashing pods without capturing logs/heap/thread dumps, or run destructive database repairs before snapshotting state.
3. **Stabilize First, Root-Cause Second**: Prioritize fast, reversible mitigations in strict order:
   - Revert recent deploy (`git revert` / rollout undo) or flip kill-switch feature flag
   - Shed non-critical load / raise rate limits / shift traffic away from degraded zone
   - Scale stateless replicas or fail over read-only/standby tier

### Step 2 — Collect Verified Telemetry & Change Correlation

Run read-only diagnostic commands and correlate timestamps strictly in **UTC** (never guess root cause before checking recent changes):

```bash
# Recent deploys & commits
git log -n 10 --format="%h %ai %an %s"

# Service / container status & logs (adapt to stack)
kubectl get pods -A --field-selector=status.phase!=Running
kubectl rollout history deployment/<service>
```

Check:
- Deployments, config/flag flips, secret rotations, schema migrations, and dependency outages within the last 60 minutes.
- Exact error signatures, affected endpoints, HTTP status distribution, and saturation metrics (CPU, memory/OOMKilled, DB connections, queue depth).

### Step 3 — Execute Reversible Mitigation & Verify Recovery

For every mitigation action, state:
1. **Exact command** to apply
2. **Rollback command** if the mitigation worsens symptoms
3. **Verification check** proving recovery (error rate returning to baseline, p95 latency stabilized, synthetic health checks green for >= 5 minutes)

**Safety Stop Gate**: Require explicit human confirmation before running destructive commands (`DROP`, `DELETE`, force-restarting stateful databases, purging queues, or revoking active production credentials).

### Step 4 — Blameless Postmortem & Preventative Action Items

After recovery is verified, write a **blameless** postmortem focusing on systems, missing guardrails, and detection gaps — never blaming individuals:

- Reconstruct an exact **UTC timeline** with source citations (alert, log line, commit SHA, Slack/status timestamp).
- Separate **Trigger** (immediate event) from **Contributing Factors** (missing alert, no canary gate, unbounded retries).
- Every follow-up action item must specify an **Owner**, **Priority (P0/P1/P2)**, **Verification Criterion**, and **Target Date** (reject vague actions like "be more careful").

## Strict Output Contract

```markdown
## Incident Triage Summary
- **Severity:** SEV-1 / SEV-2 / SEV-3
- **Customer Impact:** Exact scope, affected endpoints/regions, and start time (UTC).
- **Current Status:** Investigating / Identified / Mitigating / Monitoring / Resolved

## Immediate Stabilization Plan
1. **Action:** Exact command or flag change.
   - **Rollback:** Exact revert command.
   - **Recovery Signal:** Metric or probe confirming stabilization.

## UTC Timeline (Evidence-Backed)
| Time (UTC) | Event | Evidence Source |
| :--- | :--- | :--- |

## Root Cause & Contributing Factors
- **Trigger:** Verified immediate cause (or `UNVERIFIED — awaiting telemetry`).
- **Contributing Factors:** Systemic gaps that allowed impact or slowed recovery.

## Blameless Action Items
| Priority | Action | Owner | Verification Criterion |
| :--- | :--- | :--- | :--- |
```
