---
name: devops-pipeline
description: Build hardened, SHA-pinned CI/CD pipelines across tools.
version: 0.3.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [devops, ci-cd, github-actions, gitlab-ci, security]
    related_skills: [docker-generator, security-auditor, testing-automation, terraform-generator]
---

# DevOps Pipeline Generator

Design, harden, optimize, and migrate CI/CD pipelines (GitHub Actions, GitLab CI, CircleCI) with supply-chain security hardening, deterministic lockfile caching, least-privilege permissions, and YAML validation.

## When to Use

- Creating a production CI/CD workflow for testing, linting, container builds, security scanning, and deployments
- Hardening existing workflows against supply-chain attacks, script injection, and overly broad tokens
- Optimizing slow pipelines via dependency caching, job parallelism, and path/concurrency filters
- Migrating workflows between GitHub Actions, GitLab CI, and CircleCI

### When Not to Use

- Provisioning underlying cloud networks or compute clusters (use `terraform-generator`)

## How to Run

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/devops-pipeline --yes
hermes chat -q "Generate a hardened GitHub Actions CI/CD workflow for this repo with lint, tests, and Trivy scan"
```

## Mandatory Pipeline Engineering Protocol

### Step 1 — Inspect the Real Repository First

Before generating any YAML, read the repository manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `Dockerfile`, existing `.github/workflows/` or `.gitlab-ci.yml`):

- Match the **exact** package manager and lockfile (`npm ci` + `package-lock.json`, `pnpm --frozen-lockfile`, `uv sync --frozen`, `pip install -r`).
- Match the **exact** runtime versions and test/lint commands defined in the repo — **never invent scripts or runner labels**.

### Step 2 — Non-Negotiable Supply-Chain & Security Hardening

Every generated CI/CD workflow MUST enforce:

1. **Explicit Least-Privilege `permissions:`**:
   - Declare top-level `permissions: {}` (or `contents: read`) and grant write scopes (`packages: write`, `security-events: write`, `id-token: write`) **only** on the specific job that needs them.
2. **Prevent GitHub Actions Script Injection**:
   - **Never** interpolate untrusted event context directly inside `run:` (`${{ github.event.issue.title }}`, `${{ github.event.pull_request.title }}`, `${{ github.head_ref }}`).
   - Always pass untrusted values through an intermediate `env:` variable and quote `"$VAR"` in shell.
3. **Action Pinning & Runner Hygiene**:
   - Prefer pinning third-party actions to full 40-char commit SHAs with version comment (`uses: actions/checkout@<sha> # v4`) or explicitly flag unpinned tags for pinning if offline (never fabricate a fake SHA!).
   - Use specific runner versions (`ubuntu-24.04` or `ubuntu-latest`) and set `timeout-minutes:` on every job to prevent hung builds burning quota.
4. **Secretless Cloud Auth & Secret Safety**:
   - Prefer OIDC (`id-token: write`) over long-lived static cloud keys.
   - Never print secrets, and protect production deploy jobs with environment approval gates (`environment: production`) and branch restrictions.

### Step 3 — Speed & Reliability Optimizations

- **Concurrency control**: Cancel superseded PR runs while never canceling in-flight `main`/release deployments:

  ```yaml
  concurrency:
    group: ${{ github.workflow }}-${{ github.ref }}
    cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
  ```

- **Lockfile-keyed caching**: Use built-in `cache:` in `setup-node`/`setup-python`/`setup-go` or hash lockfiles cleanly.
- **Fail-fast job graph**: Run fast lint/typecheck jobs in parallel with unit tests; gate container build/deploy behind `needs: [lint, test, security]`.

### Step 4 — Mandatory YAML & Schema Validation

Before delivering any workflow file, validate it locally:

```bash
python3 -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('.github/workflows/ci.yml').read_text()); print('YAML OK')"
# Run actionlint if installed
actionlint
```

## Output Contract

Deliver:

1. **Workflow File(s)** — Complete, valid YAML ready to commit.
2. **Security Hardening Summary** — Permissions granted per job, injection guards, timeout/concurrency settings, and required repository secrets/OIDC roles.
3. **Validation Proof** — Actual YAML parse / `actionlint` output.
