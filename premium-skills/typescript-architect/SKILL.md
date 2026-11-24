---
name: typescript-architect
description: Build strict TypeScript and React apps with runtime safety.
version: 2.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [typescript, react, node, frontend, architecture, testing]
    related_skills: [accessibility-auditor, api-designer, security-auditor]
---

# TypeScript & React Architect

Design strictly typed, boundary-validated TypeScript applications (Node.js and React) with zero `any` leaks, exhaustive discriminated unions, safe DOM rendering, and deterministic test coverage.

## When to Use

- Designing or refactoring TypeScript modules, React components, state machines, or Node APIs
- Hardening `tsconfig.json` strictness and migrating untyped JavaScript or `any`-heavy code
- Validating untrusted external JSON/API payloads at runtime boundaries

### When Not to Use

- Pure Python services (use `python-coding-assistant`) or WCAG accessibility-only audits (use `accessibility-auditor`)

## How to Run

> **Bundled Helper Script (`v2.0.0`):** Run `python premium-skills/typescript-architect/scripts/lint_ts.py src/` to audit `tsconfig.json` strict flags and scan `.ts/.tsx` files for `: any`, `@ts-ignore`, `dangerouslySetInnerHTML`, `eval()`, and chained `!` assertions.

```bash
npx @jovianops/cortex install --agent vscode --skill typescript-architect --scope project
python premium-skills/typescript-architect/scripts/lint_ts.py . --json
```

## Mandatory TypeScript Engineering Protocol

### Step 1 — Lock Compiler & Boundary Contracts

1. Enforce `strict: true`, `noUncheckedIndexedAccess: true`, and `noImplicitOverride: true` in `tsconfig.json`.
2. Treat every external boundary (HTTP responses, URL params, `localStorage`, `process.env`, form inputs) as `unknown` until validated by a runtime schema guard.

### Step 2 — Non-Negotiable Type & Runtime Safety Rules

1. **Zero `any` Escape Hatches**: Never introduce `: any` or `as any`; model domain states with discriminated unions (`{ status: 'ok'; data: T } | { status: 'error'; error: E }`) and `satisfies`.
2. **No Blind Suppression**: Never use `@ts-ignore` or `@ts-nocheck`; fix the underlying type or use `@ts-expect-error` with an explicit ticket/reason.
3. **XSS & Execution Safety**: Never use `eval()`, `new Function()`, or unsanitized `dangerouslySetInnerHTML`.
4. **Bounded Async Effects**: Always pass `AbortSignal` into `fetch()` calls and clean up React `useEffect` subscriptions/timers on unmount.
5. **Exhaustive Switch Checks**: Include a `never` exhaustiveness helper on union switches so adding a new variant fails at compile time.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled verifier alongside `tsc --noEmit` and unit tests:

```bash
python premium-skills/typescript-architect/scripts/lint_ts.py .
npx tsc --noEmit
npm test
```

Stop and resolve all type errors and CRITICAL/HIGH static findings before concluding.

## Output Contract

Deliver:
1. **Typed Implementation** — Strict TypeScript/TSX modules with explicit boundary schemas and discriminated unions.
2. **Compiler & Safety Summary** — Strict `tsconfig` flags, error-handling paths, and cleanup guarantees.
3. **Verification Results** — Output of `lint_ts.py`, `tsc --noEmit`, and test suite.
