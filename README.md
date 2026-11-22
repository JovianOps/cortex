# Cortex

**10 Hermes Skills** — Academic assistant, college report cards, anti-hallucination, 3D modeling, code review, documentation, memory management, testing automation, web scraping, and Blender 3D modeling.

## Skills

| Skill | Description |
|-------|-------------|
| [academic-assistant](skills/academic-assistant) | Core academic assistant: report cards, coding, 3D modeling, anti-hallucination, persistent memory |
| [college-report-card](skills/college-report-card) | Deterministic report card generator from structured grade data |
| [anti-hallucination](skills/anti-hallucination) | Anti-hallucination measures and validation |
| [blender-3d-modeling](skills/blender-3d-modeling) | Blender 3D modeling guidance with validation |
| [code-review-assistant](skills/code-review-assistant) | Automated code review with deterministic checks |
| [documentation-generator](skills/documentation-generator) | Automated documentation generation |
| [memory-manager](skills/memory-manager) | Persistent memory management across sessions |
| [python-coding-assistant](skills/python-coding-assistant) | Python coding with validation and type hints |
| [testing-automation](skills/testing-automation) | Test automation with pytest and CI/CD |
| [web-scraper](skills/web-scraper) | Web scraping with validation and rate limiting |

## Installation

Cortex contains **10 core skills** in `skills/` and **10 premium/extended skills** in `premium-skills/`. Install the core collection, the premium collection, or one skill at a time. Run these commands in a Bash shell or PowerShell; no `jq` or `xargs` is needed.

### Install all 10 core skills

Bash:

```bash
hermes skills tap add JovianOps/cortex
for skill in academic-assistant college-report-card anti-hallucination blender-3d-modeling code-review-assistant documentation-generator memory-manager python-coding-assistant testing-automation web-scraper; do
  hermes skills install "JovianOps/cortex/skills/$skill" --yes
done
```

PowerShell:

```powershell
hermes skills tap add JovianOps/cortex
$skills = @('academic-assistant', 'college-report-card', 'anti-hallucination', 'blender-3d-modeling', 'code-review-assistant', 'documentation-generator', 'memory-manager', 'python-coding-assistant', 'testing-automation', 'web-scraper')
foreach ($skill in $skills) {
    hermes skills install "JovianOps/cortex/skills/$skill" --yes
}
```

### Install all 10 premium/extended skills

Bash:

```bash
hermes skills tap add JovianOps/cortex
for skill in api-designer code-migration db-optimizer devops-pipeline docker-generator performance-profiler refactoring-assistant security-auditor terraform-generator unit-test-generator; do
  hermes skills install "JovianOps/cortex/premium-skills/$skill" --yes
done
```

PowerShell:

```powershell
hermes skills tap add JovianOps/cortex
$skills = @('api-designer', 'code-migration', 'db-optimizer', 'devops-pipeline', 'docker-generator', 'performance-profiler', 'refactoring-assistant', 'security-auditor', 'terraform-generator', 'unit-test-generator')
foreach ($skill in $skills) {
    hermes skills install "JovianOps/cortex/premium-skills/$skill" --yes
}
```

### Install one skill

Add the tap once, then use the skill's name and collection path. For example, install `academic-assistant`:

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/academic-assistant --yes
```

PowerShell uses the same commands. For a premium skill, use `JovianOps/cortex/premium-skills/<skill-name>`.

## Requirements

- Hermes Agent installed
- PowerShell 5.1+ / PowerShell 7+
- For college-report-card: PowerShell 5.1+, Python (optional for PDF export)

## License

MIT — see [LICENSE](LICENSE)
