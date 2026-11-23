---
name: db-optimizer
description: Optimize SQL queries and indexes using EXPLAIN plans.
version: 0.2.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [database, sql, performance, indexing, query-optimization]
    related_skills: [performance-profiler, code-review-assistant, security-auditor]
---

# Database Optimizer

Analyze slow SQL queries, ORM access patterns, and schemas using `EXPLAIN` execution plans, composite index design (ESR rule), sargable rewrites, and concrete trade-off analysis.

## When to Use

- Diagnosing slow SQL queries (PostgreSQL, MySQL/MariaDB, SQLite, SQL Server)
- Designing or consolidating composite, partial, or covering indexes
- Eliminating ORM N+1 query storms, deep `OFFSET` pagination bottlenecks, or full table scans
- Reviewing schema migrations for lock safety and query performance

### When Not to Use

- Application-level CPU/memory profiling unrelated to database queries (use `performance-profiler`)

## How to Run

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/db-optimizer --yes
hermes chat -q "Analyze this PostgreSQL EXPLAIN ANALYZE output and optimize the query and indexes"
```

## Mandatory Query Optimization Protocol

### Step 1 — Demand or Inspect Real Context (Never Guess Blindly)

Before recommending indexes or rewrites, inspect or request:

1. **Database engine & version** (PostgreSQL 16 vs MySQL 8 vs SQLite behave differently on CTE materialization, `INCLUDE`, partial indexes, and `CONCURRENTLY`).
2. **Table schema, existing indexes, and approximate row counts / cardinality**.
3. **Actual execution plan**:
   - PostgreSQL: `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <query>;`
   - MySQL 8+: `EXPLAIN ANALYZE <query>;`
   - SQLite: `EXPLAIN QUERY PLAN <query>;`
4. If no `EXPLAIN` plan or schema is provided, **explicitly label assumptions as `[ASSUMED — VERIFY WITH EXPLAIN ANALYZE]`** and provide the exact `EXPLAIN` command the user should run first.

### Step 2 — Execution Plan & Query Anti-Pattern Audit

Systematically inspect the query and plan for these high-impact bottlenecks:

1. **Row-Estimate Skew**: Compare `estimated rows` vs `actual rows` (10x+ mismatch indicates stale stats → `ANALYZE table`, correlated columns → `CREATE STATISTICS`, or skewed distribution).
2. **Non-Sargable Predicates** (prevent index usage):
   - Functions on indexed columns: `WHERE LOWER(email) = 'a@b.com'` → expression index or `citext`; `WHERE DATE(created_at) = '2026-01-01'` → half-open range `created_at >= '2026-01-01' AND created_at < '2026-01-02'`.
   - Leading wildcard `LIKE '%foo'` → trigram (`pg_trgm` GIN) or full-text (`tsvector`) index.
   - Implicit type mismatch (`VARCHAR` column compared to integer literal).
3. **ESR Composite Index Ordering Rule**:
   - Order composite B-tree index columns strictly as: **(E)quality predicates → (S)ort (`ORDER BY`) columns → (R)ange predicates (`>`, `<`, `BETWEEN`)**.
   - Use **partial indexes** (`WHERE status = 'pending'`) when queries target a small hot subset of rows.
   - Use **covering indexes** (`INCLUDE (col1, col2)` in PostgreSQL) only when Index-Only Scans justify the extra write/storage cost.
4. **Pagination & Aggregation Traps**:
   - Replace deep `OFFSET N LIMIT K` with **keyset (seek) pagination**: `WHERE (created_at, id) < ($1, $2) ORDER BY created_at DESC, id DESC LIMIT K`.
   - Replace `SELECT *` with explicit needed columns to cut I/O and enable covering indexes.
   - Replace `NOT IN (SELECT nullable_col ...)` with `NOT EXISTS (...)` (fixes both NULL-logic bugs and anti-join planning).
5. **ORM N+1 Queries**:
   - Detect loops firing per-row queries and replace with eager loading (`selectinload`/`joinedload` in SQLAlchemy, `include` in Prisma, `prefetch_related` in Django) or a single batched `JOIN` / `WHERE id = ANY($1)`.

### Step 3 — Production Migration & Trade-Off Safety Check

Every index recommendation MUST state:

- **Exact DDL** with online-safe syntax (e.g., PostgreSQL `CREATE INDEX CONCURRENTLY ...` so production writes aren't blocked).
- **Redundancy check**: Whether the new composite index makes an existing single-column prefix index redundant.
- **Write amplification & storage trade-off**: Impact on `INSERT`/`UPDATE`/HOT updates and vacuum overhead.

## Output Contract

```markdown
## Bottleneck Diagnosis
- Root cause(s) traced directly to plan operators (`Seq Scan`, `Sort`, `Nested Loop`, buffer hits/reads, or query structure).

## Optimized SQL Rewrite
<Exact semantically equivalent SQL — verify NULL, duplicate, and ordering parity>

## Recommended Indexes (ESR-Ordered)
<Exact online-safe DDL + justification + redundancy/write-cost trade-offs>

## Verification Commands
<Exact EXPLAIN (ANALYZE, BUFFERS) command and target metrics to confirm improvement>
```
