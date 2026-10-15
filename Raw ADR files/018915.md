# Use MVVM-C (Model-View-ViewModel-Coordinator) Pattern

- Status: accepted
- Deciders: Matthias Wallner Géhri
- Date: 2025-10-03

Technical Story: Milestone 1 Task 1.2 & 1.3 - Define core architecture and navigation framework

## Context and Problem Statement

The app needs a clear architectural pattern that separates concerns, enables testing, and works well with SwiftUI's declarative nature. Which architecture pattern should we adopt?

## Decision Drivers

- **Separation of Concerns**: Clear boundaries between UI, logic, and navigation
- **Testability**: Easy to test business logic without UI
- **SwiftUI Integration**: Works naturally with SwiftUI's data flow
- **Navigation Management**: Clear ownership of navigation logic
- **Maintainability**: Simple enough for solo indie development
- **Type Safety**: Leverage Swift's type system
- **Scalability**: Can grow with the app's complexity

## Considered Options

- **Option 1**: MVVM-C (Model-View-ViewModel-Coordinator)
- **Option 2**: MV (Model-View) - SwiftUI native
- **Option 3**: VIPER (View-Interactor-Presenter-Entity-Router)
- **Option 4**: Redux/TCA (The Composable Architecture)

## Decision Outcome

Chosen option: **Option 1 - MVVM-C**

MVVM-C provides the right balance of separation of concerns, testability, and simplicity while working naturally with SwiftUI. The Coordinator pattern solves SwiftUI's navigation challenges elegantly.

### Consequences

- **Good**: Clear separation: View (UI), ViewModel (state/logic), Coordinator (navigation)
- **Good**: Testable business logic (ViewModels independent of UI)
- **Good**: Reusable views (navigation is external)
- **Good**: Type-safe navigation with route enums
- **Good**: Works naturally with SwiftUI's @Observable
- **Good**: Simple enough for solo development
- **Good**: Scalable as app grows
- **Neutral**: Requires discipline to maintain boundaries
- **Bad**: More files than simple MV pattern

### Implementation Structure

**Model Layer**:

```swift
@Model
final class Profile {
    var name: String
    var radarr: RadarrConfiguration?
    // ...
}
```

**View Layer** (Pure SwiftUI):

```swift
struct ProfileListView: View {
    @State private var viewModel: ProfileListViewModel

    var body: some View {
        List(viewModel.profiles) { profile in
            ProfileRow(profile: profile)
        }
    }
}
```

**ViewModel Layer** (Business Logic):

```swift
@MainActor
@Observable
final class ProfileListViewModel: BaseViewModel {
    private let profileService: any ProfileServiceProtocol
    var profiles: [Profile] = []

    func loadProfiles() async {
        profiles = try await profileService.fetchAll()
    }
}
```

**Coordinator Layer** (Navigation):

```swift
@MainActor
@Observable
final class SettingsCoordinator: Coordinator {
    var path: [SettingsRoute] = []

    func navigate(to route: SettingsRoute) {
        path.append(route)
    }
}

enum SettingsRoute: Hashable {
    case profiles
    case addProfile
    case appearance
}
```

## Pros and Cons of the Options

### Option 1: MVVM-C

- **Good**: Clear separation of concerns (4 layers)
- **Good**: Testable ViewModels without UI
- **Good**: Navigation logic separate from views
- **Good**: Works naturally with SwiftUI @Observable
- **Good**: Type-safe routing with enums
- **Good**: Views are reusable (no navigation logic)
- **Good**: Manageable complexity for solo dev
- **Neutral**: Requires coordinator wiring
- **Bad**: More files than simpler patterns

### Option 2: MV (Model-View)

- **Good**: Simplest approach (fewest files)
- **Good**: Native SwiftUI pattern
- **Good**: Minimal boilerplate
- **Neutral**: Business logic in views
- **Bad**: Harder to test (logic coupled to UI)
- **Bad**: No clear navigation abstraction
- **Bad**: Views become large and complex
- **Bad**: Difficult to reuse views in different contexts

