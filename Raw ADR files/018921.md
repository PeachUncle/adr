# ADR-002: Simplify to MVVM with Single NavigationStack

**Date**: October 7, 2025  
**Status**: Accepted  
**Supersedes**: Partial aspects of ADR-0001 (coordinator pattern)

## Context

After implementing MVVM-C with nested NavigationStacks, we encountered several issues:

1. **Nested NavigationStack Complexity**: Coordinator views creating their own NavigationStacks within parent NavigationStacks caused SwiftUI errors ("Only root-level navigation destinations are effective for a navigation stack with a homogeneous path")
2. **Over-engineering**: Analysis of legacy codebase shows ~110 screens with simple linear navigation flows - the coordinator pattern adds significant complexity without proportional benefit
3. **Boilerplate Overhead**: 4-5 files per feature screen with 30-50 lines of navigation plumbing
4. **Against SwiftUI Design**: Nested NavigationStacks in the same window goes against SwiftUI's native patterns

### App Scope Analysis

From legacy codebase:

- **110 screens** across 11 modules
- **Simple navigation patterns**: Mostly linear hierarchical flows
- **No coordinators in legacy**: Flutter app used direct route enums + GoRouter
- **Solo/small team**: 1-2 developers
- **No complex flows**: No multi-step wizards or complex state machines requiring orchestration

## Decision

**Adopt simplified MVVM architecture with single NavigationStack at root.**

### Architecture Pattern

```text
Single NavigationStack (Root)
  └── Bound to: [AppRoute]
        ├── All app destinations in one enum
        ├── Views use NavigationLink or path manipulation
        └── Optional navigation helpers for organization
```

**Components:**

1. **Views** - SwiftUI views with content
2. **ViewModels** - Business logic and state (@Observable)
3. **Services** - API clients, data services
4. **Models** - Data structures
5. **Single AppRoute enum** - All navigation destinations
6. **Optional Navigation Helpers** - Static functions for complex navigation (not full coordinators)

### What Changes

#### Before (MVVM-C)

```swift
// Multiple NavigationStacks
NavigationStack(path: $appCoordinator.navigationPath) {
    // AppRoute: .services, .radarr, .settings
    .navigationDestination(for: AppRoute.self) { ... }
}

// Nested NavigationStack in pushed view
struct RadarrCoordinatorView: View {
    NavigationStack(path: $radarrCoordinator.navigationPath) {
        // RadarrRoute: .home, .moviesList, .movieDetail
        .navigationDestination(for: RadarrRoute.self) { ... }
    }
}
```

#### After (Simple MVVM)

```swift
// Single NavigationStack
NavigationStack(path: $navigationPath) {
    DashboardView()
        .navigationDestination(for: AppRoute.self) { route in
            // All destinations
            switch route {
            case .services: ServicesView()
            case .radarr: RadarrHomeView()
            case .radarrMovies: MoviesListView()
            case .radarrMovieDetail(let id): MovieDetailView(id: id)
            case .settings: SettingsView()
            case .settingsProfiles: ProfileListView()
            // ... all routes in one place
            }
        }
}
```

### Files to Remove/Change

**Remove:**

- `RadarrCoordinatorView.swift`
- `SettingsCoordinatorView.swift`
- `RadarrCoordinator.swift` (or simplify to navigation helper)
- `SettingsCoordinator.swift` (or simplify to navigation helper)
- `RadarrRoute.swift` (merge into AppRoute)
- `SettingsRoute.swift` (merge into AppRoute)
- Coordinator tests (or adapt for navigation helpers)

**Keep/Modify:**

- `AppCoordinator.swift` → Rename to `NavigationManager.swift` or merge into ContentView
- `AppRoute.swift` → Expand to include all routes
- All View files (update navigation calls)
- All ViewModel files (no changes needed)
- All Service files (no changes needed)

## Consequences

### Positive

1. **✅ 70% Less Code**: Remove ~500-700 lines of coordinator boilerplate
2. **✅ SwiftUI-Native**: Single NavigationStack as designed by Apple
3. **✅ Faster Development**: 5 minutes vs 20 minutes to add a new screen
4. **✅ Clear Navigation State**: Single path array `[AppRoute]` - easy to debug
5. **✅ Simpler Deep Linking**: Set path directly without coordinator orchestration
6. **✅ Easier Testing**: Test navigation by verifying path changes
7. **✅ No Nested Stack Issues**: Eliminates entire class of bugs
8. **✅ Easier Onboarding**: Standard SwiftUI patterns, follow Apple docs

### Negative

1. **❌ Single Large Route Enum**: ~60-70 cases (mitigated by grouping with comments)
2. **❌ Less Module Encapsulation**: AppRoute knows about all features (acceptable for this app size)
3. **❌ Refactoring Effort**: 2-3 days to refactor existing code

### Mitigations

For the large enum concern:

```swift
enum AppRoute: Hashable, Sendable {
    // MARK: - Dashboard
    case dashboard

    // MARK: - Services
    case services

    // MARK: - Radarr Module (12 routes)
    case radarr
    case radarrMovies
    case radarrMovieDetail(movieId: Int)
    case radarrAddMovie(query: String = "")
    case radarrEditMovie(movieId: Int)
    // ... grouped by feature
}
```

For navigation organization:

```swift
// Optional: Navigation helpers for complex flows
enum RadarrNavigation {
    @MainActor
    static func showMovieDetail(movieId: Int, navigationPath: inout [AppRoute]) {
        navigationPath.append(.radarrMovieDetail(movieId: movieId))
    }
}
```

## Implementation Plan

### Phase 1: Foundation (Day 1)

1. ✅ Create ADR-002
2. ✅ Update documentation
3. Create unified `AppRoute` enum
4. Add navigation path to AppCoordinator or new NavigationManager
5. Update ContentView with single NavigationStack

### Phase 2: Refactor Features (Day 2)

6. Convert Radarr navigation
7. Convert Settings navigation
8. Remove coordinator view files
9. Update view navigation calls

### Phase 3: Testing & Cleanup (Day 3)

10. Update tests
11. Verify all navigation flows
12. Remove dead code
13. Update implementation summaries

## Alternatives Considered

### Alternative 1: Keep MVVM-C with Nested Stacks

**Rejected**: Goes against SwiftUI design, causes bugs, adds complexity

### Alternative 2: Tab-Based Navigation

**Rejected**: Changes UX significantly, doesn't match hierarchical navigation requirements

### Alternative 3: Protocol-Based Type-Erased Routes

**Rejected**: Adds complexity without clear benefit for this app size

## References

- [MVVM-C-ANALYSIS.md](./MVVM-C-ANALYSIS.md) - Detailed analysis
- [SwiftUI NavigationStack Documentation](https://developer.apple.com/documentation/swiftui/navigationstack)
- Legacy Flutter app: Uses simple route enums without coordinators
- Apple's sample apps: Use NavigationStack with enum routes directly

## Notes

This decision aligns with:

- **SwiftUI's design philosophy**: Simple, declarative navigation
- **App size**: ~110 screens is small-to-medium, not enterprise-scale
- **Team size**: 1-2 developers don't need heavy abstraction
- **Legacy patterns**: Original app used simple routing

This is a **simplification**, not a compromise. We're choosing the right tool for the job size.

---

**Decision made by**: Architecture review  
**Implementation start**: October 7, 2025  
**Expected completion**: October 9-10, 2025
