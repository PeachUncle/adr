# ADR-015: Deployment Strategy and CI/CD Pipeline

## Status
Accepted and Implemented

## Implementation Notes
- **Landing Page Deployment**: Implemented using OpenNext Cloudflare adapter (`@opennextjs/cloudflare v1.11.0`)
- **First Production Deployment**: November 2024 - Landing page deployed to Cloudflare Workers
- **CI/CD Pipeline**: GitHub Actions workflows operational for quality gates and automated deployment
- **Environment Strategy**: Staging (develop branch) and Production (main branch) environments active

## Context
We need to define our deployment strategy including CI/CD pipeline design, database migration handling, disaster recovery planning, blue/green deployments, and monitoring/alerting infrastructure. This strategy must support our event-sourced, multi-service architecture while maintaining simplicity for initial development.

## Decision

### Deployment Architecture Strategy

**Hybrid Deployment Architecture Implemented:**

- **Decentralized App-Centric Deployment**: Each application/service owns its deployment configuration and process
- **Technology Agnostic**: Apps can use different tech stacks (Node.js, Python, Docker, static sites)
- **Universal Makefile Interface**: Root Makefile provides consistent deployment commands across all apps
- **Platform-Specific Logic**: Apps deploy to their target platforms (Cloudflare Workers/Pages, AWS ECS/Lambda/S3)
- **Shared Deployment Functions**: Common deployment patterns abstracted into reusable functions

**Implemented Directory Structure:**

```text
/workspaces/
├── Makefile                      # Universal deployment orchestration (IMPLEMENTED)
├── deploy/                       # Shared deployment functions (IMPLEMENTED)
│   ├── shared.mk                 # Common deployment patterns
│   ├── doppler.mk               # Centralized secret management
│   ├── cloudflare.mk            # Cloudflare Workers/Pages deployment
│   ├── aws.mk                   # AWS ECS/Lambda/S3 deployment
│   └── app-template.mk          # Template for individual app Makefiles
├── apps/
│   ├── landing-page/
│   │   ├── Makefile              # Technology: nextjs, Target: cloudflare-worker
│   │   ├── package.json          # Node.js dependencies
│   │   ├── next.config.js        # Next.js + OpenNext configuration
│   │   ├── open-next.config.ts   # OpenNext Cloudflare configuration
│   │   └── wrangler.toml         # Cloudflare Worker config (not Pages)
│   └── qis-data-management/
│       ├── Makefile              # Technology: python, Target: aws-ecs
│       ├── requirements.txt      # Python dependencies
│       └── deploy/
│           ├── Dockerfile        # Container configuration
│           └── ecs-task-definition.json
├── services/
│   ├── accounts/
│   │   ├── Makefile              # Technology: nodejs, Target: cloudflare-worker
│   │   └── wrangler.toml         # Cloudflare Worker config
│   └── admin/
│       ├── Makefile              # Technology: docker, Target: aws-ecs
│       ├── Dockerfile
│       └── deploy/
│           └── ecs-task-definition.json
└── .github/
    └── workflows/
        ├── deploy.yml            # Main deployment pipeline (IMPLEMENTED)
        ├── test.yml              # Testing pipeline (IMPLEMENTED)
        ├── security.yml          # Security scanning (IMPLEMENTED)
        └── quality.yml           # Code quality checks (IMPLEMENTED)
```

**Universal Deployment Commands (IMPLEMENTED):**

```bash
# Deploy all applications and services
make deploy-all ENV=development

# Deploy specific application with change detection
make deploy-app APP=landing-page ENV=production

# Deploy specific service
make deploy-service SERVICE=accounts ENV=development

# Test all components
make test-all

# Health check all deployed services
make health-check-all ENV=production

# Setup development environment
make setup-env

# List available components
make list-apps
make list-services
```

### CI/CD Pipeline Design

**GitHub Actions as Primary CI/CD:**

- **Change Detection**: Path-based triggers deploy only modified applications
- **Parallel Deployment**: Independent apps deploy simultaneously when possible
- **Platform-Aware**: Different deployment strategies per target platform
- **Universal Commands**: CI/CD uses same Makefile interface as local development

**Pipeline Stages:**

```yaml
# .github/workflows/orchestrate-deploy.yml structure
stages:
  - detect-changes:   # Identify modified apps using dorny/paths-filter
  - quality-gates:    # Run tests only for changed apps + dependencies
  - deploy-apps:      # Deploy each changed app using its Makefile
  - validate-deploy:  # Health checks for deployed services
```

**Deployment Orchestration:**

```makefile
# Root Makefile interface
make deploy-all ENV=development     # Deploy all apps to development
make deploy-app APP=apps/landing-page ENV=production  # Deploy specific app
make test-all                       # Test all apps
make test-app APP=services/accounts # Test specific app
```

