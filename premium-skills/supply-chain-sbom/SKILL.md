---
name: supply-chain-sbom
description: Audit dependencies, lockfiles, SLSA provenance, and SBOMs.
version: 2.0.1
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sbom, supply-chain, slsa, security, dependencies, cyclonedx]
    related_skills: [security-auditor, devops-pipeline, release-engineering]
---

# Supply-Chain Security & SBOM Auditor

Harden software supply chains across npm, Python, Rust, and containers with pinned lockfiles, CycloneDX/SPDX SBOM generation, SLSA v1 provenance verification, and lifecycle-hook auditing.

## When to Use

- Auditing `package.json`, `requirements.txt`, `Cargo.toml`, or lockfiles before a production release
- Setting up CycloneDX SBOM generation, OIDC Trusted Publishing, and `npm audit signatures`
- Investigating suspicious `preinstall`/`postinstall` hooks or floating/unpinned dependencies

### When Not to Use

- Application-level OWASP SQLi/XSS reviews (use `security-auditor`) or GitHub Actions YAML-only checks (use `devops-pipeline`)

## How to Run

> **Bundled Helper Script (`v2.0.0`):** Run `python premium-skills/supply-chain-sbom/scripts/audit_sbom.py . --sbom --json` to detect missing lockfiles, unpinned/wildcard specs, insecure `http://` sources, suspicious install hooks, and generate a CycloneDX 1.6 summary.

```bash
npx @jovianops/cortex install --agent vscode --skill supply-chain-sbom --scope project
python premium-skills/supply-chain-sbom/scripts/audit_sbom.py . --sbom --json
```

## Mandatory Supply-Chain Hardening Protocol

### Step 1 — Inventory Ecosystems, Lockfiles & Registries

Identify every dependency manifest (`package.json`, `requirements*.txt`, `pyproject.toml`, `Cargo.toml`, `go.mod`), confirm its committed lockfile, and verify every registry URL uses HTTPS.

### Step 2 — Non-Negotiable Supply-Chain Controls

1. **Deterministic Lockfiles**: Every project with runtime/build dependencies MUST commit a lockfile and install with frozen/immutable flags (`npm ci`, `uv sync --frozen`, `cargo build --locked`).
2. **Zero Floating or Insecure Specs**: Reject `*`, `latest`, unpinned Python requirements, and any `http://` dependency URLs.
3. **Lifecycle-Hook & Provenance Defense**: Audit `preinstall`/`install`/`postinstall` scripts for remote shell downloads; prefer `--ignore-scripts` in untrusted CI builds and verify SLSA v1 provenance via `npm audit signatures`.
4. **Reproducible SBOM & Checksums**: Emit CycloneDX/SPDX SBOM artifacts and SHA-256 checksum manifests (`checksums.json`) on every tagged release.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled supply-chain auditor and signature checks:

```bash
python premium-skills/supply-chain-sbom/scripts/audit_sbom.py . --sbom
npm audit signatures
```

Stop and remediate all CRITICAL and HIGH supply-chain findings before publishing.

## Output Contract

Deliver:
1. **Supply-Chain Findings Report** — Missing lockfiles, unpinned packages, and lifecycle-hook risks with remediation steps.
2. **SBOM & Provenance Summary** — CycloneDX component count, lockfile status, and SLSA verification status.
3. **Verification Results** — Exact output from `audit_sbom.py`.
