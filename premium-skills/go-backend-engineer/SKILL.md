---
name: go-backend-engineer
description: Build production Go services with context and timeouts.
version: 3.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [go, golang, backend, concurrency, microservices]
    related_skills: [observability-setup, chaos-resilience-engineer, api-designer]
---

# Go Backend Engineer

Design clean, race-free, production-grade Go services with explicit `context.Context` cancellation, bounded `http.Server` / `http.Client` timeouts, wrapped errors, and graceful shutdown.

## When to Use

- Building Go HTTP/gRPC APIs, background workers, CLIs, or concurrent pipelines
- Auditing Go services for goroutine leaks, missing timeouts, ignored errors, or data races
- Refactoring monolithic Go packages into small, testable interfaces

### When Not to Use

- Rust systems programming (use `rust-systems-engineer`) or Kubernetes YAML authoring (use `kubernetes-architect`)

## How to Run

> **Bundled Helper Script (`v3.0.0`):** Run `python premium-skills/go-backend-engineer/scripts/lint_go.py .` to audit `.go` files for `http.ListenAndServe` without timeouts, default `http.Get`/`http.Post`, ignored `_ =` returns, `panic()`, `InsecureSkipVerify: true`, and `context.TODO()`.

```bash
npx @jovianops/cortex install --agent vscode --skill go-backend-engineer --scope project
python premium-skills/go-backend-engineer/scripts/lint_go.py . --json
```

## Mandatory Go Engineering Protocol

### Step 1 — Context, Interface & Shutdown Architecture

1. Accept `ctx context.Context` as the first parameter on every I/O, RPC, and DB function.
2. Define small consumer-side interfaces (1–3 methods) to keep unit tests fast and mock-free.
3. Wire `signal.NotifyContext` with `server.Shutdown(ctx)` for clean rolling deployments.

### Step 2 — Non-Negotiable Go Production Standards

1. **Bounded HTTP Servers & Clients**: Always instantiate `&http.Server{ReadHeaderTimeout, ReadTimeout, WriteTimeout, IdleTimeout}` and `&http.Client{Timeout}` — never use bare `http.ListenAndServe` or `http.Get`.
2. **Explicit Error Handling**: Wrap errors with `fmt.Errorf("op: %w", err)`, check with `errors.Is`/`errors.As`, never discard errors via `_ =`, and never `panic()` on runtime/input errors.
3. **Leak-Free Concurrency**: Every goroutine MUST have a bounded lifetime controlled by `ctx.Done()` or `errgroup.Group` + `SetLimit(n)`.
4. **TLS & Logging**: Never set `InsecureSkipVerify: true`; use structured `log/slog` with request context instead of `fmt.Println`.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled verifier plus Go race detector and vet checks when `go` is installed:

```bash
python premium-skills/go-backend-engineer/scripts/lint_go.py .
go vet ./...
go test -race ./...
```

Stop and fix any race conditions, timeout gaps, or CRITICAL/HIGH findings before shipping.

## Output Contract

Deliver:
1. **Go Implementation & Table-Driven Tests** — Idiomatic packages with context propagation, timeouts, and `_test.go` suites.
2. **Concurrency & Shutdown Summary** — Goroutine bounds, timeout values, and graceful shutdown sequence.
3. **Verification Results** — Output of `lint_go.py`, `go vet`, and `go test -race`.
