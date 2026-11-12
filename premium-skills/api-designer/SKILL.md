---
name: api-designer
description: Design and validate REST/GraphQL APIs from specifications with contract testing.
version: 0.1.0
author: Athalla Jovian Maharsa
license: MIT
platforms: [linux, macos, windows]
---

# API Designer

Design, validate, and generate API contracts from specifications.

## When to Use
- Designing a new REST or GraphQL API
- Validating API specs against OpenAPI/GraphQL SDL
- Generating boilerplate server code from API specs
- Contract testing between frontend and backend
- API versioning and deprecation planning

## How to Run
```bash
hermes skills install JovianOps/cortex/premium-skills/api-designer
hermes chat -q "Design a REST API for a task management system"
```

## Core Capabilities
1. **Spec generation** — Generate OpenAPI 3.x / GraphQL SDL from natural language
2. **Validation** — Validate specs against standards (OpenAPI, JSON Schema)
4. **Boilerplate generation** — Generate Express/Fastify/FastAPI scaffolding
4. **Contract testing** — Verify frontend and backend agree on API shape
5. **Versioning** — Plan breaking changes and deprecation paths

## Anti-Hallucination Measures
- Spec validation against official schemas
- No invented endpoints or fields
- Explicit error reporting on invalid specs
- Deterministic code generation from validated specs