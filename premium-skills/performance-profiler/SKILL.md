---
name: performance-profiler
description: Profile CPU, memory, and I/O with measured benchmarks.
version: 2.0.1
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [performance, profiling, benchmarking, optimization, memory]
    related_skills: [db-optimizer, python-coding-assistant, refactoring-assistant]
---

# Performance Profiler

Diagnose and fix CPU, memory, and I/O bottlenecks using mandatory baseline profiling, reproducible benchmarks, Amdahl's Law prioritization, and verified before-vs-after measurements.

## When to Use

- Investigating high latency, CPU saturation, memory leaks, GC pauses, or I/O bottlenecks
- Building reproducible micro- or macro-benchmarks before optimizing hot code paths
- Verifying that a proposed optimization actually speeds up execution without breaking behavior

### When Not to Use

- Pure SQL query plan & index tuning (use `db-optimizer`)

## How to Run

> **Bundled Helper Script (`v1.0.0`):** Run `python premium-skills/performance-profiler/scripts/bench_compare.py base.json cand.json` to compare p50/p95/p99 latency samples and enforce a regression threshold.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/performance-profiler --yes
hermes chat -q "Profile src/pipeline.py for CPU and memory bottlenecks and benchmark a verified fix"
```

## Mandatory Measure-First Protocol

### Step 1 — Establish a Reproducible Baseline BEFORE Editing

**Never optimize by intuition alone and never invent performance numbers.**

1. Build or run a deterministic benchmark harness with:
   - Representative realistic input size (not a 5-item toy input where startup dominates)
   - Warmup runs discarded (`>= 3` warmup iterations)
   - Multiple measured iterations reporting **median, p95, and peak memory (RSS / `tracemalloc`)**
2. Capture a real profiler trace using the native runtime profiler:

```bash
# Python CPU + Memory profiling (stdlib — always available)
python3 -m cProfile -s cumtime bench.py | head -n 30
python3 -c "import tracemalloc; tracemalloc.start(); ..."

# Node.js CPU profiling
node --cpu-prof bench.js

# Go CPU & alloc profiling
go test -bench=. -benchmem -cpuprofile=cpu.out -memprofile=mem.out
```

### Step 2 — Classify Bottleneck & Apply Amdahl's Law

Rank hotspots by **percentage of total wall time or peak allocation** (`cumtime` / `tottime` / retained bytes). Only optimize components representing meaningful wall-time share (`>= 10%` of total) and diagnose the true bottleneck class:

- **Algorithmic / CPU**: Accidental $O(N^2)$ membership checks (`x in list` → `set`), repeated regex compilation inside loops, redundant JSON/date parsing, unmemoized recomputation, Python loop vs. vectorized/built-in operations.
- **Memory & GC Pressure**: Holding entire files/streams in RAM instead of streaming/generators, string concatenation in loops (`+=` vs `"".join()`), unbounded caches (`@lru_cache(maxsize=None)` leaking memory), circular references or retained closures.
- **I/O & Concurrency**: Sequential network/DB calls inside loops (batching, connection pooling, `asyncio.gather` with `Semaphore` bound), blocking I/O inside an async event loop, unbuffered tiny file writes.

### Step 3 — Verify Functional Equivalence + After-Measurements

After implementing the optimization:

1. **Functional parity check**: Confirm existing tests + exact output equality (`baseline_output == optimized_output`) pass 100%.
2. **Re-run the exact same benchmark harness** under identical input size and warmup settings.
3. **Never cherry-pick a single lucky run** — report median, p95, peak memory, and exact speedup factor (`before / after`) from actual measured output. If an optimization does not beat baseline cleanly, revert it.

## Strict Output Contract

```markdown
## Profiling Findings (Baseline)
- **Workload:** Exact input size, iterations, environment.
- **Top Hotspots:** Exact function names and measured share from profiler output.

## Optimizations Applied
1. `file.py:line` — Root cause, complexity change (e.g., O(N^2) -> O(N)), and exact code change.

## Measured Before vs. After
| Metric | Baseline | Optimized | Change |
| :--- | ---: | ---: | ---: |
| Median latency (ms) | ... | ... | ... |
| p95 latency (ms) | ... | ... | ... |
| Peak memory (MB) | ... | ... | ... |

## Functional Parity
- Exact test / output-equality command and PASS result.
```
