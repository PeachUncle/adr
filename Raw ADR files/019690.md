# ADR-003: BI and Telemetry Architecture for Network Effects

## Date
2025-01-24

## Status
Proposed

## Context

ValidaHub needs to establish a Business Intelligence (BI) and telemetry infrastructure from the MVP stage to enable network effects through market intelligence. As more e-commerce sellers use the platform, we can aggregate anonymized data to provide valuable benchmarks and insights, creating a competitive moat.

### Business Requirements
- **Real-time operational metrics**: Monitor platform health, performance, and usage patterns
- **Customer-facing dashboards**: Show validation trends, error patterns, and marketplace benchmarks
- **Market intelligence**: Aggregate cross-customer insights (anonymized) for competitive advantage
- **Compliance**: LGPD compliance for Brazilian market, data residency requirements
- **Growth enabler**: Data should become more valuable as more customers join (network effect)

### Technical Requirements
- Capture high-volume events (10K+ validations/day projected for year 1)
- Sub-second query performance for operational dashboards
- Historical data retention (minimum 2 years)
- Multi-tenant data isolation
- Export capabilities for enterprise customers
- Integration with existing FastAPI/Celery/PostgreSQL stack

### Current State
- Basic telemetry service emitting structured events
- Events currently logged to files/stdout
- No persistent analytics storage
- No visualization layer
- No data aggregation pipeline

## Decision Drivers

1. **Time-to-Market**: Need working BI in 4 weeks for investor demos
2. **Cost Sensitivity**: Bootstrap budget (~$500/month max for infrastructure)
3. **Brazilian Market**: Data residency, LGPD compliance, local payment methods
4. **Scalability Path**: Must handle 100x growth without major refactoring
5. **Developer Experience**: Small team (2-3 devs), minimize operational overhead
6. **Data as Product**: BI insights will be a paid feature, needs to be reliable

## Considered Options

### Option 1: PostgreSQL + TimescaleDB + Metabase
**Stack**: 
- PostgreSQL with TimescaleDB extension for time-series data
- Metabase for visualization (open source BI)
- Custom Python ETL scripts
- Redis for real-time metrics

**Pros**:
- ✅ Lowest cost ($50-100/month on managed PostgreSQL)
- ✅ Single database technology (already using PostgreSQL)
- ✅ Metabase is free and user-friendly
- ✅ TimescaleDB handles time-series efficiently
- ✅ Can self-host in Brazil (data residency)

**Cons**:
- ❌ Limited to PostgreSQL scalability limits
- ❌ Manual ETL pipeline maintenance
- ❌ Metabase limitations for complex analytics
- ❌ No built-in data warehouse features (slowly changing dimensions, etc.)

### Option 2: ClickHouse + Superset
**Stack**:
- ClickHouse for OLAP (columnar storage)
- Apache Superset for visualization
- Apache Airflow for orchestration
- Kafka/Redpanda for event streaming

**Pros**:
- ✅ Exceptional query performance for analytics
- ✅ Purpose-built for OLAP workloads
- ✅ Open source, no licensing costs
- ✅ Handles billions of events efficiently
- ✅ Superset has more advanced features than Metabase

**Cons**:
- ❌ Higher operational complexity
- ❌ Requires specialized ClickHouse knowledge
- ❌ More infrastructure to manage
- ❌ Longer implementation time (6-8 weeks)

### Option 3: Google BigQuery + Looker Studio
**Stack**:
- BigQuery for data warehouse
- Looker Studio for visualization (free tier)
- Cloud Functions for ETL
- Pub/Sub for event ingestion

**Pros**:
- ✅ Serverless, zero operations
- ✅ Automatic scaling
- ✅ Pay-per-query pricing model
- ✅ Built-in ML capabilities (future use)
- ✅ Looker Studio free for basic use

