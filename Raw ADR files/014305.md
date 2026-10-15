# ADR-007: CI/CD Workflow

**Status** Accepted

**Date** December 2025

## Context

Even though this is a personal project, building a reliable code delivery process is essential for long-term maintenance and development. Automated checks verify code quality before pushing to production, which becomes especially valuable if the app gains regular users (and there is potential for that).

As a solo developer following trunk-based development, the workflow needs to be lightweight yet robust enough to catch issues before they reach production.

## Decision

Implement a two-stage quality gate approach using GitHub Actions:

### Stage 1: Pre-commit (Local)

Using `husky` + `lint-staged`, the following checks run on every commit:

-   **ESLint** — code style and potential bugs
-   **Type-checking** (`tsc --noEmit`) — TypeScript validation

### Stage 2: Pre-merge (CI)

When a PR is opened against `master`, GitHub Actions runs:

-   **Unit tests** (Vitest) — required
-   **Accessibility tests** (axe) — required
-   **Production build** (`next build`) — required
-   **E2E tests** (Playwright) — optional (currently disabled due to socket integration issues)

All required checks must pass before merging.

### Stage 3: Deployment

On merge to `master`, GitHub Actions automatically:

1. SSH into DigitalOcean VPS
2. Pull latest code
3. Rebuild Docker container
4. Deploy to production

## Branching Strategy

-   **Trunk-based development** with short-lived feature branches
-   `master` is the production branch
-   All changes go through PRs with required CI checks
-   No staging environment (production only)

## Options Considered

### CI Platform

GitHub Actions was chosen without evaluating alternatives — it integrates seamlessly with the repository and provides everything needed for the current workflow.

### Pre-commit vs CI-only Checks

There are two options for code quality checks:

1. **Pre-commit stage** — runs on local machine
2. **Pre-merge stage** — runs on CI

Both stages are necessary:

-   **Pre-commit** offers faster feedback and prevents "junk commits" from polluting git history
-   **Pre-merge** serves as the final gate and runs more comprehensive checks (tests, build)

Currently, only linting and type-checking run at pre-commit. Unit tests are run manually during development to keep commits fast.

### Accessibility Testing in Pipeline

Accessibility tests are part of the pipeline because some accessibility issues are hard to validate visually. Automated checks ensure error-free accessibility even when changes seem unrelated to a11y.

## Consequences

### Positive

-   Fast feedback loop — lint/type errors caught immediately on commit
-   Quality gate prevents broken code from reaching production
-   Automated deployment reduces manual work and human error
-   Docker caching keeps CI reasonably fast
-   No false positives in accessibility tests so far

### Negative

-   E2E tests currently don't work in CI due to socket integration complexity
-   No preview deployments for PRs (requires manual local testing)
-   Single production environment means no staging for validation

## Future Improvements

-   [ ] Fix E2E tests and make them required for merging
-   [ ] Introduce performance testing
-   [ ] Consider switching to Vercel for preview deployments on PRs
-   [ ] Add staging environment if user base grows
