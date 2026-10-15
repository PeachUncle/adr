# ADR-015: GitHub Ecosystem Maximization Strategy

**Status**: Accepted  
**Date**: 2025-12-27  
**Deciders**: James (Owner)  
**Technical Story**: Maximize GitHub Pro value for TaskMan-v2 MVP

## Context and Problem Statement

James has a **GitHub Pro subscription ($4/month)** with substantial included features that are currently underutilized. The goal is to maximize GitHub ecosystem value before adding external paid services.

## Account Analysis (2025-12-27)

### Current GitHub Account Status

| Resource | Value |
|----------|-------|
| **Account** | jhardy82 |
| **Plan** | GitHub Pro |
| **Created** | 2015-07-22 |
| **Total Repos** | 39 (30 active, 9 archived) |
| **Private Repos** | ~15 |
| **Public Repos** | ~24 |
| **Actions Workflows** | 19 active in SCCMScripts |

### GitHub Pro Included Features

| Feature | Included Amount | Current Usage |
|---------|-----------------|---------------|
| **Actions Minutes** | 3,000/month | ~500-1000 (estimate) |
| **Packages Storage** | 2 GB | 0 GB |
| **Codespaces Hours** | 180 core-hours/month | Unknown |
| **Codespaces Storage** | 20 GB | Unknown |
| **Pages for Private Repos** | ✅ Yes | ❌ Not enabled |
| **Protected Branches** | ✅ Yes | ⚠️ Not configured |
| **Environments** | ✅ Yes | ⚠️ Only 'copilot' |
| **Email Support** | ✅ Yes | Not used |

### Underutilized Features (High Value)

| Feature | Current | Recommended | Annual Value |
|---------|---------|-------------|--------------|
| GitHub Pages | ❌ Off | ✅ Frontend hosting | ~$240 saved |
| ghcr.io | ❌ Off | ✅ Docker registry | ~$120 saved |
| Environments | 1 | 3 (staging, prod) | Risk reduction |
| Branch Protection | ❌ Off | ✅ Required reviews | Quality |
| GitHub OAuth | ❌ Off | ✅ Auth provider | ~$2,880 saved |

## Decision Outcome

**Maximize GitHub ecosystem before external services**:

1. ✅ **GitHub OAuth** for authentication (vs Auth0)
2. ✅ **GitHub Pages** for frontend hosting (vs Vercel)
3. ✅ **GitHub Packages (ghcr.io)** for Docker images
4. ✅ **GitHub Environments** for staging/production
5. ✅ **GitHub Actions** for CI/CD (already using)
6. ⚠️ **Railway** for backend only (no GitHub equivalent)

### Cost Impact

| Scenario | Monthly Cost | Annual Cost |
|----------|--------------|-------------|
| **Original Plan** (Auth0 + Vercel + Railway) | $260-510 | $3,120-6,120 |
| **GitHub-Maximized** (GitHub + Railway) | $5-10 | $60-120 |
| **Savings** | $250-500/month | **$3,000-6,000/year** |

## Implementation Roadmap

### Phase 1: Enable GitHub Features (1 hour)

```bash
# 1. Enable GitHub Pages (Settings → Pages → Source: GitHub Actions)

# 2. Create OAuth App
# https://github.com/settings/developers → New OAuth App
# Name: TaskMan-v2
# Callback: https://jhardy82.github.io/SCCMScripts/auth/callback

# 3. Create Environments
gh api repos/jhardy82/SCCMScripts/environments/staging -X PUT
gh api repos/jhardy82/SCCMScripts/environments/production -X PUT

# 4. Enable Branch Protection
gh api repos/jhardy82/SCCMScripts/branches/main/protection -X PUT \
  -f required_pull_request_reviews='{"required_approving_review_count":1}'
```

### Phase 2: Deploy Frontend to GitHub Pages (4 hours)

1. Add SPA router fix (404.html redirect)
2. Create deploy-frontend.yml workflow
3. Configure VITE_API_URL for Railway backend
4. Test deployment

### Phase 3: Docker to ghcr.io (2 hours)

1. Create deploy-backend.yml workflow
2. Push TaskMan API image to ghcr.io
3. Configure Railway to pull from ghcr.io

### Phase 4: GitHub OAuth Integration (8 hours)

1. Create OAuth App in GitHub settings
2. Implement FastAPI OAuth endpoints
3. Implement React auth flow
4. Add user table with RBAC
5. Test end-to-end

## GitHub Features Checklist

### Enable Now (P0)

- [ ] **GitHub Pages** - Settings → Pages → Source: GitHub Actions
- [ ] **OAuth App** - Settings → Developer settings → OAuth Apps → New
- [ ] **Staging Environment** - Settings → Environments → New: staging
- [ ] **Production Environment** - Settings → Environments → New: production

### Configure Soon (P1)

- [ ] **Branch Protection** - Settings → Branches → main → Protect
- [ ] **Required Reviews** - At least 1 approval before merge
- [ ] **Status Checks** - Require CI to pass

### Consider Later (P2)

- [ ] **GitHub Discussions** - For community feedback
- [ ] **GitHub Wiki** - For user documentation
- [ ] **GitHub Projects** - For public roadmap visibility

## GitHub Actions Optimization

### Current State (19 workflows)

```
Quality - PSScriptAnalyzer and WU Tests
Copilot coding agent
Harness Smoke
Constitutional & Cognitive Framework Testing
Guardrail - No Quiet Flags
Governance - Logure Gap Gate
Performance Guardrail
Pytest Discovery Guard
Pytest PR Tests (Excludes Slow)
Pytest Slow Tests
Quality Gates
Unified Logging Benchmark (Scheduled)
Manual - Unified Logging Benchmark
Copilot code review
Documentation Validation
Spectre Demo Smoke
... and more
```

### Optimization Recommendations

1. **Consolidate overlapping workflows** - Reduce from 19 to ~10
2. **Use path filters** - Only run when relevant files change
3. **Add caching** - pip, npm dependencies
4. **Set concurrency** - Cancel superseded runs
5. **Use matrix builds** - Parallelize testing

### Example Optimized Workflow

```yaml
name: Quality Gates (Consolidated)

on:
  push:
    branches: [main]
    paths: ['**/*.py', '**/*.ps1', 'TaskMan-v2/**']
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: ruff check .
      - run: pytest -x --tb=short

  powershell:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - run: Invoke-ScriptAnalyzer -Path . -Recurse
      - run: Invoke-Pester -CI

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: TaskMan-v2/package-lock.json
      - working-directory: TaskMan-v2
        run: npm ci && npm run lint && npm run test
```

## Semantic Versioning Automation

Add automated releases with semantic-release:

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npx semantic-release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Links

* [GitHub Pro Features](https://github.com/pricing)
* [GitHub Pages](https://docs.github.com/en/pages)
* [GitHub OAuth Apps](https://docs.github.com/en/apps/oauth-apps)
* [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments)
* [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
