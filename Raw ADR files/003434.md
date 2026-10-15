# ADR-0006: Domain-Driven Design Boundaries

## Status
Accepted

## Context
As the application grows, we need clear boundaries between different business domains (health consultations, nutrition/feed optimization, user management, authentication) to maintain code organization, testability, and scalability.

## Decision
We will organize the codebase using Domain-Driven Design (DDD) principles with clear domain boundaries:

### Domain Modules

1. **Health Domain** (`apps/web/src/domains/health/`)
   - Health consultation logic
   - Chat history management
   - Message feedback
   - RAG query handling

2. **Nutrition Domain** (`apps/web/src/domains/nutrition/`)
   - Feed optimization logic
   - Ingredient management
   - Ration calculations

3. **Auth Domain** (`apps/web/src/domains/auth/`)
   - Authentication logic
   - User session management
   - Authorization checks

4. **User Domain** (`apps/web/src/domains/user/`)
   - User profile management
   - User preferences
   - User settings

### Domain Structure

Each domain follows this structure:
```
domains/{domain}/
├── entities/          # Domain entities/models
├── repositories/      # Repository interfaces
├── services/          # Business logic services
├── types.ts           # Domain-specific types
└── index.ts           # Public API exports
```

### Rationale

1. **Clear Boundaries**: Each domain is self-contained with minimal dependencies on other domains
2. **Testability**: Domain logic can be tested in isolation
3. **Maintainability**: Changes to one domain don't affect others
4. **Scalability**: Easy to extract domains into separate services if needed
5. **Team Collaboration**: Different developers can work on different domains

## Consequences

### Positive
- Clear separation of concerns
- Easier to test domain logic in isolation
- Better code organization
- Reduced coupling between features
- Easier to understand codebase structure

### Negative
- More files and directories
- Need to be disciplined about domain boundaries
- Some code duplication may occur (acceptable trade-off)

## Alternatives Considered

1. **Feature-based organization**: Rejected - doesn't provide clear domain boundaries
2. **Layered architecture only**: Rejected - doesn't separate business domains
3. **Microservices**: Rejected - too complex for current scale