**Code Quality Gates:**

- **SonarQube integration**: Quality gate must pass before deployment
- **Coverage threshold**: Minimum 80% test coverage for new code
- **Security scanning**: SAST/DAST scans must pass
- **Dependency scanning**: Vulnerability checks for all dependencies
- **Code duplication**: Maximum 3% duplication allowed

**Environment Promotion:**
- **Feature branches**: Developed and tested locally (not deployed)
- **Develop branch**: Auto-deploy to staging environment (pre-production validation)
- **Main branch**: Automatic production deployment after successful quality gates
- **Rollback capability**: Previous versions tagged and available for quick rollback

### Code Quality Strategy

**SonarQube Integration:**
- **Quality profiles**: Custom profiles for TypeScript, JavaScript, and SQL
- **Quality gates**: Enforce coverage, reliability, security, and maintainability thresholds
- **Pull request decoration**: SonarQube analysis results displayed in PR reviews
- **Technical debt tracking**: Monitor and track technical debt over time

**SonarQube Configuration:**
```yaml
# sonar-project.properties
sonar.projectKey=tomriddelsdell-platform
sonar.organization=tomriddelsdell
sonar.sources=src/
sonar.tests=src/
sonar.test.inclusions=**/*.test.ts,**/*.spec.ts
sonar.coverage.exclusions=**/*.test.ts,**/*.spec.ts,**/migrations/**
sonar.typescript.lcov.reportPaths=coverage/lcov.info
sonar.javascript.lcov.reportPaths=coverage/lcov.info

# Quality Gate Conditions
sonar.qualitygate.wait=true
coverage.threshold=80
reliability_rating.threshold=A
security_rating.threshold=A
maintainability_rating.threshold=A
duplicated_lines_density.threshold=3
```

**Automated Quality Checks:**
- **Pre-commit hooks**: ESLint, Prettier, type checking
- **PR quality checks**: SonarQube analysis, security scans, test coverage
- **Deployment gates**: All quality checks must pass before production deployment
- **Quality metrics**: Track trends in technical debt, coverage, and code quality

### Platform-Specific Deployment Details

#### Next.js Applications (OpenNext Cloudflare)

**Landing Page - Cloudflare Workers Deployment:**

The landing-page application uses OpenNext Cloudflare adapter (`@opennextjs/cloudflare`) to deploy Next.js to Cloudflare Workers.

**Build Process:**
```bash
# Build command (runs in GitHub Actions and locally)
pnpm run build:cloudflare

# Under the hood this executes:
npx opennextjs-cloudflare build
```

**Deployment:**
```bash
# Staging deployment
pnpm opennextjs-cloudflare deploy --env preview

# Production deployment  
pnpm opennextjs-cloudflare deploy --env production
```

**Critical Configuration Requirements:**

1. **pnpm Configuration** - Root `.npmrc` must contain:
   ```ini
   # OpenNext requires flat node_modules (no symlinks)
   node-linker=hoisted
   shamefully-hoist=true
   ```
   This is required because OpenNext's esbuild bundler cannot resolve through pnpm's `.pnpm/` symlink structure.

2. **Wrangler Configuration** - `wrangler.toml`:
   ```toml
   compatibility_date = "2024-09-23"  # Minimum for automatic Node.js built-ins
   compatibility_flags = ["nodejs_compat"]
   main = ".open-next/worker.js"
   
   # R2 bucket for ISR/caching (required for both preview and production)
   [[r2_buckets]]
   binding = "NEXT_INC_CACHE_R2_BUCKET"
   bucket_name = "landing-page-cache"
   ```

3. **Next.js Configuration** - `next.config.js`:
   ```javascript
   import { initOpenNextCloudflareForDev } from "@opennextjs/cloudflare";
   
   // Required for Cloudflare bindings access during development
   initOpenNextCloudflareForDev();
   ```

4. **R2 Bucket Requirements:**
   - Bucket must be created before first deployment
   - Required for ISR (Incremental Static Regeneration) and caching
   - Bucket name configured in both `[env.preview]` and `[env.production]` sections

**GitHub Actions Integration:**
```yaml
# Quality gates job must create .npmrc before pnpm install
- name: Setup pnpm for OpenNext
  run: |
    echo "node-linker=hoisted" > .npmrc
    echo "shamefully-hoist=true" >> .npmrc

# Build step
- name: Build application
  run: pnpm run build:cloudflare

# Deploy step (staging)
- name: Deploy to Cloudflare Workers (Preview)
  run: pnpm opennextjs-cloudflare deploy --env preview
  env:
    CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
    CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}

# Health check
- name: Health Check
  run: |
    curl --fail https://landing-page-preview.t-riddelsdell.workers.dev/api/health
    curl --fail https://landing-page-preview.t-riddelsdell.workers.dev/api/metrics
```

