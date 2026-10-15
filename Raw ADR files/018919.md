---
status: accepted
date: 2025-10-06
decision-makers:
  - Matthias Wallner Géhri
consulted:
  - AI Agent (GitHub Copilot)
  - Legacy Flutter codebase analysis
informed:
  - Future development team
---

# Hierarchical Navigation Pattern for Media Management

**Technical Story**: Replace tab-based navigation with hierarchical navigation using buttons for service access, with back/home navigation controls

## Context and Problem Statement

The current navigation uses a tab-based approach with `TabView` for the main app sections (Dashboard, Services, Settings). The Services tab then uses `fullScreenCover` to present Radarr and Sonarr modules, which themselves have internal tab navigation (Catalogue, Upcoming, Missing, More).

**Problems with current approach:**

1. **Nested tabs are confusing**: Services tab → Radarr → 4 internal tabs creates 2 levels of tabs
2. **Full screen covers hide context**: User loses sense of where they are in app hierarchy
3. **Inconsistent with media management UX**: Apps like Plex use hierarchical navigation, not tabs
4. **Legacy mismatch**: Flutter app uses GoRouter with hierarchical navigation, not tabs
5. **Limited navigation depth**: Tabs don't scale well for deep hierarchies (Service → Category → Item → Details → Edit)

The user has requested a complete redesign: remove tabs entirely, use buttons in main views for navigation, and provide back/home buttons for navigation control.

## Decision Drivers

- **User Experience**: Clear, predictable navigation that matches user mental models
- **Legacy Parity**: Flutter app uses hierarchical navigation extensively
- **Navigation Depth**: Media management requires 4-5 levels deep navigation
- **Consistency**: One navigation pattern across the entire app
- **Native Feel**: Use Apple's recommended patterns where possible
- **Maintainability**: Simple, testable navigation architecture
- **Platform Support**: Must support macOS and iOS (Catalyst)

## Legacy Navigation Analysis

### Flutter App Navigation Structure (GoRouter)

The legacy app uses a hierarchical routing structure with the following depth:

#### **Radarr Navigation Hierarchy** (Max depth: 5 levels)

```text
Level 1: /radarr                          # Home (4 tab sections: Catalogue, Upcoming, Missing, More)
├─ Level 2: /radarr/movie/:id             # Movie Details
│  ├─ Level 3: /radarr/movie/:id/edit     # Edit Movie
│  └─ Level 3: /radarr/movie/:id/releases # Search Releases
├─ Level 2: /radarr/add_movie             # Add Movie (search)
│  └─ Level 3: /radarr/add_movie/details  # Add Movie Details (configure before adding)
├─ Level 2: /radarr/history               # History
├─ Level 2: /radarr/queue                 # Queue
├─ Level 2: /radarr/manual_import         # Manual Import
│  └─ Level 3: /radarr/manual_import/details  # Manual Import Details
├─ Level 2: /radarr/system_status         # System Status
└─ Level 2: /radarr/tags                  # Tags Management
```

**Key Observations:**

- **Primary navigation**: 4 tab sections (Catalogue, Upcoming, Missing, More) inside Radarr home
- **Maximum depth**: 3 levels from Radarr home (e.g., Radarr → Movie → Edit)
- **Common flows**:
  - Radarr → Movie Details → Edit (3 levels)
  - Radarr → Add Movie → Details (3 levels)
  - Radarr → More → History/Queue/etc. (2 levels)
- **Back navigation**: Always available via system back button

#### **Sonarr Navigation Hierarchy** (Max depth: 5 levels)

```text
Level 1: /sonarr                           # Home (4 tab sections: Catalogue, Upcoming, Missing, More)
├─ Level 2: /sonarr/series/:id             # Series Details
│  ├─ Level 3: /sonarr/series/:id/edit     # Edit Series
│  └─ Level 3: /sonarr/series/:id/season/:seasonNum  # Season Details
│     └─ Level 4: /sonarr/releases         # Search Releases (for episode)
├─ Level 2: /sonarr/add_series             # Add Series (search)
│  └─ Level 3: /sonarr/add_series/details  # Add Series Details
├─ Level 2: /sonarr/history                # History
├─ Level 2: /sonarr/queue                  # Queue
├─ Level 2: /sonarr/system_status          # System Status
└─ Level 2: /sonarr/tags                   # Tags Management
```

**Key Observations:**

- **Similar structure to Radarr**: 4 tab sections at home level
- **Maximum depth**: 4 levels from Sonarr home (Series → Season → Releases)
- **Deeper than Radarr**: TV shows require extra season level

