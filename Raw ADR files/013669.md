# ADR-003: Use GitHub Actions for CI/CD

## Status
Accepted

## Context
We need a CI/CD solution to automate:
- Infrastructure deployments (Terraform)
- Code testing and validation
- Multi-environment deployments (dev, staging, production)
- Pull request validation
- Security scanning

The team uses GitHub for source control. Options considered: GitHub Actions, Azure DevOps, Jenkins, GitLab CI

## Decision
We will use **GitHub Actions** as our CI/CD platform for both infrastructure and application deployments.

## Consequences

### Positive
- **Native GitHub integration**: Seamless integration with pull requests and code review
- **No additional infrastructure**: No separate CI/CD server to manage
- **YAML-based workflows**: Version-controlled pipeline definitions
- **Marketplace ecosystem**: Large library of pre-built actions
- **Matrix builds**: Easy parallel execution across environments
- **Secrets management**: Built-in secrets management per environment
- **Environment protection**: Manual approval gates for sensitive deployments
- **Cost-effective**: Generous free tier, included with GitHub
- **Team familiarity**: Team already uses GitHub

### Negative
- **GitHub dependency**: Coupled to GitHub platform
- **Workflow complexity**: YAML can become complex for advanced scenarios
- **Limited debugging**: Harder to debug compared to local CI/CD tools
- **Runner limits**: Usage limits on free tier (mitigated with paid plan)

## Alternatives Considered

### Azure DevOps Pipelines
**Pros**: Native Azure integration, mature platform, advanced features
**Cons**: Additional platform to learn, separate from GitHub, context switching
**Reason rejected**: GitHub Actions provides sufficient features with better DX

### Jenkins
**Pros**: Very flexible, large plugin ecosystem, self-hosted
**Cons**: Requires server management, outdated UI, complex configuration
**Reason rejected**: Operational overhead not justified

### GitLab CI
**Pros**: Integrated solution, good Docker support
**Cons**: Would require migration from GitHub, team lacks experience
**Reason rejected**: Team commitment to GitHub ecosystem

## Implementation Details

### Workflow Structure

```
.github/workflows/
├── reusable-terraform.yml      # Shared Terraform workflow
├── terraform-plan.yml          # PR validation
├── terraform-deploy-dev.yml    # Auto-deploy to dev
├── terraform-deploy-staging.yml # Manual staging deploy
├── terraform-deploy-production.yml # Manual prod deploy
├── terraform-destroy.yml       # Infrastructure teardown
└── database-deploy.yml         # Database schema deployment
```

### Deployment Strategy

1. **Pull Request**: Automatic Terraform plan, security scan
2. **Merge to Main**: Automatic deployment to dev
3. **Staging**: Manual workflow dispatch with approval
4. **Production**: Manual workflow dispatch with confirmation + approval

### Security Features
- Separate service principals per environment
- GitHub environment secrets
- Environment protection rules
- Manual approval gates for staging/production
- Snyk security scanning on every PR

### Secrets Management

| Secret Type | Storage | Access |
|-------------|---------|--------|
| Azure Credentials | GitHub Secrets | Per environment |
| PostgreSQL Passwords | GitHub Secrets | Per environment |
| API Keys | GitHub Secrets | Global |

## Performance Considerations

- **Workflow duration**: Target < 10 minutes for deployments
- **Parallel execution**: Use matrix strategy for multiple environments
- **Caching**: Cache Terraform providers and modules
- **Reusable workflows**: DRY principle with shared workflows

## References
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure Login Action](https://github.com/Azure/login)
- [Terraform GitHub Actions](https://github.com/hashicorp/setup-terraform)

## Date
2025-12-04

## Author
Infrastructure Team

