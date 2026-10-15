ok # ADR-001: CQRS Architecture for Audit and Analytics

Date: 2025-01-14

## Status

Proposed

## Context

ValidaHub needs to handle complex audit requirements while maintaining good performance for both operational queries and analytical workloads. The system must:

1. **Audit Requirements**
   - Track every validation, correction, and download
   - Maintain immutable history for compliance (LGPD/GDPR)
   - Store original and corrected CSV files
   - Provide detailed activity logs per user

2. **Performance Requirements**
   - Sub-second response for recent data queries
   - Handle CSV files from 10MB to 1GB
   - Support concurrent validations
   - Generate analytics without impacting operations

3. **Business Requirements**
   - Show validation history to users
   - Generate reports for marketplace trends
   - Provide dashboards with real-time metrics
   - Enable data-driven insights for product improvement

4. **Technical Constraints**
   - Small team (need pragmatic solutions)
   - Limited initial budget
   - Must work with existing PostgreSQL setup
   - Cannot disrupt current production flow

## Decision

We will implement a **pragmatic CQRS approach** that starts simple and evolves based on actual needs:

### Phase 1: CQRS Lite (Q1 2025)
Use a single PostgreSQL database with logical separation between write and read models:

```
PostgreSQL
├── Write Models (normalized)
│   ├── validation_jobs
│   ├── correction_events
│   └── audit_events (append-only)
└── Read Models (denormalized)
    ├── validation_summary_view
    ├── user_activity_view
    └── error_statistics_view

Redis (cache layer)
└── Hot queries and recent data
```

### Phase 2: Event Sourcing (Q3 2025)
Add event sourcing for critical flows while maintaining the current system:

```
Event Store (PostgreSQL)
├── validation_events
├── correction_events
└── template_events

Projections (PostgreSQL)
├── Current state tables
└── Analytics aggregations
```

### Phase 3: Specialized Stores (Future)
Only when scale demands it, add specialized databases:

```
Write Side          Read Side
PostgreSQL     →    PostgreSQL (current)
                   TimescaleDB (time-series)
                   S3/Parquet (historical CSVs)
                   Elasticsearch (log search)
```

## Consequences

### Positive

1. **Incremental Approach**
   - Start simple, evolve based on real needs
   - No big-bang migration required
   - Learn from actual usage patterns

2. **Audit Trail**
   - Complete history of all operations
   - Immutable append-only log
   - Compliance-ready from day one

3. **Performance**
   - Read/write workloads separated
   - Cache layer for hot data
   - Materialized views for complex queries

4. **Cost-Effective**
   - Reuse existing PostgreSQL
   - No additional infrastructure initially
   - Scale costs with growth

5. **Developer Experience**
   - Clear separation of concerns
   - Easier to reason about data flow
   - Better testability

### Negative

1. **Complexity**
   - More code to maintain
   - Need to manage eventual consistency
   - Additional abstraction layer

2. **Data Duplication**
   - Same data in multiple forms
   - Increased storage costs
   - Sync complexity between models

3. **Learning Curve**
   - Team needs to understand CQRS patterns
   - New debugging challenges
   - More moving parts

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Eventual consistency issues | High | Start with sync updates, move to async gradually |
| Storage cost explosion | Medium | Implement data retention policies, archive old data |
| Query performance degradation | High | Monitor query patterns, add indexes proactively |
| Complex debugging | Medium | Comprehensive logging, correlation IDs |
| Team resistance | Low | Training, clear documentation, gradual rollout |

## Alternatives Considered

### Alternative 1: Traditional CRUD
Keep simple CRUD operations without CQRS.

- ✅ Pros: Simple, well-understood, less code
- ❌ Cons: Performance issues at scale, complex queries slow down writes
- **Rejected because**: Audit requirements need different optimization than operational queries

### Alternative 2: Full Event Sourcing from Start
Implement complete event sourcing immediately.

- ✅ Pros: Perfect audit trail, time-travel debugging
- ❌ Cons: High complexity, team not ready, overkill for current scale
- **Rejected because**: Too complex for current needs and team size

### Alternative 3: Separate Databases Immediately
Use PostgreSQL for writes and ClickHouse/TimescaleDB for reads.

- ✅ Pros: Optimized for each workload, better scale
- ❌ Cons: Higher costs, operational complexity, sync challenges
- **Rejected because**: Premature optimization, not needed yet

### Alternative 4: NoSQL Document Store
Use MongoDB or DynamoDB for flexibility.

- ✅ Pros: Schema flexibility, good for varying data
- ❌ Cons: Loss of ACID guarantees, team expertise in SQL
- **Rejected because**: Need strong consistency for financial data

## Implementation Plan

### Sprint 1: Foundation (2 weeks)
- [ ] Create audit_events table with proper indexes
- [ ] Implement command/query handler interfaces
- [ ] Add audit middleware to all endpoints
- [ ] Setup basic materialized views

### Sprint 2: Read Models (2 weeks)
- [ ] Design denormalized read models
- [ ] Implement view refresh strategy
- [ ] Add Redis caching layer
- [ ] Create dashboard queries

### Sprint 3: CSV Storage (1 week)
- [ ] Setup S3/MinIO for file storage
- [ ] Implement file versioning
- [ ] Create retrieval API
- [ ] Add cleanup policies

### Sprint 4: Monitoring (1 week)
- [ ] Add metrics collection
- [ ] Create performance dashboards
- [ ] Setup alerting
- [ ] Document runbooks

## Success Metrics

- **Query Performance**: p95 < 100ms for recent data
- **Audit Completeness**: 100% of operations logged
- **Storage Efficiency**: < 20% overhead vs traditional
- **Developer Productivity**: No decrease in velocity
- **System Reliability**: 99.9% uptime maintained

## References

- [Martin Fowler - CQRS](https://martinfowler.com/bliki/CQRS.html)
- [Microsoft - CQRS Journey](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10))
- [Event Store - Event Sourcing Basics](https://www.eventstore.com/event-sourcing)
- [Greg Young - CQRS Documents](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf)

## Review

- **Proposed by**: Architecture Team
- **Reviewed by**: _To be filled_
- **Approved by**: _To be filled_
- **Review date**: _To be filled_