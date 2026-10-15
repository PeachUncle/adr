---
status: 'superseded by ADR-0032'
date: 2025-09-24
decision-makers: Product Owner, Development Team
consulted: DevOps Engineers, Frontend Developers
informed: Project Stakeholders
---

# Use GitHub Actions Controlled Vercel Deployment

> **⚠️ SUPERSEDED**: This decision has been superseded by [ADR-0032: Switch from Vercel to Netlify for Integrated Form Handling](0032-switch-from-vercel-to-netlify-for-integrated-form-handling.proposed.md). The project has switched to Netlify hosting to enable form handling capabilities required for email capture functionality.

## Context and Problem Statement

We need to establish a deployment architecture for the voder.ai website that balances simplicity with essential capabilities. After removing the previous complex CI/CD infrastructure, we must choose how to implement deployment to Vercel with quality gates, post-deployment validation, and rollback capabilities.

The deployment solution must support:

- Quality checks before deployment (lint, test, build, security)
- Post-deployment validation and health checks
- Automatic rollback capabilities on deployment failures
- Simple maintenance and operation

## Decision Drivers

- **Quality Assurance**: Must prevent broken deployments through pre-deployment checks
- **Reliability**: Must support automatic rollback if post-deployment validation fails
- **Simplicity**: Avoid over-engineering while meeting essential requirements
- **Cost Effectiveness**: Minimize additional service costs and complexity
- **Team Expertise**: Leverage existing GitHub and Vercel knowledge
- **Observability**: Clear logging and deployment status tracking
- **Speed**: Fast deployment and rollback cycles

## Considered Options

1. **GitHub Actions Controlled Deployment** - Run quality checks and deploy via Vercel CLI from GitHub Actions
2. **Vercel Git Integration with Protection** - Let Vercel handle everything with built-in protections
3. **Hybrid GitHub Quality + Vercel Auto-deploy** - Quality checks in GitHub, deployment in Vercel
4. **GitHub Deployment Environments** - Full enterprise deployment pipeline with staging
5. **External CI/CD + Vercel** - Use third-party CI/CD service with Vercel deployment

## Decision Outcome

Chosen option: **"GitHub Actions Controlled Deployment"**, because it is the only option that meets all our critical requirements while maintaining appropriate simplicity.

### Implementation Architecture

```text
GitHub Push → Quality Gates → Deploy to Vercel → Health Checks → Rollback if Failed
├── Pre-deployment: Lint, Test, Build, Security Scan
├── Deployment: Deploy via `vercel --prod` CLI
├── Post-deployment: URL validation, smoke tests, health checks
└── Rollback: Automatic via `vercel rollback` or Git revert + redeploy
```

### Workflow Components

1. **Quality Gates**:
   - ESLint for code quality
   - Unit tests with Vitest
   - TypeScript compilation
   - Production build validation
   - Security dependency scanning

2. **Deployment Process**:
   - Deploy using Vercel CLI from GitHub Actions
   - Set deployment metadata (commit SHA, build info)
   - Wait for deployment completion

3. **Post-Deployment Validation**:
   - HTTP health checks on deployed URL
   - Smoke tests for critical functionality
   - Performance baseline validation
   - Error rate monitoring

4. **Rollback Mechanisms**:
   - Automatic rollback via `vercel rollback` to previous deployment
   - Git-based rollback: revert commit and trigger new deployment
   - Manual intervention capability for complex scenarios

### Consequences

**Good:**

- ✅ **Meets all requirements**: Quality checks, post-deployment validation, automatic rollback
- ✅ **Right complexity level**: Not too simple (missing features) or over-engineered
- ✅ **Cost effective**: Uses existing GitHub Actions, no additional services required
- ✅ **Team familiarity**: Builds on existing GitHub and Vercel experience
- ✅ **Fast rollback**: Multiple rollback strategies with sub-minute recovery times
- ✅ **Flexible evolution**: Can upgrade to GitHub Deployment Environments later if needed
- ✅ **Clear observability**: All deployment steps logged in GitHub Actions
- ✅ **Deployment gates**: Prevents broken code from reaching production

**Bad:**

- ❌ **GitHub Actions costs**: Execution time costs for quality checks and deployment
- ❌ **Token management**: Need to securely manage Vercel deployment tokens
- ❌ **Single point of failure**: GitHub Actions outage affects deployments
- ❌ **Setup complexity**: More complex initial setup than simple auto-deploy

