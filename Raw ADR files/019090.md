# ADR-014: Infrastructure and Deployment Strategy

## Status

Accepted and Implemented

## Implementation Notes
- **First Production Deployment**: Landing page deployed to Cloudflare Workers (November 2024)
- **Secrets Management**: Doppler implemented for centralized secrets management
- **CI/CD**: GitHub Actions workflows operational with automated quality gates
- **Infrastructure**: Terraform modules in development for Neon, Cloudflare, and Kafka Cloud
- **Security Scanning**: Pre-commit hooks and GitHub Actions integration planned

## Context

We need to define our CI/CD pipeline, environment management, deployment strategies, and infrastructure as code approach for the platform.

## Decision

### Environment Strategy

- **Production**: Live platform (main branch)
- **Staging**: Pre-production testing (develop branch)
- **Development**: Feature development (feature branches)
- **Ephemeral**: PR preview environments

### CI/CD Pipeline

- **GitHub Actions** for all automation
- **Terraform** for infrastructure as code
- **Docker containers** for consistent deployments
- **Automated testing** gates before deployment

### Deployment Strategy

- **Blue/green deployments** for zero downtime
- **Canary releases** for high-risk changes
- **Feature flags** for gradual rollouts
- **Automated rollback** on health check failures

### Infrastructure Components

**Compute & Hosting:**
- **Cloudflare Workers**: Serverless compute for Next.js applications (via OpenNext), APIs, and microservices
- **Deployment Adapter**: `@opennextjs/cloudflare` for Next.js → Workers deployment

**Data Storage:**
- **Neon PostgreSQL**: Event store and read model databases with branching capability
- **Cloudflare R2**: Static assets and Next.js ISR/caching storage

**Messaging & Events:**
- **Kafka Cloud (Confluent)**: Event bus for domain events and integration events
- **Event Sourcing**: All state changes captured as events in PostgreSQL

**Caching & Session:**
- **Redis Cloud**: Planned for session management and read model caching

**Secrets Management:**
- **Doppler**: Centralized secrets management across all environments (dev, staging, production)

### Deployment Pipeline

**Implemented GitHub Actions Workflows:**

```yaml
# .github/workflows/deploy-landing-page.yml (IMPLEMENTED)
name: Deploy Landing Page
on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  quality-gates:
    # Type checking, linting, testing, coverage checks
    # Runs for all branches and PRs
    
  deploy-staging:
    if: github.ref == 'refs/heads/develop'
    # Automated deployment to staging environment
    # URL: https://landing-page-preview.t-riddelsdell.workers.dev
    # Custom domain: https://staging.tomriddelsdell.com
    
  lighthouse-ci:
    needs: [deploy-staging, deploy-production]
    # Performance testing with Lighthouse CI (post-deployment)
    # Tests Core Web Vitals, performance budgets, accessibility
    # Runs after successful deployment to staging or production
    
  deploy-production:
    if: github.ref == 'refs/heads/main'
    # Automated deployment to production
    # URL: https://landing-page-prod.t-riddelsdell.workers.dev
    # Custom domain: https://tomriddelsdell.com
    # Includes smoke tests and health checks
    
  post-deploy-checks:
    # Comprehensive health checks and performance monitoring
    # Verifies all critical endpoints and metrics
```

**Implemented Security & Quality:**
1. ✅ **Security Scanning**: Pre-commit secret detection, .gitignore verification
2. ✅ **Secret Management**: Doppler for all environment variables and API tokens
3. ✅ **Performance Testing**: Lighthouse CI integrated into deployment pipeline
   - Core Web Vitals monitoring (LCP, FID, CLS, TBT)
   - Performance budgets enforced (images < 500KB, total < 1MB)
   - Accessibility and SEO validation
   - Post-deployment quality gates
4. 🔄 **Dependency Updates**: Planned with Dependabot (not yet configured)
5. 🔄 **Cost Monitoring**: Planned via Cloudflare analytics (not yet configured)
6. ✅ **Quality Gates**: Type checking, linting, test coverage enforced in CI/CD

## Custom Domain Configuration

### Cloudflare Workers Routes

Custom domains are configured using Cloudflare Worker Routes in `wrangler.toml`:

```toml
# Staging environment
[env.preview]
name = "landing-page-preview"
workers_dev = true  # Keeps .workers.dev subdomain active

[[env.preview.routes]]
pattern = "staging.tomriddelsdell.com/*"
zone_name = "tomriddelsdell.com"

# Production environment
[env.production]
name = "landing-page-prod"
workers_dev = true

[[env.production.routes]]
pattern = "tomriddelsdell.com/*"
zone_name = "tomriddelsdell.com"

[[env.production.routes]]
pattern = "www.tomriddelsdell.com/*"
zone_name = "tomriddelsdell.com"
```

**Key Configuration Notes:**
- Use `zone_name` approach (not `custom_domain = true`) to avoid DNS conflicts
- Include `/*` wildcard pattern for proper route matching
- Keep `workers_dev = true` to maintain `.workers.dev` subdomain access
- DNS records managed automatically by Cloudflare when routes are deployed
- Each environment maintains both custom domain and workers.dev access

## Database Migration Strategy

- **Forward-only migrations** with event store compatibility
- **Projection rebuilding** as part of deployment process
- **Migration rollback** capability for emergency scenarios

## Monitoring and Observability

- **Cloudflare Analytics** for basic metrics
- **Custom metrics** via Worker analytics
- **Log aggregation** using Cloudflare Logs
- **Alert integration** with email/Slack

## Alternatives Considered

1. **Kubernetes**: Overkill for Worker-based architecture
2. **Serverless Framework**: Less control than native Cloudflare tooling
3. **Manual deployments**: Not scalable or reliable

## Consequences

- Fully automated deployment pipeline
- Infrastructure as code for reproducibility
- Zero-downtime deployments capability
- Clear environment separation

## Trade-offs

**Benefits:**

- Automated and reliable deployments
- Infrastructure version control
- Multiple environment support
- Rollback capabilities

**Drawbacks:**

- Initial setup complexity
- Pipeline maintenance overhead
- Cloud provider lock-in considerations

```

```
