---
name: api-designer
description: Design strict OpenAPI and GraphQL specs with contracts.
version: 0.2.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [api, openapi, graphql, rest, contract-testing]
    related_skills: [documentation-generator, security-auditor, testing-automation]
---

# API Designer

Design, validate, and version production-grade REST (OpenAPI 3.1) and GraphQL APIs with explicit error envelopes, pagination, idempotency, security schemes, and executable contract tests.

## When to Use

- Designing a new REST or GraphQL API specification from product requirements
- Auditing an existing OpenAPI/GraphQL schema for breaking changes, security gaps, or poor ergonomics
- Generating server stubs, typed models, or contract tests directly from a validated spec
- Planning API versioning and zero-downtime deprecation rollouts

### When Not to Use

- Implementing internal business logic unrelated to HTTP/GraphQL boundary contracts

## How to Run

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/api-designer --yes
hermes chat -q "Design a validated OpenAPI 3.1 spec and contract tests for a task management REST API"
```

## Mandatory API Design Protocol

### Step 1 — Establish Domain Boundaries & Non-Functional Requirements

Before emitting YAML or SDL, lock down:

- Resource entities, ownership/tenancy boundaries, and state transitions
- Authentication & authorization model (`Bearer` JWT / OAuth2 scopes / API keys)
- Consistency & retry requirements (which mutating endpoints need `Idempotency-Key`)
- Versioning strategy (`/v1/...` URI prefix vs header) and backward-compatibility constraints

### Step 2 — Enforce Production API Design Standards

Apply every rule below — these are the exact omissions that separate production specs from toy drafts:

1. **Resource-Oriented Naming & Semantics**:
   - Plural nouns (`/v1/tasks`, `/v1/tasks/{task_id}`), lowercase kebab-case, HTTP methods matching semantics (`GET` safe/idempotent, `PUT` idempotent replace, `PATCH` partial update, `DELETE` idempotent).
   - Return `201 Created` + `Location` header on creation; `202 Accepted` + status resource for async jobs; `204 No Content` on empty deletes.
2. **Never Return Unbounded Collections**:
   - Every list endpoint MUST enforce cursor-based pagination (`cursor`, `limit` with hard `maximum`, e.g., `100`) and return `{ "data": [...], "page": { "next_cursor": "...", "has_more": true } }`.
3. **Standardized Error Contract (RFC 9457 `application/problem+json`)**:
   - Define a reusable `ProblemDetails` schema (`type`, `title`, `status`, `detail`, `instance`, `errors[]`) and attach explicit `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500` responses to every operation.
4. **Strict Schemas & Input Constraints**:
   - Specify `format` (`uuid`, `date-time`, `email`, `uri`), `minLength`/`maxLength`, `minimum`/`maximum`, explicit `required` arrays, `enum` values, and `additionalProperties: false` on request payloads.
   - Never leak internal DB auto-increment IDs or stack traces in response schemas.
5. **Idempotency, Concurrency & Rate Limits**:
   - Require `Idempotency-Key` on retry-sensitive `POST` mutations (payments, orders, job triggers).
   - Use `ETag` / `If-Match` for optimistic concurrency on contested updates.
   - Document `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, and `Retry-After` headers.
6. **GraphQL-Specific Rules** (when designing GraphQL):
   - Follow Relay Connection pagination (`edges`, `node`, `pageInfo`), explicit typed error unions on mutations, persisted-query / depth-limit recommendations, and DataLoader batching notes to prevent N+1 queries.

### Step 3 — Mandatory Spec Validation & Contract Tests

Validate every generated spec before returning:

```bash
# YAML/JSON parse check
python3 -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('openapi.yaml').read_text())"

# OpenAPI linter/validator when installed
npx @redocly/cli lint openapi.yaml
```

Provide executable contract test cases covering:

- Happy-path schema compliance (status code, `Content-Type`, response JSON schema)
- Validation rejection (`400`/`422` returning `application/problem+json` on bad field/unknown property)
- Auth failure (`401` unauthenticated, `403` wrong tenant/scope)
- Idempotency replay (`POST` with same `Idempotency-Key` does not duplicate resources)

## Output Contract

Deliver:

1. **Specification Artifact** — Complete, valid `openapi.yaml` (3.1.0) or `schema.graphql`.
2. **Endpoint & Error Matrix** — Concise table mapping routes/operations to auth scopes, pagination, idempotency, and error codes.
3. **Breaking-Change & Versioning Note** — How the contract evolves without breaking existing clients.
4. **Validation & Contract Test Suite** — Executed lint output plus runnable contract test file.
