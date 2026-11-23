---
name: terraform-generator
description: Generate hardened, validated Terraform and OpenTofu IaC.
version: 0.3.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [terraform, opentofu, iac, cloud, aws, security]
    related_skills: [devops-pipeline, security-auditor, docker-generator]
---

# Terraform / OpenTofu Generator

Generate modular, secure-by-default, validated Terraform/OpenTofu HCL configurations with pinned provider constraints, remote state locking, least-privilege IAM, encryption, and explicit cost/blast-radius notes.

## When to Use

- Authoring reusable Terraform or OpenTofu modules for AWS, GCP, or Azure infrastructure
- Hardening existing HCL configs for encryption, private networking, IAM least privilege, and state safety
- Auditing `terraform plan` diffs for destructive replacements or security regressions
- Importing existing cloud resources cleanly with `import {}` blocks

### When Not to Use

- Application container builds (use `docker-generator`) or CI/CD pipeline authoring (use `devops-pipeline`)

## How to Run

```bash
hermes skills tap add JovianOps/cortex
hermes skills install JovianOps/cortex/premium-skills/terraform-generator --yes
hermes chat -q "Generate a hardened Terraform module for an AWS VPC with public/private subnets and flow logs"
```

## Mandatory IaC Engineering Protocol

### Step 1 — Lock Architecture, Provider & State Constraints

Before generating HCL, establish or explicitly document defaults for:

- Target cloud provider(s), region(s), and environment separation (`dev`/`staging`/`prod`)
- Module layout: `versions.tf`, `variables.tf`, `main.tf`, `outputs.tf`, `locals.tf` (never cram a production module into one monolithic file without reason)
- Remote state backend with encryption and locking (e.g., S3 with `encrypt = true` + `use_lockfile = true` / DynamoDB, GCS with versioning, Azure Storage)

### Step 2 — Non-Negotiable HCL & Cloud Security Standards

Every generated module MUST enforce:

1. **Explicit Version Pinning**:
   - Pin `required_version` and pessimistic `required_providers` constraints (`~> 5.0`) in `versions.tf` — never omit version bounds.
2. **Strict Input Contracts**:
   - Declare explicit `type`, `description`, `validation {}` blocks (CIDR/regex/enum checks), and `sensitive = true` on every secret/credential variable and output.
3. **Secure-by-Default Cloud Resources**:
   - **Networking**: Private subnets for compute/databases; zero `0.0.0.0/0` ingress on SSH (`22`), RDP (`3389`), or database ports; explicit security-group descriptions on every rule.
   - **Encryption & Storage**: Encryption at rest (KMS/AES-256) enabled; S3/object storage public access explicitly blocked (`aws_s3_bucket_public_access_block`); versioning enabled on state/critical buckets; HTTPS/TLS enforced in transit.
   - **Least-Privilege IAM**: Never emit `"Action": "*"` or `"Resource": "*"` unless strictly required by the cloud API (and justified inline); prefer `data "aws_iam_policy_document"` over raw JSON heredocs.
   - **Observability & Lifecycle**: Enable audit/flow logs where applicable; guard stateful resources (databases, KMS keys, state buckets) with `lifecycle { prevent_destroy = true }` in production templates.
4. **Consistent Tagging**: Merge mandatory tags (`Project`, `Environment`, `ManagedBy = "terraform"`) via `default_tags` or `locals`.
5. **Zero Invented Resource Types or Arguments**: Only emit real, documented provider resources and arguments; do not mix deprecated attributes (e.g., inline S3 `acl`/`versioning` blocks in AWS provider v5+ instead of separate `aws_s3_bucket_*` resources).

### Step 3 — Mandatory Local Validation Gate

When `terraform` or `tofu` is installed locally, run:

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
# Optional static security scanners if installed
tflint
checkov -d . --quiet
```

Report exact command output (or note clearly if `terraform`/`tofu` CLI is not installed in the sandbox).

## Output Contract

Deliver:

1. **Module Files** — Clean, idiomatic `versions.tf`, `variables.tf`, `main.tf`, `outputs.tf` (plus usage example).
2. **Security & Lifecycle Summary** — Encryption, public-access blocks, least-privilege IAM, and `prevent_destroy` protections applied.
3. **Cost & Blast-Radius Notes** — Explicit callouts for metered resources (e.g., NAT Gateways, multi-AZ RDS, KMS keys) and any destructive replacement risks.
4. **Validation Results** — `fmt`/`validate`/scanner command output.
