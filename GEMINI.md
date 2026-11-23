# Cortex Skills Extension for Gemini CLI

This extension provides **20 deterministic v0.2.0 Agent Skills** organized into two collections:

- **Core Skills (`skills/<slug>/SKILL.md`)**: `academic-assistant`, `anti-hallucination`, `blender-3d-modeling`, `code-review-assistant`, `college-report-card`, `documentation-generator`, `memory-manager`, `python-coding-assistant`, `testing-automation`, `web-scraper`.
- **Extended Engineering Skills (`premium-skills/<slug>/SKILL.md`)**: `api-designer`, `code-migration`, `db-optimizer`, `devops-pipeline`, `docker-generator`, `performance-profiler`, `refactoring-assistant`, `security-auditor`, `terraform-generator`, `unit-test-generator`.

## How to Use

1. Match the user's request against the relevant skill's `SKILL.md` (`skills/<slug>/SKILL.md` or `premium-skills/<slug>/SKILL.md`).
2. Read the full `SKILL.md` before responding and obey its stop gates, verification checks, and output contract verbatim.
3. For standalone Gemini CLI skill discovery without the extension wrapper, install individual skills into `~/.gemini/skills/<slug>/SKILL.md` or `.gemini/skills/<slug>/SKILL.md` via `npx skills add JovianOps/cortex -a gemini-cli` or `python scripts/install_skills.py --agent gemini-cli`.