#### **App-Level Hierarchy** (Max depth: 6 levels)

```text
Level 0: Dashboard                         # Main dashboard
├─ Level 1: Radarr (see above)            # + 3-4 more levels
├─ Level 1: Sonarr (see above)            # + 4-5 more levels
├─ Level 1: Lidarr                        # Similar to Radarr
├─ Level 1: Settings                      # Settings menu
│  ├─ Level 2: Profiles                   # Profile management
│  │  └─ Level 3: Add/Edit Profile        # Profile form
│  ├─ Level 2: General Settings
│  ├─ Level 2: Appearance
│  └─ Level 2: About
└─ Level 1: Search                        # Global search
   └─ Level 2: Search Results by Service  # Results grouped by service
```

**Maximum Navigation Depth**: Dashboard → Sonarr → Series → Season → Releases = **5 levels**

### Legacy Navigation Pattern

The Flutter app uses:

- **GoRouter** for URL-based routing
- **Drawer navigation** for main app sections (Dashboard, Services, Settings)
- **Bottom tabs** within service modules (4 tabs: Catalogue, Upcoming, Missing, More)
- **Push navigation** for details and forms
- **System back button** always available

**User Flow Example** (Radarr):

```
1. Drawer menu → Tap "Radarr"
2. See 4 tabs: Catalogue, Upcoming, Missing, More
3. Catalogue tab → Tap movie
4. Movie Details → Tap edit
5. Edit form → Back to Movie Details → Back to Catalogue
```

## Considered Options

### Option 1: Pure NavigationStack with Hierarchical Button Navigation (Recommended)

**Description**:

- Remove all tabs (including internal service tabs)
- Use NavigationStack in each coordinator
- Main view shows buttons to navigate to sub-sections
- Back button provided by system
- Add custom home button to toolbar for quick return to root

**Structure**:

```text
Dashboard (root)
└─ NavigationStack
   ├─ Dashboard Home (buttons: Radarr, Sonarr, Settings, etc.)
   ├─ Radarr Module
   │  ├─ Radarr Home (buttons: Movies, Upcoming, Missing, History, Queue, etc.)
   │  ├─ Movies List
   │  │  └─ Movie Details
   │  │     ├─ Edit Movie
   │  │     └─ Search Releases
   │  ├─ Upcoming Movies
   │  ├─ Missing Movies
   │  └─ History
   ├─ Sonarr Module (similar structure)
   └─ Settings Module
```

**Example Implementation**:

```swift
struct RadarrHomeView: View {
    var onNavigateTo: (RadarrSection) -> Void

    var body: some View {
        List {
            Section("Library") {
                Button(action: { onNavigateTo(.movies) }) {
                    Label("Movies", systemImage: "film")
                }
                Button(action: { onNavigateTo(.upcoming) }) {
                    Label("Upcoming", systemImage: "calendar")
                }
                Button(action: { onNavigateTo(.missing) }) {
                    Label("Missing", systemImage: "exclamationmark.circle")
                }
            }

            Section("Activity") {
                Button(action: { onNavigateTo(.queue) }) {
                    Label("Queue", systemImage: "arrow.down.circle")
                }
                Button(action: { onNavigateTo(.history) }) {
                    Label("History", systemImage: "clock")
                }
            }

            Section("System") {
                Button(action: { onNavigateTo(.systemStatus) }) {
                    Label("System Status", systemImage: "info.circle")
                }
                Button(action: { onNavigateTo(.settings) }) {
                    Label("Settings", systemImage: "gearshape")
                }
            }
        }
        .navigationTitle("Radarr")
        .toolbar {
            ToolbarItem(placement: .navigation) {
                Button(action: { /* pop to app root */ }) {
                    Label("Home", systemImage: "house")
                }
            }
        }
    }
}
```

**Pros**:

- ✅ **Simplest implementation**: Use existing NavigationStack coordinator pattern
- ✅ **Native SwiftUI**: System back button works automatically
- ✅ **Clear hierarchy**: User always knows where they are
- ✅ **Scalable**: Handles 5+ levels easily
- ✅ **Consistent**: One pattern across entire app
- ✅ **Accessible**: VoiceOver works perfectly with native navigation
- ✅ **Keyboard navigation**: Standard macOS keyboard shortcuts work
- ✅ **URL-based routing**: Can implement deep linking easily
- ✅ **No additional dependencies**: Pure SwiftUI
- ✅ **Home button flexibility**: Can add custom toolbar button for "pop to root"

