## Summary

<!-- Briefly describe what this pull request adds, updates, or fixes. -->

## Type of Change

- [ ] New skill (`skills/` or `premium-skills/`)
- [ ] Skill update or bug fix
- [ ] Documentation or catalog update (`README.md`, `index.html`, `CONTRIBUTING.md`)
- [ ] Tooling, scripts, or CI improvement

## Checklist

- [ ] `SKILL.md` frontmatter includes all required fields (`name`, `description`, `version`, `author`, `license`, `platforms`)
- [ ] Required sections (`## When to Use` and `## How to Run`) are present
- [ ] Rebuilt ZIP distributions with `python scripts/package_skills.py` (if any `SKILL.md` changed)
- [ ] Verified all checks pass locally (`npm test` and `python scripts/validate_yaml.py`)
- [ ] Updated `README.md` and `index.html` if adding or renaming a skill
