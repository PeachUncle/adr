# ADR-002: CI/CD Pipeline Architecture

## Status

Accepted

## Context

Rule Bound needs a continuous integration and deployment pipeline that:

- Runs quality checks before code reaches production
- Automates the build and deployment process
- Provides fast feedback on pull requests
- Enforces project standards (tests, linting, accessibility)
- Integrates with the chosen hosting platform (Netlify)

The project already has quality scripts:

- `npm run test:run` - Run tests
- `npm run lint` - ESLint checks
- `npm run type-check` - TypeScript validation
- `npm run build` - Production build

## Options Considered

### 1. Netlify-Only CI/CD

**Pros:**

- Single platform for everything
- Simpler configuration
- No GitHub Actions required

**Cons:**

- Limited CI capabilities (mainly just build)
- Cannot run comprehensive test suite before deploy
- Less control over pipeline stages

### 2. GitHub Actions + Netlify Deploy

**Pros:**

- Full CI capabilities (tests, lint, type-check, build)
- GitHub-native, visible in PR checks
- Can run quality gates before Netlify deploys
- Matrix testing possible (multiple Node versions)
- Caching for faster builds

**Cons:**

- Two systems to maintain
- More configuration files

### 3. GitHub Actions with Manual Netlify Deploy

**Pros:**

- Complete control over deployment trigger
- Can add manual approval gates

**Cons:**

- More complex setup
- Loses automatic preview deployments

## Decision

We will use **GitHub Actions for CI** combined with **Netlify's automatic deployments** because:

1. **Separation of Concerns**: GitHub Actions handles quality gates; Netlify handles deployment
2. **PR Checks**: Tests must pass before merge (enforced by GitHub branch protection)
3. **Preview Deploys**: Netlify automatically creates preview URLs for PRs
4. **Production Safety**: Main branch is protected; only passing PRs can merge

### Pipeline Architecture

```
PR Created/Updated
       │
       ▼
┌─────────────────────────────────────────────┐
│         GitHub Actions CI Pipeline          │
│                                             │
│  ┌─────────┐  ┌─────────┐  ┌────────────┐  │
│  │  Lint   │  │  Type   │  │   Test     │  │
│  │         │  │  Check  │  │            │  │
│  └────┬────┘  └────┬────┘  └─────┬──────┘  │
│       │            │             │         │
│       └────────────┴─────────────┘         │
│                    │                       │
│                    ▼                       │
│              ┌──────────┐                  │
│              │  Build   │                  │
│              └──────────┘                  │
└─────────────────────────────────────────────┘
       │
       ▼ (in parallel)
┌─────────────────────────────────────────────┐
│         Netlify Auto-Deploy                 │
│                                             │
│  • Builds from branch                       │
│  • Creates preview URL                      │
│  • Posts URL to PR comments                 │
└─────────────────────────────────────────────┘
       │
       ▼
PR Review (human)
       │
       ▼ (on merge to main)
┌─────────────────────────────────────────────┐
│         Netlify Production Deploy           │
│                                             │
│  • Builds from main                         │
│  • Deploys to production URL                │
└─────────────────────────────────────────────┘
```

## Consequences

### Positive

- Quality gates enforced before merge
- Fast feedback on PRs (parallel jobs)
- Preview URLs for stakeholder testing
- Automated production deployments
- Clear audit trail via GitHub Actions logs

### Negative

- Two services to monitor (GitHub Actions + Netlify)
- Initial setup complexity
- Need to keep CI config and Netlify config in sync

### Neutral

- GitHub Actions free tier (2,000 minutes/month) is sufficient
- Branch protection rules need to be configured in GitHub settings
