---
name: db-optimizer
description: Analyze and optimize SQL queries, suggest indexes, and detect performance bottlenecks.
version: 0.1.0
author: Athalla Jovian Maharsa
license: MIT
platforms: [linux, macos, windows]
---

# Database Optimizer

Analyze SQL queries, detect performance issues, and suggest optimizations.

## When to Use
- Slow queries need optimization
- Missing indexes causing table scans
- N+1 query problems in ORMs
- Database schema review for performance
- Query plan analysis

## How to Run
```bash
hermes skills install JovianOps/cortex/premium-skills/db-optimizer
hermes chat -q "Optimize this query: SELECT * FROM orders WHERE status = 'pending'"
```

## Core Capabilities
1. **Query analysis** — Parse EXPLAIN plans, identify bottlenecks
2. **Index suggestions** — Recommend indexes based on query patterns
4. **N+1 detection** — Find ORM lazy-loading problems
4. **Schema review** — Suggest normalization/denormalization improvements
5. **Rewrite suggestions** — Provide optimized query alternatives

## Anti-Hallucination Measures
- Parse actual query plans, not guesses
- No invented index recommendations
- Deterministic analysis of query structure
- Explicit warnings when query plan is unavailable