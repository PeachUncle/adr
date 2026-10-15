# ADR-022: Comprehensive Lighthouse Testing Across All Categories

**Date:** 2025-01-21  
**Status:** Accepted  
**Author:** AI Assistant  
**Cross-References:** ADR-020 (Accessibility Compliance), QA Plan §6 (Lighthouse/axe gates), CI workflow lighthouse job

---

## Context

The FitVibe platform requires comprehensive quality assurance across multiple dimensions: performance, accessibility, best practices, and SEO. Previously, Lighthouse CI was configured to only check **Performance** category with a minimum score of 0.9 (90), leaving other critical quality dimensions unvalidated.

The QA Plan (4a.Testing_and_Quality_Assurance_Plan.md) mandates:

- **Accessibility**: WCAG 2.1 AA, axe/Lighthouse score ≥90
- **Performance**: LCP P75 < 2.5s, Lighthouse score ≥90
- **Best Practices**: Security headers, HTTPS, modern web standards
- **SEO**: Meta tags, semantic HTML, proper document structure

ADR-020 (Accessibility Compliance) explicitly requires "Lighthouse ≥ 90" for accessibility, but the CI configuration was incomplete, only validating performance metrics.

---

## Decision

Expand Lighthouse CI configuration to validate **all four Lighthouse categories** with a minimum score threshold of **0.9 (90)** for each:

1. **Performance** (≥90): Already configured; maintains existing LCP and resource size budgets
2. **Accessibility** (≥90): New assertion; validates WCAG compliance, ARIA usage, semantic HTML
3. **Best Practices** (≥90): New assertion; validates security headers, HTTPS, modern web APIs
4. **SEO** (≥90): New assertion; validates meta tags, document structure, crawlability

### Configuration Changes

Updated `tests/perf/lighthouserc.json` to include comprehensive category assertions:

```json
{
  "ci": {
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.9 }],
        "categories:best-practices": ["error", { "minScore": 0.9 }],
        "categories:seo": ["error", { "minScore": 0.9 }],
        "resource-summary:total.size": ["error", { "maxNumericValue": 307200 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }]
      }
    }
  }
}
```

### CI Integration

The existing Lighthouse CI job (`.github/workflows/ci.yml` lines 554-652) already:

- Builds the frontend production bundle
- Starts a preview server on port 4173
- Runs Lighthouse CI with the configuration file
- Uploads reports as artifacts

No workflow changes required; the configuration update automatically enforces the new thresholds.

### Local Testing

Developers can run Lighthouse locally using:

```bash
# Build frontend
pnpm --filter @fitvibe/frontend run build

# Start preview server
cd apps/frontend && pnpm preview --port 4173 --host 127.0.0.1 &

# Run Lighthouse CI
pnpm exec lhci autorun --config=tests/perf/lighthouserc.json
```

---

## Consequences

**Positive**

- **Comprehensive quality gates**: All quality dimensions (performance, accessibility, best practices, SEO) are now validated in CI
- **Early detection**: Issues in any category are caught before merge, reducing production defects
- **Alignment with requirements**: Matches QA Plan and ADR-020 requirements for Lighthouse ≥90 across all categories
- **Developer feedback**: Clear failure messages indicate which category needs improvement
- **No workflow changes**: Existing CI job automatically enforces new thresholds

**Negative / Trade-offs**

- **Stricter gates**: Previously passing builds may fail if accessibility, best practices, or SEO scores are below 90
- **Additional development effort**: Teams must address issues in all four categories, not just performance
- **Potential false positives**: Some SEO checks may be less relevant for authenticated SPA contexts (mitigated by 90 threshold, not 100)

**Operational**

- **CI feedback**: Failed Lighthouse runs will clearly indicate which category failed and by how much
- **Report artifacts**: Full Lighthouse reports are uploaded to CI artifacts for detailed analysis
- **Local validation**: Developers can run Lighthouse locally before pushing to catch issues early
- **Monitoring**: Track Lighthouse score trends over time to identify regressions

---

## Alternatives Considered

| Option                        | Description                                               | Reason Rejected                                                                        |
| ----------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Performance-only testing      | Keep existing configuration                               | Incomplete; violates ADR-020 and QA Plan requirements for accessibility ≥90            |
| Lower thresholds (0.8)        | Set minScore to 0.8 for all categories                    | Too lenient; QA Plan explicitly requires ≥90; ADR-020 mandates ≥90 for accessibility   |
| Separate CI jobs per category | Create individual jobs for each category                  | Unnecessary complexity; single job with comprehensive assertions is simpler and faster |
| Manual audits only            | Remove automated Lighthouse checks                        | Too slow; regressions slip through; not aligned with CI/CD best practices              |
| Category-specific thresholds  | Different scores per category (e.g., perf 0.9, a11y 0.85) | Inconsistent; QA Plan requires ≥90 across the board; uniform threshold is clearer      |

---

## References

- **ADR-020**: Accessibility Compliance (WCAG 2.2 AA) & Inclusive UX - mandates Lighthouse ≥90
- **QA Plan** (4a.Testing_and_Quality_Assurance_Plan.md): §6 - Lighthouse/axe gates, §30 - Accessibility target
- **CI Workflow** (`.github/workflows/ci.yml`): Lines 554-652 - Lighthouse CI job
- **Lighthouse Config** (`tests/perf/lighthouserc.json`): Configuration file with category assertions

---

## Status Log

| Version | Date       | Change                                                                 | Author       |
| ------- | ---------- | ---------------------------------------------------------------------- | ------------ |
| v1.0    | 2025-01-21 | Initial ADR for comprehensive Lighthouse testing across all categories | AI Assistant |
