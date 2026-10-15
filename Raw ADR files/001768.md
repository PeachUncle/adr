# ADR-018: CI/CD with GitHub Actions and GHCR

**Date:** 2025-10-14  
**Status:** Accepted  
**Author:** Reviewer  
**Cross-References:** PRD §7 Engineering Standards; PRD §5 NFRs (security/perf); TDD §9–§10 Build/Run/Deploy; QA §2–§14 CI gates (tests, perf, a11y, security)

---

## Context

We require a deterministic, secure, and budget-enforcing delivery pipeline. The PRD, TDD, and QA plan define mandatory stages (lint, type-check, unit/integration/E2E tests), performance/a11y/security gates, and containerized releases. This ADR standardizes the CI/CD implementation on **GitHub Actions** with **GHCR** for images, **OIDC** for cloud access, and signed/supported artifacts (SBOM, SLSA provenance).

---

## Decision

1. **Triggers & Branch Strategy**
   - **All PRs**: run full CI (quality gates, tests, security, performance, accessibility).
   - **Push to `main`, `dev`, `stage`**: run full CI + build images + publish tags (E2E and build jobs enabled).
   - **Release tags (`vX.Y.Z`)**: publish immutable images, SBOM, and provenance; deploy to staging → manual approval → production.
   - Protected branches with required checks; linear history via squash merges.

2. **Workflow Structure & Stages**

   The CI pipeline is structured as **multiple parallel and sequential jobs** for efficiency and clarity:

   **Primary Quality Gates** (run on all PRs and pushes, in parallel):
   - **`quality`** job: lint (`pnpm lint:check`), typecheck (`pnpm typecheck`), unit tests (backend/frontend with coverage), coverage gate (`pnpm test:coverage:gate`), QA baseline validation, i18n check, feature flags check, build (`pnpm build`).
   - **`database_tests`** job: migration tests and seed tests (separate from unit tests for isolation).

   **Secondary Jobs** (run after quality gates pass, mostly in parallel):
   - **`openapi_spec`**: Generate and validate OpenAPI schema.
   - **`integration`**: Integration tests with ephemeral Postgres/Redis via services; migrations/seeds per run.
   - **`metrics_contract`**: Validate Prometheus metrics exposure.
   - **`security`**: Dependency audit (`pnpm audit --prod --audit-level=high`), OSV scanner, Snyk scan, TruffleHog secret scanning, static secret scan, Trivy container scan.
   - **`zap_baseline`**: OWASP ZAP baseline scan (if target URL configured).
   - **`performance`**: k6 smoke test, performance budget assertion (API p95 < 300ms, LCP < 2.5s, no >10% regression), Lighthouse CI.
   - **`accessibility`**: Axe accessibility suite for WCAG 2.1 AA compliance.
   - **`qa_summary`**: Aggregate coverage and performance metrics, generate QA summary.

   **Conditional Jobs** (run only on push to `main`/`stage`):
   - **`e2e`**: Playwright E2E tests against preview server; artifacts (screenshots, traces) uploaded.
   - **`build`**: Build multi-arch Docker images (linux/amd64, linux/arm64), generate SBOMs (via Docker buildx), sign images with cosign (keyless OIDC), create GitHub release, upload container artifacts.

   > See `.github/workflows/ci.yml` for the complete job definitions and dependencies.

3. **Artifacts & Supply Chain Security**
   - **SBOM** generated per image and attached to release.
   - **Provenance** (SLSA generator for GitHub) publishes attestations.
   - **Cosign** image signing (keyless via OIDC) and policy verification at deploy time.

4. **Secrets & Cloud Access**
   - Use **GitHub Environments** and **OIDC federation** for cloud credentials (no long-lived keys).
   - Secrets are rotated and scoped per environment; runners have minimal permissions.

5. **Caching & Speed**
   - **pnpm** and **turbo** caches keyed by lockfile + task graph.
   - **Docker layer cache** enabled with `--cache-from` for repeatable, fast builds.
   - Matrix jobs for Node versions where helpful (LTS + current) on CI-only lanes.

6. **Testing Data & Ephemeral Infra**
   - Compose services: Postgres, Redis, MinIO, Mailhog.
   - DB migrations/seeds executed anew per job; tests clean up state.
   - Artifacts (JUnit, coverage, Playwright traces, k6 results) uploaded for PR review.

7. **Policy Gates & Budgets**
   - **Fail build** when any gate is breached: lints/warnings, type errors, unit/integration/E2E failures, Lighthouse <90, ZAP High/Critical, perf budgets or **>10% regression**.
   - Required checks configured in branch protection to enforce gates.

8. **Releases & Rollbacks**
   - Semantic versioning with conventional commits + changesets.
   - **Blue/green or canary** supported via environment config; rollback = re-deploy previous tag.
   - Release notes include OpenAPI artifact links and migration notes.

9. **Observability & Notifications**
   - Publish test & audit summaries to PR comments.
   - On deployment, post release links, image digests, and SLO snapshot (latency, error rate).
   - Alerts wired to on-call for failed post-deploy checks.

10. **Compliance & Retention**
    - Retain logs and artifacts for ≥ 30 days (PR) and ≥ 180 days (release) as per policy.
    - Access controls applied to environments; audit trail maintained for approvals.

---

## Consequences

**Positive**

- Reproducible, secure pipeline with explicit quality budgets.
- Faster feedback via caches and matrices; safer releases through canary + manual production gate.
- Strong supply chain controls (SBOM, provenance, signing).

**Negative / Trade-offs**

- Additional CI minutes for perf/a11y/security gates (intentional).
- Slight configuration complexity for OIDC and attestations.

**Operational**

- Keep lockfiles and base images updated; rotate caches; review budgets quarterly.
- Record baselines for perf to keep regression signal healthy.

---

## Alternatives Considered

| Option                | Description                | Reason Rejected                                                  |
| --------------------- | -------------------------- | ---------------------------------------------------------------- |
| Third-party CI        | CircleCI/GitLab            | GitHub-native reduces friction and integrates with GHCR and GHAS |
| Push-on-merge deploys | Auto prod on `main`        | Violates need for manual approval and staged verifications       |
| No SBOM/provenance    | Skip supply chain metadata | Fails compliance and traceability goals in PRD/TDD               |

---

## References

- PRD: Engineering standards, performance/security budgets
- TDD: Build/run/deploy conventions, container strategy
- QA: CI gates, regression policy, a11y/security/perf tooling

---

## Status Log

| Version | Date       | Change                                                                                 | Author   |
| ------- | ---------- | -------------------------------------------------------------------------------------- | -------- |
| v1.0    | 2025-10-14 | Initial ADR for CI/CD on GitHub Actions with GHCR, SBOM, provenance, and quality gates | Reviewer |
