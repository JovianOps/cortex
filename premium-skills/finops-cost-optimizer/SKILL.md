---
name: finops-cost-optimizer
description: Audit Terraform and K8s configs for cloud cost waste.
version: 3.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [finops, cloud-cost, terraform, kubernetes, aws, optimization]
    related_skills: [terraform-generator, kubernetes-architect, performance-profiler]
---

# Cloud FinOps & Cost Optimizer

Identify and eliminate cloud infrastructure waste across Terraform, Kubernetes, and storage tiers — enforcing cost-allocation tags, right-sized compute, modern storage classes (`gp3`/lifecycle rules), and measurable savings estimates.

## When to Use

- Auditing Terraform HCL or Kubernetes manifests for oversized compute, legacy `gp2` volumes, or missing FinOps tags
- Designing autoscaling, Spot/Preemptible node pools, storage lifecycle policies, and NAT/egress cost reductions
- Building unit-economics cost guardrails before scaling production workloads

### When Not to Use

- Application-level CPU/memory micro-profiling (use `performance-profiler`) or IAM security-only reviews (use `terraform-generator`)

## How to Run

> **Bundled Helper Script (`v3.0.0`):** Run `python premium-skills/finops-cost-optimizer/scripts/audit_finops.py infra/` to flag oversized instance families, legacy `gp2` EBS volumes, missing FinOps tags (`environment`, `owner`, `cost_center`), and Kubernetes workloads missing `resources.requests`.

```bash
npx @jovianops/cortex install --agent vscode --skill finops-cost-optimizer --scope project
python premium-skills/finops-cost-optimizer/scripts/audit_finops.py infra/ --json
```

## Mandatory FinOps Engineering Protocol

### Step 1 — Establish Cost Attribution & Baseline

Confirm mandatory cost-allocation tags (`environment`, `owner`, `cost_center`) across all billable resources and separate non-production (dev/staging) from production SLA constraints.

### Step 2 — Non-Negotiable Cloud Cost Hygiene Rules

1. **Compute Right-Sizing**: Flag oversized instances (`8xlarge+`/bare-metal) without documented CPU/memory utilization justification; schedule non-prod auto-shutdown outside business hours.
2. **Modern Storage & Lifecycle Tiers**: Migrate AWS EBS `gp2` -> `gp3`, attach S3/GCS lifecycle transitions (Standard -> Infrequent Access -> Glacier/Archive) and incomplete-multipart-upload abort rules, and delete unattached volumes/old snapshots.
3. **Kubernetes Bin-Packing**: Require accurate `resources.requests` paired with HPA/VPA or Karpenter so clusters scale down idle nodes cleanly.
4. **Data Transfer & Egress Awareness**: Prefer VPC Gateway/Interface Endpoints over NAT Gateways for high-volume S3/ECR traffic and document cross-AZ transfer costs.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled FinOps auditor on all IaC and Kubernetes manifests:

```bash
python premium-skills/finops-cost-optimizer/scripts/audit_finops.py infra/
```

Stop and state explicit assumptions whenever estimating monthly dollar savings (never invent cloud list prices without labeling them as estimates).

## Output Contract

Deliver:
1. **FinOps Waste Findings** — Prioritized list of oversized resources, missing tags, and storage/network inefficiencies with file:line locations.
2. **Remediation Diffs & Risk Notes** — Concrete IaC/K8s patches noting whether each change is zero-downtime or requires replacement.
3. **Verification Results** — Exact output from `audit_finops.py`.
