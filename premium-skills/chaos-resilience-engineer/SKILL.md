---
name: chaos-resilience-engineer
description: Design fault-tolerant timeouts, retries, and game days.
version: 2.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [chaos, resilience, sre, timeouts, retries, availability]
    related_skills: [observability-setup, incident-response, kubernetes-architect]
---

# Chaos & Resilience Engineer

Eliminate cascading failures by enforcing strict timeouts, exponential backoff with jitter, circuit breakers, idempotency keys, multi-replica HA, and blast-radius-bounded chaos experiments.

## When to Use

- Auditing microservices and clients for missing network/DB timeouts, retry storms, or single points of failure
- Designing circuit breakers, bulkheads, graceful degradation, and idempotent retry semantics
- Planning controlled Game Days and fault-injection hypotheses with automated abort criteria

### When Not to Use

- Live active outage triage (use `incident-response`) or metric/trace setup only (use `observability-setup`)

## How to Run

> **Bundled Helper Script (`v2.0.0`):** Run `python premium-skills/chaos-resilience-engineer/scripts/audit_resilience.py .` to flag Python `requests`/`urlopen` calls missing `timeout=`, JS/TS `fetch()` calls missing `AbortSignal`, single-replica Kubernetes Deployments, and missing `PodDisruptionBudget`s.

```bash
npx @jovianops/cortex install --agent vscode --skill chaos-resilience-engineer --scope project
python premium-skills/chaos-resilience-engineer/scripts/audit_resilience.py . --json
```

## Mandatory Resilience Engineering Protocol

### Step 1 — Map Failure Modes & Dependency Graph

Enumerate every synchronous downstream dependency (HTTP, gRPC, SQL, cache, queue) and define its failure mode: fail-closed, degrade gracefully with cached/default data, or shed load via backpressure.

### Step 2 — Non-Negotiable Fault-Tolerance Patterns

1. **Bounded Timeouts Everywhere**: Every outbound network call (`requests`, `urlopen`, `fetch`, `http.Client`, DB query) MUST set explicit connect and read timeouts derived from the parent SLO deadline.
2. **Safe Retries with Jitter & Idempotency**: Only retry idempotent operations (or operations guarded by an `Idempotency-Key`), cap max attempts (typically `<= 3`), and apply full-jitter exponential backoff + retry budgets to prevent retry storms.
3. **Bulkheads & Circuit Breakers**: Isolate slow dependencies into bounded connection/worker pools and trip circuit breakers when error rates breach threshold.
4. **Controlled Chaos Experiments**: Every fault injection MUST state a steady-state hypothesis (SLI), minimal blast radius (canary/staging first), and an automatic kill switch.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled resilience auditor across service code and cluster configs:

```bash
python premium-skills/chaos-resilience-engineer/scripts/audit_resilience.py .
```

Stop and resolve all missing-timeout and single-replica findings before production cutover.

## Output Contract

Deliver:
1. **Failure-Mode & Resilience Audit** — Exact file:line timeout, retry, and single-point-of-failure gaps with concrete code/config fixes.
2. **Chaos Game-Day Plan** — Steady-state metric, injected fault, blast-radius cap, and immediate abort trigger.
3. **Verification Results** — Exact output from `audit_resilience.py`.
