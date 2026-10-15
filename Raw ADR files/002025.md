# ADR-0004: Use GitHub Actions for CI/CD

## Status

Accepted

## Context

Grafana-banana requires automated continuous integration and continuous deployment (CI/CD) to ensure code quality, automate testing, and streamline releases. The CI/CD solution needs to:

- Automatically build and test code on every commit
- Run tests for both frontend and backend
- Perform security scanning
- Build and publish Docker containers
- Create GitHub releases with semantic versioning
- Support multiple workflows (CI, release, container testing)
- Be cost-effective for open-source projects
- Integrate seamlessly with GitHub repository
- Support caching and optimization
- Enable matrix builds for different configurations
- Be maintainable and well-documented

## Decision

We will use GitHub Actions as our CI/CD platform, implementing multiple workflows for different purposes:

1. **CI Workflow**: Build and test on every push/PR
2. **Release Workflow**: Manual releases with tagged versions
3. **Publish Release Workflow**: Automatic releases on main branch
4. **Container Testing**: Test Docker builds on PRs
5. **Maintenance Workflows**: Stale issues, greetings, labeling

## Consequences

### Positive

1. **Native Integration**: Seamlessly integrated with GitHub
2. **No Additional Service**: No need for external CI/CD service
3. **Free for Open Source**: Generous free tier for public repositories
4. **Marketplace**: Large marketplace of pre-built actions
5. **YAML Configuration**: Simple, readable workflow definitions
6. **Matrix Builds**: Easy parallel builds for multiple configurations
7. **Caching**: Built-in caching for dependencies and build artifacts
8. **Secrets Management**: Secure secrets handling
9. **Status Checks**: Automatic PR status checks
10. **Container Registry**: Integrated GitHub Container Registry (GHCR)
11. **Release Automation**: Built-in GitHub Releases integration
12. **Environment Support**: Multiple environments (dev, staging, prod)
13. **Approval Workflows**: Manual approval gates for deployments
14. **Audit Logs**: Complete audit trail of workflow runs
15. **Good Documentation**: Comprehensive GitHub documentation

### Negative

1. **Vendor Lock-in**: Tied to GitHub platform
2. **Limited Debugging**: Harder to debug workflows locally
3. **YAML Complexity**: Complex workflows can become hard to maintain
4. **Rate Limits**: API rate limits can affect workflows
5. **Runner Limitations**: Limited control over hosted runners
6. **Proprietary**: Not open source like some alternatives
7. **Cost at Scale**: Can become expensive for private repos with heavy usage
8. **Workflow Size**: Limited to 1000 concurrent jobs

### Neutral

1. **Learning Curve**: Need to learn Actions-specific syntax
2. **Hosted Runners**: Use GitHub-hosted runners (vs. self-hosted)
3. **Job Logs**: Logs expire after retention period
4. **Action Versions**: Need to manage action version updates

## Implementation

### Timeline
- Initial setup: Completed
- All workflows implemented: Completed
- Ongoing: Optimize and maintain workflows

### Owner
@markcoleman

### Dependencies
- GitHub repository with Actions enabled
- GitHub Container Registry (GHCR) for Docker images
- Secrets configured (if needed for external integrations)

### Workflow Structure

```
.github/workflows/
├── ci.yml                    # Build and test on push/PR
├── publish-release.yml       # Auto-release on main branch
├── release.yml              # Manual release workflow
├── test-containers.yml      # Test Docker builds
├── stale.yml               # Stale issue management
├── greetings.yml           # Welcome new contributors
└── labeler.yml             # Auto-label PRs
```

### Key Features Implemented

1. **Concurrency Control**: Automatic cancellation of redundant runs
2. **Path Filters**: Skip CI for documentation-only changes
3. **Caching**: Aggressive caching for .NET, npm, Docker layers
4. **Semantic Versioning**: Automatic version generation
5. **Container Publishing**: Publish to GHCR with version tags
6. **Security**: Dependabot for automated security updates
7. **Code Owners**: CODEOWNERS file for automatic reviewers

### Optimization Strategies

- Use `npm ci --prefer-offline --no-audit` for faster installs
- Cache .NET packages, npm modules, Docker layers
- Skip unnecessary workflows with path filters
- Set appropriate timeouts on all jobs
- Use matrix builds for parallel execution

