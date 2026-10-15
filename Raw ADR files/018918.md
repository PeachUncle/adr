# ADR 0010: Coordinator Navigation Initialization Pattern

**Status**: Accepted  
**Date**: 2025-10-06  
**Decision Makers**: Development Team  
**Related**: ADR 0005 (MVVM-C Pattern)

## Context

When implementing coordinators with SwiftUI's `NavigationStack`, we encountered a navigation bug where clicking on a tab would show an extra intermediate screen before displaying the intended root view. For example, clicking "Settings" would navigate to a "General Settings" screen, requiring users to click back to reach the main settings list.

### Root Cause

The issue occurred because coordinators were initializing their `navigationPath` with an initial route (e.g., `[.main]`, `[.home]`, `[.list]`) in the `start()` method. When combined with a `NavigationStack` that had a root view AND handled that route in `.navigationDestination`, it created an unintended navigation push:

```swift
// ❌ INCORRECT PATTERN
func start() {
    navigationPath = [.main]  // Creates initial route
}

// In the view:
NavigationStack(path: $coordinator.navigationPath) {
    SettingsView()  // Root view
        .navigationDestination(for: SettingsRoute.self) { route in
            switch route {
            case .main:
                // This gets pushed on top of root!
                Text("General Settings")
            }
        }
}
```

This caused the `.main` route to be handled as a navigation destination, pushing a view on top of the root `SettingsView`.

## Decision

**All coordinators MUST initialize their `navigationPath` with an empty array.**

The root view in the `NavigationStack` represents the initial/default state of that coordinator. Only subsequent navigations should add routes to the path.

### Correct Pattern

```swift
// ✅ CORRECT PATTERN

// In Coordinator:
func start() {
    // Start with empty path - root view IS the default/initial state
    navigationPath = []

    AppLogger.navigation.logStackChange(
        action: "set",
        coordinator: "ExampleCoordinator",
        stackSize: 0,
        route: "home (root)"
    )
}

// In CoordinatorView:
NavigationStack(path: $coordinator.navigationPath) {
    HomeView()  // This is the root - no route needed
        .navigationDestination(for: ExampleRoute.self) { route in
            switch route {
            case .home:
                // Root should not be in destinations
                // Include case for enum completeness but return EmptyView
                EmptyView()
            case .details(let id):
                DetailsView(id: id)  // Only pushed views here
            }
        }
}
```

## Implementation Guidelines

### For All New Coordinators

1. **Always initialize `navigationPath = []` in `start()`**
2. **Root view should NOT be in the navigation path**
3. **Handle root route case in destination switch with `EmptyView()`**
   - Include a comment explaining why
   - Keeps enum exhaustiveness checking happy

### Example Template

```swift
// Coordinator
@Observable
final class ExampleCoordinator: CoordinatorProtocol {
    var navigationPath: [ExampleRoute] = []

    func start() {
        // Start with empty path - root view represents initial state
        navigationPath = []
    }

    func showDetail(id: String) {
        navigate(to: .detail(id: id))
    }
}

// CoordinatorView
struct ExampleCoordinatorView: View {
    @Bindable var coordinator: ExampleCoordinator

    var body: some View {
        NavigationStack(path: $coordinator.navigationPath) {
            ExampleHomeView()  // Root view
                .navigationDestination(for: ExampleRoute.self) { route in
                    destination(for: route)
                }
        }
    }

    @ViewBuilder
    private func destination(for route: ExampleRoute) -> some View {
        switch route {
        case .home:
            // Root should not be pushed - this case exists for enum completeness
            EmptyView()
        case .detail(let id):
            DetailView(id: id)
        }
    }
}
```

## Consequences

### Positive

- **Correct navigation behavior**: Users see the intended root view immediately
- **Cleaner mental model**: Empty path = root, non-empty path = navigated state
- **Consistent pattern**: All coordinators follow the same initialization approach
- **Predictable stack depth**: `navigationPath.count` accurately reflects navigation depth

### Negative

- **Requires code updates**: Existing coordinators needed refactoring
- **Test updates**: Tests that checked path count needed adjustment
- **Enum completeness**: Root case must be handled in switch despite never being used

### Updated Coordinators (2025-10-06)

The following coordinators were fixed as part of this decision:

- `SettingsCoordinator` - Fixed `.main` route handling
- `DashboardCoordinator` - Fixed `.home` route handling
- `ServicesCoordinator` - Fixed `.list` route handling
- `RadarrCoordinator` - Fixed `.moviesList` route handling
- `OnboardingCoordinator` - Fixed `.welcome` route handling

## Testing Implications

When testing coordinator navigation:

```swift
@Test("Coordinator navigates correctly")
func testNavigation() {
    let coordinator = ExampleCoordinator()
    coordinator.start()

    // After start, path should be empty
    #expect(coordinator.navigationPath.isEmpty)

    // After navigation, path has exactly one item
    coordinator.showDetail(id: "123")
    #expect(coordinator.navigationPath.count == 1)
    #expect(coordinator.navigationPath.last == .detail(id: "123"))
}
```

## References

- [ADR-0001: Single NavigationStack Per Coordinator](0001-single-navigationstack-per-coordinator.md) - Foundation pattern
- [ADR-0005: MVVM-C Pattern](0005-use-mvvm-c-pattern.md) - Coordinator architecture
- [ADR-0011: Hierarchical Navigation Pattern](0011-hierarchical-navigation-pattern.md) - Button-based navigation implementation
- Original Bug Report: Settings navigation requiring back button
- Related Files:
  - `/Thriftwood/Core/Navigation/*Coordinator.swift`
  - `/Thriftwood/UI/*CoordinatorView.swift`
  - `/ThriftwoodTests/CoordinatorTests.swift`

## Review Schedule

Review this pattern if SwiftUI introduces new navigation APIs or if we encounter edge cases where empty initialization causes issues.
