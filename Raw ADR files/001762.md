# ADR-011: Internationalization – Hybrid Model with MVP Static-Only Rollout

**Date:** 2025-10-14  
**Status:** Accepted  
**Author:** Reviewer  
**Cross-References:** PRD §4 (FR-8) & §6.14 i18n/l10n; TDD §1.1, §1.2 (assumptions), §4.8, §5.5; QA §5.1 (AC-8.1…8.5), §11 (performance)

---

## Context

The PRD defines a hybrid i18n approach: all UI strings are statically translated (EN/DE), while user-generated content (UGC) may be translated dynamically via an external AI service with caching, privacy controls, and UX affordances (toggle/original).  
The TDD defers dynamic AI translation to Phase 2 while delivering static i18n in the MVP; it also mandates ADRs for cross-cutting decisions and RTM alignment.  
QA formalizes acceptance: language auto-detect + manual switch; UI tokens must come from static catalogs with EN fallback; delete requests must purge related translation cache entries; and perf budgets apply (API p95 < 300 ms; AI translation ≤ 800 ms on cache miss when enabled).

Goal: lock a decision that reconciles PRD vision (hybrid) with TDD scope (MVP = static only), and is fully testable under the QA plan.

---

## Decision

1. **Architecture (Hybrid-by-Design).**
   - **Static UI i18n (MVP):** All UI strings come from token catalogs (EN/DE) with EN fallback; no runtime translation for UI. Enforcement via lint/checks and CI token coverage. (Meets QA AC-8.1/8.3/8.4.)
   - **Dynamic UGC Translation (Feature-flagged, Phase 2):** A backend adapter (`translateText(lang, text)`) routes to a pluggable provider (OpenAI/DeepL), with caching and PII redaction before egress. When disabled, UGC renders in original language only. (Aligns PRD §6.14; deferred per TDD.)

2. **MVP Scope Switches (Defaults):**
   - `FEATURE_UGC_AI_TRANSLATION=false` in prod/staging; `true` only in controlled test envs.
   - Cache schema (`translation_cache`) and API surfaces are present but inert if the flag is off. (Keeps forward compatibility with PRD while honoring TDD’s deferral.)

3. **Contracts & Budgets:**
   - **Latency:** AI translate path target ≤ 800 ms p95 on cache miss; overall API budgets remain (p95 < 300 ms). If the feature flag is on, requests invoking translation must be async/queued when expected to exceed 800 ms, otherwise the UI shows original with “translated coming” toast.
   - **Privacy:** PII redaction on all external translation calls; only anonymized text in cache; DSR delete purges cache entries linked to user content within ≤14 days per backup purge policy.
   - **Accessibility:** `<html lang>` updated on switch; translation badge and “View original” affordance meet WCAG guidance. (QA a11y checks apply.)

4. **Testability & Observability:**
   - **Metrics:** `i18n_translation_requests_total{provider,hit}` and `i18n_translation_latency_ms` exported; alert if p95 > 800 ms sustained 10 min.
   - **QA Hooks:** Playwright asserts token coverage, language persistence, and cache-purge on DSR. k6 smoke includes translated feed route when flag is enabled.

---

## Consequences

**Positive**

- Unblocks MVP with static i18n now, while keeping clean seams for Phase-2 dynamic UGC translation (no refactor tax).
- Aligns with PRD vision but respects TDD scope via feature flag governance and CI gates.
- Clear QA coverage (AC-8.1…8.5) and performance/observability budgets.

**Negative / Trade-offs**

- Carrying dormant code paths (adapter/cache) adds small maintenance and security surface; mitigated by feature flag = off and CI checks.
- Translation quality/cost risks are deferred, requiring a Phase-2 rollout plan and provider evaluation.

**Operational**

- Feature flag defaults verified in CI/CD; prod config must pin `FEATURE_UGC_AI_TRANSLATION=false`. Rollouts require canary + metrics SLO watch.

---

## Alternatives Considered

| Option                         | Description                                          | Reason Rejected                                                                  |
| ------------------------------ | ---------------------------------------------------- | -------------------------------------------------------------------------------- |
| Static-only i18n (drop hybrid) | Ship only token catalogs; no UGC translation at all. | Conflicts with PRD’s hybrid direction and global UX goals.                       |
| Enable AI translation in MVP   | Turn on UGC translation immediately.                 | Contradicts TDD MVP assumption; adds cost & perf risk before QA infra is proven. |
| Client-side translation        | Perform translation in the browser via JS SDK.       | Violates privacy model (PII control) and complicates caching/observability.      |

---

## References

- ADR template & ADR governance (TDD §15.1.1): required headers, links, status lifecycle.
- PRD – i18n Hybrid (FR-8, §6.14): static UI + dynamic UGC translation, caching, privacy.
- TDD – Scope & Assumptions: MVP = static i18n; dynamic UGC translation explicitly Phase 2.
- QA Plan – AC-8.x, Perf gates: token catalogs, EN fallback, DSR cache purge; API p95 < 300 ms; AI path ≤ 800 ms when enabled.

---

## Status Log

| Version | Date       | Change                                                                     | Author   |
| ------- | ---------- | -------------------------------------------------------------------------- | -------- |
| v1.0    | 2025-10-14 | Initial rewrite with MVP static rollout + Phase-2 flag for UGC translation | Reviewer |