**Deployment URLs:**
- **Staging**: `https://landing-page-preview.t-riddelsdell.workers.dev`
- **Production**: `https://landing-page-prod.t-riddelsdell.workers.dev`

**Build Output:**
- Build artifacts: `.open-next/` directory (gitignored)
- Worker entry point: `.open-next/worker.js`
- Static assets: Bundled into Worker deployment

**Limitations & Considerations:**
- OpenNext adapter compatibility limited to Next.js 14.x (14.2.18 verified)
- R2 bucket required even if ISR not actively used
- Worker compatibility_date must be >= 2024-09-23 for Node.js built-ins
- pnpm `node-linker=hoisted` affects entire monorepo (trade-off for OpenNext support)

### Database Migration Strategy

**Event Store Migration Approach:**
- **Schema evolution**: Additive changes only (new columns, tables, indexes)
- **Breaking changes**: Implement as new event types with upcasting
- **Migration scripts**: Stored in `/migrations` with version numbering
- **Rollback strategy**: Forward-only migrations with compensating scripts

**Projection Migration Strategy:**
- **Projection rebuilds**: Full rebuilds from event history when schema changes
- **Zero-downtime updates**: New projection versions run in parallel during migration
- **Checkpoint management**: Track migration progress and resume capability
- **Validation**: Compare old vs new projections before switching traffic

**Migration Process:**
1. **Pre-deployment**: Validate migration scripts in staging
2. **Deployment**: Apply additive schema changes first
3. **Data migration**: Rebuild affected projections from events
4. **Validation**: Verify data integrity and performance
5. **Cleanup**: Remove deprecated schemas after successful migration

### Disaster Recovery Plan

**Backup Strategies:**
- **Event store backups**: Daily automated backups with 30-day retention
- **Point-in-time recovery**: Leverage Neon's PITR capabilities (7-day window initially)
- **Cross-region replication**: Event store replicated to secondary region
- **Projection backups**: Daily snapshots of projection databases

**Recovery Time/Point Objectives:**
- **RTO (Recovery Time Objective)**: 4 hours for full service restoration
- **RPO (Recovery Point Objective)**: 1 hour maximum data loss
- **Critical path**: Event store → Core projections → Application services

**Disaster Scenarios:**
- **Database corruption**: Restore from PITR or latest backup
- **Region failure**: Failover to secondary region with event store replica
- **Application bugs**: Rollback to previous version + projection rebuild
- **Data center outage**: Cloudflare Workers provide geographic distribution

### Blue/Green and Canary Deployments

**Initial Approach: Simple Blue/Green**
- **Blue environment**: Current production version
- **Green environment**: New version deployed and tested
- **Traffic switching**: DNS-based cutover via Cloudflare
- **Rollback**: Immediate DNS switch back to blue environment
- **Automated health checks**: New version must pass health checks before traffic switch

**Canary Strategy (Future):**
- **Traffic percentage**: Start with 5% traffic to new version
- **Monitoring period**: 30 minutes before increasing traffic
- **Success criteria**: Error rates < 1%, latency within 10% of baseline
- **Automatic rollback**: If error thresholds exceeded

**Implementation:**
```typescript
// Deployment configuration
interface DeploymentConfig {
  strategy: 'blue-green' | 'canary';
  canaryPercentage?: number;
  monitoringPeriod: string;
  rollbackThresholds: {
    errorRate: number;
    latencyIncrease: number;
  };
  qualityGates: {
    sonarQube: boolean;
    testCoverage: number;
    securityScan: boolean;
    healthChecks: boolean;
  };
}
```

### Monitoring and Alerting

**Service Level Indicators (SLIs):**
- **Availability**: 99.5% uptime for core user journeys
- **Latency**: 95th percentile response time < 2 seconds
- **Error rate**: < 1% error rate for API requests
- **Event processing lag**: < 5 minutes for projection updates

**Service Level Objectives (SLOs):**
- **Monthly uptime**: 99.5% (3.6 hours downtime per month)
- **API response time**: P95 < 2s, P99 < 5s
- **Event processing**: 95% of events processed within 1 minute
- **Error budget**: 0.5% monthly error budget for graceful degradation

**Alerting Strategy:**
- **Critical alerts**: Page immediately (uptime, security, data loss)
- **Warning alerts**: Slack notifications (performance degradation, high error rates)
- **Info alerts**: Dashboard updates (capacity planning, trends)

