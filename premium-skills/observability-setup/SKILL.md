---
name: observability-setup
description: Add structured logs, OTel traces, SLOs, and clean alerts.
version: 0.4.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [observability, opentelemetry, logging, metrics, slo]
    related_skills: [performance-profiler, incident-response, devops-pipeline, docker-generator]
---

# Observability Setup

Instrument services with high-signal, low-cardinality observability: structured JSON logs with trace correlation, OpenTelemetry distributed traces, RED/USE golden metrics, measurable SLOs with error budgets, and actionable low-noise alerts.

## When to Use

- Instrumenting a new API, worker, or microservice with logs, metrics, and distributed tracing
- Migrating unstructured `print`/`console.log` calls to structured JSON logging with `trace_id`/`request_id`
- Defining SLOs, SLIs, dashboards, and burn-rate alerts that eliminate alert fatigue
- Auditing existing metrics for cardinality explosions or PII/secret leakage in logs

### When Not to Use

- One-off CPU/memory micro-benchmarking (use `performance-profiler` instead)
- Active outage triage where stabilization takes priority (use `incident-response` instead)

## How to Run

```bash
# Universal CLI (Claude Code, Codex, Gemini CLI, Cursor, Copilot, OpenCode, OpenClaw, Goose, Cline)
npx skills add JovianOps/cortex --skill observability-setup -g -y

# Hermes Agent
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/observability-setup --yes
```

## Mandatory Observability Protocol

### Step 1 — Map Critical User Journeys & Signal Contract

Before adding SDKs or dashboards, enumerate:
- Top user-facing endpoints, background jobs, and external dependencies (DB, cache, queues, third-party APIs).
- Exact **SLIs** (availability ratio, p95/p99 latency, job completion freshness) and target **SLOs** (e.g., 99.9% 30-day availability = 43.2m error budget).

### Step 2 — Enforce Strict Telemetry Guardrails (Stop Gates)

1. **Zero High-Cardinality Metric Labels**: NEVER put unbounded values (`user_id`, `request_id`, `email`, raw URL path with IDs, timestamps) into metric labels/tags! Use normalized route templates (`/orders/:id`), status classes (`2xx`/`4xx`/`5xx`), and bounded enums.
2. **Zero PII or Secrets in Logs/Traces**: Scrub `Authorization`, `Cookie`, API keys, tokens, passwords, and sensitive personal fields before serialization.
3. **Trace-to-Log Correlation**: Every structured JSON log line emitted inside a request or job must include `timestamp` (ISO-8601 UTC), `level`, `service`, `event`, `trace_id`, `span_id`, and `duration_ms` where applicable.
4. **RED + USE Coverage**:
   - **RED** (services): **R**ate, **E**rrors, **D**uration histograms (with explicit buckets matching SLO thresholds).
   - **USE** (resources): **U**tilization, **S**aturation (queue depth/pool wait), **E**rrors.

### Step 3 — Design Actionable, Low-Noise Alerts

Every alert rule MUST satisfy all four criteria or be rejected:
1. **Symptom-based** (SLO multi-window burn rate or customer-visible failure), not raw CPU noise.
2. **Actionable** — requires a human decision or verified automated remediation.
3. **Runbook-linked** — includes exact dashboard link, impact statement, and first diagnostic step.
4. **Severity-routed** — `page` (immediate wake-up: fast burn >= 14.4x over 1h) vs. `ticket` (slow burn / capacity warning).

### Step 4 — Verify Instrumentation End-to-End

Run local tests or dry-run collectors to verify:
- Logs emit valid single-line JSON with `trace_id` populated and secrets redacted.
- `/metrics` (or OTLP export) exposes expected metric names with bounded label cardinality.
- Alert YAML/JSON rules pass syntax validation (`promtool check rules` / `yamllint` when installed).

## Strict Output Contract

```markdown
## Observability Architecture Summary
- **Service & Critical Journeys:** Endpoints/workers covered.
- **SLIs & SLOs:** Exact formulas, targets, and 30-day error budgets.

## Telemetry Implementation
1. **Structured Logging:** Schema fields, redaction list, and correlation wiring.
2. **Metrics (RED / USE):** Metric names, types, histogram buckets, and bounded label sets.
3. **Distributed Tracing (OpenTelemetry):** Span boundaries, context propagation, and sampling strategy.

## Alerting Rules (Low-Noise Contract)
| Alert | Severity | Trigger Condition | Runbook First Step |
| :--- | :--- | :--- | :--- |

## Verification Evidence
- Exact test/lint commands executed confirming valid JSON logs, bounded cardinality, and rule syntax.
```
