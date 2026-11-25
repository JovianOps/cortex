# Cortex Agent Skills Index

This repository ships **36 modular, deterministic v3.0.0 Agent Skills** following the open `SKILL.md` standard, with bundled deterministic helper scripts and SHA-256 integrity verification (`checksums.json`).

Runtime engines: `cortex mcp` (11 tools / 39 resources), `cortex studio` (7 panels / 12 endpoints), `cortex compile`, `cortex scan`, `cortex graph`, `cortex bundle`, and the `cortex guard` release gate.

## Core Skills (`skills/`)

| Skill | Path | Purpose | Bundled Script |
| :--- | :--- | :--- | :--- |
| `academic-assistant` | `skills/academic-assistant/SKILL.md` | Orchestrate grading, coding, and 3D academic workflows. | `scripts/citation_check.py` |
| `anti-hallucination` | `skills/anti-hallucination/SKILL.md` | Verify AI claims and code with deterministic audit gates. | `scripts/verify_claims.py` |
| `blender-3d-modeling` | `skills/blender-3d-modeling/SKILL.md` | Build and validate Blender 3D meshes with bmesh checks. | `scripts/bmesh_check.py` |
| `code-review-assistant` | `skills/code-review-assistant/SKILL.md` | Run evidence-backed code reviews with severity rubrics. | `scripts/diff_review.py` |
| `college-report-card` | `skills/college-report-card/SKILL.md` | Generate exact report cards using Decimal grade scripts. | `scripts/grade_calc.py` |
| `documentation-generator` | `skills/documentation-generator/SKILL.md` | Generate code-verified docs, API specs, and diagrams. | `scripts/check_docs.py` |
| `memory-manager` | `skills/memory-manager/SKILL.md` | Persist versioned session memory with staleness checks. | `scripts/memory_store.py` |
| `python-coding-assistant` | `skills/python-coding-assistant/SKILL.md` | Write typed, linted, and tested Python code reliably. | `scripts/check_python_ast.py` |
| `testing-automation` | `skills/testing-automation/SKILL.md` | Build branch-tested pytest suites with CI coverage gates. | `scripts/check_test_coverage_map.py` |
| `web-scraper` | `skills/web-scraper/SKILL.md` | Scrape web data politely with strict schema validation. | `scripts/check_robots.py` |

## Extended Engineering Skills (`premium-skills/`)

