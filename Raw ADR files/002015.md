# ADR-003: CI/CD Pipeline Design

**Date:** 2025-11-15  
**Status:** Accepted  
**Accepted Date:** 2025-11-15  
**Deciders:** Agent Frontend, Agent Backend, Agent Blockchain  
**Technical Story:** Phase 0.3 - Continuous Integration & Deployment  
**Relates to:** ADR-001 (Tech Stack), ADR-002 (Mono-Repo)

---

## Context and Problem Statement

Ghost Protocol requires automated pipelines for:
- Code quality enforcement (linting, type checking)
- Automated testing (unit, integration, E2E)
- Security scanning (dependencies, code analysis)
- Build verification
- Automated deployment (staging, production)
- Multi-environment management (dev, staging, production)

**Question:** What CI/CD platform and workflow should we use?

## Decision Drivers

- **Speed:** Build + test < 10 minutes for fast feedback
- **Reliability:** >99% pipeline availability
- **Cost:** Optimize for free tier initially, scalable pricing
- **Developer Experience:** Easy to debug, clear error messages
- **Security:** Secrets management, audit logs
- **Flexibility:** Support multiple languages (TypeScript, Rust, Python)
- **Integration:** Works with GitHub, Kubernetes, monitoring tools

## Considered Options

1. **GitHub Actions**
2. GitLab CI/CD
3. CircleCI
4. Jenkins
5. Buildkite

## Decision Outcome

**Chosen option:** "GitHub Actions", because:
- Native GitHub integration (no external service)
- Generous free tier (2,000 minutes/month, unlimited for public repos)
- Excellent ecosystem (actions marketplace)
- Matrix builds (parallel execution)
- Built-in secrets management
- Self-hosted runners option (cost control)

### Pipeline Architecture

```
┌─────────────────────────────────────────┐
│         PR Opened/Updated               │
└─────────────┬───────────────────────────┘
              │
              ├──> Lint & Format Check
              ├──> Type Check (TypeScript)
              ├──> Unit Tests
              ├──> Security Scan (Snyk)
              ├──> Build Verification
              └──> Preview Deployment (Vercel/Railway)
              
┌─────────────────────────────────────────┐
│         Merge to main                   │
└─────────────┬───────────────────────────┘
              │
              ├──> Full Test Suite
              ├──> Integration Tests
              ├──> Build All Packages
              ├──> Lighthouse CI (Frontend)
              ├──> Deploy to Staging
              └──> Automated Smoke Tests
              
┌─────────────────────────────────────────┐
│         Tag Release (v*)                │
└─────────────┬───────────────────────────┘
              │
              ├──> Full Test Suite
              ├──> Security Audit
              ├──> Build Production Artifacts
              ├──> Deploy to Production (Manual Approval)
              └──> Post-Deployment Tests
```

### Workflow Files

**File Structure:**
```
.github/
└── workflows/
    ├── frontend-ci.yml         # Frontend CI/CD
    ├── backend-ci.yml          # Backend CI/CD
    ├── contracts-ci.yml        # Smart Contracts CI/CD
    ├── chain-ci.yml            # Blockchain Node CI/CD
    ├── security-scan.yml       # Daily security scans
    └── deploy-production.yml   # Production deployment
```

### Frontend CI Pipeline

```yaml
name: Frontend CI

on:
  pull_request:
    paths:
      - 'packages/frontend/**'
  push:
    branches: [main]
    paths:
      - 'packages/frontend/**'

jobs:
  lint-test-build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package: [web, admin, components]
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'
          cache-dependency-path: packages/frontend/${{ matrix.package }}/pnpm-lock.yaml
      
      - name: Install Dependencies
        run: cd packages/frontend/${{ matrix.package }} && pnpm install --frozen-lockfile
      
      - name: Lint
        run: cd packages/frontend/${{ matrix.package }} && pnpm run lint
      
      - name: Type Check
        run: cd packages/frontend/${{ matrix.package }} && pnpm run type-check
      
      - name: Test
        run: cd packages/frontend/${{ matrix.package }} && pnpm test -- --coverage
      
      - name: Build
        run: cd packages/frontend/${{ matrix.package }} && pnpm run build
      
      - name: Lighthouse CI
        if: matrix.package == 'web'
        uses: treosh/lighthouse-ci-action@v10
        with:
          urls: |
            http://localhost:3000
          uploadArtifacts: true
          temporaryPublicStorage: true
```

### Backend CI Pipeline

```yaml
name: Backend CI

on:
  pull_request:
    paths:
      - 'packages/backend/**'
  push:
    branches: [main]

jobs:
  lint-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    
    strategy:
      matrix:
        service: [api-gateway, indexer, rpc-orchestrator, ai-engine]
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install
        run: cd packages/backend/${{ matrix.service }} && pnpm install --frozen-lockfile
      
      - name: Lint
        run: cd packages/backend/${{ matrix.service }} && pnpm run lint
      
      - name: Type Check
        run: cd packages/backend/${{ matrix.service }} && pnpm run type-check
      
      - name: Test
        run: cd packages/backend/${{ matrix.service }} && pnpm test
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
      
      - name: Integration Tests
        run: cd packages/backend/${{ matrix.service }} && pnpm run test:e2e
```

### Smart Contracts CI Pipeline