**Cons**:

- ⚠️ **No persistent section tabs**: Users must navigate back to home to switch sections
- ⚠️ **More taps**: Requires navigation to sub-section vs. direct tab access
- ⚠️ **Different from legacy**: Changes tab-based service navigation to buttons

**Neutral**:

- 🔵 **macOS adaptation**: Works well, but could also use NavigationSplitView (see Option 2)

---

### Option 2: NavigationSplitView with Sidebar (macOS-Optimized)

**Description**:

- Use `NavigationSplitView` with sidebar for main sections
- Sidebar shows: Dashboard, Services (Radarr, Sonarr), Settings
- Detail pane uses NavigationStack for deep navigation
- Perfect for macOS, decent for iPad, awkward for iPhone

**Structure**:

```swift
NavigationSplitView {
    // Sidebar
    List(selection: $selectedSection) {
        Section("Main") {
            Label("Dashboard", systemImage: "square.grid.2x2")
        }
        Section("Services") {
            Label("Radarr", systemImage: "film")
            Label("Sonarr", systemImage: "tv")
        }
        Section("Settings") {
            Label("Settings", systemImage: "gearshape")
        }
    }
} detail: {
    // Detail pane with NavigationStack
    NavigationStack(path: $path) {
        selectedSectionView()
            .navigationDestination(for: Route.self) { route in
                // Deep navigation within section
            }
    }
}
```

**Pros**:

- ✅ **macOS native**: Matches macOS app conventions perfectly
- ✅ **Quick section switching**: Sidebar always visible on macOS/iPad
- ✅ **Split-screen friendly**: Works well with macOS window management
- ✅ **Keyboard navigation**: Cmd+1, Cmd+2 for section switching
- ✅ **Discoverable**: All main sections visible at once
- ✅ **iPad optimization**: Uses space efficiently in landscape

**Cons**:

- ❌ **Poor iPhone UX**: Sidebar is awkward on small screens
- ❌ **Requires separate layouts**: Need conditional logic for iPhone vs. iPad/Mac
- ❌ **State management complexity**: Sidebar selection + NavigationStack path
- ❌ **Coordinator complications**: Harder to integrate with existing coordinator pattern
- ❌ **Not suitable for services**: Radarr/Sonarr shouldn't have persistent sidebar
- ❌ **Inconsistent depth**: App-level gets sidebar, service-level doesn't

**Neutral**:

- 🔵 **Best for app-level only**: Could use for Dashboard/Services/Settings split, not within services

---

### Option 3: Hybrid - NavigationSplitView for App + NavigationStack for Services

**Description**:

- Use NavigationSplitView at app root level (Dashboard, Services, Settings)
- Within each service (Radarr, Sonarr), use NavigationStack with button-based navigation
- Best of both worlds for macOS, but introduces inconsistency

**Structure**:

```text
NavigationSplitView (App Level)
├─ Sidebar: Dashboard, Services, Settings
└─ Detail Pane:
   ├─ Dashboard → NavigationStack (hierarchical content)
   ├─ Services → NavigationStack
   │  └─ Radarr → NavigationStack (button-based navigation)
   │     └─ Movies → Movie Details → Edit (3 levels deep)
   └─ Settings → NavigationStack
```

**Pros**:

- ✅ **macOS optimized**: Sidebar for main sections
- ✅ **Service simplicity**: Radarr/Sonarr use simple NavigationStack
- ✅ **Quick main navigation**: Switch Dashboard/Services/Settings via sidebar
- ✅ **Deep service navigation**: NavigationStack handles 5+ levels well

**Cons**:

- ❌ **Inconsistent UX**: Different navigation patterns at different levels
- ❌ **iPhone complexity**: Need different layouts for iPhone
- ❌ **Cognitive overhead**: Users must learn two navigation patterns
- ❌ **Coordinator complexity**: Two navigation paradigms to support
- ⚠️ **Testing burden**: Must test both navigation patterns

**Neutral**:

- 🔵 **Platform-specific**: Could adapt per platform (sidebar on Mac, tabs on iPhone)

---

### Option 4: Custom Navigation with Third-Party Package

**Evaluated Packages**:

#### **SUICoordinator** (felilo/SUICoordinator)

- Coordinator pattern library for SwiftUI
- Tab-based and navigation-based coordination
- Good for complex apps with multiple coordinators
- **Verdict**: Overkill - we already have coordinator pattern

