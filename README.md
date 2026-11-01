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

```bash
# Install a single skill
hermes skills install JovianOps/cortex/skills/academic-assistant

# Or add the entire tap
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/skills/academic-assistant
```

## Requirements

- Hermes Agent installed
- PowerShell 5.1+ / PowerShell 7+
- For college-report-card: PowerShell 5.1+, Python (optional for PDF export)

## License

MIT — see [LICENSE](LICENSE)