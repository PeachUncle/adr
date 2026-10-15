# ADR-004: Error Handling Strategy with BaseViewModel and AppError

## Status
Accepted

## Context
The ClariFi iOS app had inconsistent error handling across the codebase:

1. **Fragmented Error Types**: Mix of `Error`, `NSError`, custom errors, and `AppError`
2. **Inconsistent Handling**: Each ViewModel handled errors differently
3. **Duplicate Code**: Error handling logic repeated across ViewModels
4. **Poor User Experience**: Inconsistent error presentation to users
5. **Missing Context**: Errors lacked contextual information for debugging
6. **No Centralized Logging**: Error tracking scattered across components

The app already had a well-designed `AppError` enum with:
- Categorized error cases (storage, network, validation, etc.)
- `LocalizedError` conformance for user-facing messages
- Recovery suggestions for some errors

The problem was inconsistent usage and lack of standardized patterns.

## Decision
We will implement a centralized error handling strategy with:

1. **BaseViewModel**: Common base class for all ViewModels with standardized error handling
2. **AppError Standardization**: Use `AppError` enum consistently across all layers
3. **Error Mapping**: Map lower-level errors to `AppError` cases
4. **Centralized Presentation**: SwiftUI modifier for consistent error display
5. **Context Enrichment**: Add contextual information to all errors
6. **Analytics Integration**: Automatically track errors for monitoring

### BaseViewModel Pattern
```swift
@MainActor
class BaseViewModel: ObservableObject {
    @Published var error: AppError?
    @Published var isLoading: Bool = false
    
    func handleError(_ error: Error, context: [String: Any] = [:]) {
        if let appError = error as? AppError {
            self.error = appError
        } else {
            self.error = .unknownError
        }
        Analytics.captureException(error, context: context)
    }
}
```

### Error Presentation Modifier
```swift
extension View {
    func errorAlert(error: Binding<AppError?>) -> some View {
        alert(
            "Error",
            isPresented: Binding(
                get: { error.wrappedValue != nil },
                set: { if !$0 { error.wrappedValue = nil } }
            ),
            presenting: error.wrappedValue
        ) { _ in
            Button("OK") { error.wrappedValue = nil }
        } message: { appError in
            Text(appError.errorDescription ?? "An error occurred")
        }
    }
}
```

## Consequences

### Positive
1. **Consistency**: All ViewModels handle errors the same way
2. **Reduced Duplication**: Error handling logic in one place (BaseViewModel)
3. **Better UX**: Consistent error presentation across the app
4. **Improved Debugging**: Contextual information captured with errors
5. **Automatic Tracking**: All errors automatically logged to analytics
6. **Type Safety**: `AppError` enum provides compile-time safety
7. **Maintainability**: Changes to error handling in one place
8. **Clear Contracts**: ViewModels expose `error` property consistently

### Negative
1. **Inheritance Required**: ViewModels must inherit from BaseViewModel
2. **Limited Flexibility**: Some ViewModels may need custom error handling
3. **Error Mapping Overhead**: Lower-level errors need mapping to AppError

### Neutral
1. **Learning Curve**: Team needs to understand BaseViewModel pattern
2. **Migration Effort**: Existing ViewModels need updating

## Implementation Details

### AppError Enum (Existing)
```swift
enum AppError: LocalizedError {
    case storageError(underlying: Error)
    case networkError(underlying: Error)
    case validationError(message: String)
    case authenticationError
    case permissionDenied
    case dataCorruption
    case unknownError
    
    var errorDescription: String? {
        switch self {
        case .storageError:
            return "Failed to save or retrieve data"
        case .networkError:
            return "Network connection failed"
        case .validationError(let message):
            return message
        case .authenticationError:
            return "Authentication failed"
        case .permissionDenied:
            return "Permission denied"
        case .dataCorruption:
            return "Data corruption detected"
        case .unknownError:
            return "An unexpected error occurred"
        }
    }
    
    var recoverySuggestion: String? {
        switch self {
        case .storageError:
            return "Please try again or restart the app"
        case .networkError:
            return "Check your internet connection and try again"
        case .validationError:
            return "Please check your input and try again"
        case .authenticationError:
            return "Please sign in again"
        case .permissionDenied:
            return "Please grant the required permissions in Settings"
        case .dataCorruption:
            return "Please contact support"
        case .unknownError:
            return "Please try again or contact support"
        }
    }
}
```

### Error Mapping Extension
```swift
extension AppError {
    static func from(_ error: Error, context: String = "") -> AppError {
        if let appError = error as? AppError {
            return appError
        }
        
        if let repoError = error as? RepositoryError {
            return .storageError(underlying: repoError)
        }
        
        if let urlError = error as? URLError {
            return .networkError(underlying: urlError)
        }
        
        return .unknownError
    }
}
```

