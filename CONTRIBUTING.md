# Contributing to Cortex

Thank you for contributing to the Cortex skills collection!

## Adding a New Skill

1. **Brainstorming what the skill will be
i mean brainstorming is like you find what new skills you want to make category coding uhh i mean anything?

3. **Create the skill directory:**
   ```
   skills/<category>/<skill-name>/
   ├── SKILL.md          # Required: skill definition with frontmatter

   ```

4. **Follow the skill authoring standards:**
   - Frontmatter with all required fields
   - Description ≤ 60 chars, one sentence, ends with period
   - Author credits human first: `Name (github-handle), Hermes Agent`
   - `platforms:` audited against actual code
   - All `related_skills` exist in-repo

5. **Add tests** at `tests/skills/test_<name>_skill.py`

6. **Regenerate docs:** `python website/scripts/generate-skill-docs.py`

7. **Submit PR** with clean commit history

## Skill Template

```markdown
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
    related_skills: [other-skill]
---
```

## Code Style

- Use Hermes tools (`read_file`, `write_file`, `patch`, `search_files`) not raw shell
- PowerShell: `#Requires -Version 5.1`
- Python: type hints, `ruff`/`mypy` clean
- Deterministic outputs, no hallucination

## Reporting Issues

Use GitHub Issues with:
- Skill name
- Steps to reproduce
- Expected vs actual behavior
- Hermes version (`hermes --version`)
