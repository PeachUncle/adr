# ADR-001: Adopt Clean Architecture

**Status:** Accepted
**Date:** 2025-11-24
**Decision Makers:** Development Team
**Technical Story:** Epic 1 - Foundation & Architecture

## Context

We needed to choose an architectural pattern for the Wardrobe Consultant app that would:
- Support long-term maintainability
- Enable comprehensive testing
- Allow for technology changes (e.g., changing persistence layer)
- Separate business logic from UI and infrastructure
- Support multiple platforms (visionOS, iOS)

## Decision

We will adopt Clean Architecture with three distinct layers:

1. **Domain Layer** (Innermost)
   - Contains business logic and entities
   - No dependencies on external frameworks
   - Pure Swift code
   - Defines repository protocols

2. **Infrastructure Layer** (Middle)
   - Implements repository protocols
   - Handles external dependencies (Core Data, APIs)
   - Manages persistence and external services

3. **Presentation Layer** (Outermost)
   - Contains UI (SwiftUI views)
   - View models orchestrate domain logic
   - Depends on domain layer only
   - MVVM pattern within this layer

**Dependency Rule:** Dependencies point inward only. Domain layer has zero dependencies.

## Consequences

### Positive
- **Testability**: Business logic can be tested without UI or database
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Can swap infrastructure implementations easily
- **Team Scalability**: Different teams can work on different layers
- **Platform Independence**: Domain logic portable across platforms
- **Future-Proof**: Easy to add new features without affecting existing code

### Negative
- **Initial Complexity**: More files and abstractions than simpler patterns
- **Learning Curve**: Team needs to understand layered architecture
- **Boilerplate**: Some code duplication in mapping between layers
- **Over-Engineering Risk**: May be overkill for very simple features

### Risks
- **Performance**: Multiple layers could introduce overhead (mitigated by Swift's optimization)
- **Inconsistent Application**: Team must maintain discipline in following the pattern

## Alternatives Considered

### MVC (Model-View-Controller)
- **Pros**: Simple, familiar, less boilerplate
- **Cons**: Massive view controllers, poor testability, tight coupling
- **Rejected**: Not suitable for complex app with multiple data sources

### VIPER (View-Interactor-Presenter-Entity-Router)
- **Pros**: Very granular separation, highly testable
- **Cons**: Extreme boilerplate, too many files, overkill for our needs
- **Rejected**: Too complex for team size and app scope

### Simple MVVM
- **Pros**: Less complex than Clean Architecture, good for SwiftUI
- **Cons**: Lacks clear infrastructure separation, harder to swap persistence
- **Rejected**: Insufficient separation for our multi-platform goals

### MVI (Model-View-Intent)
- **Pros**: Unidirectional data flow, predictable state
- **Cons**: Less familiar to team, more complex state management
- **Rejected**: Team more comfortable with MVVM within presentation layer

## Implementation Details

### Directory Structure
```
WardrobeConsultant/
├── Domain/
│   ├── Entities/           # Business models
│   ├── Protocols/          # Repository interfaces
│   └── Services/           # Business logic
├── Infrastructure/
│   ├── Persistence/        # Core Data implementation
│   └── Services/           # External services
└── Presentation/
    ├── Screens/            # SwiftUI views
    ├── ViewModels/         # MVVM view models
    └── Utilities/          # UI helpers
```

### Example Flow
1. View calls ViewModel method
2. ViewModel uses Domain Service
3. Domain Service uses Repository Protocol
4. Infrastructure implements Repository
5. Data flows back through layers

### Testing Strategy
- **Domain**: Pure unit tests, no mocks needed
- **Infrastructure**: Integration tests with in-memory database
- **Presentation**: UI tests and view model tests

## References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [iOS Clean Architecture](https://tech.olx.com/clean-architecture-and-mvvm-on-ios-c9d167d9f5b3)
- [Swift by Sundell - Architecture](https://www.swiftbysundell.com/articles/different-flavors-of-dependency-injection-in-swift/)

## Review History

- 2025-11-24: Initial proposal
- 2025-11-24: Accepted after team review

---

**Related ADRs:**
- [ADR-002: Use SwiftUI with MVVM Pattern](ADR-002-swiftui-mvvm.md)
- [ADR-006: Protocol-Oriented Design](ADR-006-protocol-oriented.md)
