# ADR-003: Service Layer Architecture with Protocol-Based Design

## Status
Accepted

## Context
The ClariFi iOS app has a growing service layer that handles business logic, analytics, OCR processing, insights generation, and more. However, the service layer had several architectural issues:

1. **Inconsistent Patterns**: Mix of singletons, direct instantiation, and ad-hoc creation
2. **Hidden Dependencies**: Services created with `ServiceName.shared` hiding dependencies
3. **Poor Testability**: Difficult to inject mock services for testing
4. **Tight Coupling**: Direct dependencies on concrete service implementations
5. **No Clear Boundaries**: Services directly accessing other services via singletons
6. **Lifecycle Confusion**: Unclear when services should be singleton vs transient

The service layer includes:
- **Analytics Services**: PostHogAnalyticsService
- **Business Logic Services**: BudgetMonitoringService, InsightsEngine
- **Processing Services**: OCRService, TransactionParserService, SmartTransactionParser
- **Domain Services**: CategoryService, RuleEngine, BudgetTemplateService
- **Security Services**: BiometricAuthService, EncryptionService

## Decision
We will standardize the service layer architecture with:

1. **Protocol-Based Design**: All services define clear protocol interfaces
2. **DI Container Management**: All services registered and resolved through DI container
3. **Constructor Injection**: Services receive dependencies through constructors
4. **Clear Lifecycle Management**: Explicit singleton vs transient registration
5. **Layer Separation**: Services depend on repositories via protocols, not concrete implementations

### Service Categories and Lifecycles

**Singleton Services** (created once, reused):
- Analytics services (maintain state, expensive initialization)
- OCR services (expensive ML model loading)
- Insights engine (complex state, expensive initialization)
- Budget monitoring (maintains state)
- Template services (static data, expensive to load)

**Transient Services** (created each time):
- Currently none, but pattern supports future stateless services

### Protocol Design Pattern
```swift
protocol ServiceNameProtocol {
    // Service interface
    func performOperation() async throws -> Result
}

class ConcreteService: ServiceNameProtocol {
    private let dependency1: Dependency1Protocol
    private let dependency2: Dependency2Protocol
    
    init(dependency1: Dependency1Protocol, dependency2: Dependency2Protocol) {
        self.dependency1 = dependency1
        self.dependency2 = dependency2
    }
    
    func performOperation() async throws -> Result {
        // Implementation
    }
}
```

## Consequences

### Positive
1. **Explicit Dependencies**: Service constructors clearly show all dependencies
2. **Improved Testability**: Easy to inject mock services for testing
3. **Reduced Coupling**: Services depend on protocols, enabling flexibility
4. **Clear Boundaries**: Protocol interfaces define clear contracts
5. **Better Composition**: Services can be composed without tight coupling
6. **Consistent Patterns**: All services follow same architectural pattern
7. **Easier Refactoring**: Protocol boundaries make refactoring safer

### Negative
1. **More Boilerplate**: Each service needs protocol definition
2. **Migration Effort**: Existing singleton services need refactoring
3. **Protocol Proliferation**: More protocols to maintain
4. **Indirection**: Extra layer between caller and implementation

### Neutral
1. **Performance**: Minimal impact from protocol dispatch (Swift optimizes)
2. **Code Volume**: More files but better organization

## Implementation Details

### Service Registration
```swift
// In AppDIContainer+Registration.swift

// Analytics
container.registerSingleton(AnalyticsServiceProtocol.self) { _ in
    PostHogAnalyticsService.shared
}

// OCR and Parsing
container.registerSingleton(OCRService.self) { _ in
    VisionOCRService()
}
container.registerSingleton(TransactionParserService.self) { _ in
    SmartTransactionParser()
}

// Business Logic
container.registerSingleton(InsightsEngineProtocol.self) { _ in
    InsightsEngine(context: context)
}
container.registerSingleton(BudgetMonitoringService.self) { c in
    BudgetMonitoringService(
        budgetRepository: c.resolve(BudgetRepository.self),
        budgetCategoryRepository: c.resolve(BudgetCategoryRepository.self),
        transactionRepository: c.resolve(TransactionRepository.self),
        context: context
    )
}

// Domain Services
container.registerSingleton(CategoryService.self) { _ in
    CategoryService(context: context)
}
container.registerSingleton(RuleEngine.self) { _ in
    RuleEngine(context: context)
}
container.registerSingleton(BudgetTemplateService.self) { _ in
    BudgetTemplateService.shared
}
```

