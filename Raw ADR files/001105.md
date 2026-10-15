# ADR-005: State Management Patterns (@StateObject vs @ObservedObject)

## Status
Accepted

## Context
SwiftUI provides multiple property wrappers for state management, and the ClariFi iOS app was using them inconsistently:

1. **Confusion**: Unclear when to use `@StateObject` vs `@ObservedObject` vs `@EnvironmentObject`
2. **Memory Issues**: Incorrect usage causing ViewModels to be recreated unnecessarily
3. **State Loss**: Views losing state during navigation or parent view updates
4. **Performance Problems**: Unnecessary view updates from improper state management
5. **Testing Challenges**: Difficult to test views with inconsistent state patterns

The app uses MVVM architecture with:
- ViewModels conforming to `ObservableObject`
- Views observing ViewModels for state changes
- Core Data for persistence
- `@AppStorage` for user preferences

## Decision
We will standardize state management patterns with clear rules:

### 1. @StateObject - View Owns the ViewModel
Use `@StateObject` when the view **creates and owns** the ViewModel:
- View is responsible for ViewModel lifecycle
- ViewModel created when view appears
- ViewModel destroyed when view disappears
- Survives view updates (body re-evaluation)

**Pattern:**
```swift
struct FeatureView: View {
    @StateObject private var viewModel: FeatureViewModel
    
    init(viewModel: FeatureViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }
}
```

### 2. @ObservedObject - View Receives the ViewModel
Use `@ObservedObject` when the view **receives** the ViewModel from parent:
- Parent owns the ViewModel lifecycle
- ViewModel shared across multiple views
- ViewModel may be recreated by parent
- View just observes, doesn't own

**Pattern:**
```swift
struct ChildView: View {
    @ObservedObject var viewModel: ParentViewModel
    
    init(viewModel: ParentViewModel) {
        self.viewModel = viewModel
    }
}
```

### 3. @EnvironmentObject - App-Wide Shared State
Use `@EnvironmentObject` for app-wide shared state:
- Authentication state
- User preferences
- Theme settings
- App configuration

**Pattern:**
```swift
struct FeatureView: View {
    @EnvironmentObject var authState: AuthenticationState
    
    var body: some View {
        // Use authState
    }
}
```

### 4. @AppStorage - Simple Preferences
Use `@AppStorage` for simple user preferences:
- Boolean flags
- String values
- Integer values
- No complex objects

**Pattern:**
```swift
struct SettingsView: View {
    @AppStorage("isDarkMode") private var isDarkMode = false
    @AppStorage("notificationsEnabled") private var notificationsEnabled = true
}
```

### 5. @State - View-Local State
Use `@State` for simple view-local state:
- UI state (sheet presentation, selection)
- Temporary values
- No business logic

**Pattern:**
```swift
struct FeatureView: View {
    @State private var isShowingSheet = false
    @State private var selectedItem: Item?
}
```

## Consequences

### Positive
1. **Predictable Behavior**: Clear rules prevent state management bugs
2. **Better Performance**: Correct usage prevents unnecessary view updates
3. **Memory Efficiency**: ViewModels lifecycle managed correctly
4. **Easier Debugging**: Consistent patterns make issues easier to trace
5. **Improved Testing**: Clear ownership makes testing straightforward
6. **Team Alignment**: Everyone follows same patterns

### Negative
1. **Learning Curve**: Team needs to understand property wrapper differences
2. **Boilerplate**: `@StateObject` initialization requires custom init
3. **Migration Effort**: Existing views need auditing and updating

### Neutral
1. **SwiftUI Limitation**: Property wrapper initialization constraints
2. **Documentation Needed**: Patterns must be documented for team

## Implementation Details

### Pattern 1: View Creates ViewModel (Most Common)
```swift
struct BudgetView: View {
    @Environment(\.diContainer) private var container
    @StateObject private var viewModel: BudgetViewModel
    
    init() {
        // Resolve from DI container
        let container = AppDIContainer.createProductionContainer()
        let vm = container.resolve(BudgetViewModel.self)
        _viewModel = StateObject(wrappedValue: vm)
    }
    
    var body: some View {
        content
            .errorAlert(error: $viewModel.error)
    }
}
```

