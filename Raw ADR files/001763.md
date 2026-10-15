# ADR-012: Monorepo Structure, Tooling, and Governance

**Date:** 2025-10-14  
**Status:** Accepted  
**Author:** Reviewer  
**Cross-References:** PRD §7 Engineering Standards; TDD §0–§2 (stack & repo); QA §2–§9 (CI pipeline gates)

---

## Context

We maintain a single codebase that hosts backend, frontend, shared libraries, infra code, and test harnesses. The PRD and TDD establish **pnpm workspaces** as the standard, with optional **Turborepo** for task orchestration and caching, and **Docker Compose** for local orchestration. QA requires CI stages (lint → typecheck → unit/integration/E2E), coverage reporting, performance/a11y/security gates, and artifactized Docker images.

The decision must optimize for: fast local dev, reproducible CI, cacheable builds, clear boundaries, and auditability (CODEOWNERS, changesets, and release notes).

---

## Decision

1. **Repository Layout (top-level)**

```
fitvibe/
├─ apps/
│  ├─ backend/            # Node.js (Express) API
│  └─ frontend/           # React + Vite SPA
├─ packages/
│  ├─ shared/             # TS utilities, domain types, API SDK
│  └─ i18n/               # token catalogs and tooling
├─ tests/                 # e2e (Playwright), perf (k6), security configs
├─ infra/                 # docker-compose, k8s manifests (if any), scripts
├─ .github/               # workflows, CODEOWNERS, issue templates
└─ docs/                  # ADR index, architecture diagrams
```

2. **Package Management & Orchestration**

- **pnpm workspaces** with `link-workspace-packages=true` and `shared-workspace-lockfile=true`.
- **Turborepo** optional but recommended for pipeline caching (`turbo run build --filter=...`).
- Enforce Node/PNPM versions via `.nvmrc` and `packageManager` field.

3. **TypeScript Project References**

- Each app/package is a TS project with references to enable incremental builds (`tsc -b`).
- Disallow cross-layer imports that bypass public APIs via ESLint boundaries.

4. **Build & Run**

- Local: `docker compose up` provides Postgres, Redis, mailhog, and object storage (e.g., MinIO).
- Apps can run outside Docker during dev, but **CI builds Docker images** using deterministic multi-stage Dockerfiles.

5. **Governance**

- **CODEOWNERS** per directory; **conventional commits**; **changesets** for versioning of published packages.
- **Feature flags** centralized in `packages/shared/flags.ts`; defaults set by env and validated in CI (e.g., `FEATURE_UGC_AI_TRANSLATION=false` in prod).
- ADR index maintained under `docs/` with bidirectional links to PRD/TDD sections.

6. **Environment & Secrets**

- Non-production secrets managed via `.env.example` and GitHub Environments; production via secrets manager (referenced by CI).
- No secrets in repo; CI blocks on secret scanning hits.

7. **Caching & Artifacts**

- Turbo/pnpm cache in CI; Docker layer caching for images; test and coverage artifacts uploaded per job.
- Reproducible builds pinned by lockfile; CI fails on lockfile drift.

8. **Testing & CI Pipeline (summary)**

- **lint** → **typecheck** → **unit** (vitest/jest) → **integration** (ephemeral DB) → **e2e** (Playwright) → **coverage upload** (Codecov) → **lighthouse** (CI) → **security scan** (deps + ZAP baseline) → **docker build & GHCR push** → **perf k6 smoke** with budgets → **policy gates**.
- Budgets: API p95 < 300 ms; LCP < 2.5 s; CI fails on >10% perf regression.

9. **Release & Deployment**

- Backend/frontend images pushed to **GHCR** with semver tags; SBOM and provenance (SLSA generator) attached.
- Manual approval gate for production; CD reads feature-flag defaults from environment configuration.

---

## Consequences

**Positive**

- Predictable local and CI builds; clear ownership and publish rules; cacheable tasks.
- Strong alignment to PRD/TDD standards; QA gates enforce quality and budgets.

**Negative / Trade-offs**

- Turborepo adds one more layer of configuration (mitigated with templates).
- Strict boundaries can slow ad-hoc cross-package imports (by design).

**Operational**

- Maintain workspace health checks (orphaned deps, circular refs).
- Nightly job runs `pnpm dedupe`, dependency audit, and license checks.

---

## Alternatives Considered

| Option              | Description                                | Reason Rejected                                                           |
| ------------------- | ------------------------------------------ | ------------------------------------------------------------------------- |
| Yarn workspaces     | Use Yarn instead of pnpm                   | Not aligned with PRD/TDD; slower cold installs in CI                      |
| Polyrepo            | Separate repos for backend, frontend, libs | Complicates shared types, versioning, and coordinated releases            |
| Nx instead of Turbo | Use Nx for orchestration                   | Added complexity for our current scope; Turbo meets needs with less setup |

---

## References

- PRD §7 Engineering standards (monorepo, tooling alignment)
- TDD §0–§2 Repository, stack, and build contracts
- QA §2–§9 CI pipeline, budgets, and gates

---

## Status Log

| Version | Date       | Change                                                                  | Author   |
| ------- | ---------- | ----------------------------------------------------------------------- | -------- |
| v1.0    | 2025-10-14 | Initial ADR using pnpm workspaces + optional Turbo; CI/QA gates defined | Reviewer |
