# ADR-001: Clean Architecture with CQRS Pattern

## Status

**Accepted**

## Context

OrbitOS needs a scalable, maintainable architecture that:
- Supports multiple frontends (web, mobile)
- Enables AI-assisted development with clear boundaries
- Allows for easy testing at all levels
- Maintains separation of concerns
- Supports future microservices extraction if needed

## Decision

Adopt **Clean Architecture** with **CQRS (Command Query Responsibility Segregation)** pattern:

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│  (API Controllers, Web, Mobile)         │
├─────────────────────────────────────────┤
│           Application Layer             │
│  (Commands, Queries, Handlers, DTOs)    │
├─────────────────────────────────────────┤
│             Domain Layer                │
│  (Entities, Value Objects, Interfaces)  │
├─────────────────────────────────────────┤
│          Infrastructure Layer           │
│  (EF Core, External Services, Auth)     │
└─────────────────────────────────────────┘
```

### Layer Dependencies

- **Domain**: No dependencies on other layers
- **Application**: Depends only on Domain
- **Infrastructure**: Depends on Domain (implements interfaces)
- **Presentation**: Depends on Application and Infrastructure

### CQRS Pattern

- **Commands**: Write operations (Create, Update, Delete)
- **Queries**: Read operations (optimized for display)
- **Handlers**: Process commands/queries
- **No shared data models** between commands and queries

## Consequences

### Positive
- Clear separation enables parallel development
- AI can generate code following predictable patterns
- Easy to test each layer independently
- Infrastructure can be swapped without touching business logic
- Future-proof for microservices if needed

### Negative
- More boilerplate code initially
- Steeper learning curve for new developers
- Over-engineering risk for simple CRUD operations

### Neutral
- Requires consistent enforcement via architecture tests
- Documentation must be maintained

## Alternatives Considered

### Option 1: Traditional N-Tier
- Simpler initial setup
- Less boilerplate
- **Rejected**: Tighter coupling, harder to test, harder for AI to follow patterns

### Option 2: Vertical Slices
- Feature-based organization
- Less abstraction layers
- **Rejected**: Harder to enforce consistency across features

### Option 3: Modular Monolith
- Module boundaries
- Internal communication protocols
- **Considered for future**: May evolve to this as product grows

## Implementation

1. Project structure created in `orbitos-api/src/`:
   - `OrbitOS.Domain/` - Entities, interfaces
   - `OrbitOS.Application/` - Commands, queries, handlers
   - `OrbitOS.Infrastructure/` - EF Core, external services
   - `OrbitOS.Api/` - Controllers, middleware

2. Architecture tests enforce layer dependencies:
   - Domain must not reference other projects
   - Application must not reference Infrastructure
   - Controllers must not directly use DbContext

3. Code generation follows these patterns:
   - New entity → Domain + Application handler + Infrastructure repo
   - New feature → Command/Query in Application

## Related

- Related Features: All features follow this pattern
- Related Entities: All entities live in Domain layer

---

**Date**: 2026-01-13
**Author**: Core Team
**Reviewers**: Technical Architecture Review
