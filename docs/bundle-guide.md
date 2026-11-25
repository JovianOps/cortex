# Portable Bundles (`cortex bundle`)

`cortex bundle` packages selected Cortex skills into one deterministic, offline ZIP that carries its own SHA-256 manifest. It is the hand-off format for air-gapped machines, vendored repositories, artifact registries, and CI jobs that must not clone GitHub.

## Build

```bash
# A curated role pack
python scripts/cortex_bundle.py --pack cloud-native --out dist/cortex-cloud-native.zip

# Every extended skill
python scripts/cortex_bundle.py --collection extended --out dist/cortex-extended.zip

# An explicit set
python scripts/cortex_bundle.py --skill security-auditor --skill kubernetes-architect --out dist/cortex-selected.zip

# Machine-readable build receipt
python scripts/cortex_bundle.py --pack fullstack --json
```

Default output is `dist/cortex-<selection>.zip` in the current working directory. `--pack` and `--skill` accept repeats, and can be combined; `--collection core|extended|all` adds a whole tier.

## Verify

```bash
python scripts/cortex_bundle.py --verify dist/cortex-cloud-native.zip
python scripts/cortex_bundle.py --verify dist/cortex-cloud-native.zip --json
```

Verification needs only the ZIP. It recomputes the SHA-256 of every declared file and fails on any missing, extra, or modified member.

## Contents

```text
cortex-cloud-native.zip
├── bundle.json            # manifest: version, selection, per-file SHA-256
├── README.md              # install and verification instructions
└── skills/
    ├── kubernetes-architect/SKILL.md
    ├── kubernetes-architect/scripts/lint_k8s.py
    ├── terraform-generator/SKILL.md
    └── ...
```

`bundle.json` records:

| Field | Meaning |
| :--- | :--- |
| `schema_version` | Bundle format version (`1.0`). |
| `cortex_version` | Cortex release that produced the bundle. |
| `selection` | Packs, skills, and collection requested. |
| `skill_count` / `file_count` | Declared totals, checked during verification. |
| `skills.<slug>.files` | Relative path → SHA-256 for every shipped file. |
| `manifest_sha256` | SHA-256 over the manifest itself (excluding this field). |

## Determinism

ZIP entries are written in sorted order with a fixed timestamp (`2026-01-01T00:00:00`) and normalised LF line endings for text files. Building the same selection from the same commit produces the same archive bytes and therefore the same archive SHA-256 — safe to compare across machines or cache in CI.

## Install a bundle

```bash
unzip cortex-cloud-native.zip -d /tmp/cortex-bundle
cp -r /tmp/cortex-bundle/skills/* ~/.claude/skills/
```

Every skill directory is self-contained (`SKILL.md` plus its `scripts/` verifier), so it can be copied into any supported agent's skills directory.

## Exit codes

| Code | Meaning |
| :--- | :--- |
| `0` | Bundle built or verified successfully. |
| `1` | Verification failed (missing, extra, or modified member). |
| `2` | Invalid selection, unknown pack/skill, or unwritable output path. |

MCP clients can build bundles with `cortex_build_bundle` inside the workspace; Studio does not expose write access to arbitrary paths.
