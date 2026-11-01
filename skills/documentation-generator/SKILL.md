---
name: documentation-generator
description: Automated documentation generation from code and specs.
version: 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [documentation, generation, markdown, api-docs]
    related_skills: [api-development, python-coding-assistant]
---
# Documentation Generator Skill

Automated documentation generation from code and specifications.

## When to Use
- API documentation from code
- README generation
- Architecture diagrams
- Changelog generation

## Prerequisites
- Python with mkdocs/sphinx

## How to Run
```bash
hermes skills install owner/repo/skills/documentation-generator
hermes chat -q "Generate API docs from my FastAPI code"
```

## Features
- Auto-generate from docstrings
- OpenAPI/Swagger export
- Mermaid diagram generation
- Version-aware docs