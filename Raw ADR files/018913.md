# Use Swinject for Dependency Injection

- Status: accepted
- Deciders: Matthias Wallner Géhri
- Date: 2025-10-04

Technical Story: Milestone 1 Task 1.2 - Implement dependency injection container for services

## Context and Problem Statement

The app needs a dependency injection solution to manage service lifecycles, enable testing with mocks, and maintain loose coupling between components. Which DI approach should we use?

## Decision Drivers

- **Testability**: Easy to inject mocks for testing
- **Type Safety**: Compile-time checking where possible
- **Swift 6 Compatibility**: Must work with strict concurrency
- **Maintainability**: Simple API for solo indie development
- **Feature Set**: Supports singletons, factories, and dependency graphs
- **Community Support**: Well-maintained with active development
- **Performance**: Minimal runtime overhead

## Considered Options

- **Option 1**: Swinject (established iOS/macOS DI framework)
- **Option 2**: Factory (modern Swift DI library)
- **Option 3**: Custom DI container
- **Option 4**: Manual dependency passing

## Decision Outcome

Chosen option: **Option 1 - Swinject**

Swinject provides a mature, well-tested DI solution with a simple API that works seamlessly with Swift 6 concurrency. Its widespread adoption means good community support and examples.

### Consequences

- **Good**: Battle-tested framework used in production apps
- **Good**: Simple container-based API
- **Good**: Supports singletons (`.inObjectScope(.container)`)
- **Good**: Supports factory creation
- **Good**: Thread-safe by design
- **Good**: Good documentation and examples
- **Good**: Works with Swift 6 strict concurrency
- **Neutral**: Uses runtime resolution (not compile-time)
- **Bad**: Requires explicit registration for each service

### Implementation Details

**DIContainer Setup**:

```swift
final class DIContainer {
    static let shared = DIContainer()
    private let container = Container()

    init() {
        registerServices()
    }

    private func registerServices() {
        // Data layer
        container.register(DataService.self) { _ in
            DataService(container: .thriftwoodContainer())
        }.inObjectScope(.container)

        // Services
        container.register((any UserPreferencesServiceProtocol).self) { resolver in
            UserPreferencesService(
                dataService: resolver.resolve(DataService.self)!
            )
        }.inObjectScope(.container)

        // Theme
        container.register(MPWGThemeManager.self) { _ in
            MPWGThemeManager()
        }.inObjectScope(.container)
    }

    func resolve<Service>(_ serviceType: Service.Type) -> Service {
        container.resolve(serviceType)!
    }
}
```

**Service Registration Patterns**:

- **Singleton**: `.inObjectScope(.container)` for stateful services
- **Factory**: No scope specified for transient objects
- **Protocol**: Register via protocol for testability

## Pros and Cons of the Options

### Option 1: Swinject

- **Good**: Mature, production-ready framework
- **Good**: Simple Container API
- **Good**: Lifecycle management (singleton, transient, graph)
- **Good**: Thread-safe out of the box
- **Good**: Active maintenance and community
- **Good**: Works with Swift 6 concurrency
- **Neutral**: Runtime resolution (not compile-time)
- **Bad**: Small external dependency (~2000 LOC)

### Option 2: Factory

- **Good**: Modern Swift-first design
- **Good**: Property wrapper API (`@Injected`)
- **Good**: Compile-time safety in some cases
- **Good**: Lightweight implementation
- **Neutral**: Newer framework (less battle-tested)
- **Bad**: Less community support and examples
- **Bad**: Swift 6 compatibility needs verification

### Option 3: Custom DI Container

- **Good**: Full control over implementation
- **Good**: No external dependencies
- **Good**: Tailored to exact needs
- **Bad**: Time to implement and test
- **Bad**: Need to handle thread safety
- **Bad**: Need to implement lifecycle management
- **Bad**: Reinventing the wheel
- **Bad**: Solo maintenance burden

### Option 4: Manual Dependency Passing

- **Good**: No framework needed
- **Good**: Explicit dependencies in init
- **Good**: Type-safe at compile time
- **Good**: Easy to understand
- **Bad**: Verbose initialization code
- **Bad**: Deep dependency graphs become unwieldy
- **Bad**: ViewModels require many parameters
- **Bad**: Difficult to swap implementations

## More Information

### Service Resolution in Views

```swift
struct SettingsView: View {
    @State private var preferences: any UserPreferencesServiceProtocol

    init() {
        let container = DIContainer.shared
        self.preferences = container.resolve((any UserPreferencesServiceProtocol).self)
    }
}
```

### Testing with Mocks

```swift
@Test("Profile service can create profile")
func testCreateProfile() async throws {
    // Setup mock
    let mockService = MockProfileService()

    // Use mock in ViewModel
    let viewModel = ProfileListViewModel(profileService: mockService)

    // Test behavior
    await viewModel.createProfile(name: "Test")
    #expect(mockService.createCalled == true)
}
```

### Service Lifecycle

- **Container Scope**: Single instance shared across app (DataService, ThemeManager)
- **Transient**: New instance per resolution (ViewModels)
- **Graph**: Dependencies resolved automatically

## Related Decisions

- 0002: Use SwiftData Over CoreData - Swinject manages DataService lifecycle
- 0003: Swift 6 Approachable Concurrency - Swinject is thread-safe by default

## References

- [Swinject GitHub](https://github.com/Swinject/Swinject)
- [Swinject Documentation](https://github.com/Swinject/Swinject/tree/master/Documentation)
- Package: `https://github.com/Swinject/Swinject.git` @ 2.10.0
