# Contributing to Cortex

Thank you for contributing to **Cortex**! Every skill, helper script, manifest, and workflow in this repository is built to be deterministic, zero-dependency, and cryptographically verifiable.

## Quick Setup

```bash
git clone https://github.com/JovianOps/cortex.git
cd cortex
python3 -m pip install pyyaml ruff
python3 scripts/cortex.py doctor
```

If you use **Visual Studio Code**, open the repo and run **Tasks: Run Task → Cortex: Run Full Validation & Tests** (configured in `.vscode/tasks.json`).

## Adding a New Skill

1. Scaffold a 100/100 audit-ready skill with a bundled helper script:
   ```bash
   python3 scripts/cortex.py new my-skill-name --tier extended --with-script
   ```
2. Complete `SKILL.md` (frontmatter, clear trigger criteria, numbered workflow, explicit stop gates, and output contract) and implement your zero-dependency Python 3 helper script under `scripts/`.
3. Add a 100-point paired A/B evaluation rubric in `evals/skill_evals.json`.
4. Add unit tests for the bundled script in `tests/test_cortex_tooling.py`.
5. Register the skill in all 9 multi-agent manifests (and `packs.json` if part of a role pack), then rebuild deterministic ZIPs and checksums:
   ```bash
   python3 scripts/package_skills.py
   ```

## Required Pre-PR Verification Gate

All checks below run in CI across Python 3.12/3.13 and Linux/macOS/Windows:

```bash
python3 -m compileall -q -f scripts skills premium-skills tests
ruff check --select E9,F scripts skills premium-skills tests
python3 scripts/validate_yaml.py
python3 scripts/validate_skills.py
python3 scripts/package_skills.py --check
python3 scripts/validate_manifests.py
python3 scripts/eval_skills.py
python3 scripts/verify_site.py
python3 skills/documentation-generator/scripts/check_docs.py README.md
python3 premium-skills/devops-pipeline/scripts/lint_actions.py .github/workflows
python3 -m unittest discover -s tests -v
```

## Cutting a Release

Use the atomic release script so all 36 skills, 9 manifests, ZIPs, `checksums.json`, CLI constants, and `index.html` stay in lockstep:

```bash
python3 scripts/bump_version.py 1.1.0
```