**Neutral:**

- **Learning curve**: Team needs to understand GitHub Actions deployment workflows
- **Maintenance**: Requires ongoing maintenance of workflow configurations

### Confirmation

Implementation success will be confirmed by:

1. **Functional Testing**:
   - Quality checks successfully prevent broken deployments
   - Post-deployment validation catches runtime issues
   - Rollback mechanisms work reliably within SLA timeframes

2. **Performance Metrics**:
   - Deployment time from commit to live: < 5 minutes
   - Rollback time: < 2 minutes
   - False positive rate for quality checks: < 5%

3. **Operational Validation**:
   - Zero production outages due to broken deployments
   - All deployment failures automatically resolved through rollback
   - Clear audit trail for all deployment activities

## Pros and Cons of the Options

### GitHub Actions Controlled Deployment

**Implementation**: Quality checks in GitHub Actions → Deploy via Vercel CLI → Post-deployment validation → Automatic rollback

- Good, because it provides complete control over the deployment pipeline
- Good, because it supports sophisticated post-deployment validation logic
- Good, because it enables multiple rollback strategies (Vercel CLI + Git-based)
- Good, because it leverages existing team expertise with GitHub Actions
- Good, because it provides detailed logging and observability
- Bad, because it requires managing Vercel CLI tokens securely
- Bad, because it adds GitHub Actions execution costs

### Vercel Git Integration with Protection

**Implementation**: Git push → Vercel auto-build with quality checks → Deploy

- Good, because it has the simplest setup and maintenance
- Good, because it provides native Vercel integration without external dependencies
- Bad, because it has very limited post-deployment validation capabilities
- Bad, because it lacks automatic rollback mechanisms
- Bad, because quality check capabilities are limited (no security scanning, complex test scenarios)
- **Neutral, because this option was ruled out due to missing critical requirements**

### Hybrid GitHub Quality + Vercel Auto-deploy

**Implementation**: GitHub Actions for quality → Success triggers Vercel auto-deploy → Manual rollback

- Good, because it provides robust quality checking capabilities
- Good, because it uses native Vercel deployment features
- Bad, because it lacks automatic post-deployment validation
- Bad, because rollback is manual-only process
- Bad, because it requires complex coordination between two systems
- **Neutral, because this option was ruled out due to missing automatic rollback**

### GitHub Deployment Environments

**Implementation**: Quality checks → Deploy to staging → Validation → Deploy to production → Post-deployment checks

- Good, because it provides enterprise-grade deployment controls
- Good, because it supports sophisticated approval workflows
- Good, because it offers the most comprehensive audit trails
- Good, because it enables complex multi-environment validation scenarios
- Bad, because it has the highest implementation and maintenance complexity
- Bad, because it requires GitHub Pro/Enterprise features
- Neutral, because this is viable but over-engineered for current needs

### External CI/CD + Vercel

**Implementation**: External CI service → Quality checks → Deploy to Vercel → Validation

- Good, because it often provides superior rollback and deployment features
- Good, because it offers more flexibility in tooling choices
- Good, because it can support complex validation scenarios
- Bad, because it adds additional service costs and vendor dependencies
- Bad, because it requires learning new tools and integrations
- Bad, because it increases overall system complexity
- Neutral, because this is viable but adds unnecessary complexity

## More Information

This decision supports the project's goal of maintaining essential deployment capabilities while avoiding the complexity that led to the previous infrastructure removal. The chosen approach can evolve naturally:

- **Phase 1**: Implement basic GitHub Actions controlled deployment
- **Phase 2**: Add more sophisticated health checks and monitoring
- **Phase 3**: Consider upgrading to GitHub Deployment Environments if enterprise features become necessary

**Related Decisions**:

- [ADR-0026: Use Vercel for Static Site Deployment](0026-use-vercel-for-static-site-deployment.accepted.md) - Establishes Vercel as deployment platform
- [ADR-0024: Adopt DORA-style Trunk-based Development](0024-adopt-dora-style-trunk-based-development.accepted.md) - Deployment strategy must support trunk-based workflow

**Implementation Timeline**: This decision enables the re-implementation of deployment capabilities that were removed during the infrastructure cleanup, providing a clean foundation for reliable deployments.
