---
name: docker-generator
description: Generate hardened multi-stage Docker and Compose setups.
version: 0.3.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [docker, containers, docker-compose, kubernetes, security]
    related_skills: [devops-pipeline, security-auditor, terraform-generator]
---

# Docker Generator

Generate production-hardened, layer-cached, multi-stage `Dockerfile`, `.dockerignore`, and `compose.yaml` configurations tailored strictly to the inspected project layout.

## When to Use

- Containerizing a Python, Node.js, Go, Rust, or Java application for production
- Auditing and shrinking bloated or insecure existing Dockerfiles
- Creating multi-service `compose.yaml` stacks with healthchecks, isolated networks, and persistent volumes
- Converting container setups into hardened Kubernetes Deployment/Service manifests

### When Not to Use

- CI/CD pipeline authoring (use `devops-pipeline`) or cloud VPC/cluster provisioning (use `terraform-generator`)

## How to Run

> **Bundled Helper Script (`v0.3.0`):** Run `python premium-skills/docker-generator/scripts/lint_dockerfile.py Dockerfile` to audit pinned base tags, non-root `USER`, secret `ENV`s, `curl | sh`, and `HEALTHCHECK`.

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/docker-generator --yes
hermes chat -q "Generate a hardened multi-stage Dockerfile, .dockerignore, and compose.yaml for this project"
```

## Mandatory Container Engineering Protocol

### Step 1 — Inspect the Actual Application First

Read `package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml`, lockfiles, entry points, and listening ports before generating a single Dockerfile line:

- Never guess the start command, build output folder, port, or package manager.
- Verify whether native C extensions or system libs (`libpq`, `gcc`) are required at build time vs. runtime.

### Step 2 — Non-Negotiable Dockerfile Production Standards

Every generated `Dockerfile` MUST enforce ALL of the following:

1. **Pinned Base Images (Never `:latest`)**:
   - Pin explicit minor versions (e.g., `python:3.12-slim-bookworm`, `node:22-alpine`, `gcr.io/distroless/static-debian12:nonroot`) — recommend pinning `@sha256:...` digests for production immutability.
2. **Multi-Stage Build**:
   - Separate build/compile dependencies (`builder` stage) from the minimal runtime stage so compilers, dev dependencies, and build caches never ship in the final image.
3. **Optimal Layer Caching (Lockfile-First Copy)**:
   - Copy dependency manifests and lockfiles first (`COPY package.json package-lock.json ./` or `COPY pyproject.toml uv.lock ./`), install dependencies (`npm ci --omit=dev`, `pip install --no-cache-dir`), and copy application source **afterward** so code edits don't bust the dependency cache.
4. **Non-Root Execution**:
   - Create and switch to a dedicated non-root user (`USER appuser` with fixed UID/GID e.g. `10001`), owning only writable runtime directories.
5. **Proper Signal Handling (`exec` Form)**:
   - Always use JSON `exec` form for `ENTRYPOINT` / `CMD` (e.g., `CMD ["node", "dist/server.js"]`) so PID 1 receives `SIGTERM` cleanly instead of being swallowed by `/bin/sh -c`.
6. **Zero Baked-In Secrets**:
   - Never pass secrets via `ARG` or `ENV` baked into image layers; use BuildKit secret mounts (`RUN --mount=type=secret,id=...`) when build-time auth is needed.
7. **Always Pair with `.dockerignore`**:
   - Exclude `.git`, `node_modules`, `.venv`, `__pycache__`, `.env*`, `*.log`, `tests/`, and `dist/` so secrets and huge local caches never enter the build context.
8. **Healthcheck & Container Hardening**:
   - Include `HEALTHCHECK` (or Compose `healthcheck`) and in `compose.yaml` apply `read_only: true`, `tmpfs: [/tmp]`, `security_opt: [no-new-privileges:true]`, `cap_drop: [ALL]`, and explicit `depends_on: { db: { condition: service_healthy } }`.

### Step 3 — Verification Gate

Validate generated files locally when tools are available:

```bash
# Validate Compose YAML syntax
python3 -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('compose.yaml').read_text())"
docker compose config --quiet   # if docker is available
hadolint Dockerfile             # if hadolint is available
```

## Output Contract

Deliver:

1. **`Dockerfile`** — Multi-stage, non-root, cache-ordered, `exec`-form CMD.
2. **`.dockerignore`** — Complete build-context exclusion list.
3. **`compose.yaml`** (when multi-service) — Healthchecks, hardened security options, explicit env vars (no hardcoded production passwords).
4. **Security & Size Audit Notes** — What was excluded from the runtime image, non-root UID, signal handling, and exact build/run commands.
