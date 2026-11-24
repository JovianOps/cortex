# Cortex Agent Skills Index

This repository ships **24 modular, deterministic v1.0.0 Agent Skills** following the open `SKILL.md` standard, with bundled deterministic helper scripts and SHA-256 integrity verification (`checksums.json`).

## Core Skills (`skills/`)

| Skill | Path | Purpose | Bundled Script |
| :--- | :--- | :--- | :--- |
| `academic-assistant` | `skills/academic-assistant/SKILL.md` | Orchestrate grading, coding, and 3D academic workflows. | — |
| `anti-hallucination` | `skills/anti-hallucination/SKILL.md` | Verify AI claims and code with deterministic audit gates. | — |
| `blender-3d-modeling` | `skills/blender-3d-modeling/SKILL.md` | Build and validate Blender 3D meshes with bmesh checks. | `scripts/bmesh_check.py` |
| `code-review-assistant` | `skills/code-review-assistant/SKILL.md` | Run evidence-backed code reviews with severity rubrics. | — |
| `college-report-card` | `skills/college-report-card/SKILL.md` | Generate exact report cards using Decimal grade scripts. | `scripts/grade_calc.py` |
| `documentation-generator` | `skills/documentation-generator/SKILL.md` | Generate code-verified docs, API specs, and diagrams. | `scripts/check_docs.py` |
| `memory-manager` | `skills/memory-manager/SKILL.md` | Persist versioned session memory with staleness checks. | `scripts/memory_store.py` |
| `python-coding-assistant` | `skills/python-coding-assistant/SKILL.md` | Write typed, linted, and tested Python code reliably. | — |
| `testing-automation` | `skills/testing-automation/SKILL.md` | Build branch-tested pytest suites with CI coverage gates. | — |
| `web-scraper` | `skills/web-scraper/SKILL.md` | Scrape web data politely with strict schema validation. | — |

## Extended Engineering Skills (`premium-skills/`)

| Skill | Path | Purpose | Bundled Script |
| :--- | :--- | :--- | :--- |
| `accessibility-auditor` | `premium-skills/accessibility-auditor/SKILL.md` | Audit HTML/UI for WCAG 2.2 AA flaws with exact code fixes. | `scripts/a11y_scan.py` |
| `api-designer` | `premium-skills/api-designer/SKILL.md` | Design strict OpenAPI and GraphQL specs with contracts. | `scripts/lint_openapi.py` |
| `code-migration` | `premium-skills/code-migration/SKILL.md` | Migrate languages and frameworks with parity tests. | — |
| `db-optimizer` | `premium-skills/db-optimizer/SKILL.md` | Optimize SQL queries and indexes using EXPLAIN plans. | — |
| `devops-pipeline` | `premium-skills/devops-pipeline/SKILL.md` | Build hardened, SHA-pinned CI/CD pipelines across tools. | `scripts/lint_actions.py` |
| `docker-generator` | `premium-skills/docker-generator/SKILL.md` | Generate hardened multi-stage Docker and Compose setups. | `scripts/lint_dockerfile.py` |
| `incident-response` | `premium-skills/incident-response/SKILL.md` | Triage outages, contain blast radius, and write postmortems. | — |
| `observability-setup` | `premium-skills/observability-setup/SKILL.md` | Add structured logs, OTel traces, SLOs, and clean alerts. | — |
| `performance-profiler` | `premium-skills/performance-profiler/SKILL.md` | Profile CPU, memory, and I/O with measured benchmarks. | — |
| `refactoring-assistant` | `premium-skills/refactoring-assistant/SKILL.md` | Refactor complex code safely with parity verification. | — |
| `release-engineering` | `premium-skills/release-engineering/SKILL.md` | Cut SemVer releases with changelogs, checksums, and gates. | `scripts/semver_bump.py` |
| `security-auditor` | `premium-skills/security-auditor/SKILL.md` | Audit code for OWASP flaws, secrets, and CWE findings. | `scripts/secret_scan.py` |
| `terraform-generator` | `premium-skills/terraform-generator/SKILL.md` | Generate hardened, validated Terraform and OpenTofu IaC. | — |
| `unit-test-generator` | `premium-skills/unit-test-generator/SKILL.md` | Generate branch-covering unit tests from source code. | — |

## Operating Rules for Agents Working in This Repository

1. Treat `skills/<slug>/` and `premium-skills/<slug>/` as the single source of truth.
2. After editing any `SKILL.md` or bundled script, regenerate ZIP archives and `checksums.json` with `python scripts/cortex.py package` and verify everything with `python scripts/cortex.py doctor && npm test`.
3. Keep all 7 platform manifests (`.claude-plugin/`, `.agents/plugins/`, `.cursor-plugin/`, `plugin.json`, `gemini-extension.json`) and `packs.json` synchronized with all 24 skills.
4. Use `python scripts/cortex.py new <slug> --with-script` to scaffold new 100/100 audit-ready skills.
