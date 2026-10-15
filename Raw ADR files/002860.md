# ADR-004: Terraform + Terragrunt for IaC

## Status

Accepted

## Context

We need Infrastructure as Code (IaC) tooling that:

- Supports AWS resources comprehensively
- Enables DRY configuration across environments
- Provides state management and locking
- Is widely adopted with good community support

## Decision

We use **Terraform** for infrastructure definitions and **Terragrunt** for DRY configuration and environment management.

### Why Terraform?

- Industry standard for IaC
- Excellent AWS provider coverage
- Declarative syntax
- Large community and ecosystem
- State management with locking

### Why Terragrunt?

- DRY configuration (don't repeat backend config)
- Environment-specific variables without duplication
- Dependency management between modules
- `run-all` for multi-module operations

### Structure

```
nedlia-IaC/
  terragrunt.hcl              # Root config (backend, provider)
  environments/
    dev/
    testing/
    staging/
    production/
  modules/
    vpc/
    aurora/
    lambda/
    ...
```

### Alternatives Considered

| Tool           | Pros                   | Cons                             | Decision |
| -------------- | ---------------------- | -------------------------------- | -------- |
| AWS CDK        | TypeScript, type-safe  | AWS-only, abstraction overhead   | Rejected |
| Pulumi         | Multi-language, modern | Smaller community, state service | Rejected |
| CloudFormation | AWS-native             | Verbose, limited features        | Rejected |
| SAM            | Lambda-focused         | Limited to serverless            | Rejected |

## Consequences

### Positive

- Proven, stable tooling
- Easy to hire developers with Terraform experience
- Clear separation of modules and environments
- State locking prevents concurrent modifications

### Negative

- HCL syntax has a learning curve
- Terragrunt adds another layer of abstraction
- State file management requires care
- Drift detection requires manual runs

### Mitigations

- Document common Terraform patterns
- Use CI to run `terraform plan` on PRs
- Implement state backup and versioning
- Consider Terraform Cloud for enhanced features (future)
