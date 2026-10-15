# ADR-002: Repository Pattern Standardization and RepositoryFactory Removal

## Status
Accepted

## Context
The ClariFi iOS app uses the Repository Pattern to abstract Core Data access, which is a good architectural decision. However, the implementation had significant issues:

1. **Singleton Factory**: `RepositoryFactory.shared` was used throughout the codebase (39+ references)
2. **Hidden Dependencies**: Components accessed repositories via the singleton, hiding dependencies
3. **Testing Challenges**: Difficult to inject mock repositories for testing
4. **Tight Coupling**: Direct dependency on `RepositoryFactory` singleton
5. **Inconsistent Access**: Mix of factory access and direct instantiation

The repository implementations themselves were well-designed with:
- Clear protocol definitions (`TransactionRepository`, `AccountRepository`, etc.)
- Proper Core Data encapsulation
- Async/await support
- Error handling with `RepositoryError`

The problem was the delivery mechanism (singleton factory), not the pattern itself.

## Decision
We will standardize the Repository Pattern by:

1. **Remove RepositoryFactory Singleton**: Eliminate `RepositoryFactory.shared`
2. **DI Container Registration**: Register all repositories in the DI container as singletons
3. **Constructor Injection**: Inject repositories through constructors, making dependencies explicit
4. **Protocol-Based Design**: Maintain existing protocol-based design (no changes needed)
5. **Lifecycle Management**: Repositories managed as singletons by DI container

### Repository Lifecycle
All repositories will be registered as **singletons** because:
- They wrap Core Data context (expensive to create)
- They maintain no mutable state (thread-safe)
- Single instance per context is sufficient
- Reduces memory overhead

### Migration Approach
1. Keep all existing repository protocols and implementations unchanged
2. Register repositories in `AppDIContainer+Registration.swift`
3. Update all 39+ references to use injected dependencies
4. Mark `RepositoryFactory.shared` as deprecated
5. Remove singleton after all references migrated

## Consequences

### Positive
1. **Explicit Dependencies**: ViewModels and services clearly declare repository dependencies
2. **Improved Testability**: Easy to inject mock repositories for unit testing
3. **Reduced Coupling**: No direct dependency on singleton factory
4. **Consistent Pattern**: All dependencies managed through DI container
5. **Better Code Navigation**: IDE can trace dependency flow through constructors
6. **Cleaner Architecture**: Separation of concerns between creation and usage

### Negative
1. **Migration Effort**: 39+ references need updating across Views, ViewModels, Services, and Tests
2. **Constructor Complexity**: Some constructors have more parameters (mitigated by clear naming)
3. **Breaking Change**: Existing code must be updated (managed through deprecation warnings)

### Neutral
1. **No Performance Impact**: Singleton lifecycle maintained, just different management
2. **Same Abstractions**: Repository protocols remain unchanged

## Implementation Details

### Repository Registration
```swift
// In AppDIContainer+Registration.swift
container.registerSingleton(TransactionRepository.self) { _ in
    CoreDataTransactionRepository(context: context)
}
container.registerSingleton(AccountRepository.self) { _ in
    CoreDataAccountRepository(context: context)
}
container.registerSingleton(BudgetRepository.self) { _ in
    CoreDataBudgetRepository(context: context)
}
// ... other repositories
```

### ViewModel Pattern (Before)
```swift
class BudgetViewModel: ObservableObject {
    private let budgetRepository: BudgetRepository
    
    init(budgetRepository: BudgetRepository = RepositoryFactory.shared.budgetRepository) {
        self.budgetRepository = budgetRepository
    }
}
```

### ViewModel Pattern (After)
```swift
class BudgetViewModel: BaseViewModel {
    private let budgetRepository: BudgetRepository
    
    init(budgetRepository: BudgetRepository) {
        self.budgetRepository = budgetRepository
        super.init()
    }
}
```

### View Usage (After)
```swift
struct BudgetView: View {
    @Environment(\.diContainer) private var container
    @StateObject private var viewModel: BudgetViewModel
    
    init() {
        let container = AppDIContainer.createProductionContainer()
        _viewModel = StateObject(wrappedValue: container.resolve(BudgetViewModel.self))
    }
}
```

### Test Usage
```swift
class BudgetViewModelTests: XCTestCase {
    func testBudgetLoading() async {
        // Arrange
        let mockRepository = MockBudgetRepository()
        let viewModel = BudgetViewModel(budgetRepository: mockRepository)
        
        // Act & Assert
        await viewModel.loadBudgets()
        XCTAssertEqual(viewModel.budgets.count, mockRepository.mockData.count)
    }
}
```

## Alternatives Considered

### 1. Keep RepositoryFactory with DI
**Rejected**: Would maintain unnecessary abstraction layer. Direct registration in DI container is simpler.

### 2. Service Locator Pattern
**Rejected**: Service locator hides dependencies like singletons do. Constructor injection is more explicit.

### 3. Factory Pattern per Repository
**Rejected**: Adds complexity without benefits. DI container already provides factory functionality.

### 4. Protocol Extensions for Default Implementations
**Rejected**: Would still hide dependencies. Explicit injection is clearer.

## Migration Checklist

### Phase 1: Setup (Completed)
- [x] Register all repositories in DI container
- [x] Create test container with mock repositories
- [x] Verify container can resolve all repositories

### Phase 2: ViewModels (Completed)
- [x] Update BudgetViewModel
- [x] Update InsightsViewModel
- [x] Update StatementUploadViewModel
- [x] Update TransactionEntryViewModel
- [x] Update BudgetCreationViewModel
- [x] Update BatchCategorizationViewModel

### Phase 3: Views (Completed)
- [x] Update MainTabView
- [x] Update DashboardView
- [x] Update TransactionsListView
- [x] Remove all RepositoryFactory.shared from Views

### Phase 4: Tests (Completed)
- [x] Update IntegrationTests.swift
- [x] Update UIIntegrationTests.swift
- [x] Update all unit tests
- [x] Remove RepositoryFactory.shared from tests

### Phase 5: Cleanup (Completed)
- [x] Mark RepositoryFactory.shared as deprecated
- [x] Verify zero references to deprecated singleton
- [x] Remove RepositoryFactory.shared property
- [x] Update RepositoryFactory to be instantiated via DI only

## References
- Requirements: 3.1, 3.3, 3.4, 3.6
- Related ADRs: ADR-001 (DI Container), ADR-003 (Service Layer)
- Design Document: Section "Repository Layer Standardization"
- Audit Document: `REPOSITORY_FACTORY_AUDIT.md`

## Date
2025-10-12

## Authors
ClariFi iOS Team
