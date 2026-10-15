# Architecture Decision Record: Pivot from Cloud-Native AWS to Streamlit/DuckDB

**ADR Number:** 001  
**Date:** October 2025  
**Status:** Implemented  
**Authors:** TS  

## Title
Transition from Cloud-Native AWS Architecture to Streamlit/DuckDB Analytics Platform

## Context

The HAILIE Insights Engine was initially conceived as a cloud-native AWS application to process UK government TSM (Tenant Satisfaction Measures) data for social housing providers. The original architecture (August 2025) specified:

- **Frontend:** React.js with Material-UI
- **Authentication:** AWS Cognito  
- **Backend:** Node.js/Express on AWS Elastic Beanstalk
- **Database:** PostgreSQL on AWS RDS
- **File Processing:** AWS Lambda functions triggered by S3 uploads
- **Infrastructure:** Multi-AZ deployment, CloudFront CDN, ElastiCache

This enterprise-grade architecture was designed for maximum scalability, multi-tenancy, and production resilience.

## Decision

We pivoted to a streamlined analytics-focused architecture:

- **Frontend/Backend:** Unified Streamlit application
- **Database:** DuckDB for analytics storage
- **Processing:** Python-based ETL pipeline
- **Deployment:** Single-server Streamlit deployment on Replit
- **Data Model:** Pre-calculated analytics database

## Rationale

### 1. Use Case Clarification
- The primary use case emerged as executive analytics dashboards rather than a multi-tenant SaaS platform
- Single government dataset (TSM 2024) rather than continuous multi-provider uploads
- Focus on insights delivery rather than operational data management

### 2. Development Velocity
- Streamlit enables rapid prototyping and iteration of data visualizations
- Single Python codebase reduces context switching
- Built-in components for data presentation accelerate development

### 3. Analytics Performance
- DuckDB provides columnar storage optimized for analytical queries
- Pre-calculated metrics eliminate runtime computation overhead
- In-process database removes network latency

### 4. Operational Simplicity
- No cloud infrastructure to manage or monitor
- Single deployment artifact
- Reduced security surface area
- No ongoing AWS costs

### 5. Data Characteristics
- Static annual government dataset (updated yearly)
- 355 providers with ~4,260 data points
- Read-heavy workload with minimal writes
- Analytics queries benefit from columnar storage

## Alternatives Considered

### Alternative 1: Maintain Original AWS Architecture
- **Pros:** Scalability, multi-tenancy ready, enterprise features
- **Cons:** Over-engineered for current needs, high operational overhead, slower iteration

### Alternative 2: Hybrid Approach (Streamlit + PostgreSQL)
- **Pros:** Relational data integrity, SQL standards compliance
- **Cons:** Network overhead for analytics, requires database server management

### Alternative 3: Static Site Generation
- **Pros:** Zero runtime compute, perfect caching
- **Cons:** No interactivity, difficult to update with new data

## Consequences

### Positive Consequences
✅ **Reduced Time to Market:** MVP delivered in weeks instead of months  
✅ **Lower Total Cost:** No cloud infrastructure costs  
✅ **Improved Performance:** Sub-second query response times  
✅ **Simplified Deployment:** Single command deployment  
✅ **Better Developer Experience:** Unified Python stack  
✅ **Easier Maintenance:** Fewer moving parts to monitor  

### Negative Consequences
❌ **Limited Scalability:** Single-server constraint  
❌ **No Multi-Tenancy:** Cannot isolate data per housing provider  
❌ **Authentication Gap:** No user management system  
❌ **Reduced Resilience:** No automatic failover or redundancy  
❌ **API Limitations:** No REST API for external integrations  

### Neutral Consequences
➖ **Technology Lock-in:** Tightly coupled to Streamlit framework  
➖ **Database Choice:** DuckDB less common than PostgreSQL  
➖ **Deployment Platform:** Replit-specific optimizations  

## Implementation Details

### Migration Path
1. **Data Layer:** Excel → DuckDB ETL pipeline replaced Lambda/S3/RDS flow
2. **Analytics:** Pre-calculated percentiles and correlations stored in database
3. **Frontend:** Streamlit components replaced React components
4. **Deployment:** Replit deployment replaced AWS multi-region setup

### Key Architecture Changes

| Component | Original (AWS) | Current (Streamlit/DuckDB) |
|-----------|---------------|----------------------------|
| User Interface | React.js + Material-UI | Streamlit |
| Authentication | AWS Cognito | None (single-user) |
| API Layer | Node.js/Express REST API | Direct Python function calls |
| Database | PostgreSQL (RDS) | DuckDB (embedded) |
| File Processing | Lambda + S3 + SQS | Python ETL script |
| Caching | Redis (ElastiCache) | DuckDB pre-calculations |
| CDN | CloudFront | None needed |
| Monitoring | CloudWatch | Application logs |

## Validation

The pivot was validated through:
- Successfully processing 355 providers with 4,260 TSM scores
- Achieving instant (<100ms) metric retrieval
- Delivering three core insights: Rank, Momentum, Priority
- Simplified deployment and maintenance

## Lessons Learned

1. **Start Simple:** Beginning with complex architecture can slow initial delivery
2. **Analytics First:** For analytics applications, specialized databases outperform general-purpose ones
3. **Unified Stack:** Single-language applications reduce complexity
4. **Pre-calculation:** Trading storage for compute improves user experience
5. **Right-Sizing:** Architecture should match current needs, not hypothetical scale

## References

- Original Architecture Document: HAILIE Insights Engine - Architecture (August 2025)
- Current Implementation: Version 2.0 (October 2025)
- TSM Data Source: UK Government TSM 2024 Dataset