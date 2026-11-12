---
name: docker-generator
description: Generate optimized Dockerfiles, docker-compose, and container orchestration configs.
version: 0.1.0
author: Athalla Jovian Maharsa
license: MIT
platforms: [linux, macos, windows]
---

# Docker Generator

Generate optimized Dockerfiles, docker-compose files, and container configurations.

## When to Use
- Containerizing a new application
- Optimizing existing Dockerfile (size, layers, security)
- Creating docker-compose for multi-service apps
- Setting up development containers
- Generating Kubernetes manifests from Docker configs

## How to Run
```bash
hermes skills install JovianOps/cortex/premium-skills/docker-generator
hermes chat -q "Create a Dockerfile for this Node.js app"
```

## Core Capabilities
1. **Dockerfile generation** — Multi-stage builds, minimal base images
4. **docker-compose** — Multi-service orchestration with networking
4. **Optimization** — Layer caching, .dockerignore, multi-stage builds
5. **Security** — Non-root user, minimal attack surface
6. **K8s manifests** — Generate Kubernetes Deployments/Services from Docker configs

## Anti-Hallucination Measures
- Validate Dockerfile syntax before delivery
- No invented base images or commands
- Deterministic generation from project structure
- Explicit security warnings for risky patterns