---
name: graphql-architect
description: Design schema-first GraphQL APIs with Relay pagination.
version: 2.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [graphql, api, schema, relay, dataloader, security]
    related_skills: [api-designer, db-optimizer, security-auditor]
---

# GraphQL Schema & Resolver Architect

Design schema-first, backwards-compatible GraphQL APIs featuring Relay cursor pagination, dedicated Mutation Input/Payload types, DataLoader N+1 batching, and query-depth/complexity protection.

## When to Use

- Designing new GraphQL SDL schemas or evolving existing federated/monolith graphs safely
- Eliminating GraphQL N+1 resolver bottlenecks with DataLoader batching
- Hardening public GraphQL endpoints against query-depth DoS, introspection leaks, and authorization bypasses

### When Not to Use

- REST/OpenAPI-only endpoint design (use `api-designer`) or raw SQL index tuning (use `db-optimizer`)

## How to Run

> **Bundled Helper Script (`v2.0.0`):** Run `python premium-skills/graphql-architect/scripts/lint_graphql.py schema.graphql` to audit GraphQL SDL for unbounded list queries, mutations missing Input types, nullable `id: ID`, and `@deprecated` directives lacking a reason.

```bash
npx @jovianops/cortex install --agent vscode --skill graphql-architect --scope project
python premium-skills/graphql-architect/scripts/lint_graphql.py schema.graphql --json
```

## Mandatory GraphQL Engineering Protocol

### Step 1 — Schema-First Domain & Authorization Model

1. Model domain entities as clear GraphQL object types with non-null `id: ID!` and explicit nullability (nullable fields allow partial failure without nulling entire queries).
2. Define authorization rules at the domain/service boundary — never rely solely on field hiding or client-side filtering.

### Step 2 — Non-Negotiable GraphQL Contract Standards

1. **Bounded Relay Pagination**: Every collection field on `Query` or nested high-cardinality edges MUST use cursor pagination (`first`, `after`, `edges`, `pageInfo`) with an enforced server-side maximum page size.
2. **Input & Payload Types on Mutations**: Wrap every mutation's parameters in `<Action>Input!` and return `<Action>Payload!` containing both the mutated resource and structured typed `userErrors`.
3. **N+1 Prevention**: Pair every relational resolver with a per-request DataLoader batch function (never reuse DataLoader instances across requests).
4. **Evolution & Security Controls**: Never delete or break live fields without `@deprecated(reason: "...")`; enforce query depth limits, cost/complexity budgets, and disable production introspection unless explicitly public.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled schema auditor on every `.graphql`/`.gql` file:

```bash
python premium-skills/graphql-architect/scripts/lint_graphql.py schema/
```

Stop and fix all unbounded list queries and contract violations before merging.

## Output Contract

Deliver:
1. **GraphQL SDL Schema** — Types, Relay Connections, Input/Payload mutations, and documented deprecations.
2. **Resolver & Security Blueprint** — DataLoader batch keys, authorization checks, and depth/complexity limits.
3. **Verification Results** — Exact output from `lint_graphql.py`.
