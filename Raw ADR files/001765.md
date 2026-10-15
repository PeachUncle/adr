# ADR-014: Technology Stack & Runtime Standards

**Date:** 2025-10-14  
**Status:** Accepted  
**Author:** Reviewer  
**Cross-References:** PRD §5–§7 (NFRs, security, engineering standards); TDD §0–§3 (stack, build/run, DB), §10 (ops); QA §2–§14 (CI gates, perf/a11y/security)

---

## Context

The product requires a web stack that is type-safe, observable, and CI-friendly while remaining simple enough for a small team to operate. The TDD establishes PostgreSQL as the system-of-record with SQL migrations, a three-layer backend, React SPA frontend, and CI-driven quality gates. This ADR selects concrete technologies, versions, and defaults that satisfy PRD NFRs (security, performance, privacy), keep alignment with the TDD architecture, and remain testable under the QA plan.

---

## Decision

1. **Languages & Frameworks**
   - **TypeScript** (strict mode) across frontend and backend.
   - **Backend:** Node.js (LTS) with **Express** + `express-async-errors`.
   - **Frontend:** **React** + **Vite** + **React Router**; styling with **TailwindCSS**.
   - **Schema/Validation:** **Zod** for input DTOs shared between router and tests.

2. **Data & Migrations**
   - **Database:** **PostgreSQL** (14+).
   - **Data Access:** **Knex.js** (query builder) with first-class **migrations** and **seeds**; no ORM layer.
   - **IDs:** ULIDs for public resources; DB primary keys use BIGINT sequences (or ULID if justified).
   - **Transactions:** Service-managed; repositories accept an optional `trx` handle.

3. **Caching & Messaging**
   - **Cache:** In-memory for local; **Redis** optional for prod read-path acceleration (feature-gated).
   - **Invalidation:** Event-driven invalidation on writes; TTLs for defensive expiry.
   - **Async Jobs / Events:** Lightweight queue (e.g., BullMQ) behind an interface; jobs must be idempotent.

4. **Storage & Media**
   - **User uploads (avatars/media):** Object storage (S3-compatible) in production; dev fallback to local `/uploads`.
   - **Security:** Antivirus scan on upload; server-side re-encode to JPEG/PNG/WebP; size ≤ **5 MB**; private-by-default + **signed URLs**/**proxy** for access.

5. **Security & Identity**
   - **Auth:** JWT **RS256** access tokens + server-stored **rotating refresh tokens**.
   - **RBAC:** Server-side enforcement at router and service layers.
   - **Headers:** CSP (no `unsafe-inline`), HSTS, Referrer-Policy, Permissions-Policy.
   - **CSRF:** Protection for cookie-based sessions/state-changing routes.
   - **Secrets:** From environment/secret manager; never committed.
   - **Logging:** No PII/secrets; include **correlation ID**.

6. **API Design**
   - **Style:** RESTful; JSON over HTTP/HTTPS; **OpenAPI** spec generated from route definitions and Zod schemas.
   - **Idempotency:** `Idempotency-Key` on unsafe writes with deterministic replay and 409 on payload mismatch.
   - **Pagination:** Cursor-based where appropriate; include `next` tokens.
   - **Versioning:** `/v1` prefix; additive changes preferred.

7. **Frontend Standards**
   - **i18n:** Static token catalogs (EN/DE) shipped at build; UGC translation is feature-flagged and off in MVP.
   - **Accessibility:** WCAG AA baseline; axe/Lighthouse in CI.
   - **Performance:** Image optimization, code splitting, route-level suspense.

8. **Observability & Metrics**
   - **Metrics:** Prometheus histograms for request latency (per route), counters for auth failures, cache hits, background job outcomes.
   - **Tracing:** OpenTelemetry ready (HTTP + DB spans).
   - **Logs:** Structured JSON; PII scrubbing in middleware.

9. **Tooling & Build**
   - **Monorepo:** pnpm workspaces (+ Turborepo recommended).
   - **Testing:** Unit (vitest/jest), integration (ephemeral Postgres), E2E (Playwright), perf smoke (k6), ZAP baseline.
   - **Containers:** Multi-stage Dockerfiles; images pushed to **GHCR** with SBOM/provenance.
   - **Budgets:** API **p95 < 300 ms**; LCP **< 2.5 s**; CI fails on **>10%** perf regression.

10. **Feature Flags**
    - Centralized typed flags in `packages/shared/flags.ts` with environment-backed defaults.
    - Critical defaults (e.g., `FEATURE_UGC_AI_TRANSLATION=false` in prod) verified in CI.

---

## Consequences

**Positive**

- SQL-first approach with Knex keeps migrations explicit and reviewable; easier debugging under load.
- Minimal, common libraries reduce cognitive and operational overhead.
- Strong default security posture (headers/CSRF/RBAC/PII-safe logs) and clear observability.

**Negative / Trade-offs**

- No full ORM conveniences (relations/loading); requires disciplined repository patterns.
- Additional work to maintain OpenAPI generation from Zod schemas (automated in CI).

**Operational**

- Migrations are mandatory for all schema changes; forward/backfill steps documented in PRs.
- CI gates performance, a11y, and security; image builds are reproducible and signed.

---

## Alternatives Considered

| Option                             | Description                             | Reason Rejected                                                           |
| ---------------------------------- | --------------------------------------- | ------------------------------------------------------------------------- |
| Prisma ORM                         | Higher-level DX and schema modeling     | Diverges from TDD’s SQL-first migrations; risks opaque queries under load |
| NestJS                             | Opinionated framework with DI & modules | Extra complexity for MVP; Express + modules suffice                       |
| Client-side uploads directly to S3 | Skip server proxy/signing               | Weakened privacy/control; harder to AV-scan/authorize                     |

---

## References

- PRD: NFRs (security/privacy/perf), engineering standards, API principles
- TDD: Stack/architecture, DB/migrations, module layering, build/run contracts
- QA: CI pipeline, budgets, ZAP/Lighthouse/k6, regression thresholds

---

## Status Log

| Version | Date       | Change                                                                                        | Author   |
| ------- | ---------- | --------------------------------------------------------------------------------------------- | -------- |
| v1.0    | 2025-10-14 | Initial ADR selecting Node/Express, React/Vite, Knex/Postgres, object storage, and CI budgets | Reviewer |
