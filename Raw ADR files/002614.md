# ADR 001: Adopt Clean/Hexagonal Architecture

## Status
Accepted

## Context
The current codebase mixes business logic with data access and infrastructure concerns. Server actions directly access the database, making it difficult to:
- Test business logic in isolation
- Change persistence mechanisms
- Understand and maintain domain rules
- Ensure security and validation are applied consistently

The codebase has grown to ~12k LOC with 116 TypeScript files but lacks clear architectural boundaries.

## Decision
We will refactor the codebase to follow Clean/Hexagonal Architecture principles:

### Layer Structure
1. **Domain Layer** (`src/domain/`)
   - Pure business logic, no framework dependencies
   - Entities: Core business objects (Restaurant, User, TokenLending, Ticket)
   - Value Objects: Immutable values (Price, Email, TokenCount)
   - Domain Services: Business rules that don't belong to a single entity

2. **Application Layer** (`src/application/`)
   - Use cases: Orchestration of business operations
   - Ports: Interfaces for external dependencies (repositories, services)
   - DTOs: Input/output data transfer objects
   - Transactional boundaries

3. **Infrastructure Layer** (`src/infrastructure/`)
   - Adapters: Implementations of ports (database, auth, logging)
   - Framework-specific code
   - External service integrations

4. **Presentation Layer** (`src/app/`, `src/actions/`)
   - Next.js routes and components
   - Server actions as thin wrappers around use cases
   - Input validation and response formatting

### Dependency Rule
Dependencies point inward: Presentation → Application → Domain
Infrastructure adapters are injected at runtime.

### Migration Strategy
1. Create new layer structure alongside existing code
2. Extract domain entities and value objects
3. Define port interfaces
4. Implement adapters
5. Refactor use cases to use ports
6. Update server actions to call use cases
7. Remove old direct database access

## Consequences

### Positive
- Clear separation of concerns
- Business logic can be tested without database
- Easy to swap implementations (e.g., different database, caching)
- Better code organization and discoverability
- Explicit dependencies make system easier to understand
- Security and validation can be enforced at layer boundaries

### Negative
- More files and abstractions (acceptable tradeoff for maintainability)
- Initial refactoring effort required
- Team needs to understand and follow architectural patterns

### Risks
- Must maintain backward compatibility during migration
- All existing tests and behaviors must continue to work
- Care needed to avoid over-engineering simple operations

## Alternatives Considered
1. **Keep current structure** - Rejected: Technical debt continues to accumulate
2. **Simple layering without ports** - Rejected: Still couples to specific implementations
3. **Microservices** - Rejected: Overkill for current scale, adds operational complexity
