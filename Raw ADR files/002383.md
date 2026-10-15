---
title: ADR-006: FCN API Service Architecture
doc_type: adr
status: Accepted
version: 0.2.0
date: 2025-10-22
owner: siripong.s@yuanta.co.th
approver: siripong.s@yuanta.co.th
classification: Internal
tags: [adr, architecture, fcn, api, service]
related:
  - adr-003-fcn-version-activation.md
  - adr-004-parameter-alias-policy.md
  - adr-005-fcn-supersession-governance.md
  - ../interfaces/openapi/fcn-openapi-starter.yaml
  - ../../ba/products/structured-notes/fcn/business-rules.md
---

# ADR-006: FCN API Service Architecture

## 1. Context

The FCN (Fixed Coupon Note) domain has matured with specifications (v1.0, v1.1.0), governance (ADR-003/004/005), OpenAPI contract, Spectral ruleset, and validation tooling. We now proceed to implement a production runtime.

Originally this ADR was proposed with open questions around runtime, database, and tracing. Those choices are now confirmed:
- Runtime Framework: FastAPI (Python)
- Primary Database: Microsoft SQL Server (MSSQL)
- Distributed Tracing: Full adoption using OpenTelemetry (OTel) instrumentation from Day 1

## 2. Decision

Adopt a **Modular Monolith** service implemented in **Python/FastAPI**, backed by **MSSQL** for persistence, with **OpenTelemetry tracing** integrated across HTTP, database calls, and domain service execution. This supports rapid iteration, aligns with internal Python expertise and enterprise MSSQL standards, and ensures observability baseline (traces, metrics, logs) is available early.

Key points:
- FastAPI chosen for async performance, strong typing (Pydantic), and ecosystem maturity.
- MSSQL selected due to enterprise standardization, existing operational tooling (backups, HA, compliance).
- OTel instrumentation (via `opentelemetry-instrumentation-fastapi`, MSSQL driver wrapper instrumentation) with OTLP exporter to collector (Jaeger/Tempo).
- Future microservice decomposition deferred until scaling or organizational boundaries require it (see Migration & Scalability Triggers).

## 3. Alternatives Considered

| Alternative | Pros | Cons | Reason Rejected |
|-------------|------|------|-----------------|
| NestJS + PostgreSQL | Strong TypeScript ecosystem | Team expertise Python; MSSQL integration less standard | Mismatch with internal skill profile |
| Microservices early | Independent scaling | Infra & coordination overhead | Premature; complexity before domain stabilizes |
| Event Sourcing + CQRS | Replayability & audit perfection | High implementation & ops cost | Overkill for v1 lifecycle needs |
| No tracing until later | Lower initial complexity | Harder latency diagnosis & regression detection | Observability critical; tracing adopted now |

## 4. Drivers / Requirements Mapping

| Driver | Architectural Response |
|--------|------------------------|
| Deterministic lifecycle logic (BR-005..025) | Domain service layer with pure functions & scenario tests |
| Governance enforcement (supersession, activation) | Startup loader from OpenAPI `x-governance`; request pre-validation |
| Enterprise DB alignment | MSSQL schema & migration scripts |
| Observability & audit | Structured logging + tracing spans (controller, domain, DB) |
| Performance & latency targets | FastAPI async; pool management; prepared statements |
| Idempotent booking & observations | Idempotency middleware (backend decision pending) |

## 5. Architecture Overview

Layers:
```
app/         (FastAPI routers, controllers, DTO serialization)
domain/      (Models, value objects, lifecycle & settlement services)
validation/  (Rule registry: schema + cross-field + governance)
infra/       (MSSQL repositories, optional Redis cache/idempotency)
observability/ (Tracing config, metrics, logging adapters)
tests/       (unit, integration, contract, scenario, performance)
```

## 6. Domain Components

- TemplateService: Create/update/deprecate templates; enforce active spec_version.
- TradeService: Booking, amendment (limited), termination.
- ObservationService: Evaluate autocall (KO), coupon eligibility, KI status.
- SettlementService: Maturity redemption (capital-at-risk logic).
- LifecycleService: Append lifecycle events (autocall, coupon_payment, maturity).

## 7. Persistence (MSSQL)

Tables (prefix `fcn_`):
| Table | Purpose | Notes |
|-------|---------|-------|
| fcn_template | Template definitions | `status`, `spec_version`, `issuer`, JSON/NVARCHAR for arrays |
| fcn_trade | Trade instances | Flags: `autocall_triggered`, `ki_triggered` |
| fcn_observation | Per observation data | Unique (trade_id, observation_date) |
| fcn_lifecycle_event | Audit trail of events | Event payload (JSON) |
| fcn_idempotency_key | Idempotency store (if MSSQL chosen) | `key_hash`, `request_fingerprint`, `response_snapshot`, `expires_at` |

Migrations: Alembic + MSSQL driver (SQLAlchemy). Use `datetimeoffset` for timestamps, proper indexing.

Indexes:
- fcn_trade(spec_version, status)
- fcn_observation(trade_id, observation_date)
- fcn_lifecycle_event(trade_id, event_type)

## 8. Idempotency