**Monitoring Stack:**
- **Application metrics**: Custom metrics via Cloudflare Workers analytics
- **Infrastructure metrics**: Neon database monitoring + custom dashboards
- **Log aggregation**: Cloudflare Workers logs + structured logging
- **Alerting**: Cloudflare notifications + webhook integrations

## Implementation Details

### Environment Configuration
```yaml
environments:
  development:
    database: "neon-dev-branch"
    workers_env: "dev"
    monitoring: "basic"
    sonarqube: "disabled"
    
  staging:
    database: "neon-staging-branch"
    workers_env: "staging"
    monitoring: "full"
    sonarqube: "enabled"
    
  production:
    database: "neon-main"
    workers_env: "production"
    monitoring: "full"
    sonarqube: "enabled"
    backup_schedule: "daily"
```

### Deployment Checklist
- [ ] Code quality checks pass (SonarQube quality gate)
- [ ] All tests pass (unit, integration, e2e)
- [ ] Test coverage meets threshold (80% minimum)
- [ ] Security scans clean (SAST/DAST)
- [ ] Dependency vulnerability scans pass
- [ ] Database migrations validated
- [ ] Projection rebuilds completed
- [ ] Performance benchmarks met
- [ ] Health checks pass in target environment
- [ ] Monitoring dashboards updated
- [ ] Rollback plan documented

### SonarQube Integration Pipeline
```yaml
# Example GitHub Actions integration
- name: SonarQube Scan
  uses: sonarqube-quality-gate-action@master
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    
- name: Quality Gate Check
  run: |
    if [ "${{ steps.sonarqube.outputs.quality-gate-status }}" != "PASSED" ]; then
      echo "SonarQube quality gate failed"
      exit 1
    fi
```

## Alternatives Considered

1. **Kubernetes-based deployment**: Too complex for current scale
2. **Multi-cloud strategy**: Unnecessary complexity for MVP
3. **Complex canary deployments**: Premature optimization
4. **Real-time database replication**: Cost vs benefit not justified initially
5. **Manual production approvals**: Creates deployment bottleneck and reduces velocity
6. **Alternative code quality tools**: Considered CodeClimate and Codacy, but SonarQube provides better integration and customization

## Consequences

**Benefits:**
- **Simple, reliable deployments** using proven GitHub Actions
- **Quick rollback capability** via blue/green switching
- **Comprehensive monitoring** aligned with business objectives
- **Automated testing and quality gates** prevent deployment of broken code
- **Database safety** through additive migrations and PITR
- **Continuous quality improvement** through SonarQube integration
- **Faster deployment velocity** without manual approval bottlenecks

**Drawbacks:**
- **GitHub Actions dependency** creates single point of failure
- **Limited canary capabilities** initially
- **Cross-region complexity** deferred to future phases
- **Quality gate failures** may block deployments temporarily
- **SonarQube maintenance** adds operational overhead

## Trade-offs

**Automation vs Control:**
- Choosing automated deployment over manual approval gates
- Relying on comprehensive quality checks instead of human approval

**Quality vs Speed:**
- Enforcing quality gates may slow individual deployments
- Preventing technical debt accumulation improves long-term velocity

**Simplicity vs Advanced Features:**
- Choosing proven, simple approaches over cutting-edge deployment strategies
- Adding SonarQube complexity for long-term code quality benefits

**Cost vs Resilience:**
- Basic disaster recovery vs comprehensive multi-region setup
- Balanced approach to monitoring vs full observability stack

## Migration Strategy

**Phase 1: Basic CI/CD with Quality Gates (MVP)**
- GitHub Actions with automated production deployment
- SonarQube integration and quality gates
- Blue/green deployments via DNS switching
- Basic monitoring and alerting
- Neon PITR for disaster recovery

**Phase 2: Enhanced Automation**
- Automated canary deployments
- Advanced SonarQube rules and quality profiles
- Cross-region backup strategy
- Performance regression testing
- Enhanced security scanning

**Phase 3: Advanced Operations**
- Chaos engineering practices
- Advanced capacity planning
- Multi-region active-active setup
- Comprehensive observability stack
- Advanced quality metrics and trends

## Security Considerations

**Deployment Security:**
- **Secret management**: GitHub Actions secrets for credentials
- **Image scanning**: Container vulnerability scanning in CI/CD
- **Access control**: Least privilege for deployment automation
- **Audit logging**: All deployment actions logged and monitored
- **SonarQube security**: SAST analysis integrated into quality gates

**Environment Isolation:**
- **Network segmentation**: Staging and production in separate environments
- **Data isolation**: No production data in lower environments
- **Access restrictions**: Production access limited to specific personnel
- **Compliance**: Deployment process supports audit requirements
- **Quality governance**: SonarQube quality profiles enforce security standards
