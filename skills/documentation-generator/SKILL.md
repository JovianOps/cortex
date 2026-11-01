---
name: documentation-generator
description: Automated documentation generation from code and specs with validation.
version: 0.1.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [documentation, generation, markdown, api-docs, validation]
    related_skills: [api-development, python-coding-assistant]
---
# Documentation Generator Skill

Automated documentation generation from code and specifications with validation.

## When to Use
- Generate API documentation from code
- Create README from codebase
- Generate architecture diagrams
- Create changelogs

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
- Validation against actual code