| Skill | Path | Purpose | Bundled Script |
| :--- | :--- | :--- | :--- |
| `accessibility-auditor` | `premium-skills/accessibility-auditor/SKILL.md` | Audit HTML/UI for WCAG 2.2 AA flaws with exact code fixes. | `scripts/a11y_scan.py` |
| `api-designer` | `premium-skills/api-designer/SKILL.md` | Design strict OpenAPI and GraphQL specs with contracts. | `scripts/lint_openapi.py` |
| `architecture-decision-records` | `premium-skills/architecture-decision-records/SKILL.md` | Author and validate MADR Architecture Decision Records. | `scripts/check_adrs.py` |
| `chaos-resilience-engineer` | `premium-skills/chaos-resilience-engineer/SKILL.md` | Design fault-tolerant timeouts, retries, and game days. | `scripts/audit_resilience.py` |
| `code-migration` | `premium-skills/code-migration/SKILL.md` | Migrate languages and frameworks with parity tests. | `scripts/migration_inventory.py` |
| `db-optimizer` | `premium-skills/db-optimizer/SKILL.md` | Optimize SQL queries and indexes using EXPLAIN plans. | `scripts/lint_sql.py` |
| `devops-pipeline` | `premium-skills/devops-pipeline/SKILL.md` | Build hardened, SHA-pinned CI/CD pipelines across tools. | `scripts/lint_actions.py` |
| `docker-generator` | `premium-skills/docker-generator/SKILL.md` | Generate hardened multi-stage Docker and Compose setups. | `scripts/lint_dockerfile.py` |
| `finops-cost-optimizer` | `premium-skills/finops-cost-optimizer/SKILL.md` | Audit Terraform and K8s configs for cloud cost waste. | `scripts/audit_finops.py` |
| `git-history-surgeon` | `premium-skills/git-history-surgeon/SKILL.md` | Execute safe Git rebases, bisects, and repo hygiene audits. | `scripts/audit_git_hygiene.py` |
| `go-backend-engineer` | `premium-skills/go-backend-engineer/SKILL.md` | Build production Go services with context and timeouts. | `scripts/lint_go.py` |
| `graphql-architect` | `premium-skills/graphql-architect/SKILL.md` | Design schema-first GraphQL APIs with Relay pagination. | `scripts/lint_graphql.py` |
| `incident-response` | `premium-skills/incident-response/SKILL.md` | Triage outages, contain blast radius, and write postmortems. | `scripts/incident_timeline.py` |
| `kubernetes-architect` | `premium-skills/kubernetes-architect/SKILL.md` | Design hardened Kubernetes and Helm workloads with probes. | `scripts/lint_k8s.py` |
| `llm-security-auditor` | `premium-skills/llm-security-auditor/SKILL.md` | Audit AI agents and prompts against OWASP LLM Top 10. | `scripts/audit_prompts.py` |
| `observability-setup` | `premium-skills/observability-setup/SKILL.md` | Add structured logs, OTel traces, SLOs, and clean alerts. | `scripts/check_slo.py` |
| `performance-profiler` | `premium-skills/performance-profiler/SKILL.md` | Profile CPU, memory, and I/O with measured benchmarks. | `scripts/bench_compare.py` |
| `privacy-compliance-auditor` | `premium-skills/privacy-compliance-auditor/SKILL.md` | Audit code and logs for GDPR, CCPA, and raw PII leaks. | `scripts/scan_pii.py` |
| `refactoring-assistant` | `premium-skills/refactoring-assistant/SKILL.md` | Refactor complex code safely with parity verification. | `scripts/complexity_scan.py` |
| `release-engineering` | `premium-skills/release-engineering/SKILL.md` | Cut SemVer releases with changelogs, checksums, and gates. | `scripts/semver_bump.py` |
| `rust-systems-engineer` | `premium-skills/rust-systems-engineer/SKILL.md` | Write safe, idiomatic Rust with verified unsafe invariants. | `scripts/lint_rust.py` |
| `security-auditor` | `premium-skills/security-auditor/SKILL.md` | Audit code for OWASP flaws, secrets, and CWE findings. | `scripts/secret_scan.py` |
| `supply-chain-sbom` | `premium-skills/supply-chain-sbom/SKILL.md` | Audit dependencies, lockfiles, SLSA provenance, and SBOMs. | `scripts/audit_sbom.py` |
| `terraform-generator` | `premium-skills/terraform-generator/SKILL.md` | Generate hardened, validated Terraform and OpenTofu IaC. | `scripts/lint_terraform.py` |
| `typescript-architect` | `premium-skills/typescript-architect/SKILL.md` | Build strict TypeScript and React apps with runtime safety. | `scripts/lint_ts.py` |
| `unit-test-generator` | `premium-skills/unit-test-generator/SKILL.md` | Generate branch-covering unit tests from source code. | `scripts/test_skeleton.py` |

## Operating Rules for Agents Working in This Repository

1. Treat `skills/<slug>/` and `premium-skills/<slug>/` as the single source of truth.
2. After editing any `SKILL.md` or bundled script, regenerate ZIP archives and `checksums.json` with `python scripts/cortex.py package` and verify everything with `python scripts/cortex.py doctor && npm test`.
3. Keep all 9 platform manifests (`.claude-plugin/`, `.agents/plugins/`, `.cursor-plugin/`, `plugin.json`, `gemini-extension.json`) and `packs.json` synchronized with all 36 skills.
4. Use `python scripts/cortex.py new <slug> --with-script` to scaffold new 100/100 audit-ready skills.
5. Before release, run `python scripts/cortex.py guard check` (see `docs/guard-guide.md`).
