---
name: docker-manager
description: Manage Docker containers, images, and compose files with smart automation.
version: 0.1.0
author: Your Name (github-handle), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docker, container, devops]
    related_skills: []
---
# Docker Manager Skill

Manage Docker containers, images, and compose files with smart automation.

## When to Use
- Manage container lifecycle
- Build and push images
- Manage docker-compose stacks

## Prerequisites
- Docker installed and running
- Docker Compose v2+

## How to Run
```bash
hermes skills install owner/repo/skills/docker-manager
hermes chat -q "Build and push the Docker image for the API service"
```

## Commands
| Command | Description |
|---------|-------------|
| `docker-build` | Build images with cache optimization |
| `docker-compose-up` | Start compose stack with health checks |
| `docker-cleanup` | Remove unused images/containers |
| `docker-logs` | Tail logs with filtering |

## Usage Examples
- "Build and push the API Docker image"
- "Start the full stack with health checks"
- "Clean up unused Docker resources"