### Option 3: VIPER

- **Good**: Maximum separation of concerns
- **Good**: Very testable
- **Neutral**: Enterprise-grade architecture
- **Bad**: Too complex for this project
- **Bad**: Massive amount of boilerplate
- **Bad**: 5 layers per feature (overkill)
- **Bad**: Difficult for solo maintenance
- **Bad**: Doesn't align well with SwiftUI

### Option 4: Redux/TCA

- **Good**: Single source of truth
- **Good**: Predictable state changes
- **Good**: Time-travel debugging
- **Good**: Great for complex state management
- **Neutral**: Functional programming paradigm
- **Bad**: Steep learning curve
- **Bad**: Boilerplate for actions/reducers
- **Bad**: Overkill for this app's complexity
- **Bad**: Third-party framework dependency

## More Information

### Layer Responsibilities

**Model Layer**:

- SwiftData models (@Model)
- Domain entities (Codable structs)
- No business logic

**View Layer**:

- Pure SwiftUI views
- No business logic
- No navigation logic
- Observes ViewModel state

**ViewModel Layer**:

- Business logic and state management
- @Observable for SwiftUI updates
- @MainActor isolated
- Protocol-based services via DI
- Inherits from BaseViewModel

**Coordinator Layer**:

- Navigation logic
- Route definitions (Hashable enums)
- Manages NavigationStack path
- Creates child coordinators
- Handles deep linking

### BaseViewModel Protocol

```swift
@MainActor
protocol BaseViewModel: Observable {
    var isLoading: Bool { get set }
    var error: (any Error)? { get set }

    func load() async
    func reload() async
    func cleanup()
}
```

### File Organization

```
Thriftwood/
├── Core/
│   ├── Navigation/       # Coordinators and Routes
│   ├── ViewModels/       # BaseViewModel
│   └── ...
├── UI/
│   ├── Components/       # Reusable views
│   ├── Settings/
│   │   ├── SettingsView.swift
│   │   ├── ProfileListView.swift
│   │   └── ...
│   └── ...
└── ThriftwoodTests/
    ├── CoordinatorTests.swift
    ├── ProfileListViewModelTests.swift
    └── ...
```

### Testing Strategy

**ViewModels** - Unit tests with mock services:

```swift
@Test("Load profiles successfully")
func testLoadProfiles() async {
    let mockService = MockProfileService()
    mockService.profilesResult = .success([testProfile])

    let viewModel = ProfileListViewModel(profileService: mockService)
    await viewModel.load()

    #expect(viewModel.profiles.count == 1)
}
```

**Coordinators** - Navigation logic tests:

```swift
@Test("Navigate to profile detail")
func testNavigateToProfile() {
    let coordinator = SettingsCoordinator()
    coordinator.navigate(to: .profiles)

    #expect(coordinator.path.last == .profiles)
}
```

**Views** - Snapshot or integration tests (future):

```swift
// Using ViewInspector or similar
```

## Related Decisions

- [ADR-0001: Single NavigationStack Per Coordinator](0001-single-navigationstack-per-coordinator.md) - Defines coordinator navigation pattern
- [ADR-0002: Use SwiftData Over CoreData](0002-use-swiftdata-over-coredata.md) - Models are SwiftData @Model objects
- [ADR-0003: Use Swinject for DI](0003-use-swinject-for-dependency-injection.md) - Services injected into ViewModels
- [ADR-0010: Coordinator Navigation Initialization](0010-coordinator-navigation-initialization.md) - Empty path initialization
- [ADR-0011: Hierarchical Navigation Pattern](0011-hierarchical-navigation-pattern.md) - Button-based hierarchical navigation

## References

- [Advanced iOS App Architecture (raywenderlich.com)](https://www.raywenderlich.com/books/advanced-ios-app-architecture)
- [Coordinator Pattern in SwiftUI](https://www.hackingwithswift.com/articles/216/complete-guide-to-navigationstack)
- [SwiftUI MVVM Guide](https://www.swiftbysundell.com/articles/swiftui-state-management-guide/)