#### **SUINavigation** (ozontech/SUINavigation)

- Alternative NavigationStack with iOS 14 support
- Bug fixes for Apple navigation issues
- **Verdict**: Not needed - targeting iOS 17+, no known NavigationStack bugs

#### **NavigationKit** (Commercial - Rebel Operator)

- Paid navigation framework
- Advanced features like sheet coordination
- **Verdict**: Against project philosophy - prefer open-source, no budget

**General Assessment**:

- ❌ **Unnecessary dependency**: Current NavigationStack works well
- ❌ **Maintenance risk**: External packages can become abandoned
- ❌ **Learning curve**: Team must learn package API
- ❌ **Swift 6 compatibility**: Not all packages support strict concurrency
- ❌ **GPL license conflicts**: Some packages have incompatible licenses
- ✅ **Only if needed**: Consider if NavigationStack has critical bugs

**Decision**: Do NOT use third-party navigation packages. Apple's NavigationStack is mature and well-supported.

---

### Option 5: Custom UIKit-Style Navigation (Manual Push/Pop)

**Description**:

- Implement custom navigation without NavigationStack
- Manually manage view stack with `@State` array
- Custom animations and transitions
- Full control over navigation behavior

**Example**:

```swift
@State private var viewStack: [AnyView] = []

var body: some View {
    ZStack {
        if let topView = viewStack.last {
            topView
        } else {
            rootView
        }
    }
    .animation(.default, value: viewStack.count)
}

func push(_ view: AnyView) {
    viewStack.append(view)
}

func pop() {
    _ = viewStack.popLast()
}
```

**Pros**:

- ✅ **Full control**: Custom animations, gestures, transitions
- ✅ **No Apple bugs**: Not dependent on NavigationStack implementation

**Cons**:

- ❌ **Massive implementation effort**: Must replicate all NavigationStack features
- ❌ **No system back button**: Must implement swipe-to-go-back gesture
- ❌ **Accessibility nightmare**: VoiceOver navigation must be implemented manually
- ❌ **Keyboard navigation**: Must implement all macOS keyboard shortcuts
- ❌ **State restoration**: Must implement navigation state persistence
- ❌ **Deep linking**: Must implement URL routing manually
- ❌ **Toolbar integration**: Must handle toolbars manually
- ❌ **Testing complexity**: Must test all navigation edge cases
- ❌ **Maintenance burden**: Ongoing work for iOS/macOS updates

**Verdict**: ❌ **Do NOT implement custom navigation.** The effort-to-benefit ratio is terrible for a solo indie project.

---

## Decision Outcome

**Chosen option**: "Option 1 - Pure NavigationStack with Hierarchical Button Navigation"

### Rationale

1. **Simplest to implement**: Uses existing coordinator pattern, just removes tabs
2. **Native SwiftUI**: No dependencies, fully supported by Apple
3. **Matches legacy depth**: Handles 5-level navigation (legacy max: 5 levels)
4. **Scalable**: Easy to add new sections and services
5. **Consistent UX**: One navigation pattern throughout the app
6. **Accessible**: System back button, VoiceOver, keyboard navigation all work
7. **Platform-agnostic**: Works well on macOS, iOS, and Catalyst
8. **Low maintenance**: Apple maintains NavigationStack, not us
9. **Testable**: Coordinator tests already exist, minimal changes needed

### Hybrid Consideration (Future Enhancement)

For a future **macOS-specific optimization**, consider:

- Use NavigationSplitView **only at app root level** (Dashboard, Services, Settings)
- Keep NavigationStack for all service-level navigation (Radarr, Sonarr)
- Conditionally enable sidebar on macOS/iPad only

**Implementation:**

```swift
#if os(macOS)
    NavigationSplitView { /* sidebar */ } detail: { /* content */ }
#else
    NavigationStack { /* hierarchical navigation */ }
#endif
```

**Decision**: Implement pure NavigationStack first, evaluate NavigationSplitView after MVP.

### Consequences

#### Positive