```yaml
name: Contracts CI

on:
  pull_request:
    paths:
      - 'packages/contracts/**'
  push:
    branches: [main]

jobs:
  test-analyze:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        contract: [chaing-token, marketplace]
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install
        run: cd packages/contracts/${{ matrix.contract }} && pnpm install --frozen-lockfile
      
      - name: Compile
        run: cd packages/contracts/${{ matrix.contract }} && pnpx hardhat compile
      
      - name: Test
        run: cd packages/contracts/${{ matrix.contract }} && pnpx hardhat test
      
      - name: Coverage
        run: cd packages/contracts/${{ matrix.contract }} && pnpx hardhat coverage
      
      - name: Gas Report
        run: cd packages/contracts/${{ matrix.contract }} && REPORT_GAS=true pnpx hardhat test
      
      - name: Slither Analysis
        uses: crytic/slither-action@v0.3.0
        with:
          target: packages/contracts/${{ matrix.contract }}/contracts/
      
      - name: Coverage Check
        run: |
          COVERAGE=$(jq '.total.statements.pct' packages/contracts/${{ matrix.contract }}/coverage/coverage-summary.json)
          if (( $(echo "$COVERAGE < 95" | bc -l) )); then
            echo "Coverage $COVERAGE% is below 95%"
            exit 1
          fi
```

### Security Scanning Pipeline

```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
  pull_request:
  push:
    branches: [main]

jobs:
  snyk-scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        workspace:
          - packages/frontend/web
          - packages/backend/api-gateway
          - packages/contracts/chaing-token
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high --file=${{ matrix.workspace }}/package.json
```

### Deployment Pipeline (Staging)

```yaml
name: Deploy to Staging

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG_STAGING }}
      
      - name: Deploy Frontend
        run: kubectl apply -k infra/k8s/overlays/staging/frontend/
      
      - name: Deploy Backend
        run: kubectl apply -k infra/k8s/overlays/staging/backend/
      
      - name: Wait for Rollout
        run: kubectl rollout status deployment/ghost-frontend -n staging
      
      - name: Smoke Tests
        run: pnpm run test:smoke -- --env=staging
```

### Positive Consequences

- **Fast Feedback:** Parallel matrix builds (all packages tested simultaneously)
- **Cost Efficient:** Free tier covers development phase
- **Security:** Automated scanning (Snyk, Slither) on every PR
- **Quality Gates:** Cannot merge if tests fail or coverage <threshold
- **Deployment Safety:** Staging deployment + smoke tests before production
- **Audit Trail:** All deployments logged with commit SHA
- **Developer Experience:** Clear error messages, artifacts downloadable

### Negative Consequences

- **GitHub Lock-in:** Harder to migrate to other platforms
  - **Mitigation:** Keep workflows simple, avoid GitHub-specific features
- **Runner Limits:** Free tier has minute limits
  - **Mitigation:** Use self-hosted runners if needed
- **Complex Workflows:** Matrix + conditions can be hard to debug
  - **Mitigation:** Document workflows, use act for local testing

## Pros and Cons of the Options

### GitHub Actions

**Pros:**
- Native GitHub integration
- Free for public repos, generous free tier
- Excellent marketplace (reusable actions)
- Matrix builds (parallel)
- Built-in secrets management
- Self-hosted runners option

**Cons:**
- Vendor lock-in (GitHub-specific)
- YAML can be verbose
- Limited debugging (vs local testing)

### GitLab CI/CD

**Pros:**
- Excellent built-in features
- Better debugging (job artifacts)
- Free tier generous
- Can self-host

**Cons:**
- Requires GitLab account (separate from GitHub)
- Learning curve if team uses GitHub
- Not as tightly integrated with GitHub

### CircleCI

**Pros:**
- Fast builds (optimized runners)
- Good caching
- Excellent dashboard

**Cons:**
- Expensive (credits-based pricing)
- Free tier very limited (400 credits/week)
- Extra service to manage

### Jenkins

**Pros:**
- Self-hosted (full control)
- Highly customizable
- No vendor lock-in

**Cons:**
- Requires maintenance (server updates, plugins)
- More complex setup
- No free hosting

### Buildkite

**Pros:**
- Fastest builds (self-hosted agents)
- Excellent UI
- Good debugging

**Cons:**
- Expensive ($15/user/month)
- Requires managing agents

**Why GitHub Actions:** Best balance of cost, integration, and features for our use case.

---

## Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Snyk GitHub Action](https://github.com/snyk/actions)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)

## Notes

### Environment Strategy

**Environments:**
1. **Development** - Local (Docker Compose)
2. **Staging** - Kubernetes cluster (auto-deploy on main)
3. **Production** - Kubernetes cluster (manual approval)

**Secrets Management:**
- GitHub Secrets for CI/CD
- HashiCorp Vault for application runtime
- Separate secrets per environment

### Deployment Strategy

**Staging:**
- Auto-deploy on merge to main
- Smoke tests after deployment
- Rollback if tests fail

**Production:**
- Manual approval required
- Deploy during low-traffic hours
- Canary deployment (10% → 50% → 100%)
- Monitor for 1 hour before full rollout

### Performance Optimizations

**Caching:**
```yaml
- uses: actions/cache@v3
  with:
    path: ~/.pnpm-store
    key: ${{ runner.os }}-node-${{ hashFiles('**/pnpm-lock.yaml') }}
```

**Conditional Execution:**
```yaml
- name: Test Frontend
  if: contains(github.event.head_commit.modified, 'packages/frontend/')
```

**Parallel Matrix:**
```yaml
strategy:
  matrix:
    package: [web, admin, api-gateway, indexer]
    node-version: [20]
```

### Cost Management

**Monthly Estimate:**
- Free tier: 2,000 minutes/month
- Expected usage: ~500 minutes/month (development)
- If exceed: Self-hosted runner (~$50/month EC2 t3.medium)

**Optimization:**
- Cache dependencies
- Only run affected packages
- Skip jobs for doc-only changes

---

**Review Date:** 2025-12-15  
**Next Review:** After exceeding free tier or if build time >15min
