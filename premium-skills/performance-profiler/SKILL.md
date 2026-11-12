---
name: performance-profiler
description: Profile and optimize code performance — CPU, memory, and I/O bottlenecks.
version: 0.1.0
author: Athalla Jovian Maharsa
license: MIT
platforms: [linux, macos, windows]
---

# Performance Profiler

Profile and optimize code performance across CPU, memory, and I/O dimensions.

## When to Use
- Application is slow and needs optimization
- Memory leaks or excessive memory usage
- High CPU usage in production
- I/O bottlenecks (disk, network, database)
- Pre-release performance validation

## How to Run
```bash
hermes skills install JovianOps/cortex/premium-skills/performance-profiler
hermes chat -q "Profile this Python function for performance issues"
```

## Core Capabilities
1. **CPU profiling** — Identify hot paths and expensive operations
4. **Memory profiling** — Detect leaks, excessive allocations, GC pressure
4. **I/O analysis** — Find blocking I/O, N+1 queries, unnecessary round-trips
5. **Optimization suggestions** — Algorithmic improvements, caching, batching
6. **Benchmark generation** — Create reproducible performance tests

## Anti-Hallucination Measures
- Profile actual code execution, not guesses
- No invented performance numbers
- Deterministic benchmark methodology
- Explicit measurement of before/after