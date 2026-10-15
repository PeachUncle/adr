# ADR-017: CI/CD Pipeline Architecture

## Status
Accepted

## Context
BitVelocity needs automated CI/CD pipelines to:
- Enforce quality gates (tests, security, performance)
- Enable rapid feedback loops
- Practice DevOps and shift-left principles
- Learn industry-standard CI/CD patterns
- Support safe deployment strategies

## Decision

### Platform
**GitHub Actions** - Selected for:
- Native GitHub integration
- Free for public repositories
- Rich ecosystem of actions
- YAML-based configuration
- Matrix builds for parallelization
- Good documentation

### Pipeline Structure

#### 1. CI Pipeline (`ci-build-test.yml`)
**Triggers**: Every push and PR  
**Duration Target**: < 10 minutes  

**Stages**:
1. Checkout code
2. Setup Java 17
3. Cache Maven dependencies
4. Build (`mvn clean install`)
5. Unit tests (`mvn test`)
6. Integration tests (`mvn verify -P integration-tests`)
7. Generate test reports
8. Upload coverage to Codecov

**Gates**: All tests must pass

#### 2. Security Pipeline (`security-scanning.yml`)
**Triggers**: Push to main/develop, PRs, weekly schedule  
**Duration Target**: < 15 minutes  

**Scans**:
1. **OWASP Dependency Check**: Known CVE scanning
2. **Snyk**: Dependency vulnerabilities
3. **Trivy**: Container image scanning
4. **TruffleHog**: Secrets detection

**Gates**: Fail on CRITICAL vulnerabilities

#### 3. Contract Tests (`contract-tests.yml`)
**Triggers**: PRs, push to main  
**Duration Target**: < 5 minutes  

**Tests**:
1. **Pact**: Consumer-driven contract tests (REST)
2. **Buf**: gRPC contract validation
3. **Schema Registry**: Event contract validation

**Gates**: No breaking changes

#### 4. Performance Smoke (`performance-smoke.yml`)
**Triggers**: PRs to main, nightly  
**Duration Target**: < 5 minutes  

**Tests**:
1. Start infrastructure (Docker Compose)
2. Build and start services
3. Run k6 smoke tests
4. Report results in PR comment

**Gates**: p95 < 200ms, error rate < 1%

### Quality Gates

| Stage | Gate | Action on Failure |
|-------|------|-------------------|
| Build | Compilation success | Block merge |
| Unit Tests | 100% pass, >80% coverage | Block merge |
| Integration Tests | 100% pass | Block merge |
| Security | No CRITICAL CVEs | Block merge |
| Security | < 5 HIGH CVEs | Warning, manual review |
| Contract | No breaking changes | Block merge |
| Performance | < 10% degradation | Warning, manual review |

### Branch Strategy

```
main (protected)
  ↑
  └─ feature/* (PRs require all gates)
  └─ develop (integration branch)
```

**Protection Rules** for `main`:
- Require PR reviews (1 approval)
- Require status checks to pass
- Require branches to be up to date
- No force push
- No deletions

### Artifact Management

**Container Images**:

- Build on merge to main
- Tag with commit SHA and semantic version
- Push to GitHub Container Registry (ghcr.io)
- Scan before push

**Maven Artifacts**:

- Publish to GitHub Packages (shared libs)
- Semantic versioning (MAJOR.MINOR.PATCH)
- SNAPSHOT for development branches

### Deployment Strategy

**Environments**:
1. **Local**: Developer machines
2. **Dev**: Feature branch deployments (ephemeral)
3. **Staging**: Integration testing
4. **Production**: Manual approval (future)

**Deployment Methods**:

- Dev: Automatic on merge
- Staging: Manual trigger
- Production: Manual with approval gates

### Secrets Management

- Store in GitHub Secrets
- Use environment-specific secrets
- Never log secrets
- Rotate regularly
- Use OIDC for cloud credentials (future)

### Notification Strategy

**Slack/Teams Integration**:
- Build failures
- Security vulnerabilities found
- Deployment events
- Performance degradation alerts

### Observability

All pipelines emit:
- Build duration metrics
- Test result trends
- Security scan trends
- Deployment frequency
- Lead time for changes
- Change failure rate

### Cost Optimization

- Use caching aggressively (Maven, Docker layers)
- Run expensive tests only when needed
- Parallel execution where possible
- Cancel redundant runs on new commits
- Use self-hosted runners for heavy workloads (future)

## Consequences

### Positive
- Automated quality enforcement
- Fast feedback (< 10 min for most checks)
- Hands-on learning of CI/CD practices
- Safe deployment process
- Reduced manual errors
- Better code quality through gates

### Negative
- Initial setup complexity
- Maintenance overhead
- Pipeline execution time adds to PR cycle
- Requires discipline to maintain
- Flaky tests can block progress

### Trade-offs
- GitHub Actions over Jenkins/GitLab CI for simplicity
- Multiple smaller pipelines over one monolith for speed
- Parallel execution over sequential for faster feedback
- Fail fast on critical issues

## Implementation Plan

1. **Phase 1 (Week 1)**: Core CI
   - `ci-build-test.yml`
   - Basic unit and integration tests
   - Test reporting

2. **Phase 2 (Week 2)**: Security
   - `security-scanning.yml`
   - Dependency check
   - Container scanning
   - Secrets detection

3. **Phase 3 (Week 3)**: Contract & Performance
   - `contract-tests.yml`
   - `performance-smoke.yml`
   - PR comment integration

4. **Phase 4 (Week 4)**: Polish
   - Branch protection rules
   - Notification setup
   - Documentation
   - Team training

5. **Phase 5 (Ongoing)**: Optimization
   - Add caching
   - Optimize test execution
   - Add deployment pipelines
   - Metrics collection

## Learning Objectives

Through implementing and using these pipelines, learn:
1. **CI/CD Best Practices**: Pipeline design, optimization
2. **Testing Pyramid**: Unit, integration, contract, E2E
3. **Security**: Shift-left security, vulnerability management
4. **Performance**: Regression detection, benchmarking
5. **DevOps Metrics**: DORA metrics, lead time, deployment frequency
6. **GitOps**: Infrastructure and config as code

## References
- `.github/workflows/ci-build-test.yml`
- `.github/workflows/security-scanning.yml`
- `.github/workflows/contract-tests.yml`
- `.github/workflows/performance-smoke.yml`
- ADR-015: Load Testing Strategy
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [DORA Metrics](https://cloud.google.com/blog/products/devops-sre/using-the-four-keys-to-measure-your-devops-performance)
