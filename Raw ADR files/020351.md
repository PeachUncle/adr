# 4. Event-Driven Architecture

**Date:** 2024-01-15

## Status

Accepted

## Context

With a microservices architecture, services need to communicate about business state changes. Two primary patterns exist:

1. **Synchronous (Request-Response)**: Direct HTTP/gRPC calls between services
2. **Asynchronous (Event-Driven)**: Publishing events that other services consume

A trading platform has many cross-cutting concerns:
- When an order is filled, multiple services need to react (portfolio, ledger, funds, notifications)
- Tight coupling via synchronous calls would create fragile dependencies
- Services should be able to evolve independently

## Decision

We adopt an **event-driven architecture** using domain events for all significant business state changes. The platform defines **26 domain events** across 6 categories:

### User Events (6)
- `UserCreatedEvent`, `UserUpdatedEvent`, `UserLoginEvent`
- `UserStatusChangedEvent`, `UserRoleChangedEvent`, `UserPasswordChangedEvent`

### Order Events (6)
- `OrderCreatedEvent`, `OrderValidatedEvent`, `OrderFilledEvent`
- `OrderCancelledEvent`, `OrderExpiredEvent`, `OrderRejectedEvent`

### Funds Events (4)
- `FundsDepositedEvent`, `FundsWithdrawnEvent`
- `FundsLockedEvent`, `FundsReleasedEvent`

### Trade Events (6)
- `TradeCreatedEvent`, `TradePlacedEvent`, `TradeExecutedEvent`
- `TradeClosedEvent`, `TradeCancelledEvent`, `TradeFailedEvent`

### Payment Events (4)
- `PaymentCreatedEvent`, `PaymentSuccessEvent`
- `PaymentFailedEvent`, `PaymentExpiredEvent`

### Report Events (2)
- `ReportRequestedEvent`, `ReportCompletedEvent`

All events:
- Are defined in the `common` module for consistency
- Contain the minimal data needed (event sourcing ready)
- Are published to RabbitMQ with topic-based routing
- Include timestamp and correlation IDs for tracing

## Consequences

### Positive
- Loose coupling between services
- Services can react to events without the publisher knowing
- Natural audit trail of business activities
- Enables event sourcing patterns (Report Service uses this)
- Easier to add new consumers without modifying publishers

### Negative
- Eventual consistency (not immediate)
- Debugging distributed flows is more complex
- Event schema evolution requires coordination
- Need to handle duplicate events (idempotency)

### Mitigations
- Correlation IDs for distributed tracing
- Idempotent event handlers where critical
- Event versioning strategy for schema changes
- Dead-letter queues for failed processing