- Good, because it simplifies architecture with one navigation pattern instead of tabs + navigation
- Good, because it handles deep navigation (5+ levels) naturally
- Good, because it uses native system back button and navigation conventions
- Good, because coordinator tests are simpler without tab state
- Good, because VoiceOver navigation is more predictable
- Good, because standard macOS keyboard shortcuts work (Cmd+[ for back)
- Good, because it provides consistent UX across the entire app

#### Negative

- Bad, because users familiar with Flutter app must learn new pattern
- Bad, because switching sections requires navigating back to home vs. tab switching (more taps)
- Bad, because significant refactoring is required for all coordinator views and routes
- Bad, because existing users may find navigation different during migration

#### Neutral

- Neutral, because macOS optimization with NavigationSplitView is deferred but can be added later
- Neutral, because custom animations can be added later without architectural changes

### Confirmation

The implementation will be validated through:

1. **Automated Testing**

   - Coordinator navigation tests must pass
   - Route enum tests must pass
   - View lifecycle tests must pass
   - Navigation state restoration tests must pass

2. **Manual Testing Checklist**

   - Navigate 5 levels deep: App Home → Services → Radarr → Movies → Movie Detail → Edit
   - Back button works at every level
   - Home button returns to app home from any depth
   - Navigation state preserved on orientation change (iOS)
   - Navigation state preserved on window resize (macOS)
   - VoiceOver announces navigation changes correctly
   - Keyboard shortcuts work (Cmd+[ for back on macOS)
   - Deep linking works (thriftwood://radarr/movies/123)

3. **Performance Testing**

   - Navigation transitions are smooth (60fps)
   - Memory usage is stable (no leaks)
   - Large navigation stacks don't cause slowdown

4. **Code Review**
   - All coordinator views follow single NavigationStack pattern
   - No nested NavigationStacks in destination views
   - Home button present in all deep views
   - Routes follow established naming conventions

---

## Implementation Plan

### Phase 1: Remove Tabs, Add Button Navigation (Week 1)

#### 1.1 Update Route Enums

**Add new routes for service home screens:**

```swift
// RadarrRoute.swift
enum RadarrRoute: Hashable, Sendable {
    case home              // NEW: Radarr home with buttons
    case moviesList        // Renamed from .moviesCatalogue
    case upcoming
    case missing
    case queue
    case history
    case movieDetail(movieId: Int)
    case addMovie(query: String = "")
    case settings
    case systemStatus
}

// AppRoute.swift
enum AppRoute: Hashable, Sendable {
    case dashboard
    case services         // NEW: Services home with buttons
    case radarr
    case sonarr
    case settings
}
```

#### 1.2 Remove TabView, Implement Button-Based Navigation

**Remove:**

- `MainTabView.swift` - Delete tab-based main app navigation
- `TabCoordinator.swift` - Replace with hierarchical coordinator
- Tab navigation within Radarr/Sonarr

**Create:**

- `AppHomeView.swift` - App home with buttons (Dashboard, Services, Settings)
- `ServicesHomeView.swift` - Services home with buttons (Radarr, Sonarr, etc.)
- `RadarrHomeView.swift` - Radarr home with buttons (Movies, Upcoming, etc.)

#### Example: ServicesHomeView.swift

```swift
struct ServicesHomeView: View {
    let onNavigateTo: (Service) -> Void

    var body: some View {
        List {
            Section("Media Management") {
                Button(action: { onNavigateTo(.radarr) }) {
                    HStack {
                        Image(systemName: "film")
                            .foregroundColor(.blue)
                        VStack(alignment: .leading) {
                            Text("Radarr")
                                .font(.headline)
                            Text("Movie library management")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                Button(action: { onNavigateTo(.sonarr) }) {
                    HStack {
                        Image(systemName: "tv")
                            .foregroundColor(.purple)
                        VStack(alignment: .leading) {
                            Text("Sonarr")
                                .font(.headline)
                            Text("TV show library management")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
        }
        .navigationTitle("Services")
    }
}
```

#### 1.3 Add Home Button to Toolbars

**Create reusable toolbar modifier:**

```swift
extension View {
    func homeButton(action: @escaping () -> Void) -> some View {
        self.toolbar {
            ToolbarItem(placement: .navigation) {
                Button(action: action) {
                    Label("Home", systemImage: "house")
                }
                .help("Return to home screen")
            }
        }
    }
}

// Usage in RadarrHomeView:
.homeButton {
    coordinator.popToRoot()
}
```

#### 1.4 Update Coordinators

**AppCoordinator changes:**

```swift
func start() {
    navigationPath = []  // Start at app home
}

func showServices() {
    navigate(to: .services)
}

func showRadarr() {
    navigate(to: .radarr)
}
```

**RadarrCoordinator changes:**

```swift
func start() {
    navigationPath = []  // Start at Radarr home (not movies list)
}

func showHome() {
    popToRoot()
}

func showMovies() {
    navigate(to: .moviesList)
}

func showUpcoming() {
    navigate(to: .upcoming)
}
```

#### 1.5 Update Views

**Remove:**

- `fullScreenCover` presentation in `ServicesCoordinatorView.swift`
- Tab-based navigation in Radarr/Sonarr

**Update:**

- All coordinator views to use NavigationStack destinations
- Add home button to all deep views

### Phase 2: Update Tests (Week 1)

#### 2.1 Coordinator Tests

Update `CoordinatorTests.swift` to test new navigation:

```swift
@Test("Navigate from app home to Radarr")
@MainActor
func navigateToRadarr() {
    let coordinator = AppCoordinator(/* dependencies */)
    coordinator.start()

    #expect(coordinator.navigationPath.isEmpty)

    coordinator.showServices()
    #expect(coordinator.navigationPath.count == 1)
    #expect(coordinator.navigationPath.last == .services)

    coordinator.showRadarr()
    #expect(coordinator.navigationPath.count == 2)
    #expect(coordinator.navigationPath.last == .radarr)
}

@Test("Navigate within Radarr")
@MainActor
func navigateWithinRadarr() {
    let coordinator = RadarrCoordinator(/* dependencies */)
    coordinator.start()

    #expect(coordinator.navigationPath.isEmpty)

    coordinator.showMovies()
    #expect(coordinator.navigationPath.count == 1)
    #expect(coordinator.navigationPath.last == .moviesList)

    coordinator.showMovieDetail(movieId: 123)
    #expect(coordinator.navigationPath.count == 2)
}
```

#### 2.2 View Tests

Add UI tests for button navigation:

```swift
@Test("Services home displays all service buttons")
func servicesHomeButtons() throws {
    let view = ServicesHomeView(onNavigateTo: { _ in })

    // Test that buttons render correctly
    // (Use ViewInspector or manual inspection)
}
```

### Phase 3: Documentation Updates (Week 1)

#### 3.1 Update ADRs

- Update `0001-single-navigationstack-per-coordinator.md` to reflect hierarchical navigation
- Update `0010-coordinator-navigation-initialization.md` with new route patterns

#### 3.2 Update Architecture Docs

- Update `docs/architecture/README.md` with new navigation hierarchy
- Update `docs/architecture/NAVIGATION_QUICK_REFERENCE.md` with button navigation pattern
- Update `docs/CODING_CONVENTIONS.md` with navigation guidelines

#### 3.3 Update Migration Docs

- Update `docs/migration/design.md` to reflect hierarchical navigation decision
- Document differences from legacy tab-based service navigation

### Phase 4: User Testing & Refinement (Week 2)

- Test all navigation flows (5 levels deep)
- Verify back button works at all levels
- Test home button from all depths
- Verify keyboard navigation (macOS)
- Test VoiceOver navigation
- Gather feedback and iterate

## More Information

### Future Enhancements

For a future **macOS-specific optimization** after MVP:

- Use NavigationSplitView **only at app root level** (Dashboard, Services, Settings)
- Keep NavigationStack for all service-level navigation (Radarr, Sonarr)
- Conditionally enable sidebar on macOS/iPad only with `#if os(macOS)` directive

### Implementation Timeline

- **Week 1**: Remove tabs, add button navigation, update coordinators and routes
- **Week 1**: Update tests and documentation
- **Week 2**: User testing and refinement
- **Post-MVP**: Consider NavigationSplitView for macOS optimization

### Related Decisions

- [ADR-0001: Single NavigationStack Per Coordinator](0001-single-navigationstack-per-coordinator.md) - Foundation for this decision
- [ADR-0010: Coordinator Navigation Initialization](0010-coordinator-navigation-initialization.md) - Empty path initialization
- [ADR-0005: MVVM-C Pattern](0005-use-mvvm-c-pattern.md) - Coordinator pattern usage

### References

- [SwiftUI NavigationStack Documentation](https://developer.apple.com/documentation/swiftui/navigationstack)
- [Human Interface Guidelines - Navigation](https://developer.apple.com/design/human-interface-guidelines/navigation)
- [Hacking with Swift - NavigationStack Guide](https://www.hackingwithswift.com/articles/216/complete-guide-to-navigationstack)
- [Legacy Flutter App - Router Implementation](../../../legacy/lib/router/)
- [Reddit Discussion - NavigationStack vs Coordinator](https://www.reddit.com/r/swift/comments/1l1flmz/swiftui_navigation_coordinator_vs_navigationstack/)
