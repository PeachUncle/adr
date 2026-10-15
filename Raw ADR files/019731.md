# ADR-001: Service-Oriented Architecture

## Status
Accepted

## Context

Building a multi-vendor marketplace platform managing 750,000+ digital assets with the following requirements:

**Functional Requirements:**
- Support multiple product types (icons, illustrations, sets, families)
- Handle complex business workflows (cart, order, payment, fulfillment)
- Manage user accounts, roles, and permissions
- Process transactions and maintain account balances
- Support contributor uploads and product management

**Non-Functional Requirements:**
- Modular codebase for maintainability
- Clear boundaries for testing
- Patterns that facilitate AI-assisted development
- Ability to deploy modules independently
- Consistent patterns across all modules

**Development Constraints:**
- Solo development with AI pair programming
- Need for clear, explicit patterns to enable effective AI collaboration
- Long-term maintainability without a large team

## Decision

Implement Service-Oriented Architecture (SOA) with Entity-Repository-Service pattern.

Each module encapsulates three layers:

1. **Entity Layer**: Immutable data containers with validation
   - Wraps database records as frozen objects
   - Filters hidden fields (passwords, sensitive data)
   - Materializes relations when requested
   - Location: `src/<module>/<Module>Entity.js`

2. **Repository Layer**: Data access operations
   - CRUD operations with transaction support
   - Query building with Objection.js
   - Entity wrapping of results
   - Pagination (offset and cursor-based)
   - Location: `src/<module>/<Module>Repository.js`

3. **Service Layer**: Business logic orchestration
   - Calls across repositories
   - Event emission for observability
   - Input normalization (Entity → POJO)
   - Transaction coordination
   - Location: `src/<module>/<Module>Service.js`

**Module Structure:**
```
src/<module>/
├── <Module>Entity.js        # Data model
├── <Module>Repository.js    # Data access
├── <Module>Service.js       # Business logic
├── index.js                 # Public interface
└── __tests__/              # Tests for this module
```

## Consequences

### Positive

**Modularity:**
- 78 modules with clear boundaries
- Easy to locate code (product logic in `src/products/`, user logic in `src/users/`)
- New modules follow established pattern

**Testing:**
- Independent testing per layer
- Entity tests validate data transformation
- Repository tests validate queries (integration tests with real DB)
- Service tests validate business logic
- Test contracts ensure consistency

**AI-Assisted Development:**
- Clear patterns enable focused AI context
- Explicit layer boundaries guide AI code generation
- Consistent structure across all modules reduces AI confusion
- AI can generate new modules following existing patterns

**Maintainability:**
- Changes localized to specific layers
- Refactoring one layer doesn't affect others
- Easy to understand data flow: Entity ← Repository ← Service

**Consistency:**
- Same pattern repeated 78 times
- Predictable file locations
- Uniform method signatures

### Negative

**Boilerplate:**
- More code than monolithic approach
- Each module requires minimum 3 files (Entity, Repository, Service)
- Some operations require touching multiple layers

**Learning Curve:**
- Developers must understand layer responsibilities
- Discipline required to maintain boundaries
- Cannot bypass layers without breaking pattern

**Overhead:**
- Additional abstraction layers add minor performance cost
- Entity wrapping allocates additional objects
- Not suitable for extremely high-frequency operations (though acceptable for web API workloads)

## Alternatives Considered

### Monolithic Architecture
**Approach:** Single large codebase with functional modules but no strict layer separation.

**Rejected Because:**
- Module boundaries unclear, leading to tangled dependencies
- Testing complexity increases with codebase size
- Difficult to provide focused context for AI assistance
- Harder to reason about data flow

### Microservices Architecture
**Approach:** Separate deployable services per domain (Users, Products, Orders, etc.).

**Rejected Because:**
- Operational overhead not justified for current scale
- Distributed transactions add complexity
- Network latency between services
- Requires service discovery, API gateway, distributed tracing
- Solo development makes orchestration challenging

### Active Record Pattern
**Approach:** Domain objects contain both data and persistence logic (e.g., `user.save()`).

**Rejected Because:**
- Couples business logic to database operations
- Harder to test in isolation
- Entity objects become mutable, violating immutability principle
- Difficult to mock for unit testing

## Implementation Notes

**Base Classes:**
- `src/common/BaseEntity.js` - Foundation for all entities
- `src/common/BaseRepository.js` - Foundation for all repositories
- `src/common/BaseService.js` - Foundation for all services

**Factory Pattern:**
- Entities created via `createEntityFromModel()` factory
- Derives JSON schema from Objection.js model
- Filters fields based on `allowedColumns` and `hiddenFields`

**Initialization:**
```javascript
// src/accounts/index.js
const initAccountService = () => {
  const repository = new AccountRepository({ DB });
  return new AccountService({ repository, entityClass: AccountEntity });
};
```

**Dependency Injection:**
- Services receive repository instances (not create them)
- Enables testing with mock repositories
- Allows swapping implementations

## Related Decisions

- [ADR-002: Mixin Pattern](./ADR-002-mixin-pattern.md) - Extends services with capabilities
- [ADR-003: Event-Driven Architecture](./ADR-003-event-driven-architecture.md) - Observability layer
- [ADR-004: Contract-Based Testing](./ADR-004-contract-based-testing.md) - Validates SOA contracts
- [ADR-005: Entity Immutability](./ADR-005-entity-immutability.md) - Entity layer design

## References

- Entity-Repository-Service pattern documentation: `ARCHITECTURE.md`
- Module structure: `src/accounts/` (reference implementation)
- Test contracts: `src/__tests__/contracts/`

---

**Date:** 2025-10-17
**Author:** Scott Lewis
