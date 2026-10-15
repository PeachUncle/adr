# ADR-004: Lighthouse CI for Automated Performance Testing

**Status**: Approved
**Date**: 2025-12-09
**Deciders**: Development Team
**Context**: Premium UI/UX Enhancement Feature

## Context and Problem Statement

The premium UI/UX enhancement has strict performance and accessibility requirements:
- **SC-005**: Lighthouse performance score > 90 (desktop and mobile)
- **SC-007**: WCAG 2.1 AA compliance with 0 critical violations
- **FR-011**: All animations run at 60fps without degradation
- **SC-010**: Site becomes interactive in < 2 seconds

We need an automated testing solution that:
- Catches performance regressions before production
- Runs on every pull request
- Validates accessibility compliance
- Provides actionable feedback
- Integrates with GitHub Actions CI/CD

## Decision Drivers

- **Automation**: Must run automatically on every PR
- **Cost**: Prefer free/low-cost solutions
- **Actionability**: Clear feedback on what needs fixing
- **CI/CD Integration**: Works with GitHub Actions
- **Reliability**: Consistent results, minimal flakes
- **Developer Experience**: Fast feedback loop

## Considered Options

### Option 1: Manual Lighthouse Testing Only
Run Lighthouse audits manually before merging PRs.

**Pros:**
- No setup required
- No CI costs
- Developers already know Lighthouse

**Cons:**
- **Error-prone**: Easy to forget
- **No enforcement**: Can't block PRs automatically
- **Inconsistent**: Different results per developer
- **Slow feedback**: Only tested when developer remembers
- **No history**: No trend tracking

**Cost**: Free
**Automation**: None

### Option 2: Lighthouse CI (SELECTED)
Official Lighthouse CI tool from Google.

**Pros:**
- **Official tool**: Well-maintained by Google
- **Free**: Open source, runs in GitHub Actions
- **Automated**: Runs on every PR automatically
- **Consistent**: Same audit environment every time
- **Actionable**: Fails PR if thresholds not met
- **Trending**: Track performance over time
- **Configurable**: Set custom thresholds per metric
- **Assertions**: Can assert specific budgets (Performance > 90, Accessibility > 95)

**Cons:**
- Slight CI time overhead (~2-3 minutes per run)
- Can be flaky due to network variance (mitigated with averages)
- Requires configuration setup

**Cost**: Free (runs in GitHub Actions)
**Automation**: Full

### Option 3: SpeedCurve or Calibre (SaaS)
Commercial performance monitoring platforms.

**Pros:**
- Advanced dashboards
- Real user monitoring (RUM)
- Competitive analysis
- Custom alerts
- Historical data retention

**Cons:**
- **Cost**: $20-200/month depending on plan
- Overkill for single project
- Requires account management
- External dependency

**Cost**: $20-200/month
**Automation**: Full

### Option 4: WebPageTest CI
WebPageTest integration for CI.

**Pros:**
- Industry-standard testing tool
- Real browser testing
- Advanced metrics (SpeedIndex, etc.)

**Cons:**
- More complex setup
- Slower than Lighthouse CI
- Requires API key management
- Less integrated with GitHub

**Cost**: Free (public instance) or $200/month (private)
**Automation**: Partial

## Decision Outcome

**Chosen Option**: Lighthouse CI in GitHub Actions

### Implementation

**1. Install Dependency**
```bash
npm install -D @lhci/cli@^0.13.0
```

**2. Create `.lighthouserc.json` Configuration**
```json
{
  "ci": {
    "collect": {
      "staticDistDir": "./build",
      "url": [
        "/",
        "/docs/intro"
      ],
      "numberOfRuns": 3
    },
    "assert": {
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.95}],
        "categories:best-practices": ["error", {"minScore": 0.9}],
        "categories:seo": ["warn", {"minScore": 0.9}],
        "first-contentful-paint": ["warn", {"maxNumericValue": 1800}],
        "largest-contentful-paint": ["error", {"maxNumericValue": 2500}],
        "cumulative-layout-shift": ["error", {"maxNumericValue": 0.1}],
        "total-blocking-time": ["error", {"maxNumericValue": 200}]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

**3. Add GitHub Actions Workflow**
```yaml
# .github/workflows/lighthouse-ci.yml
name: Lighthouse CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build site
        run: npm run build

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli@0.13.0
          lhci autorun

      - name: Upload results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: lighthouse-results
          path: .lighthouseci
