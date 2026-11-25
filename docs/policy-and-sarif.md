# Unified Policy & SARIF 2.1.0 Scanner (`cortex scan`)

**`cortex scan`** orchestrates Cortex's bundled zero-dependency verifiers in a single pass across your repository and outputs human-readable tables, JSON, **SARIF 2.1.0** (for GitHub Code Scanning), or **JUnit XML** (for CI test dashboards).

## Included Scanners (14)

`actions`, `secrets`, `terraform`, `kubernetes`, `typescript`, `rust`, `go`, `graphql`, `sbom`, `pii`, `finops`, `resilience`, `llm`, `git`.

## Usage Examples

```bash
# Run all applicable scanners across the current repo (fails on HIGH/CRITICAL by default)
npx @jovianops/cortex scan .

# Write a starter .cortex-policy.json in the target directory
npx @jovianops/cortex scan . --init-policy

# Emit structured JSON (--json or --format json)
npx @jovianops/cortex scan . --json --fail-on high

# Run selected scanners and export SARIF 2.1.0 for GitHub Code Scanning
npx @jovianops/cortex scan . --only actions --only secrets --only sbom --format sarif --output cortex.sarif

# Export JUnit XML for CI test reports
npx @jovianops/cortex scan . --format junit --output cortex-junit.xml --fail-on medium
```

## Org-Wide Policy Configuration (`.cortex-policy.json`)

Validate against [`schemas/policy.schema.json`](../schemas/policy.schema.json):

```json
{
  "schema_version": "3.0.0",
  "fail_on": "high",
  "disabled_scanners": ["finops"],
  "ignore_rules": ["git-non-conventional-commit"],
  "ignore_paths": ["tests/fixtures/*", "docs/*"]
}
```

## GitHub Actions Code Scanning Integration

```yaml
- name: Run Cortex SARIF Scan
  run: npx @jovianops/cortex scan . --format sarif --output cortex.sarif --fail-on high

- name: Upload SARIF to GitHub Code Scanning
  if: always()
  uses: github/codeql-action/upload-sarif@1bd86f2fdb4b86187fa4059f16f31a3202acc9ea # v4
  with:
    sarif_file: cortex.sarif
```
