# Cortex Skills Extension for Gemini CLI (`v0.4.0`)

This extension provides **24 deterministic v0.4.0 Agent Skills** organized into two collections:

- **Core Skills (`skills/<slug>/SKILL.md`)**: `academic-assistant`, `anti-hallucination`, `blender-3d-modeling`, `code-review-assistant`, `college-report-card`, `documentation-generator`, `memory-manager`, `python-coding-assistant`, `testing-automation`, `web-scraper`.
- **Extended Engineering Skills (`premium-skills/<slug>/SKILL.md`)**: `accessibility-auditor`, `api-designer`, `code-migration`, `db-optimizer`, `devops-pipeline`, `docker-generator`, `incident-response`, `observability-setup`, `performance-profiler`, `refactoring-assistant`, `release-engineering`, `security-auditor`, `terraform-generator`, `unit-test-generator`.

## Bundled Deterministic Helper Scripts (10 Tools)

Ten skills ship runnable zero-dependency Python scripts inside their skill folder:
- `skills/college-report-card/scripts/grade_calc.py`
- `skills/blender-3d-modeling/scripts/bmesh_check.py`
- `skills/memory-manager/scripts/memory_store.py`
- `skills/documentation-generator/scripts/check_docs.py`
- `premium-skills/accessibility-auditor/scripts/a11y_scan.py`
- `premium-skills/api-designer/scripts/lint_openapi.py`
- `premium-skills/docker-generator/scripts/lint_dockerfile.py`
- `premium-skills/devops-pipeline/scripts/lint_actions.py`
- `premium-skills/release-engineering/scripts/semver_bump.py`
- `premium-skills/security-auditor/scripts/secret_scan.py`

## Role-Based Skill Packs & Unified CLI (`v0.4.0`)

Install curated 6-skill role packs (`fullstack`, `devops-sre`, `security-hardening`, `python-pro`, `academic`, `clean-migration`) or run diagnostics via `python scripts/cortex.py`:
- `python scripts/cortex.py detect` / `doctor` / `packs` / `search --has-script`
- `python scripts/cortex.py install --agent gemini-cli --pack fullstack`

## How to Use

1. Match the user's request against the relevant skill's `SKILL.md` (`skills/<slug>/SKILL.md` or `premium-skills/<slug>/SKILL.md`).
2. Read the full `SKILL.md` before responding and obey its stop gates, verification checks, and output contract verbatim.
3. For standalone Gemini CLI skill discovery without the extension wrapper, install skills into `~/.gemini/skills/<slug>/SKILL.md` or `.gemini/skills/<slug>/SKILL.md` via `npx skills add JovianOps/cortex -a gemini-cli` or `python scripts/install_skills.py --agent gemini-cli --remote`.