Decision pending on backend storage (Redis vs MSSQL). Interim abstraction:
- `IdempotencyStore` interface with MSSQL and Redis adapters.
- Default initial implementation: MSSQL (ensures durability) until Redis cluster provisioned.

## 9. Validation & Rule Registry

Rule categories:
- Structural: Derived from OpenAPI & JSON Schema.
- Cross-field: e.g., `knock_in_barrier_pct < put_strike_pct`.
- Governance: Reject superseded `spec_version`.
- Business logic preconditions: Memory coupon constraints, observation date ordering.

Interface:
```python
class ValidationRule:
    id: str
    severity: Literal["error","warn"]
    applies(entity) -> bool
    evaluate(entity) -> list[Violation]
```

## 10. Observability

### Tracing
- Root span per request (`http.request`).
- Child spans: `validation.run`, `repository.query`, `domain.observation.evaluate`, `settlement.calculate`.
- Export OTLP → Collector → Jaeger/Tempo.

### Metrics (Prometheus)
- Counter: `fcn_trades_created_total`
- Counter: `fcn_observations_processed_total`
- Counter: `fcn_autocalls_triggered_total`
- Counter: `fcn_validation_errors_total{code}`
- Histogram: `fcn_observation_latency_seconds`
- Gauge: `fcn_active_versions_count`

### Logging
- JSON lines: `{ "ts": "...", "level": "info", "trace_id": "...", "msg": "Trade booked", "trade_id": "..." }`
- Exclude sensitive PII; follow internal masking policy.

## 11. Error Envelope

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Coupon memory cap violated",
    "violations": [{ "path": "$.memory_carry_cap_count", "constraint": "non_negative" }],
    "trace_id": "uuid",
    "details": { "provided": -1 }
  }
}
```

## 12. Performance & Non-Functional Targets

| Metric | Target (P95) | Notes |
|--------|--------------|-------|
| Trade booking latency | < 500 ms | Validation + persistence |
| Observation processing | < 350 ms | Evaluation + lifecycle writes |
| Error rate (validation) | < 2% normative | Governance & rule quality |
| Availability | 99.9% monthly | Excludes planned maintenance |
| Cold start | < 2 s | FastAPI app init |

## 13. Migration & Scalability Triggers

Decompose modular monolith when ANY of:
- Sustained observation rate > 20K/minute.
- Independent scaling needs (coupon engine CPU vs booking I/O).
- Separate ownership teams for lifecycle vs booking emerge.

First decomposition target: Extract Observation + Lifecycle into separate service.

## 14. Testing Strategy

| Test Type | Tooling | Goal |
|-----------|---------|------|
| Unit | pytest | ≥ 90% domain services coverage |
| Integration | testcontainers (MSSQL), redis (if used) | Repository correctness |
| Contract | Schemathesis / Dredd | Drift prevention |
| Scenario | Custom fixtures (multi-observation) | Exercise BR-005..025 paths |
| Load | k6 (HTTP) | Validate latency targets |
| Trace Audit | OTel inspection | Ensure span naming & coverage |

## 15. Security

- JWT Bearer auth (issuer, audience validated).
- Scope checks per endpoint: `template:write`, `trade:observe`.
- Strict input parsing (Pydantic models) & server-side validation.
- MSSQL: least-privilege user; parameterized queries.

## 16. Governance Integration

Startup:
1. Load OpenAPI spec.
2. Parse `x-governance.active_versions`, `superseded_versions`.
3. Inject into `GovernanceService`.

Runtime:
- Booking rejects superseded version with `SPEC_VERSION_SUPERSEDED`.
- `/internal/governance` endpoint returns governance snapshot.



## 17. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| MSSQL ORM inefficiencies | Latency spike | Use SQLAlchemy Core for hot paths |
| Tracing overhead | Increased latency | Dynamic sampling; exclude health endpoints |
| Idempotency collisions | Duplicate or missed replay | Hash canonical request body + headers |
| Governance drift | Accept invalid versions | Spectral + startup sanity check |
| Complex coupon logic edge cases | Incorrect payouts | Exhaustive scenario tests + boundary checks |

## 18. Acceptance Criteria

- Architecture updated with chosen stack (FastAPI, MSSQL, OTel).
- Runtime & tracing open questions resolved.
- Idempotency backend decision deferred with abstraction defined.
- Performance targets enumerated.
- Security & observability strategy defined.

## 19. Open Questions (Updated)

| ID | Question | Owner | Target Date |
|----|----------|-------|-------------|
| OQ-ADR006-02 | Finalize idempotency backend (Redis vs MSSQL hybrid) | SA + Ops | 2025-10-26 |
| OQ-ADR006-04 | Decision on async task queue for heavy lifecycle ops (RQ/Celery) | SA | 2025-11-05 |
| OQ-ADR006-05 | Data retention policy for lifecycle events (regulatory) | Compliance + SA | 2025-11-10 |

## 20. Change Log

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 0.1.0 | 2025-10-22 | siripong.s@yuanta.co.th | Initial Proposed ADR |
| 0.2.0 | 2025-10-22 | siripong.s@yuanta.co.th | Accepted; finalized FastAPI, MSSQL, tracing; added performance targets & updated open questions |

