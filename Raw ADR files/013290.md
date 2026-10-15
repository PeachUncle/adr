# ADR-004: Database Migration Strategy (Flyway)

**Status:** Accepted  
**Date:** 2025-12-31  
**Decision Type:** Architecture & Implementation  

## Related

- ADR-001 — Modular Monolith Architecture  
- ADR-002 — Integration Model (Sync-first)  
- ADR-003 — Deferred Microservices & Distribution Strategy  
- `requirements-refined.md` (Maintainability, Reliability)  
- Iteration 2 — Executable Architecture

## Context

The Order Processing System (OPS) requires a consistent, versioned approach for managing database schema changes.

Key architectural drivers:

- **Maintainability:** Schema changes must be traceable, testable, and reversible.  
- **Reliability:** Database state should be predictable across environments.  
- **Time-to-Market:** Avoid heavy tooling or manual DB administration early on.  
- **Scalability (Deferred):** Strategy must support future evolution to AWS-managed DBs.

Current delivery scope:

- Local development & CI with Testcontainers (PostgreSQL)
- No cloud resources provisioned yet
- Schema evolves as part of codebase

## Decision

We will use **Flyway** as the database migration tool for managing PostgreSQL schema changes.

### Why Flyway?

- **Convention-driven** — minimal configuration
- **Version-controlled** — SQL migrations live in repo alongside code
- **Simple rollback & forward-only strategy**
- **Native Spring Boot integration**
- **Compatible with PostgreSQL in AWS (RDS / Aurora)**

### Where Migrations Live

```
order-system-services/
    order-database/
        src/main/resources/db/migration/
        V1__init_schema.sql
        V2__add_order_status_history.sql
        ...
```

### Execution Model

| Environment | Execution Trigger | Notes |
|-------------|-------------------|-------|
| Local Dev (Spring Boot) | App startup | Using Testcontainers |
| CI Pipeline | Integration tests | Ensures schema consistency |
| AWS Deployment | App startup or Terraform hook (future) | TBD in Iteration 4 |

**Migrations are mandatory** for schema changes — manual DB modifications are not allowed.

## Rationale

Flyway satisfies current NFRs and roadmap because:

| Requirement | Coverage |
|-------------|-----------|
| Maintainability | Each schema change traceable by version |
| Reliability | Predictable structure across environments |
| Time-to-Market | Quick setup + no extra infrastructure |
| Scalability (Deferred) | Works with RDS, versioned DB state |

Alternatives like Liquibase offer more automation but add complexity **not justified** at current system maturity.

## Alternatives Considered

| Option | Status | Reason |
|--------|--------|--------|
| **Liquibase** | Deferred | Higher flexibility but more config overhead |
| **Manual SQL scripts** | Rejected | No traceability; error-prone; breaks IaC strategy |
| **EF / Hibernate auto-DDL** | Rejected | Non-deterministic & environment-dependent |

## Consequences

### Positive

- Predictable schema evolution
- Enables Dev/Test/Prod alignment
- Inline with Infrastructure-as-Code direction
- Very low friction for Team-of-1 evolution

### Negative / Trade-offs

- Limited reversible migrations (forward-only preferred)
- Migration conflicts will require discipline as team size grows
- Cross-service DB schemas will need governance later

### Future Considerations (Iteration 4+)

- Terraform lifecycle integration
- Remote state validation in CI
- Separate migration container for production deployment
- Read/write DB roles once scalability becomes priority

## Status

**Approved for Iteration 2** — Flyway integrated as the baseline DB migration strategy.

Migration workflow now becomes part of system onboarding, testing, and deployment.

**Decision Accepted — Flyway is the migration baseline for schema versioning.**
