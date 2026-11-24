# Security Policy

## Supported Versions

| Version | Supported |
| :--- | :---: |
| `1.x` | Yes |
| `0.x` (beta) | Security fixes only via upgrade to `1.x` |

## Supply-Chain & Integrity Guarantees

Cortex enforces cryptographic integrity at every distribution boundary:

1. **SHA-256 Skill & Archive Manifest (`checksums.json`)**:
   - Every `SKILL.md`, bundled Python helper script, and deterministic `.zip` archive is hashed with SHA-256.
   - `cortex install --remote` verifies every downloaded file against `checksums.json` before writing to disk.
   - `cortex verify` and `cortex doctor` detect local tampering or drift against `.cortex-lock.json`.
2. **npm SLSA v1 Provenance**:
   - `@jovianops/cortex` releases are published from GitHub Actions via tokenless OIDC Trusted Publishing with `npm publish --provenance --access public`.
   - Verify published packages with `npm audit signatures`.
3. **SHA-Pinned GitHub Actions**:
   - All workflow actions in `.github/workflows/` are pinned to 40-character commit SHAs and continuously audited by `premium-skills/devops-pipeline/scripts/lint_actions.py`, Trivy, and CodeQL.

## Reporting a Vulnerability

Please **do not** open a public issue for security vulnerabilities.

1. Use GitHub's private **Security Advisories** feature:
   `https://github.com/JovianOps/cortex/security/advisories/new`
2. Include a clear description, affected file(s) or skill(s), reproduction steps, and potential impact.
3. We aim to acknowledge reports within **48 hours** and coordinate disclosure once a fix is verified.
