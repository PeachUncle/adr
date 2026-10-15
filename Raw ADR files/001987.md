# ADR-066 — LM Studio + Control Plane Integration

- **Status:** Accepted
- **Date:** 2025-11-14
- **Supersedes:** ADR-007 (partial — LM Studio integration approach)
- **Superseded by:** (none)

## Context

We want LM Studio to be a first-class local LM backend while preserving:

- Guarded Tool Calls and hermetic behavior
- Postgres control-plane observability (schema `control`)
- Existing DSN and governance rules

RFC-080 (`docs/rfcs/RFC-080-lm-studio-control-plane-integration.md`) proposes:

- `agentpm/adapters/lm_studio.py` as the HTTP adapter
- `agentpm/runtime/lm_routing.py` as the routing helper
- `agentpm/runtime/lm_logging.py` for control-plane logging
- Health-aware routing and control-plane logging for LM calls

This ADR ratifies that design and records the architectural decision.

**Related ADRs:**
- ADR-007 — LLM Integration and Confidence Metadata (earlier design)
- ADR-010 — Qwen Integration
- ADR-065 — Postgres SSOT / control plane

## Decision

We adopt RFC-080 as the authoritative design for LM Studio integration:

1. **All LM Studio usage must go through:**
   - Adapter: `agentpm/adapters/lm_studio.py`
   - Routing helper: `agentpm/runtime/lm_routing.py`
   - Logging wrapper: `agentpm/runtime/lm_logging.py` (for control-plane observability)

2. **LM calls are observable via the Postgres `control` schema when DB is available.**
   - Logging is best-effort and becomes a no-op when DB is unreachable or disabled (db_off).
   - Tool identifier: `lm_studio` in `control.agent_run` table

3. **`pmagent health lm` is the canonical health surface for LM Studio**, using the adapter + routing.

4. **No new DSNs or schemas are introduced**; we reuse the existing `GEMATRIA_DSN` and `control` schema.

5. **Centralized configuration** via `scripts/config/env.py`:
   - `get_lm_studio_settings()` returns unified config dict
   - No direct `os.environ` calls in adapter/routing code

Where ADR-007 conflicts with this ADR, this ADR + RFC-080 take precedence for the current implementation.

## Rationale

- **Centralized adapter pattern** ensures consistent LM Studio behavior across the codebase
- **Control-plane logging** provides observability without breaking hermetic CI behavior
- **Health-aware routing** enables graceful fallback to remote LLMs when LM Studio is unavailable
- **Reuse of existing infrastructure** (DSNs, control schema) minimizes architectural complexity

## Consequences

### Pros

- Centralized LM Studio behavior (adapter + routing + logging)
- Control-plane visibility for LM-backed calls
- Hermetic behavior in CI and db_off modes
- Health-aware routing enables reliable fallback strategies

### Cons / Tradeoffs

- Extra indirection in runtime (adapter + routing + logging layers)
- Requires keeping adapter, routing, and control-plane logging in sync
- Additional test surface area (DB-on vs DB-off scenarios)

## Implementation Notes

Initial implementation landed in:

- **PR #532** — LM Studio adapter + routing (P0 + P1)
  - Created `agentpm/adapters/lm_studio.py` with `lm_studio_chat()` function
  - Created `agentpm/runtime/lm_routing.py` with `select_lm_backend()` helper
  - Created `agentpm/runtime/lm_logging.py` with `lm_studio_chat_with_logging()` wrapper
  - Updated `scripts/guards/guard_lm_health.py` to use adapter
  - Added comprehensive tests (25/25 passing, all hermetic)

Follow-up Phase-3C PRs for:

- `pmagent health lm` wiring (completed in PR #532)
- Control-plane logging wrapper (completed in PR #532)
- Tests for DB-on/DB-off behavior (completed in PR #532)
- Routing integration into real pipelines (P1b/P2 — pending)
- Documentation (LM Studio setup runbook — P2 — pending)

## Phase-4: LM Observability Exports

Phase-4 extends the control-plane integration with observability exports for downstream applications:

1. **`lm_usage_7d.json`** — Raw usage metrics (total calls, successful/failed, latency) for the last 7 days
2. **`lm_health_7d.json`** — Health metrics (success rate, error rate, health score) for the last 7 days
3. **`lm_insights_7d.json`** — Aggregated insights (LM Studio usage ratio, top error reasons, fallback rates)
4. **`lm_indicator.json`** — **Canonical LM status signal for downstream apps** (offline/healthy/degraded)

All exports are db_off + LM-off safe (graceful fallback when DB or LM Studio unavailable).

**For downstream applications** (StoryMaker, BibleScholar, etc.), **use `lm_indicator.json` as the primary LM status signal** instead of parsing raw metrics. The indicator provides a simple, stable interface:
- `status`: "offline" | "healthy" | "degraded"
- `reason`: "db_off" | "no_calls" | "high_error_rate" | "ok"
- Core metrics: `success_rate`, `error_rate`, `total_calls`, `db_off`

See `docs/SSOT/MASTER_PLAN.md` Phase-4 section for implementation details.

## References

- **RFC-080** — LM Studio + Control Plane Integration (design specification)
- **ADR-007** — LLM Integration and Confidence Metadata (earlier design)
- **ADR-010** — Qwen Integration
- **ADR-065** — Postgres SSOT / control plane
- **PLAN / MASTER_PLAN** entries for Phase-3C and Phase-4

