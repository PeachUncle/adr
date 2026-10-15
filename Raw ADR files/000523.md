**📍 Navigation Path:** [AGOG Home](../../README.md) → [Project Spirit](../README.md) → [ADR](./README.md) → API-First Design

# ADR 1: API-First Design Approach

## Status
Accepted - 2025-10-29

## Context
The AGOG Print Industry ERP system is designed as a comprehensive multi-tenant SaaS platform that must support:

- Multiple client applications (web, mobile, desktop)
- Extensive third-party integrations (CRM, e-commerce, shipping, payment processors)
- Industry-specific protocols (JDF/JMF for equipment integration)
- Modern supply chain APIs (EDI, supplier portals)
- Future extensibility and ecosystem growth
- 8 distinct manufacturing strategies with varying integration needs
- 10+ specialized business unit dashboards requiring consistent data access

### Strategic Imperatives
1. **No Legacy System Support**: Deliberately avoiding integration with legacy print MIS systems (EFI Pace, Printer's Plan, Avanti)
2. **Modern Integration First**: All integrations via modern REST/GraphQL APIs
3. **Ecosystem Play**: Position AGOG as the central hub for print industry operations
4. **Multi-Tenant at Scale**: Support hundreds of tenants with varying integration requirements

## Decision
We will adopt a comprehensive API-first design approach where:

1. **APIs are designed and documented before implementation**
   - OpenAPI/Swagger specifications created first
   - Contract-driven development
   - API documentation as a deliverable, not an afterthought

2. **All functionality exposed via APIs**
   - No direct database access by clients
   - UI applications are API consumers
   - Internal services communicate via APIs

3. **Modern API standards**
   - **GraphQL (Apollo Federation):** PWA frontend, complex queries, real-time dashboards
   - **RESTful APIs:** External integrations, partners, equipment, third-party developers
   - **Webhook support:** Event-driven integrations
   - **gRPC:** High-performance internal microservice communication (not externally exposed)

4. **Versioned and backward compatible**
   - Semantic versioning (v1, v2, etc.)
   - Deprecation policies with migration paths
   - Multiple API versions supported simultaneously

### Architectural Foundation: OLAP → OLTP → API → UX

AGOG's API layer is part of a larger architectural principle:

```
Business Goals (KPIs - OLAP)
  "Calculate equipment utilization"
    ↓ defines data requirements
Database Schemas (OLTP)
  "Store: status, duration_minutes, is_productive_time"
    ↓ exposed through
API Layer (This ADR)
  "GET /equipment/:id/utilization returns validated metrics"
    ↓ consumed by
Dashboards (UX)
  "<UtilizationGauge value={0.75} />"
```

**Why this matters for API design:**
- **APIs aren't just CRUD operations** - they expose validated business metrics
- **Every endpoint supports specific KPIs** - if a dashboard needs data, the API provides it
- **Type safety through the stack** - KPI validation ensures API contracts are reliable
- **Real-time business intelligence** - APIs return calculated metrics, not raw data

This means AGOG APIs are fundamentally different from generic REST APIs:
- ❌ Traditional: "Here's raw data, calculate metrics client-side"
- ✅ AGOG: "Here's validated business metrics, ready to display"

Example:
```graphql
type ProductionRun {
  # Raw fields (OLTP)
  actualStartTime: DateTime!
  actualEndTime: DateTime!
  quantityProduced: Int!
  quantityGood: Int!
  
  # Calculated KPIs (OLAP)
  oee: Float!              # Validated calculation
  firstPassYield: Float!   # Guaranteed available
  utilizationRate: Float!  # Never returns null
}
```

See [Business Value - Architectural Foundation](../BUSINESS_VALUE.md#architectural-foundation-analytics-driven-development) for full context.

## Rationale

### Print Industry Integration Complexity
The print industry requires integration with:
- Equipment (JDF/JMF protocols)
- Prepress systems (Adobe, Esko)
- Shipping carriers (FedEx, UPS)
- E-commerce platforms (Shopify, WooCommerce)
- CRM systems (Salesforce, HubSpot, Dynamics)
- Payment processors (Stripe, PayPal)
- Supply chain (EDI, paper merchants)

An API-first approach ensures consistent, reliable integration patterns.

### Multi-Tenant Requirements
Different tenants need:
- Custom integrations with their specific tools
- White-label API access
- Partner/reseller API capabilities
- Controlled data access and isolation

### Future-Proofing
API-first design enables:
- Easy addition of new client types (mobile apps, IoT devices)
- Third-party ecosystem development
- Marketplace for add-ons and integrations
- AI/ML service integration

## Implementation Strategy

### API Categories
1. **Core Business APIs**
   - Customer Management
   - Order Management
   - Production Scheduling
   - Inventory Management
   - Financial Transactions

2. **Manufacturing Strategy APIs**
   - MTS (Make-to-Stock)
   - MTO (Make-to-Order)
   - CTO (Configure-to-Order)
   - ETO (Engineer-to-Order)
   - POD (Print-on-Demand)
   - VDP (Variable Data Printing)

3. **Integration APIs**
   - Webhook subscriptions
   - Batch data import/export
   - Real-time event streaming
   - File handling (artwork, proofs)

4. **Analytics & Reporting APIs**
   - Dashboard data endpoints
   - KPI calculations
   - Custom report generation
   - Data export services

### API Design Principles

**Hybrid API Strategy:**

AGOG uses a **hybrid API approach** where different API technologies serve different use cases:

**1. GraphQL (Apollo Federation) - PWA & Dashboards**
- **Use cases:** PWA frontend, BI dashboards, internal applications
- **Benefits:** 
  - Client-defined queries (fetch exactly what's needed)
  - Single endpoint simplifies development
  - Real-time subscriptions for live updates
  - Type-safe schema with auto-documentation
  - Reduced over-fetching/under-fetching
- **Technology:** Apollo Federation for microservices composition
- **Related:** See [graphql-specification.md](../../Project%20Architecture/api/graphql-specification.md) for schema details

**2. REST APIs - External Integrations**
- **Use cases:** Shipping carriers, payment processors, e-commerce, equipment, third-party developers
- **Benefits:**
  - Industry standard (partners expect REST)
  - Simple authentication (JWT tokens)
  - Excellent caching support
  - OpenAPI/Swagger documentation familiar to integrators
  - Webhooks for event-driven patterns
- **Technology:** RESTful design with OpenAPI 3.0 specs
- **Related:** See [api-specification.md](../../Project%20Architecture/api/api-specification.md) for endpoints

**3. gRPC - Internal Microservices**
- **Use cases:** High-performance internal service-to-service communication
- **Benefits:** Efficient binary protocol, type safety, bidirectional streaming
- **Scope:** Internal only, not exposed to external clients

**When to use which:**
```
Request from PWA frontend? → GraphQL
Request from BI dashboard? → GraphQL
Request from shipping carrier API? → REST
Request from payment processor? → REST
Request from third-party developer? → REST
Internal microservice call? → gRPC
```

**REST Design Principles:**
1. **Resource-Oriented**: URLs represent resources, not actions
2. **Stateless**: Each request contains all necessary information
3. **Consistent Naming**: Follow established conventions
4. **Error Handling**: Comprehensive error codes and messages
5. **Pagination**: All list endpoints support pagination
6. **Filtering & Sorting**: Flexible query capabilities
7. **Partial Responses**: Field selection to optimize performance
8. **Rate Limiting**: Protect system resources
9. **Caching**: Appropriate cache headers
10. **Security**: OAuth 2.0, JWT tokens, tenant isolation

### Documentation Standards

**For REST APIs:**
- OpenAPI 3.0 specifications
- Interactive API documentation (Swagger UI)
- Code samples in multiple languages
- Integration guides by use case
- Sandbox environment for testing
- Webhook payload examples

**For GraphQL APIs:**
- GraphQL schema documentation (auto-generated)
- Apollo Studio for schema exploration
- Example queries and mutations
- Subscription examples for real-time updates
- Federation gateway documentation

## Consequences

### Positive
- **Clear Contracts**: Well-defined interfaces between components
- **Parallel Development**: Frontend and backend teams can work independently
- **Third-Party Integration**: Easy onboarding of partners and integrations
- **Better Testing**: API contracts enable comprehensive integration testing
- **Documentation Excellence**: API specs serve as living documentation
- **Ecosystem Growth**: Enables third-party developers and add-ons
- **Mobile-Ready**: Same APIs power web and mobile applications
- **Microservices-Friendly**: Clean boundaries for service decomposition
- **Client Flexibility**: Support any client technology stack
- **Compliance**: Easier audit trails and access control

### Negative
- **Initial Overhead**: Upfront time investment in API design
- **Versioning Complexity**: Managing multiple API versions
- **Tooling Requirements**: Need for API design, testing, and monitoring tools
- **Learning Curve**: Team needs API design expertise
- **Performance Considerations**: Additional network layer vs. direct access
- **Breaking Changes**: Careful management required for API evolution

### Mitigation Strategies
1. **Tooling Investment**: Use industry-standard tools (Swagger, Postman, API gateways)
2. **Training**: Invest in API design best practices training
3. **API Governance**: Establish review process for API changes
4. **Performance Optimization**: Caching, CDN, efficient serialization
5. **Deprecation Policy**: Clear timeline and migration paths for changes

## Monitoring & Success Metrics
- API response time (p95, p99)
- API error rates by endpoint
- API adoption rates (endpoint usage)
- Third-party integration success rate
- Developer satisfaction scores
- Time-to-integration for new partners

## References
- [REST API Standards](../../Standards/api/rest-standards.md)
- [GraphQL Standards](../../Standards/api/graphql-standards.md)
- [REST API Specification](../../Project%20Architecture/api/api-specification.md)
- [GraphQL API Specification](../../Project%20Architecture/api/graphql-specification.md)
- [Integration Architecture](../../Project%20Architecture/integrations/)
- [Original Requirements](../../SAAS%20Conversation.txt)

## Related Decisions
- [ADR 002: Multi-Tenant SaaS with Edge Architecture](./002-multi-tenant-saas-edge-architecture.md) - Defines hybrid API strategy
- ADR 003: Security & Authentication Strategy (TBD)
- ADR 004: Data Model & SCD Type 2 (TBD)

---

[⬆ Back to top](#adr-1-api-first-design-approach) | [🏠 AGOG Home](../../README.md) | [🎯 Project Spirit](../README.md) | [📋 ADR](./README.md)