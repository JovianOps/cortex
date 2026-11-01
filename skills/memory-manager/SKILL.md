---
name: memory-manager
description: Persistent memory and context management across sessions with anti-forgetting measures.
version: 0.1.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, context, persistence, anti-forgetting]
    related_skills: [academic-assistant]
---
# Memory Manager Skill

Persistent memory and context management across sessions with anti-forgetting measures.

## When to Use
- Maintain context across sessions
- Prevent AI from forgetting task state
- Persistent context across restarts
- Cross-session memory

## How to Run
```bash
hermes skills install owner/repo/skills/memory-manager
hermes chat -q "Save my current project context and restore it next session"
```

## Features
- Persistent context.json across sessions
- Task state serialization
- Key-value memory store
- Session resumption
- Auto-save on context change
- Cross-session memory queries

## Commands
| Command | Description |
|---------|-------------|
| `save-context` | Save current context to disk |
| `load-context` | Restore previous context |
| `query-memory` | Query stored memory |
| `clear-memory` | Clear specific/all memory |
| `list-memories` | List all stored memories |

## Anti-Forgetting Measures
- Auto-save on context change
- Periodic auto-save timer
- Session resumption with `--continue`
- Cross-session entity tracking
- Task state serialization