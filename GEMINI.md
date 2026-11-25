# Cortex Skills Extension for Gemini CLI (`v3.0.0`)

This extension provides **36 deterministic v3.0.0 Agent Skills** organized into two collections:

- **Core Skills (`skills/<slug>/SKILL.md`)** (10): `academic-assistant`, `anti-hallucination`, `blender-3d-modeling`, `code-review-assistant`, `college-report-card`, `documentation-generator`, `memory-manager`, `python-coding-assistant`, `testing-automation`, `web-scraper`.
- **Extended Engineering Skills (`premium-skills/<slug>/SKILL.md`)** (26): `accessibility-auditor`, `api-designer`, `architecture-decision-records`, `chaos-resilience-engineer`, `code-migration`, `db-optimizer`, `devops-pipeline`, `docker-generator`, `finops-cost-optimizer`, `git-history-surgeon`, `go-backend-engineer`, `graphql-architect`, `incident-response`, `kubernetes-architect`, `llm-security-auditor`, `observability-setup`, `performance-profiler`, `privacy-compliance-auditor`, `refactoring-assistant`, `release-engineering`, `rust-systems-engineer`, `security-auditor`, `supply-chain-sbom`, `terraform-generator`, `typescript-architect`, `unit-test-generator`.

## Bundled Deterministic Helper Scripts (36 Tools — 100% Coverage)

Every skill ships a runnable zero-dependency Python verifier inside its skill folder, for example:
- `skills/college-report-card/scripts/grade_calc.py`
- `skills/memory-manager/scripts/memory_store.py`
- `premium-skills/accessibility-auditor/scripts/a11y_scan.py`
- `premium-skills/kubernetes-architect/scripts/lint_k8s.py`
- `premium-skills/security-auditor/scripts/secret_scan.py`
- `premium-skills/terraform-generator/scripts/lint_terraform.py`

## Role Packs, Runtime Engines & Unified CLI (`v3.0.0`)

Install one of the 10 curated role packs (`fullstack`, `devops-sre`, `cloud-native`, `ai-red-team`, `polyglot-systems`, `platform-architecture`, `security-hardening`, `python-pro`, `academic`, `clean-migration`) or use the runtime:
- `python scripts/cortex.py detect` / `doctor` / `packs` / `search --has-script`
- `python scripts/cortex.py install --agent gemini-cli --pack fullstack`
- `python scripts/cortex.py compile --target gemini --pack cloud-native`
- `python scripts/cortex.py scan . --fail-on high`
- `python scripts/cortex.py graph --format mermaid`
- `python scripts/cortex.py bundle --pack cloud-native --out dist/cortex.zip`
- `python scripts/cortex.py guard check`

## How to Use

1. Match the user's request against the relevant skill's `SKILL.md` (`skills/<slug>/SKILL.md` or `premium-skills/<slug>/SKILL.md`).
2. Read the full `SKILL.md` before responding and obey its stop gates, verification checks, and output contract verbatim.
3. For standalone Gemini CLI skill discovery without the extension wrapper, install skills into `~/.gemini/skills/<slug>/SKILL.md` or `.gemini/skills/<slug>/SKILL.md` via `npx skills add JovianOps/cortex -a gemini-cli` or `python scripts/install_skills.py --agent gemini-cli --remote`.
