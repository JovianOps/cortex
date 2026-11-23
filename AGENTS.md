# Cortex Agent Skills Index

This repository ships **20 modular, deterministic v0.2.0 Agent Skills** following the open `SKILL.md` standard. Each skill directory contains a self-contained `SKILL.md` with YAML frontmatter (`name`, `description`, `version`, `license`, `platforms`), trigger/non-trigger boundaries, mandatory verification gates, and strict output contracts.

## Core Skills (`skills/`)

| Skill | Path | Purpose |
| :--- | :--- | :--- |
| `academic-assistant` | `skills/academic-assistant/SKILL.md` | Orchestrate grading, coding, and 3D academic workflows. |
| `anti-hallucination` | `skills/anti-hallucination/SKILL.md` | Verify AI claims and code with deterministic audit gates. |
| `blender-3d-modeling` | `skills/blender-3d-modeling/SKILL.md` | Build and validate Blender 3D meshes with bmesh checks. |
| `code-review-assistant` | `skills/code-review-assistant/SKILL.md` | Run evidence-backed code reviews with severity rubrics. |
| `college-report-card` | `skills/college-report-card/SKILL.md` | Generate exact report cards using Decimal grade scripts. |
| `documentation-generator` | `skills/documentation-generator/SKILL.md` | Generate code-verified docs, API specs, and diagrams. |
| `memory-manager` | `skills/memory-manager/SKILL.md` | Persist versioned session memory with staleness checks. |
| `python-coding-assistant` | `skills/python-coding-assistant/SKILL.md` | Write typed, linted, and tested Python code reliably. |
| `testing-automation` | `skills/testing-automation/SKILL.md` | Build branch-tested pytest suites with CI coverage gates. |
| `web-scraper` | `skills/web-scraper/SKILL.md` | Scrape web data politely with strict schema validation. |

## Extended Engineering Skills (`premium-skills/`)

| Skill | Path | Purpose |
| :--- | :--- | :--- |
| `api-designer` | `premium-skills/api-designer/SKILL.md` | Design strict OpenAPI and GraphQL specs with contracts. |
| `code-migration` | `premium-skills/code-migration/SKILL.md` | Migrate languages and frameworks with parity tests. |
| `db-optimizer` | `premium-skills/db-optimizer/SKILL.md` | Optimize SQL queries and indexes using EXPLAIN plans. |
| `devops-pipeline` | `premium-skills/devops-pipeline/SKILL.md` | Build hardened, SHA-pinned CI/CD pipelines across tools. |
| `docker-generator` | `premium-skills/docker-generator/SKILL.md` | Generate hardened multi-stage Docker and Compose setups. |
| `performance-profiler` | `premium-skills/performance-profiler/SKILL.md` | Profile CPU, memory, and I/O with measured benchmarks. |
| `refactoring-assistant` | `premium-skills/refactoring-assistant/SKILL.md` | Refactor complex code safely with parity verification. |
| `security-auditor` | `premium-skills/security-auditor/SKILL.md` | Audit code for OWASP flaws, secrets, and CWE findings. |
| `terraform-generator` | `premium-skills/terraform-generator/SKILL.md` | Generate hardened, validated Terraform and OpenTofu IaC. |
| `unit-test-generator` | `premium-skills/unit-test-generator/SKILL.md` | Generate branch-covering unit tests from source code. |

## Operating Rules for Agents Working in This Repository

1. Treat `skills/<slug>/SKILL.md` and `premium-skills/<slug>/SKILL.md` as the single source of truth.
2. After editing any `SKILL.md`, regenerate ZIP archives with `python scripts/package_skills.py` and verify parity with `npm test`.
3. Keep all platform manifests (`.claude-plugin/`, `.agents/plugins/`, `.cursor-plugin/`, `plugin.json`, `gemini-extension.json`) in sync with `skills/` and `premium-skills/`.
