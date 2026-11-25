---
name: kubernetes-architect
description: Design hardened Kubernetes and Helm workloads with probes.
version: 3.0.0
author: Athalla Jovian Maharsa (athallajovian9-cyber), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [kubernetes, k8s, helm, containers, security, sre]
    related_skills: [docker-generator, terraform-generator, chaos-resilience-engineer]
---

# Kubernetes & Helm Architect

Design production-ready, least-privilege Kubernetes manifests and Helm charts enforcing Pod Security Standards (Restricted), bounded resource quotas, probes, network policies, and zero-downtime rollouts.

## When to Use

- Authoring Kubernetes Deployments, StatefulSets, Jobs, NetworkPolicies, or Helm charts
- Hardening existing manifests to comply with Pod Security Standards (`Restricted`)
- Diagnosing crash loops, OOMKills, eviction cascades, or rollout stalls

### When Not to Use

- Container image Dockerfile optimization (use `docker-generator`) or cloud VPC/IAM provisioning (use `terraform-generator`)

## How to Run

> **Bundled Helper Script (`v3.0.0`):** Run `python premium-skills/kubernetes-architect/scripts/lint_k8s.py k8s/` to audit manifests for `privileged: true`, `:latest` tags, missing `runAsNonRoot`/`readOnlyRootFilesystem`, missing resource limits, and missing probes.

```bash
npx @jovianops/cortex install --agent vscode --skill kubernetes-architect --scope project
python premium-skills/kubernetes-architect/scripts/lint_k8s.py k8s/ --json
```

## Mandatory Kubernetes Engineering Protocol

### Step 1 — Lock Cluster & Security Baseline

Before emitting YAML, verify or document:
- Kubernetes API version compatibility (avoid deprecated APIs like `extensions/v1beta1`)
- Pod Security Standard target (`Restricted` by default) and namespace isolation
- Traffic ingress path, TLS termination, and external secret provider (ExternalSecrets / Vault — never raw Secrets committed to Git)

### Step 2 — Non-Negotiable Pod Hardening & Reliability Rules

Every generated workload MUST enforce:
1. **Immutable Image References**: Pin explicit SemVer tags or `@sha256:` digests — never `:latest`.
2. **Restricted SecurityContext**:
   - `runAsNonRoot: true`, explicit non-zero `runAsUser`
   - `readOnlyRootFilesystem: true` (mount `emptyDir` for `/tmp` if needed)
   - `allowPrivilegeEscalation: false` and `capabilities: { drop: ["ALL"] }`
   - `seccompProfile: { type: RuntimeDefault }`
   - Never enable `privileged: true`, `hostNetwork`, `hostPID`, or `hostIPC`.
3. **Resource Governance**: Declare both `resources.requests` and `resources.limits` (CPU & memory) on every container.
4. **Health & Zero-Downtime Lifecycle**:
   - Configure `readinessProbe`, `livenessProbe`, and `startupProbe` (for slow starters)
   - Pair production Deployments with `replicas >= 2`, `PodDisruptionBudget`, `topologySpreadConstraints`, and `terminationGracePeriodSeconds`
5. **Default-Deny NetworkPolicy**: Include explicit ingress/egress allowlists alongside services.

### Step 3 — Mandatory Verification Gate

Run Cortex's bundled verifier (plus `kubectl --dry-run=client` / `helm lint` when installed):

```bash
python premium-skills/kubernetes-architect/scripts/lint_k8s.py k8s/
helm lint ./chart
kubectl apply --dry-run=client -f k8s/
```

Stop and fix any CRITICAL or HIGH findings before shipping.

## Output Contract

Deliver:
1. **Manifests / Chart Files** — Clean, validated YAML separated by concern (`deployment.yaml`, `service.yaml`, `pdb.yaml`, `networkpolicy.yaml`).
2. **Security & HA Summary** — Pod Security compliance, RBAC least privilege, and rollout/PDB guarantees.
3. **Verification Results** — Exact `lint_k8s.py` / `helm lint` output.
