# Guard Gate, CI & Pre-commit (`cortex guard`)

`cortex guard` is the single command that answers "is this Cortex release shippable?" It runs every deterministic gate in one pass, then can generate the same enforcement for GitHub Actions and Git hooks.

## One gate, six checks

```bash
python scripts/cortex.py guard check
python scripts/cortex.py guard check --json
python scripts/cortex.py guard check --only graph --only scan
python scripts/cortex.py guard check --fail-fast
```

| Check | Runs | Blocks on |
| :--- | :--- | :--- |
| `package` | `package_skills.py --check` | ZIP/`checksums.json` drift (skipped outside a source checkout). |
| `skills` | `validate_skills.py` | Missing frontmatter, sections, or archive mismatch. |
| `manifests` | `validate_manifests.py` | Manifest version/skill-list drift. |
| `audit` | `eval_skills.py` | Any skill below 100/100 or an invalid eval suite. |
| `graph` | `cortex_graph.py --check --strict` | Dangling pack/related references or skills in no role pack. |
| `scan` | `cortex_scan.py --fail-on high` | Any HIGH/CRITICAL finding in `.cortex-policy.json` scope. |

The report is stable JSON:

```json
{
  "version": "3.0.0",
  "project_dir": "C:/repo",
  "ok": true,
  "checks_run": 6,
  "checks_passed": 6,
  "checks_skipped": 0,
  "checks": [
    { "name": "graph", "ok": true, "skipped": false, "detail": "Capability graph: 36 skills, 10 packs, 179 edges - OK", "duration_ms": 119 }
  ]
}
```

Exit code `0` means every selected check passed; `1` means at least one blocked; `2` means an unknown check name was requested.

## Generate hardened CI

```bash
# Print to stdout
python scripts/cortex.py guard --print-workflow

# Write .github/workflows/cortex-guard.yml
python scripts/cortex.py guard --write-workflow
```

The generated workflow is deliberately boring and hardened:

- Every action is pinned to a 40-character commit SHA.
- `permissions: contents: read` at workflow level.
- Job-level `timeout-minutes`.
- A `concurrency` group that cancels superseded runs.
- No `github.event.*` values interpolated into `run:` scripts.
- SARIF uploaded to GitHub code scanning with `if: always()`.

It passes Cortex's own `lint_actions.py` audit unmodified.

## Git pre-commit hook

```bash
# Print the hook
python scripts/cortex.py guard --print-pre-commit

# Write .githooks/pre-commit and set core.hooksPath when inside a git repo
python scripts/cortex.py guard install
```

The hook runs `cortex verify` and `cortex scan --fail-on high`, using the local checkout when `scripts/cortex.py` exists and `npx -y @jovianops/cortex` otherwise. Installation never overwrites `.git/hooks`; it uses the versionable `.githooks/` directory.

## In MCP and Studio

- MCP tool: `cortex_release_gate` accepts `only` and `fail_fast`.
- Studio: **07 / Capability Graph → Run Release Gate** (`POST /api/guard`).

Both return the same JSON report as the CLI.