### Service Protocol Example
```swift
// Analytics Service Protocol
protocol AnalyticsServiceProtocol {
    var isEnabled: Bool { get set }
    func track(event: AnalyticsEvent, properties: [String: Any]?)
    func identify(userId: String, properties: [String: Any]?)
    func captureException(_ error: Error, context: [String: Any]?)
}

// Concrete Implementation
class PostHogAnalyticsService: AnalyticsServiceProtocol {
    var isEnabled: Bool = true
    
    func track(event: AnalyticsEvent, properties: [String: Any]?) {
        // PostHog implementation
    }
    
    func identify(userId: String, properties: [String: Any]?) {
        // PostHog implementation
    }
    
    func captureException(_ error: Error, context: [String: Any]?) {
        // PostHog implementation
    }
}
```

### ViewModel Usage
```swift
@MainActor
class InsightsViewModel: BaseViewModel {
    private let insightsEngine: InsightsEngineProtocol
    private let transactionRepository: TransactionRepository
    
    init(
        insightsEngine: InsightsEngineProtocol,
        transactionRepository: TransactionRepository,
        budgetRepository: BudgetRepository,
        context: NSManagedObjectContext
    ) {
        self.insightsEngine = insightsEngine
        self.transactionRepository = transactionRepository
        super.init()
    }
    
    func generateInsights() async {
        do {
            let insights = try await insightsEngine.generateInsights()
            // Process insights
        } catch {
            handleError(error, context: ["component": "insights_view_model"])
        }
    }
}
```

### Testing with Mocks
```swift
class MockInsightsEngine: InsightsEngineProtocol {
    var mockInsights: [Insight] = []
    var generateInsightsCallCount = 0
    
    func generateInsights() async throws -> [Insight] {
        generateInsightsCallCount += 1
        return mockInsights
    }
}

class InsightsViewModelTests: XCTestCase {
    func testInsightsGeneration() async {
        // Arrange
        let mockEngine = MockInsightsEngine()
        mockEngine.mockInsights = [/* test data */]
        let viewModel = InsightsViewModel(
            insightsEngine: mockEngine,
            transactionRepository: MockTransactionRepository(),
            budgetRepository: MockBudgetRepository(),
            context: PersistenceController.preview.container.viewContext
        )
        
        // Act
        await viewModel.generateInsights()
        
        // Assert
        XCTAssertEqual(mockEngine.generateInsightsCallCount, 1)
    }
}
```

## Service Layer Principles

### 1. Single Responsibility
Each service has one clear responsibility:
- `AnalyticsService`: Track events and user behavior
- `InsightsEngine`: Generate financial insights
- `BudgetMonitoringService`: Monitor budget status and alerts
- `OCRService`: Extract text from images
- `TransactionParserService`: Parse transaction data

### 2. Dependency Inversion
Services depend on abstractions (protocols), not concrete implementations:
- `BudgetMonitoringService` depends on `BudgetRepository` protocol
- `InsightsViewModel` depends on `InsightsEngineProtocol`
- Enables testing with mocks and future implementation changes

### 3. Interface Segregation
Protocols are focused and minimal:
- Clients only depend on methods they use
- Protocols can be composed for complex needs
- Easier to mock for testing

### 4. Open/Closed Principle
Services are open for extension, closed for modification:
- New implementations can be added via protocols
- Existing code doesn't need changes
- DI container handles wiring

## Alternatives Considered

### 1. Keep Singleton Pattern
**Rejected**: Maintains tight coupling and poor testability. Same issues as repository layer.

### 2. Concrete Classes Without Protocols
**Rejected**: Makes testing harder and increases coupling. Protocol boundaries provide flexibility.

### 3. Service Locator Pattern
**Rejected**: Hides dependencies like singletons. Constructor injection is more explicit.

### 4. Functional Approach (Pure Functions)
**Rejected**: Some services need state (analytics, caching). OOP with protocols is more natural for iOS.

### 5. Separate Protocol and Implementation Files
**Considered**: Could improve organization but adds file overhead. Current approach keeps related code together.

## Migration Strategy

### Phase 1: Protocol Definition (Completed)
- [x] Create `AnalyticsServiceProtocol`
- [x] Create `InsightsEngineProtocol`
- [x] Ensure other service protocols exist

### Phase 2: DI Registration (Completed)
- [x] Register analytics service
- [x] Register OCR and parsing services
- [x] Register business logic services
- [x] Register domain services

### Phase 3: ViewModel Migration (Completed)
- [x] Update ViewModels to receive services via constructor
- [x] Remove direct service instantiation
- [x] Remove singleton access

### Phase 4: Testing (Completed)
- [x] Create mock service implementations
- [x] Update tests to use DI container
- [x] Verify all service tests pass

## References
- Requirements: 2.1, 2.2, 2.3, 2.4, 2.6
- Related ADRs: ADR-001 (DI Container), ADR-002 (Repository Pattern)
- Design Document: Section "Service Layer Architecture"

## Date
2025-10-12

## Authors
ClariFi iOS Team
