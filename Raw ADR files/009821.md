# ADR-002: Progressive Secrets Management Learning

## Status

Accepted (supersedes previous ESO-first approach)

## Context

Need to learn GitOps-friendly secrets management for a Kubernetes learning lab. Key requirements:
- Understand trade-offs between different approaches
- No cloud dependencies for core infrastructure (CapEx home lab over OpEx cloud)
- OpenBao on hub cluster as the production target
- Progressive learning from simple to complex

## Decision

**Learn secrets management progressively:** Sealed Secrets → SOPS+age → ESO+OpenBao

Each approach teaches different concepts:

| Approach | What You Learn |
|----------|----------------|
| **Sealed Secrets** | Asymmetric encryption, cluster-bound keys, GitOps basics |
| **SOPS + age** | Key management, cluster-independent encryption, ArgoCD plugins |
| **ESO + OpenBao** | Central secrets store, dynamic secrets, production patterns |

## Comparison

| Factor | Sealed Secrets | SOPS + age | ESO + OpenBao |
|--------|----------------|------------|---------------|
| **GitOps-friendly** | Yes | Yes | Yes |
| **Cluster-independent** | No | Yes | Yes |
| **Central management** | No | No | Yes |
| **Rotation** | Manual re-seal | Manual re-encrypt | Automatic |
| **Dynamic secrets** | No | No | Yes |
| **Complexity** | Low | Medium | Higher |
| **External dependencies** | None | age key | OpenBao service |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Hub Cluster (N100 / Kind / K3s)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  OpenBao                                             │   │
│  │  - KV secrets engine (static secrets)               │   │
│  │  - Database engine (dynamic creds)                  │   │
│  │  - PKI engine (certificates)                        │   │
│  │  - Kubernetes auth per experiment                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
     ▼                   ▼                   ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Experiment  │   │ Experiment  │   │ Experiment  │
│ Cluster A   │   │ Cluster B   │   │ Cluster C   │
│ (ESO)       │   │ (SOPS)      │   │ (Sealed)    │
└─────────────┘   └─────────────┘   └─────────────┘
```

## When to Use Each

**Sealed Secrets:**
- Quick experiments that don't need secret portability
- Learning GitOps basics
- Single-cluster, short-lived deployments

**SOPS + age:**
- Multi-cluster deployments with same secrets
- CI/CD pipelines that need to decrypt locally
- When you control the encryption keys

**ESO + OpenBao:**
- Production workloads
- Dynamic database credentials
- Secret rotation requirements
- Audit logging needs
- Central secrets governance

## Why Not Cloud Secret Managers?

Previous approach used Azure Key Vault + ESO. Rejected because:
- Creates cloud OpEx dependency for infrastructure
- Home lab should be self-contained (CapEx model)
- Cloud secret managers make sense for *experiments* that need cloud resources, not for core infrastructure

Cloud secret managers (Azure Key Vault, AWS Secrets Manager) remain options for experiments via Crossplane, but the hub cluster uses OpenBao.

## Consequences

**Positive:**
- Learn trade-offs through hands-on experience
- No cloud lock-in for core infrastructure
- Self-contained home lab

**Negative:**
- Must operate OpenBao (backup, HA, upgrades)
- More complex than managed cloud service

## References

- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [SOPS](https://github.com/getsops/sops)
- [age encryption](https://github.com/FiloSottile/age)
- [External Secrets Operator](https://external-secrets.io/)
- [OpenBao](https://openbao.org/) (Vault fork)

## Decision Date

2025-12-12