### Pattern 2: Parent Passes ViewModel to Child
```swift
struct ParentView: View {
    @StateObject private var viewModel = ParentViewModel()
    
    var body: some View {
        VStack {
            ChildView(viewModel: viewModel)
            AnotherChildView(viewModel: viewModel)
        }
    }
}

struct ChildView: View {
    @ObservedObject var viewModel: ParentViewModel
    
    var body: some View {
        Text(viewModel.sharedData)
    }
}
```

### Pattern 3: Environment Object for App State
```swift
@main
struct ClariFiApp: App {
    @StateObject private var authState = AuthenticationState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authState)
        }
    }
}

struct FeatureView: View {
    @EnvironmentObject var authState: AuthenticationState
    
    var body: some View {
        if authState.isAuthenticated {
            AuthenticatedContent()
        } else {
            LoginView()
        }
    }
}
```

### Pattern 4: Simple Preferences
```swift
struct SettingsView: View {
    @AppStorage("isDarkMode") private var isDarkMode = false
    @AppStorage("notificationsEnabled") private var notificationsEnabled = true
    @AppStorage("defaultCurrency") private var defaultCurrency = "USD"
    
    var body: some View {
        Form {
            Toggle("Dark Mode", isOn: $isDarkMode)
            Toggle("Notifications", isOn: $notificationsEnabled)
            Picker("Currency", selection: $defaultCurrency) {
                Text("USD").tag("USD")
                Text("EUR").tag("EUR")
                Text("GBP").tag("GBP")
            }
        }
    }
}
```

### Pattern 5: View-Local State
```swift
struct TransactionListView: View {
    @StateObject private var viewModel: TransactionViewModel
    @State private var isShowingFilter = false
    @State private var selectedTransaction: Transaction?
    @State private var searchText = ""
    
    var body: some View {
        List {
            ForEach(filteredTransactions) { transaction in
                TransactionRow(transaction: transaction)
                    .onTapGesture {
                        selectedTransaction = transaction
                    }
            }
        }
        .searchable(text: $searchText)
        .sheet(isPresented: $isShowingFilter) {
            FilterView()
        }
        .sheet(item: $selectedTransaction) { transaction in
            TransactionDetailView(transaction: transaction)
        }
    }
    
    private var filteredTransactions: [Transaction] {
        viewModel.transactions.filter { transaction in
            searchText.isEmpty || transaction.merchant?.contains(searchText) == true
        }
    }
}
```

## Decision Matrix

| Scenario | Property Wrapper | Reason |
|----------|-----------------|--------|
| View creates and owns ViewModel | `@StateObject` | View controls lifecycle |
| Parent passes ViewModel to child | `@ObservedObject` | Parent owns lifecycle |
| App-wide shared state | `@EnvironmentObject` | Shared across view hierarchy |
| Simple user preference | `@AppStorage` | Persisted, simple value |
| UI state (sheet, selection) | `@State` | View-local, temporary |
| Computed value from state | `var` (computed) | Derived from other state |
| Constant value | `let` | Never changes |

## Common Pitfalls and Solutions

### Pitfall 1: Using @ObservedObject When View Owns ViewModel
**Problem:**
```swift
struct BudgetView: View {
    @ObservedObject var viewModel = BudgetViewModel() // ❌ Wrong!
    // ViewModel recreated on every view update
}
```

**Solution:**
```swift
struct BudgetView: View {
    @StateObject private var viewModel: BudgetViewModel // ✅ Correct
    
    init(viewModel: BudgetViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }
}
```

### Pitfall 2: Using @StateObject for Passed ViewModels
**Problem:**
```swift
struct ChildView: View {
    @StateObject var viewModel: ParentViewModel // ❌ Wrong!
    // Creates new instance instead of using parent's
}
```

