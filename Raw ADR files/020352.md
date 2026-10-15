# 5. Database per Service Pattern

**Date:** 2024-01-15

## Status

Accepted

## Context

In a microservices architecture, a key decision is how to manage data:

1. **Shared Database**: All services access a single database
2. **Database per Service**: Each service has its own database

A shared database would:
- Create tight coupling through the schema
- Make it impossible to scale databases independently
- Prevent services from choosing optimal storage types
- Create deployment dependencies

## Decision

Each service owns and manages its own dedicated PostgreSQL database:

| Service | Database |
|---------|----------|
| User Service | `winvestco_user_db` |
| Market Service | `winvestco_market_db` |
| Portfolio Service | `winvestco_portfolio_db` |
| Funds Service | `winvestco_funds_db` |
| Ledger Service | `winvestco_ledger_db` |
| Order Service | `winvestco_order_db` |
| Trade Service | `winvestco_trade_db` |
| Payment Service | `winvestco_payment_db` |
| Notification Service | `winvestco_notification_db` |
| Report Service | `winvestco_report_db` |

Each database:
- Is only accessed by its owning service
- Has its own Flyway migrations
- Can have an optimized schema for its use case
- Can be scaled or tuned independently

Cross-service data access is achieved through:
- **REST APIs** (synchronous): Feign clients for real-time queries
- **Domain Events** (asynchronous): Services build local projections from events

## Consequences

### Positive
- True service independence and encapsulation
- Independent schema evolution per service
- Independent scaling and performance tuning
- Services can optimize storage for their access patterns
- Clear data ownership boundaries

### Negative
- No cross-service joins (must use APIs or events)
- Distributed transactions are complex (saga pattern needed)
- Data consistency is eventual, not immediate
- Increases total infrastructure resources

### Mitigations
- Flyway for consistent, version-controlled migrations
- Feign clients for synchronous cross-service queries
- Event-driven projections for read-heavy patterns (Report Service)
- Saga pattern for distributed business transactions
