# ADR-019: Caching & Performance Strategy

**Date:** 2025-10-14  
**Status:** Accepted  
**Author:** Reviewer  
**Cross-References:** PRD §5 NFRs (Performance, Security), §7 Engineering Standards; TDD §3–§7 (architecture, routes), §9–§10 (build/run), §15 (ADR index); QA §11 (performance), §14 (regression), §8–§12 (CI gates)

---

## Context

We must guarantee responsive UX and predictable backend latency while preserving correctness and privacy. The PRD establishes user-facing performance goals (fast content, efficient media), and the TDD/QA specify **API p95 < 300 ms**, **LCP < 2.5 s**, and **CI regression gates**. Caching improves tail latency and cost, but requires **disciplined invalidation** and **observable budgets** to avoid stale data or inconsistency.

This ADR defines the caching layers, invalidation rules, and performance budgets enforced in CI/CD and runtime.

---

## Decision

1. **Performance Budgets (enforced)**
   - **API latency (overall):** **p95 < 300 ms** (per release, measured in staging parity).
   - **Endpoint groups:** auth ≤ 200 ms; CRUD ≤ 300 ms; feed ≤ 400 ms; analytics/reporting ≤ 600 ms.
   - **Frontend:** **LCP < 2.5 s** (mid-tier 4G, cold cache) and CLS ≤ 0.1.
   - **Regression policy:** **Fail CI** on **> 10%** degradation vs baseline (k6 + Lighthouse).

2. **Caching Layers**
   - **Application cache** (in-memory for dev/test; **Redis** optional in prod): wraps repository/service reads with `cache.get/set/invalidate`.
   - **HTTP caching**: `ETag`/`Last-Modified` and `Cache-Control` for safe GETs; conditional requests supported.
   - **CDN/edge** (if configured): static assets, public feeds (feature-flagged), and media derivatives (signed URLs or proxy).
   - **Translation cache** (feature-flagged): keyed by `hash(text + lang)` with TTL and DSR purge hooks.

3. **What Gets Cached**
   - **Read-heavy, stable queries**: exercise library lookups, session summaries, leaderboard/feed slices (if not personalized), configuration, and static catalogs (i18n).
   - **Materialized views** for analytics aggregates (as per ADR-008), refreshed incrementally on writes and by schedule.
   - **OpenAPI spec and SDK** responses (short TTL) to reduce build-time fetches during local dev.

4. **Invalidation Rules**
   - **Write-through events**: services emit `entity.updated|created|deleted` → invalidate keys for affected views.
   - **Key strategy**: `domain:entity:{id}:v{schema}` and `view:{name}:{params_hash}`; bump `v{schema}` on incompatible schema changes.
   - **TTL defaults**: 60–300 s for dynamic views; 24 h for static catalogs; **no infinite TTL** for user-scoped data.
   - **DSR deletes**: purge user-scoped cache entries by `owner_user_id` index; complete within **≤ 24 h**; translation cache ≤ **14 days** for backups.

5. **Correctness & Privacy**
   - **Private-by-default**: no public cache for user-scoped resources; CDN only for explicitly public or signed media.
   - **Authn/z aware caching**: cache keys include user/role scope when results depend on identity.
   - **No PII in cache keys/values** beyond stable IDs; redact or hash sensitive text for translation cache.

6. **Observability & SLOs**
   - Metrics: `cache_hits_total`, `cache_misses_total`, `cache_write_errors_total`, `http_request_duration_seconds{route}`, `lighthouse_lcp_seconds`, `perf_regression_ratio`.
   - Dashboards show hit ratio, tail latency, and invalidation events per domain; alerts if API p95 > budget for 10 min or hit ratio < 30% on targeted caches.

7. **CI/CD Enforcement**
   - **k6 smoke** runs against staging-parity compose services; gates on budgets and regression ratio.
   - **Lighthouse CI** runs for SPA; fail if **LCP ≥ 2.5 s** or score < **90**.
   - **Perf baselines** stored per branch/release; PR comments summarize deltas.
   - **Load profile config** (ramp-up, VUs, duration) checked into repo for reproducibility.

8. **Fallbacks & Degradation**
   - If Redis is unavailable, the app falls back to in-memory with **reduced TTLs** and logs a warning (SLO impact observed).
   - On high error rates or cold caches, rate limit expensive endpoints to protect databases and return fast, partial responses where acceptable (feature-flagged).

9. **Media & Asset Optimization**
   - Images pre-sized/derivatized (see ADR-017); `Accept`/`Content-Type` negotiated to serve WebP/AVIF when supported.
   - Static assets fingerprinted (`app.[hash].js`); long-term `Cache-Control` with immutable flags; HTML gets short TTL and must-revalidate.

10. **Testing Strategy**
    - **Unit**: cache key generation and invalidation hooks tested per domain.
    - **Integration**: write → read paths verify fresh data after invalidation; ETag/conditional requests covered.
    - **E2E**: Playwright verifies perceived performance and correctness after edits.
    - **Perf**: k6 scripts exercise hot endpoints and report p95/p99; baseline stored.

---

## Consequences

**Positive**

- Predictable performance with guardrails in CI; reduced DB load via targeted caching.
- Clear invalidation semantics tied to domain events; privacy preserved by scoping and signed access.
- Observability enables fast detection of regressions and cache pathologies.

**Negative / Trade-offs**

- Engineering effort to maintain keys, events, and dashboards.
- Edge caching for semi-public content requires careful capability flags and purge tooling.

**Operational**

- Rotate Redis passwords/credentials; monitor memory pressure and eviction policies.
- Regularly review TTLs and hit ratios; tune baselines quarterly.

---

## Alternatives Considered

| Option                        | Description              | Reason Rejected                                                     |
| ----------------------------- | ------------------------ | ------------------------------------------------------------------- |
| Cache everything aggressively | Long TTLs for all reads  | Staleness and privacy risks; fails correctness for user-scoped data |
| DB query caching only         | Rely on DB-level cache   | Limited control/visibility; less effective across services and CDN  |
| No regression gate            | Skip k6/Lighthouse gates | Violates QA policy; risks unbounded perf drift                      |

---

## References

- PRD: Performance budgets, security/privacy guidance for caching
- TDD: Architecture, modules, ADR index, build/run contracts
- QA: Performance tests, regression policy, CI gates (k6, Lighthouse)

---

## Status Log

| Version | Date       | Change                                                                         | Author   |
| ------- | ---------- | ------------------------------------------------------------------------------ | -------- |
| v1.0    | 2025-10-14 | Initial ADR defining caching layers, invalidation, budgets, and CI enforcement | Reviewer |
