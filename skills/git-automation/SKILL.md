---
name: git-automation
description: Automate common git workflows with smart commits and branch management.
version: 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, automation, version-control]
    related_skills: []
---
# Git Automation Skill

Automate common git workflows with smart commits, branch management, and PR creation.

## When to Use
- Automate repetitive git operations
- Create consistent commit messages
- Manage branches and PRs programmatically

## Prerequisites
- Git installed and configured
- GitHub CLI (gh) for PR operations

## How to Run
```bash
hermes skills install owner/repo/skills/git-automation
hermes chat -q "Create a feature branch and commit changes with conventional commit message"
```

## Commands
| Command | Description |
|---------|-------------|
| `git-auto-commit` | Smart commit with conventional messages |
| `git-branch-cleanup` | Clean up merged branches |
| `git-pr-create` | Create PR with template |
| `git-sync` | Sync fork with upstream |

## Usage Examples
- "Create a feature branch for user-auth and commit changes"
- "Clean up all merged branches"
- "Create a PR for the current branch with conventional commit message"