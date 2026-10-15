# ADR 001: Why Seam-Driven Development

**Date**: 2025-11-21
**Status**: Accepted
**Deciders**: Development Team

## Context

We needed an architecture that allows:
1. Rapid iteration without breaking existing code
2. Easy swapping of infrastructure (dev/prod)
3. Testing without external dependencies
4. Multiple developers working in parallel

## Decision

Implement **Seam-Driven Development** with ports/adapters pattern (Hexagonal Architecture).

## Rationale

### Benefits
1. **Clean Boundaries**: Core business logic never knows about IndexedDB, WebSocket, etc.
2. **Testability**: Mock adapters for fast unit tests
3. **Flexibility**: Swap IndexedDB → Postgres without touching business logic
4. **Parallel Work**: Team can build adapters independently
5. **Contract-First**: Zod schemas catch errors at runtime boundaries

### Trade-offs
- More boilerplate (interfaces + implementations)
- Requires discipline (don't bypass seams)
- Learning curve for new developers

## Seams Defined

1. **Storage** (TaskStorePort) - Persistence
2. **Sync** (SyncBusPort) - Real-time communication
3. **Auth** (AuthProviderPort) - Identity
4. **Errors** (ErrorReporterPort) - Observability

## Consequences

**Positive**:
- ✅ Dev team built 4 adapters in parallel (4 hours vs 16 hours sequential)
- ✅ Can run E2E tests with IndexedDB OR Postgres (CI matrix)
- ✅ Zero coupling between business logic and infrastructure
- ✅ Easy to add new storage backend (e.g., Firebase) without touching TaskService

**Negative**:
- ⚠️  More files to maintain (2x: interface + impl)
- ⚠️  DI configuration can be confusing for newcomers

## Alternatives Considered

**1. Direct Dependencies** (services import concrete classes)
- Rejected: Tight coupling, hard to test, impossible to swap

**2. Repository Pattern** (single abstraction for all storage)
- Rejected: Too generic, doesn't handle WebSocket/Auth well

**3. Full DDD with Aggregates**
- Rejected: Overkill for 2-6 user app, too much ceremony

## References

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/)
