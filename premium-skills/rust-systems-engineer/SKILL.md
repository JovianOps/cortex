---
name: rust-systems-engineer
description: Write safe, idiomatic Rust with verified unsafe invariants.
version: 2.0.1
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [rust, systems, memory-safety, concurrency, cargo]
    related_skills: [performance-profiler, security-auditor, unit-test-generator]
---

# Rust Systems Engineer

Author idiomatic, panic-free, ownership-clean Rust crates with explicit `Result` error types, documented `// SAFETY:` invariants on every `unsafe` block, pinned Cargo dependencies, and zero Clippy warnings.

## When to Use

- Designing Rust libraries, CLIs, async services, or FFI bindings
- Auditing existing Rust code for panics (`.unwrap()`), undocumented `unsafe`, or memory/concurrency hazards
- Optimizing allocations, borrowing lifetimes, and lock contention in Rust

### When Not to Use

- Go services (use `go-backend-engineer`) or Python services (use `python-coding-assistant`)

## How to Run

> **Bundled Helper Script (`v2.0.0`):** Run `python premium-skills/rust-systems-engineer/scripts/lint_rust.py .` to audit `.rs` files and `Cargo.toml` for undocumented `unsafe {}`, `.unwrap()` in non-test code, `todo!()`, `mem::transmute`, and wildcard `*` crate versions.

```bash
npx @jovianops/cortex install --agent vscode --skill rust-systems-engineer --scope project
python premium-skills/rust-systems-engineer/scripts/lint_rust.py . --json
```

## Mandatory Rust Engineering Protocol

### Step 1 — Ownership, Error & Concurrency Design

1. Define structured domain errors (implementing `std::error::Error + Display` or `thiserror` for libraries; `anyhow` only at binary entrypoints).
2. Prefer borrowing (`&T`, `&[T]`, `&str`) over unnecessary `.clone()`; prefer message passing or scoped locks over holding `MutexGuard` across `.await` points.

### Step 2 — Non-Negotiable Rust Safety Rules

1. **No Production Panics**: Never use `.unwrap()`, `.expect()` without proven invariants, `todo!()`, or `unimplemented!()` in runtime paths; propagate with `?`.
2. **Strict `unsafe` Hygiene**: Minimize `unsafe` to the smallest safe abstraction and require an adjacent `// SAFETY: ...` comment proving every precondition. Avoid `std::mem::transmute` in favor of `from_ne_bytes`/`TryFrom`.
3. **Dependency Discipline**: Pin explicit SemVer constraints in `Cargo.toml` (never `*`), commit `Cargo.lock` for binaries, and enable minimal crate features.
4. **Concurrency Safety**: Never hold `std::sync::Mutex` across `.await`; use bounded channels to enforce backpressure.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled verifier plus Cargo checks when `cargo` is installed:

```bash
python premium-skills/rust-systems-engineer/scripts/lint_rust.py .
cargo fmt --check
cargo clippy --all-targets -- -D warnings
cargo test
```

Stop and resolve every `unsafe` documentation gap and Clippy warning before completion.

## Output Contract

Deliver:
1. **Rust Implementation & Tests** — Clean modules, structured error enums, and unit/property tests.
2. **Safety & Ownership Notes** — Explicit rationale for any `unsafe` boundary, concurrency primitives, and allocations.
3. **Verification Results** — Exact output of `lint_rust.py`, `cargo clippy`, and `cargo test`.