## Alternatives Considered

### Alternative 1: Jenkins

**Pros:**
- Open source
- Highly customizable
- Large plugin ecosystem
- Self-hosted (full control)
- Mature and proven
- Good for complex pipelines
- Can use custom hardware

**Cons:**
- Requires self-hosting and maintenance
- Infrastructure costs
- Complex setup and configuration
- Older UI/UX
- Plugin management overhead
- Security requires constant attention
- Slower evolution than modern CI tools

**Why Rejected:**
The operational overhead of running and maintaining Jenkins outweighs the benefits. GitHub Actions provides sufficient functionality without infrastructure management.

### Alternative 2: GitLab CI/CD

**Pros:**
- Integrated with GitLab
- Free for open source
- Excellent CI/CD features
- Auto DevOps capabilities
- Built-in container registry
- Self-hosted option
- Good pipeline visualization

**Cons:**
- Requires GitLab platform (would need to migrate)
- Different ecosystem from GitHub
- Migration effort significant
- Less marketplace than GitHub Actions
- Self-hosted version requires maintenance

**Why Rejected:**
Would require migrating from GitHub to GitLab, which is not justified given GitHub Actions meets our needs.

### Alternative 3: CircleCI

**Pros:**
- Fast builds
- Good caching
- Clean UI
- SSH debugging
- Insights and analytics
- Good Docker support
- Orbs (reusable config)

**Cons:**
- External service (another account)
- Cost for private repos
- Limited free tier
- Configuration in separate file
- Less native GitHub integration
- Another service to manage

**Why Rejected:**
As an external service, CircleCI adds complexity and potential costs. GitHub Actions provides native integration without additional services.

### Alternative 4: Travis CI

**Pros:**
- Popular historically
- Simple configuration
- Good for open source
- GitHub integration
- Matrix builds

**Cons:**
- Declining popularity
- Reduced free tier
- Less active development
- Limited features vs. newer tools
- Company stability concerns
- Slower builds recently

**Why Rejected:**
Travis CI has declined in popularity and features compared to newer solutions. GitHub Actions is more actively developed and better integrated.

### Alternative 5: Azure Pipelines

**Pros:**
- Generous free tier
- Good Windows support
- Integrated with Azure
- YAML configuration
- Good for .NET projects
- Cross-platform

**Cons:**
- Microsoft ecosystem lock-in
- Less integrated with GitHub
- More complex configuration
- Requires Azure DevOps account
- Less community momentum
- UI less intuitive

**Why Rejected:**
While Azure Pipelines is powerful, especially for .NET, GitHub Actions provides equal capability with better GitHub integration and no additional accounts.

### Alternative 6: Drone CI

**Pros:**
- Open source
- Container-native
- Simple YAML
- Good Docker integration
- Lightweight
- Can self-host

**Cons:**
- Smaller community
- Less marketplace/plugins
- Requires self-hosting for full features
- Less documentation
- Fewer integrations
- Less mature ecosystem

**Why Rejected:**
Smaller ecosystem and community support make Drone less attractive than GitHub Actions, which has stronger backing and more resources.

### Alternative 7: Self-Hosted Runners with GitHub Actions

**Pros:**
- More control over environment
- Can use custom hardware
- Potentially faster builds
- Access to internal resources
- No runner costs
- Customizable

**Cons:**
- Infrastructure to maintain
- Security responsibility
- Operational overhead
- Need to handle scaling
- Update management

**Why Rejected:**
For current project scale, hosted runners are sufficient. Self-hosted runners would add operational complexity without clear benefits.

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Project CI/CD Documentation](../CI_CD_WORKFLOWS.md)
- [Workflow Optimizations](../../.github/WORKFLOW_OPTIMIZATIONS.md)
- [Project Repository](https://github.com/markcoleman/Grafana-banana)

## Related ADRs

- [ADR-0005: Adopt Semantic Versioning](./ADR-0005-semantic-versioning.md)

## Metadata

| Field | Value |
|-------|-------|
| **Created** | 2025-10-25 |
| **Updated** | 2025-10-25 |
| **Author** | @markcoleman |
| **Reviewers** | Architecture Review Board |
| **Status** | Accepted |
| **Implementation Status** | Complete |
