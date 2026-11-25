---
name: git-history-surgeon
description: Execute safe Git rebases, bisects, and repo hygiene audits.
version: 3.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [git, rebase, bisect, hygiene, conventional-commits, workflow]
    related_skills: [release-engineering, code-review-assistant, devops-pipeline]
---

# Git History Surgeon & Repo Hygiene Auditor

Execute zero-data-loss Git history operations (`git bisect`, interactive rebase, cherry-pick, reflog recovery) and enforce repository hygiene (zero merge conflict markers, zero oversized blobs, and Conventional Commits).

## When to Use

- Isolating regressions systematically with automated `git bisect run` scripts
- Cleaning up local feature-branch commits safely before review or recovering lost commits via `git reflog`
- Auditing repositories for leftover merge conflict markers, accidental large binaries, or commit message compliance

### When Not to Use

- Semantic version tagging and changelog generation (use `release-engineering`) or secret rotation (use `security-auditor`)

## How to Run

> **Bundled Helper Script (`v3.0.0`):** Run `python premium-skills/git-history-surgeon/scripts/audit_git_hygiene.py .` to scan for unresolved `<<<<<<<` merge conflict markers, oversized files (`--max-file-kb`), and Conventional Commits compliance across recent history.

```bash
npx @jovianops/cortex install --agent vscode --skill git-history-surgeon --scope project
python premium-skills/git-history-surgeon/scripts/audit_git_hygiene.py . --json
```

## Mandatory Git Safety Protocol

### Step 1 — Pre-Flight Backup & Branch Isolation (Hard Stop Gate)

Before ANY history-rewriting command (`rebase`, `reset`, `filter-repo`, `amend`):
1. Verify working tree status (`git status --short`) and record the starting commit SHA (`git rev-parse HEAD`) or create a safety backup tag/branch.
2. **NEVER** force-push (`--force`) to shared/protected branches (`main`, `master`, `release/*`); when updating a personal PR branch, always use `--force-with-lease`.

### Step 2 — Non-Negotiable History & Hygiene Standards

1. **Automated `git bisect`**: Provide a deterministic exit-code test script (`0` good, `1` bad, `125` skip unbuildable) and always finish with `git bisect reset`.
2. **Clean Conflict Resolution**: After resolving any merge/rebase conflict, verify zero `<<<<<<<` / `=======` / `>>>>>>>` markers remain and re-run the full test suite.
3. **Conventional Commits**: Format subjects as `<type>(<scope>): <imperative summary>` (`feat`, `fix`, `docs`, `refactor`, `test`, `ci`, `chore`, `release`).
4. **Artifact & Binary Hygiene**: Keep build outputs, archives, and oversized files out of Git history unless tracked intentionally or via Git LFS.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled repository hygiene auditor before pushing:

```bash
python premium-skills/git-history-surgeon/scripts/audit_git_hygiene.py .
```

Stop immediately if any CRITICAL merge conflict markers are detected.

## Output Contract

Deliver:
1. **Exact Command Plan & Recovery Path** — Safe step-by-step Git commands plus the exact `git reflog` / backup rollback command.
2. **Hygiene Audit Summary** — Conflict-marker check, large-file report, and commit convention status.
3. **Verification Results** — Exact output from `audit_git_hygiene.py`.
