# 2. Microservices Architecture

**Date:** 2024-01-15

## Status

Accepted

## Context

WINVESTCO is a stock trading platform requiring:
- High availability for market data and order processing
- Independent scaling of different components (e.g., market data vs. user management)
- Isolation of failures to prevent system-wide outages
- Parallel development by multiple teams
- Different data storage requirements per domain

A monolithic architecture would couple all these concerns together, making it difficult to scale specific components or deploy changes independently.

## Decision

We will adopt a microservices architecture with the following 12 services:

| Service | Responsibility |
|---------|----------------|
| **Eureka Server** | Service discovery and registry |
| **API Gateway** | Single entry point, routing, authentication |
| **User Service** | Authentication, registration, user management |
| **Market Service** | Real-time market data, NSE API integration |
| **Portfolio Service** | Holdings management, P&L tracking |
| **Funds Service** | Wallet, deposits, withdrawals, fund locking |
| **Ledger Service** | Immutable financial ledger (source of truth) |
| **Order Service** | Order lifecycle management |
| **Trade Service** | Trade execution and state machine |
| **Payment Service** | Payment gateway integration (Razorpay) |
| **Notification Service** | Push notifications, WebSocket |
| **Report Service** | Async report generation (P&L, Tax, Transactions) |

Each service:
- Has its own codebase within the Maven multi-module project
- Owns its data and database
- Communicates via REST (synchronous) or messaging (asynchronous)
- Can be deployed and scaled independently

## Consequences

### Positive
- Independent deployability and scalability per service
- Technology flexibility (though we standardize on Spring Boot)
- Fault isolation - one service failure doesn't cascade
- Teams can work on different services in parallel
- Smaller, more maintainable codebases per service

### Negative
- Increased operational complexity (12 services to manage)
- Network latency for inter-service communication
- Distributed system challenges (eventual consistency, distributed transactions)
- Need for robust monitoring and observability
- More complex local development setup

### Mitigations
- Docker Compose for local development
- Service discovery (Eureka) for dynamic routing
- Event-driven architecture for loose coupling
- PLG stack (Prometheus, Loki, Grafana) for observability
