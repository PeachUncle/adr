# ADR-001: Adopt Modular Monolith Architecture

## Status

Accepted

## Context

We are building a new HR Recruitment System from scratch. We need to choose an architecture that:
- Enables rapid MVP development
- Maintains clean boundaries between business domains
- Can scale with the business
- Allows future migration to microservices if needed
- Minimizes operational complexity during early stages

The main architectural options considered were:
1. Traditional monolith
2. Microservices from the start
3. Modular monolith

## Decision

We will build the HR Recruitment System as a **modular monolith** with clear module boundaries that can be extracted into microservices in the future.

### Key Design Principles:

1. **Module Independence**: Each module (Jobs, Candidates, Applications) has its own:
   - Service layer (business logic)
   - Repository layer (data access)
   - Database schema
   - Public API surface

2. **Communication Patterns**:
   - Modules communicate via events (Event Bus) for asynchronous flows
   - Direct service calls only through well-defined public APIs
   - No direct database access across module boundaries

3. **Shared Infrastructure**:
   - Single database instance (but separate schemas/tables per module)
   - Shared authentication/authorization
   - Common event bus
   - Unified API gateway

## Consequences

### Positive

1. **Faster Time to Market**: Single deployment unit, simplified debugging, easier transactions
2. **Lower Operational Overhead**: One database connection pool, no service discovery, simpler monitoring
3. **Future-Proof Architecture**: Clean boundaries make extraction straightforward
4. **Team Productivity**: Developers can work on modules independently without coordination overhead
5. **Performance**: In-process calls are faster than network calls
6. **Transactional Integrity**: Can use database transactions across modules when needed

### Negative

1. **Deployment Coupling**: Cannot deploy modules independently (mitigated by CI/CD)
2. **Technology Lock-in**: All modules must use the same tech stack (Bun/Elysia)
3. **Scaling Limitations**: Must scale the entire application (acceptable for MVP)
4. **Testing Complexity**: Need to ensure module boundaries are respected

### Mitigation Strategies

1. **Enforce Boundaries**: Use linting rules to prevent cross-module imports
2. **Event-Driven Design**: Use events from day one to prepare for distributed architecture
3. **Repository Pattern**: Abstract all data access to ease future service extraction
4. **Module Testing**: Test modules in isolation with mocked dependencies

## Migration Path

When ready to extract a module to a microservice:

1. Replace in-process event bus with message broker (NATS/RabbitMQ)
2. Move module code to new repository
3. Replace repository implementation with API client
4. Deploy as separate service
5. Update routing in API gateway

The service layer remains unchanged during extraction.

## References

- [MonolithFirst by Martin Fowler](https://martinfowler.com/bliki/MonolithFirst.html)
- [Modular Monolith: A Primer by Kamil Grzybek](https://www.kamilgrzybek.com/design/modular-monolith-primer/)
- [The Majestic Monolith by DHH](https://m.signalvnoise.com/the-majestic-monolith/)