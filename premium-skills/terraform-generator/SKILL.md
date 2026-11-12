---
name: terraform-generator
description: Generate and validate Terraform/OpenTofu infrastructure as code.
version: 0.1.0
author: Athalla Jovian Maharsa
license: MIT
platforms: [linux, macos, windows]
---

# Terraform Generator

Generate and validate Terraform/OpenTofu infrastructure as code.

## When to Use
- Provisioning cloud infrastructure (AWS, GCP, Azure)
- Writing reusable Terraform modules
- Importing existing infrastructure
- Validating Terraform configs
- Planning infrastructure changes

## How to Run
```bash
hermes skills install JovianOps/cortex/premium-skills/terraform-generator
hermes chat -q "Generate Terraform for an AWS VPC with public and private subnets"
```

## Core Capabilities
1. **Resource generation** — Generate HCL for cloud resources
4. **Module creation** — Reusable, parameterized modules
4. **Validation** — Validate against provider schemas
5. **State management** — Remote state config, workspace setup
6. **Plan analysis** — Parse and explain terraform plan output

## Anti-Hallucination Measures
- Validate HCL syntax before delivery
- No invented resource types or attributes
- Deterministic generation from requirements
- Explicit cost/security implications for each resource