**Cons**:
- ❌ Data leaves Brazil (compliance concerns)
- ❌ Vendor lock-in to GCP
- ❌ Costs unpredictable at scale
- ❌ Cold start latency for queries
- ❌ Learning curve for GCP ecosystem

### Option 4: Snowflake + Tableau/PowerBI
**Stack**:
- Snowflake data warehouse
- Tableau or PowerBI for visualization
- Fivetran/Airbyte for ETL
- S3 for data lake

**Pros**:
- ✅ Best-in-class data warehouse
- ✅ Excellent performance and features
- ✅ Strong ecosystem of tools
- ✅ Multi-cloud (can use AWS São Paulo region)

**Cons**:
- ❌ Expensive ($2000+/month minimum)
- ❌ Overkill for MVP stage
- ❌ Complex pricing model
- ❌ Requires dedicated data engineer

### Option 5: Hybrid Progressive Architecture (Recommended)
**Phase 1 (MVP - Months 0-6)**:
- PostgreSQL + TimescaleDB for event storage
- Materialized views for aggregations
- Metabase for dashboards
- Simple Python ETL using existing Celery

**Phase 2 (Growth - Months 6-12)**:
- Add ClickHouse for historical data
- Keep PostgreSQL for hot data (last 30 days)
- Upgrade to Superset or Preset Cloud
- Add dbt for transformations

**Phase 3 (Scale - Year 2+)**:
- Evaluate cloud migration (BigQuery/Snowflake)
- Consider dedicated data pipeline (Airflow/Dagster)
- Add ML platform for predictive analytics

## Decision

**We will adopt Option 5: Hybrid Progressive Architecture**, starting with PostgreSQL + TimescaleDB + Metabase and evolving based on actual usage patterns.

### Rationale

1. **Fastest Time-to-Value**: Can deliver working BI in 2 weeks using familiar tools
2. **Cost-Effective**: ~$100/month for MVP, scales gradually with revenue
3. **Low Risk**: Uses proven technologies we already understand
4. **Brazilian Compliance**: Can be fully hosted in Brazil (AWS São Paulo)
5. **Progressive Enhancement**: Each phase builds on previous, no throwaway work
6. **Data Portability**: Standard SQL and Parquet formats prevent lock-in

### Implementation Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐       │
│  │   FastAPI   │  │   Celery    │  │   Frontend   │       │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘       │
└─────────┼─────────────────┼────────────────┼────────────────┘
          │                 │                │
          ▼                 ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Telemetry Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Event Emitter (TelemetryService)           │  │
│  └────────────────────┬─────────────────────────────────┘  │
└───────────────────────┼──────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │   PostgreSQL     │  │   TimescaleDB    │               │
│  │   (Operational)  │  │   (Time-series)  │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                 Transformation Layer                         │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Materialized    │  │     Python       │               │
│  │     Views        │  │   ETL Scripts    │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Visualization Layer                         │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │    Metabase      │  │   API Endpoints  │               │
│  │   (Dashboards)   │  │   (JSON/CSV)     │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Consequences

### Positive Consequences
- ✅ **Quick MVP delivery**: BI available in 2 weeks
- ✅ **Low initial investment**: ~$100/month operating costs
- ✅ **Team familiarity**: Uses PostgreSQL, Python, Docker
- ✅ **Incremental complexity**: Grows with the business
- ✅ **Data sovereignty**: Can guarantee Brazilian data residency
- ✅ **Vendor flexibility**: Not locked into any cloud provider

### Negative Consequences
- ⚠️ **Technical debt**: Will need migration to ClickHouse around 10M events/month
- ⚠️ **Limited analytics**: Initial version won't support complex OLAP queries
- ⚠️ **Manual processes**: ETL will be Python scripts, not automated pipelines
- ⚠️ **Performance limits**: Metabase may struggle with 100+ concurrent users
- ⚠️ **Feature gaps**: No real-time streaming analytics initially

### Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| PostgreSQL performance degradation | High | Medium | Plan ClickHouse migration at 10M events |
| Metabase limitations | Medium | Low | Prepare Superset migration path |
| ETL script failures | Medium | Medium | Implement monitoring and alerting |
| LGPD compliance issues | Low | High | Audit data handling quarterly |
| Rapid growth overwhelming system | Low | High | Load test monthly, have migration plan |

## Implementation Plan

### Phase 1: MVP (Weeks 1-4)
**Week 1-2: Infrastructure**
- [ ] Deploy TimescaleDB extension on existing PostgreSQL
- [ ] Create hypertables for events, metrics, aggregations
- [ ] Implement event batching in TelemetryService
- [ ] Create data retention policies (raw: 90 days, aggregated: 2 years)

**Week 2-3: ETL & Aggregations**
- [ ] Create materialized views for common queries
- [ ] Implement hourly/daily aggregation jobs in Celery
- [ ] Build data quality checks
- [ ] Create backup and recovery procedures

**Week 3-4: Visualization**
- [ ] Deploy Metabase using Docker
- [ ] Create operational dashboards (latency, errors, throughput)
- [ ] Build customer dashboards (validations, corrections, trends)
- [ ] Implement row-level security for multi-tenancy
- [ ] Create benchmark reports (anonymized cross-customer)

### Phase 2: Enhancement (Months 2-6)
- [ ] Add ClickHouse for cold storage
- [ ] Implement CDC (Change Data Capture) from PostgreSQL
- [ ] Upgrade to Superset if needed
- [ ] Add dbt for transformation layer
- [ ] Implement data catalog

### Phase 3: Scale (Months 6-12)
- [ ] Evaluate cloud data warehouse migration
- [ ] Implement streaming analytics if needed
- [ ] Add ML pipeline for predictions
- [ ] Consider dedicated data team hire

## Monitoring and Success Metrics

### Technical Metrics
- Query performance: p95 < 1 second for dashboards
- Data freshness: < 5 minute lag for operational metrics
- System availability: 99.9% uptime for BI layer
- Storage efficiency: < $0.10 per million events

### Business Metrics
- User engagement: 80% of customers accessing dashboards weekly
- Feature adoption: 50% of Pro customers using benchmarks
- Revenue impact: 20% price premium for BI features
- Network effect: 10% month-over-month growth in shared insights

## Rollback Plan

If the chosen architecture fails to meet requirements:

1. **Data Portability**: All event data stored in standard formats (JSON, Parquet)
2. **Migration Path**: Can export all data to any SQL database or data lake
3. **Gradual Migration**: Can run old and new systems in parallel
4. **Feature Flags**: BI features can be toggled off per customer
5. **Fallback**: Worst case, provide CSV exports until new solution ready

## Review Schedule

- **Month 1**: Validate query performance and data quality
- **Month 3**: Review storage costs and scaling projections  
- **Month 6**: Evaluate need for Phase 2 technologies
- **Month 12**: Full architecture review and Phase 3 planning

## References

- [TimescaleDB vs ClickHouse Benchmark](https://www.timescale.com/blog/timescaledb-vs-clickhouse/)
- [Metabase vs Superset Comparison](https://www.holistics.io/blog/metabase-vs-apache-superset/)
- [LGPD Technical Requirements](https://www.gov.br/anpd/pt-br)
- [Building Network Effects with Data](https://a16z.com/2018/12/13/network-effects-data/)
- [ValidaHub Telemetry Service Implementation](../architecture/ARCHITECTURE.md)

## Decision Participants

- **Author**: Senior Software Architect
- **Reviewers**: CTO, Lead Developer, Product Manager
- **Approval**: Pending

## Notes

This ADR focuses on pragmatic choices for a bootstrap startup in the Brazilian market. The progressive architecture allows us to start simple and evolve based on actual usage patterns rather than premature optimization. The key insight is that our BI layer is not just for internal metrics but a core product feature that enables network effects through market intelligence.