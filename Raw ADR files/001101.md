# ADR-001: Dependency Injection Container Adoption

## Status
Accepted

## Context
The ClariFi iOS codebase had grown organically with inconsistent dependency management patterns. We identified several problems:

1. **Singleton Overuse**: 39+ references to `RepositoryFactory.shared` throughout the codebase
2. **Tight Coupling**: Direct dependencies on concrete implementations made testing difficult
3. **Inconsistent Patterns**: Mix of singleton access, default parameters, manual injection, and environment objects
4. **Poor Testability**: Difficult to inject mock dependencies for unit testing
5. **Hidden Dependencies**: Constructor signatures didn't reveal all dependencies

These issues made the codebase harder to maintain, test, and reason about. As the app grew, the technical debt from these patterns was becoming increasingly problematic.

## Decision
We will implement a centralized Dependency Injection (DI) container to manage all application dependencies. The DI container will:

1. **Manage Lifecycles**: Support both singleton (created once, reused) and transient (created each time) lifecycles
2. **Type-Safe Resolution**: Use Swift generics for compile-time type safety
3. **Constructor Injection**: All dependencies will be injected through constructors, making dependencies explicit
4. **SwiftUI Integration**: Integrate with SwiftUI's environment system for seamless view integration
5. **Test Support**: Enable easy injection of mock dependencies for testing

### Implementation Details

**Core Container Protocol:**
```swift
protocol DIContainer {
    func register<T>(_ type: T.Type, factory: @escaping (DIContainer) -> T)
    func registerSingleton<T>(_ type: T.Type, factory: @escaping (DIContainer) -> T)
    func resolve<T>(_ type: T.Type) -> T
    func resolveOptional<T>(_ type: T.Type) -> T?
    func reset()
}
```

**Registration Pattern:**
- Repositories: Singleton lifecycle (expensive to create, maintain state)
- Services: Singleton lifecycle (maintain state, expensive initialization)
- ViewModels: Transient lifecycle (new instance per view)

**SwiftUI Integration:**
```swift
extension EnvironmentValues {
    var diContainer: DIContainer { get set }
}
```

## Consequences

### Positive
1. **Explicit Dependencies**: Constructor signatures clearly show all dependencies
2. **Improved Testability**: Easy to inject mock implementations for testing
3. **Centralized Configuration**: All dependency wiring in one place (`AppDIContainer+Registration.swift`)
4. **Lifecycle Control**: Clear control over singleton vs transient lifecycles
5. **Reduced Coupling**: Components depend on protocols, not concrete implementations
6. **Better Maintainability**: Easier to understand and modify dependency relationships

### Negative
1. **Initial Learning Curve**: Team needs to understand DI container patterns
2. **Boilerplate Code**: Registration code required for each dependency
3. **Runtime Resolution**: Dependency errors caught at runtime, not compile time (mitigated by fail-fast approach)
4. **SwiftUI Limitations**: `@StateObject` initialization requires workarounds for DI

### Neutral
1. **Migration Effort**: Significant refactoring required to migrate existing code
2. **Performance Impact**: Minimal (<20ms for typical resolution), acceptable for mobile app

## Alternatives Considered

### 1. Continue with Singleton Pattern
**Rejected**: Maintains tight coupling and poor testability. Technical debt would continue to grow.

### 2. Manual Dependency Injection (No Container)
**Rejected**: Would require passing dependencies through many layers. Becomes unwieldy as app grows.

### 3. Third-Party DI Framework (Swinject, Resolver)
**Rejected**: Adds external dependency and complexity. Our needs are simple enough for a custom solution that's tailored to our architecture.

### 4. SwiftUI Environment Objects Only
**Rejected**: Environment objects are designed for view hierarchy state, not general dependency injection. Mixing concerns would be confusing.

## Implementation Notes

### Migration Strategy
1. Create DI container infrastructure alongside existing singletons
2. Gradually migrate components to use DI
3. Remove singletons only after all references migrated
4. Maintain backward compatibility during transition

### Key Files
- `Core/DependencyInjection/DIContainer.swift` - Protocol definition
- `Core/DependencyInjection/AppDIContainer.swift` - Implementation
- `Core/DependencyInjection/AppDIContainer+Registration.swift` - Dependency registration
- `Core/DependencyInjection/DIContainer+Environment.swift` - SwiftUI integration

### Testing Support
- `Tests/TestHelpers/DIContainer+Testing.swift` - Test container factory
- Mock implementations registered in test container
- In-memory Core Data stack for repository testing

## References
- Requirements: 1.1, 1.2, 1.3, 1.5, 1.6
- Related ADRs: ADR-002 (Repository Pattern), ADR-003 (Service Layer)
- Design Document: Section "Dependency Injection Container"

## Date
2025-10-12

## Authors
ClariFi iOS Team