**Solution:**
```swift
struct ChildView: View {
    @ObservedObject var viewModel: ParentViewModel // ✅ Correct
}
```

### Pitfall 3: Storing Complex Objects in @AppStorage
**Problem:**
```swift
@AppStorage("user") var user: User // ❌ Won't compile
// @AppStorage only supports simple types
```

**Solution:**
```swift
// Use Core Data or ViewModel for complex objects
@StateObject private var userViewModel: UserViewModel // ✅ Correct
```

### Pitfall 4: Not Using private for @State and @StateObject
**Problem:**
```swift
struct FeatureView: View {
    @State var isShowing = false // ❌ Should be private
    @StateObject var viewModel: ViewModel // ❌ Should be private
}
```

**Solution:**
```swift
struct FeatureView: View {
    @State private var isShowing = false // ✅ Correct
    @StateObject private var viewModel: ViewModel // ✅ Correct
}
```

## Testing Implications

### Testing Views with @StateObject
```swift
class BudgetViewTests: XCTestCase {
    func testBudgetView() {
        // Create test ViewModel
        let mockRepository = MockBudgetRepository()
        let viewModel = BudgetViewModel(budgetRepository: mockRepository)
        
        // Create view with test ViewModel
        let view = BudgetView(viewModel: viewModel)
        
        // Test view behavior
        // ViewHosting or snapshot testing
    }
}
```

### Testing ViewModels Independently
```swift
class BudgetViewModelTests: XCTestCase {
    func testLoadBudgets() async {
        // Arrange
        let mockRepository = MockBudgetRepository()
        mockRepository.mockData = [/* test data */]
        let viewModel = BudgetViewModel(budgetRepository: mockRepository)
        
        // Act
        await viewModel.loadBudgets()
        
        // Assert
        XCTAssertEqual(viewModel.budgets.count, 1)
    }
}
```

## Documentation and Code Comments

All views should include comments explaining state management:

```swift
struct BudgetView: View {
    // MARK: - State Management
    
    /// ViewModel owned by this view, manages budget data and business logic
    @StateObject private var viewModel: BudgetViewModel
    
    /// UI state for filter sheet presentation
    @State private var isShowingFilter = false
    
    /// Currently selected budget for detail view
    @State private var selectedBudget: Budget?
    
    // MARK: - Initialization
    
    init(viewModel: BudgetViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }
    
    // MARK: - Body
    
    var body: some View {
        // View implementation
    }
}
```

## Alternatives Considered

### 1. Always Use @StateObject
**Rejected**: Inefficient for passed ViewModels. Creates unnecessary instances.

### 2. Always Use @ObservedObject
**Rejected**: ViewModels would be recreated on parent updates, losing state.

### 3. Use Combine Publishers Directly
**Rejected**: SwiftUI property wrappers are more idiomatic and easier to use.

### 4. Custom Property Wrapper
**Rejected**: SwiftUI's built-in wrappers cover all use cases. Custom wrapper adds complexity.

### 5. Redux-Style State Management
**Rejected**: Overkill for this app. SwiftUI's built-in state management is sufficient.

## Migration Checklist

### Phase 1: Audit (Completed)
- [x] Identify all views using state management
- [x] Document current usage patterns
- [x] Identify incorrect usage

### Phase 2: Update Views (Completed)
- [x] Update views to use @StateObject for owned ViewModels
- [x] Update views to use @ObservedObject for passed ViewModels
- [x] Add private access control
- [x] Add documentation comments

### Phase 3: Testing (Completed)
- [x] Verify views maintain state correctly
- [x] Test navigation flows
- [x] Test parent-child view relationships

### Phase 4: Documentation (Completed)
- [x] Document patterns in ARCHITECTURE.md
- [x] Create this ADR
- [x] Add code comments to examples

## References
- Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
- Related ADRs: ADR-001 (DI Container), ADR-004 (Error Handling)
- Design Document: Section "State Management Standardization"
- Apple Documentation: [Managing Model Data in Your App](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app)

## Date
2025-10-12

## Authors
ClariFi iOS Team