### ViewModel Implementation Pattern
```swift
@MainActor
class BudgetViewModel: BaseViewModel {
    @Published var budgets: [Budget] = []
    
    private let budgetRepository: BudgetRepository
    
    init(budgetRepository: BudgetRepository) {
        self.budgetRepository = budgetRepository
        super.init()
    }
    
    func loadBudgets() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            budgets = try await budgetRepository.fetchAll()
        } catch {
            handleError(error, context: [
                "component": "budget_view_model",
                "operation": "load_budgets"
            ])
        }
    }
    
    func createBudget(_ budget: Budget) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            try await budgetRepository.save(budget)
            await loadBudgets() // Refresh
        } catch {
            handleError(error, context: [
                "component": "budget_view_model",
                "operation": "create_budget",
                "budget_name": budget.name ?? "unknown"
            ])
        }
    }
}
```

### View Implementation Pattern
```swift
struct BudgetView: View {
    @StateObject private var viewModel: BudgetViewModel
    
    init(viewModel: BudgetViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }
    
    var body: some View {
        NavigationView {
            content
                .errorAlert(error: $viewModel.error)
                .overlay {
                    if viewModel.isLoading {
                        ProgressView()
                    }
                }
        }
        .task {
            await viewModel.loadBudgets()
        }
    }
    
    private var content: some View {
        List(viewModel.budgets) { budget in
            BudgetRow(budget: budget)
        }
    }
}
```

## Error Handling Principles

### 1. Fail Fast
Errors should be caught and handled as close to the source as possible:
- Repository errors caught in ViewModels
- Service errors caught in ViewModels
- Validation errors caught before operations

### 2. User-Friendly Messages
All errors should have clear, actionable messages:
- Avoid technical jargon
- Provide recovery suggestions
- Guide users to resolution

### 3. Context Enrichment
All errors should include contextual information:
- Component name
- Operation being performed
- Relevant data (sanitized)
- User state

### 4. Automatic Tracking
All errors should be automatically tracked:
- Sent to analytics service
- Include full context
- Enable monitoring and alerting

### 5. Graceful Degradation
App should continue functioning when possible:
- Non-critical errors don't crash app
- Fallback behaviors when appropriate
- Clear indication of degraded state

## Testing Strategy

### Unit Testing Error Handling
```swift
class BudgetViewModelTests: XCTestCase {
    func testErrorHandling() async {
        // Arrange
        let mockRepository = MockBudgetRepository()
        mockRepository.shouldThrowError = true
        let viewModel = BudgetViewModel(budgetRepository: mockRepository)
        
        // Act
        await viewModel.loadBudgets()
        
        // Assert
        XCTAssertNotNil(viewModel.error)
        XCTAssertTrue(viewModel.error is AppError)
        XCTAssertFalse(viewModel.isLoading)
    }
    
    func testErrorClearing() async {
        // Arrange
        let viewModel = BudgetViewModel(budgetRepository: MockBudgetRepository())
        viewModel.error = .unknownError
        
        // Act
        viewModel.error = nil
        
        // Assert
        XCTAssertNil(viewModel.error)
    }
}
```

### Integration Testing Error Flows
```swift
class ErrorHandlingIntegrationTests: XCTestCase {
    func testEndToEndErrorFlow() async {
        // Test that errors propagate correctly through layers
        // Repository -> ViewModel -> View
    }
}
```

## Alternatives Considered

### 1. Result Type Instead of Throwing
**Rejected**: Swift's async/await with throwing is more idiomatic. Result type adds verbosity.

### 2. Error Callbacks
**Rejected**: Callbacks are less composable than async/await. Modern Swift favors structured concurrency.

### 3. Global Error Handler
**Rejected**: Would hide error handling logic. Explicit handling in ViewModels is clearer.

### 4. Custom Error Protocol
**Rejected**: `LocalizedError` protocol already provides what we need. No need for custom protocol.

### 5. No BaseViewModel (Composition)
**Considered**: Could use protocol with default implementation. Inheritance is simpler for this use case.

## Migration Checklist

### Phase 1: Infrastructure (Completed)
- [x] Create BaseViewModel with error handling
- [x] Create error presentation modifier
- [x] Create error mapping utilities

### Phase 2: ViewModel Migration (Completed)
- [x] Update BudgetViewModel to inherit from BaseViewModel
- [x] Update InsightsViewModel to inherit from BaseViewModel
- [x] Update StatementUploadViewModel to inherit from BaseViewModel
- [x] Update TransactionEntryViewModel to inherit from BaseViewModel
- [x] Update BudgetCreationViewModel to inherit from BaseViewModel
- [x] Update BatchCategorizationViewModel to inherit from BaseViewModel

### Phase 3: View Migration (Completed)
- [x] Update BudgetView to use errorAlert modifier
- [x] Update InsightsView to use errorAlert modifier
- [x] Update StatementUploadView to use errorAlert modifier
- [x] Update TransactionEntryView to use errorAlert modifier
- [x] Update DashboardView to use errorAlert modifier

### Phase 4: Testing (Completed)
- [x] Add error handling tests for ViewModels
- [x] Test error presentation in Views
- [x] Verify analytics tracking

## References
- Requirements: 5.1, 5.2, 5.3, 5.4, 5.6
- Related ADRs: ADR-001 (DI Container), ADR-005 (State Management)
- Design Document: Section "Error Handling Strategy"
- Implementation: `Presentation/ViewModels/Base/BaseViewModel.swift`

## Date
2025-10-12

## Authors
ClariFi iOS Team
