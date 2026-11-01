---
name: blender-3d-modeling
description: Blender 3D modeling guidance with validation checks and step-by-step workflows.
version: 0.1.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [3d-modeling, blender, modeling, validation]
    related_skills: [academic-assistant]
---
# Blender 3D Modeling Skill

3D modeling guidance with validation checks and step-by-step workflows.

## When to Use
- Learn 3D modeling workflows
- Validate model integrity
- Export format verification
- Step-by-step modeling guidance

## Prerequisites
- Blender installed (v3.0+)
- Basic Blender navigation knowledge

## How to Run
```bash
hermes skills install owner/repo/skills/blender-3d-modeling
hermes chat -q "Guide me through creating a low-poly chair in Blender"
```

## Workflows
| Workflow | Description |
|----------|-------------|
| `low-poly-modeling` | Low-poly modeling workflow |
| `hard-surface` | Hard surface modeling |
| `organic-modeling` | Organic modeling |
| `uv-unwrapping` | UV unwrapping workflow |
| `export-validation` | Export format validation |

## Validation Checks
- Mesh integrity (non-manifold edges, duplicate vertices)
- UV overlap detection
- Scale/transform application
- Naming conventions
- Export format validation

## Usage Examples
- "Guide me through creating a low-poly chair"
- "Validate my model for 3D printing"
- "Help me UV unwrap a character"