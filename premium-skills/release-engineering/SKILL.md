---
name: release-engineering
description: Cut SemVer releases with changelogs, checksums, and gates.
version: 0.3.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [release-engineering, semver, changelog, versioning, devops]
    related_skills: [devops-pipeline, documentation-generator, code-review-assistant, security-auditor]
---

# Release Engineering

Plan, verify, and ship deterministic software releases using strict SemVer calculation, Keep-a-Changelog formatting, SHA-256 artifact checksums, pre-release verification gates, and tested rollback steps.

## When to Use

- Cutting a new SemVer release (`MAJOR.MINOR.PATCH` or prerelease) for a library, CLI, container, or skill repository
- Generating accurate, commit-verified `CHANGELOG.md` and GitHub Release notes
- Auditing version synchronization across multiple manifests (`package.json`, `pyproject.toml`, plugin manifests, lockfiles)
- Verifying build artifacts, SHA-256 checksums, and release rollback readiness

### When Not to Use

- Day-to-day feature development or unmerged WIP branches
- Publishing artifacts without passing test, lint, and security verification gates

## How to Run

```bash
# Universal CLI (Claude Code, Codex, Gemini CLI, Cursor, Copilot, OpenCode, OpenClaw, Goose, Cline)
npx skills add JovianOps/cortex --skill release-engineering -g -y

# Hermes Agent
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/release-engineering --yes
```

## Mandatory Release Engineering Protocol

### Step 1 — Inspect Commit Range & Compute SemVer Deterministically

Never guess the next version number. Inspect the exact git history since the latest tag:

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
git log "${LAST_TAG:+${LAST_TAG}..}HEAD" --format="%h %s%n%b"
```

Apply strict SemVer rules:
- **MAJOR (`X.0.0`)**: Breaking API/CLI/schema removal or behavior change (`BREAKING CHANGE:` footer or `!:` commit type; note `0.y.z` may document breaking changes in `0.(y+1).0` if pre-1.0).
- **MINOR (`x.Y.0`)**: Backward-compatible new features (`feat:`).
- **PATCH (`x.y.Z`)**: Backward-compatible bug fixes, security patches, or doc/perf improvements (`fix:`, `perf:`, `security:`).

### Step 2 — Version Parity Audit (Stop Gate)

Verify every version-bearing file in the repository agrees before tagging:
- Package manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, plugin/extension JSONs)
- Lockfiles, generated archives, and documentation badges
- **Stop Gate**: Abort release prep if any manifest version disagrees or `git status --porcelain` has unexpected untracked/dirty files.

### Step 3 — Run Full Pre-Release Verification Suite

Execute the repository's real build, test, lint, and packaging commands and record exact exit codes (zero fabricated checks):

```bash
# Example checks — run the actual commands configured in the repo
npm test
pytest
sha256sum dist/* > SHA256SUMS
```

Verify:
1. Clean working tree or only intentional release-bump changes.
2. Reproducible build outputs and SHA-256 checksums generated and verified.
3. No leaked secrets, `.env` files, or private directories bundled in release artifacts.

### Step 4 — Draft Verified Changelog & Rollback Plan

Group release notes strictly from verified commits in the release range using Keep-a-Changelog headings (`Breaking Changes`, `Added`, `Changed`, `Fixed`, `Security`), linking real commit SHAs or PR numbers only.

Always include an explicit **Rollback Procedure** (yanking/deprecating a broken package version, deleting/superseding a faulty tag, or cutting a `patch` hotfix rather than force-pushing published immutable tags).

## Strict Output Contract

```markdown
## Release Plan — `vX.Y.Z`
- **Previous Tag:** `vA.B.C` (or `none`)
- **SemVer Rationale:** Why MAJOR / MINOR / PATCH was chosen from verified commits.
- **Version Parity Files:** Exact list of synchronized manifests.

## Pre-Release Verification Gates
| Gate | Command | Result |
| :--- | :--- | :--- |

## Verified Release Notes (`CHANGELOG.md` Entry)
### Added / Changed / Fixed / Security
- Bullet items strictly grounded in commits in range.

## Publish & Rollback Commands
- **Tag & Publish:** Exact `git tag -a` / `gh release create` commands (requiring human confirmation before publishing).
- **Rollback Plan:** Exact steps if post-release smoke tests fail.
```
