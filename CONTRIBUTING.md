# Contributing to Cortex

Thank you for contributing to the **Cortex** skills collection for Hermes Agent! This guide explains how to propose, author, validate, and submit a skill.

## Adding a New Skill

1. **Define the skill scope**
   Decide what concrete, repeatable workflow the skill solves (for example: coding, testing, documentation, security, DevOps, or academic tooling) and whether it belongs in `skills/` (core) or `premium-skills/` (extended).

2. **Create the skill directory**
   Add a kebab-case folder matching the skill's `name` field containing a `SKILL.md` file:

   ```text
   skills/<skill-name>/
   └── SKILL.md
   ```

   Or for extended engineering skills:

   ```text
   premium-skills/<skill-name>/
   └── SKILL.md
   ```

3. **Follow the authoring standards**
   - Include YAML frontmatter with all required fields (`name`, `description`, `version`, `author`, `license`, `platforms`).
   - Keep `name` identical to the parent directory name.
   - Keep `description` concise (ideally `<= 60` characters), one sentence, ending with a period.
   - Include both required Markdown headings: `## When to Use` and `## How to Run`.
   - Credit the human author first (for example: `Your Name (github-handle), Hermes Agent`).
   - Ensure `platforms` only lists platforms verified against the skill instructions (`linux`, `macos`, `windows`).
   - Verify any entries in `metadata.hermes.related_skills` match real skills in this repository.

4. **Package the ZIP distribution**
   Every skill in `skills/` and `premium-skills/` must have a matching archive in `zips/` or `premium-zips/`:

   ```bash
   python scripts/package_skills.py
   ```

5. **Run all local validation checks**
   Ensure skill metadata, required sections, YAML files, and ZIP archives all pass before opening a PR:

   ```bash
   npm test
   python scripts/validate_yaml.py
   ```

6. **Update catalog references**
   Add your new skill to the skill tables and batch install commands in [`README.md`](README.md) and to the `SKILLS` list in [`index.html`](index.html).

7. **Open a pull request**
   Submit a PR with a clear description, clean commit history, and passing CI checks.

## Frontmatter Reference

| Field | Required | Format / Constraints |
| :--- | :---: | :--- |
| `name` | Yes | Kebab-case string matching the skill folder name |
| `description` | Yes | Single sentence ending with a period (target `<= 60` chars) |
| `version` | Yes | SemVer string (e.g., `0.1.0`) |
| `author` | Yes | `Your Name (github-handle), Hermes Agent` |
| `license` | Yes | SPDX identifier (e.g., `MIT`) |
| `platforms` | Yes | Subset of `[linux, macos, windows]` |
| `metadata.hermes.tags` | Recommended | List of lowercase topic tags |
| `metadata.hermes.related_skills` | Optional | List of related in-repo skill slugs |

## Skill Template

````markdown
---
name: skill-name
description: One-sentence capability statement under 60 chars.
version: 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tag1, tag2]
    related_skills: [academic-assistant]
---

# Skill Name

Brief overview of what this skill does and how it enforces deterministic outputs.

## When to Use

- Scenario one where this skill helps
- Scenario two where this skill helps

## How to Run

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/skill-name --yes
```
````

## Code & Content Standards

- **Hermes tools first:** Prefer Hermes built-in tools (`read_file`, `write_file`, `patch`, `search_files`) over raw shell commands inside skill instructions.
- **Deterministic outputs:** Include concrete validation steps and anti-hallucination checks wherever possible.
- **PowerShell:** Target `#Requires -Version 5.1` when providing Windows scripts.
- **Python:** Use type hints and keep helper scripts clean with `ruff` and `mypy`.
- **Markdown:** Follow [`.markdownlint.json`](.markdownlint.json) rules.

## Reporting Issues

Please open a [GitHub Issue](https://github.com/JovianOps/cortex/issues) using the issue templates and include:

- Skill name and collection (`skills/` or `premium-skills/`)
- Steps to reproduce
- Expected vs. actual behavior
- Operating system, shell, and Hermes version (`hermes --version`)