```

**4. Add Package Script**
```json
{
  "scripts": {
    "lighthouse": "lhci autorun"
  }
}
```

### Configuration Details

**Thresholds (from spec.md)**:
- **Performance**: > 90 (error if below)
- **Accessibility**: > 95 (error if below)
- **Best Practices**: > 90 (error if below)
- **SEO**: > 90 (warning if below)
- **LCP**: < 2.5s (error if above)
- **CLS**: < 0.1 (error if above)
- **TBT**: < 200ms (error if above)

**Test Pages**:
- `/` (Homepage - premium landing page)
- `/docs/intro` (Docs page - typography test)

**Number of Runs**: 3 (median score used for consistency)

**Upload Target**: Temporary public storage (accessible for 7 days)

### Rationale

1. **Automated Enforcement**: PRs cannot merge if performance/accessibility thresholds are not met
2. **Fast Feedback**: Developers know within minutes if changes regress performance
3. **Consistent Environment**: Same audit conditions every time (eliminates "works on my machine")
4. **Zero Cost**: Runs in GitHub Actions free tier
5. **Official Tool**: Maintained by Google Chrome team
6. **Actionable Reports**: Clear indication of what metrics failed and by how much

## Consequences

### Positive Consequences

1. **Prevents Regressions**: Catches performance issues before they reach production
2. **Enforces Quality**: Makes performance/accessibility non-negotiable
3. **Developer Awareness**: Immediate feedback educates developers on performance impact
4. **Continuous Validation**: Every change is tested, not just major releases
5. **Historical Data**: Can track performance trends over time
6. **Free**: No additional costs

### Negative Consequences

1. **CI Time**: Adds ~2-3 minutes to PR checks
2. **Occasional Flakes**: Network variance can cause inconsistent results (mitigated by 3 runs + median)
3. **Blocking PRs**: Developers must fix issues before merging (this is also a positive)

### Mitigation Strategies

1. **Multiple Runs**: Use `numberOfRuns: 3` and median score for consistency
2. **Reasonable Thresholds**: Set thresholds that are achievable but strict (90, not 100)
3. **Warning vs Error**: Use warnings for nice-to-have metrics (SEO), errors for critical (performance)
4. **Local Testing**: Developers can run `npm run lighthouse` before pushing
5. **Skip When Needed**: Allow `[skip ci]` in commit messages for urgent hotfixes (use sparingly)

## Performance Budget Enforcement

**Lighthouse CI enforces these budgets** (from spec.md):

| Metric | Target | Assertion Level |
|--------|--------|----------------|
| Performance Score | > 90 | Error |
| Accessibility Score | > 95 | Error |
| LCP (Largest Contentful Paint) | < 2.5s | Error |
| CLS (Cumulative Layout Shift) | < 0.1 | Error |
| TBT (Total Blocking Time) | < 200ms | Error |
| FCP (First Contentful Paint) | < 1.8s | Warning |

**If any ERROR assertion fails**: PR build fails, cannot merge
**If any WARN assertion fails**: PR build succeeds with warnings

## Alternative Configurations

**If Network Flakes Become an Issue**:
```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 5  // Increase runs for more stable median
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["warn", {"minScore": 0.9}]  // Downgrade to warning
      }
    }
  }
}
```

**If CI Time Becomes a Problem**:
```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 1,  // Single run (faster but less consistent)
      "url": ["/"]  // Test only homepage
    }
  }
}
```

## Integration with Existing Workflow

**PR Workflow**:
1. Developer creates PR
2. GitHub Actions triggers:
   - Build check (existing)
   - TypeScript check (existing)
   - **Lighthouse CI** (new)
3. If Lighthouse fails → PR marked as failing
4. Developer fixes performance issues
5. Push new commit → Lighthouse re-runs
6. All checks pass → PR can be merged

**Branch Protection**:
```yaml
# .github/workflows must be required in branch protection rules
Required checks:
  - build
  - lighthouse
```

## Monitoring and Validation

**Check Lighthouse CI is Working**:
1. Create test PR that intentionally regresses performance
2. Verify CI fails
3. Fix performance issue
4. Verify CI passes

**Production Monitoring** (separate from Lighthouse CI):
- Use Google Analytics for real user performance
- Set up alerts if performance degrades
- Monthly review of Lighthouse CI trends

## Links and References

- [Lighthouse CI Documentation](https://github.com/GoogleChrome/lighthouse-ci)
- [Lighthouse CI GitHub Action](https://github.com/treosh/lighthouse-ci-action)
- [Lighthouse Scoring Guide](https://web.dev/performance-scoring/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- Related ADRs: ADR-002 (Animation Performance), ADR-003 (Font Loading)
