---
name: database-manager
description: Database operations with migrations, queries, and validation.
version: 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [database, sql, migrations, validation]
    related_skills: [python-coding-assistant, api-development]
---
# Database Manager Skill

Database operations with migrations, queries, and validation.

## When to Use
- Database schema management
- Query optimization
- Migration management
- Data validation

## Prerequisites
- SQLAlchemy/Alembic or similar

## How to Run
```bash
hermes skills install owner/repo/skills/database-manager
hermes chat -q "Create migration for user table with validation"
```

## Features
- Migration management
- Query building with validation
- Schema validation
- Backup/restore utilities