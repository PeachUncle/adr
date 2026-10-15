# ADR-001: MVVM Architecture with Clean Architecture Principles

**Date:** 2025-12-25  
**Status:** ACCEPTED  
**Deciders:** Development Team  
**Affected Components:** All  

## Context

The NoghreSod Android application needs a robust, testable, and maintainable architecture that:
1. Separates concerns clearly
2. Makes testing easy
3. Scales with team growth
4. Follows Android best practices
5. Supports offline-first functionality

## Decision

We have decided to use **MVVM (Model-View-ViewModel)** architecture with **Clean Architecture** principles:

```
┌─────────────────────────────────────────────────────┐
│ Presentation Layer (UI)                             │
│ ├─ Jetpack Compose (Declarative UI)                │
│ ├─ ViewModels (State Management)                   │
│ └─ Screens/Composables                             │
├─────────────────────────────────────────────────────┤
│ Domain Layer (Business Logic)                       │
│ ├─ UseCases                                         │
│ ├─ Repository Interfaces                           │
│ └─ Entities                                         │
├─────────────────────────────────────────────────────┤
│ Data Layer (Data Source)                            │
│ ├─ Repository Implementations                      │
│ ├─ Remote (Retrofit + REST API)                    │
│ ├─ Local (Room Database)                           │
│ └─ Mappers (Domain ↔ Data)                         │
└─────────────────────────────────────────────────────┘
```

## Technology Stack

### Presentation Layer
- **Jetpack Compose:** Declarative UI framework
- **ViewModel:** State management and lifecycle-aware
- **LiveData/StateFlow:** Reactive data binding
- **Hilt:** Dependency injection

### Domain Layer
- **Use Cases:** Business logic encapsulation
- **Entities:** Pure domain models (independent of framework)
- **Repository Interfaces:** Abstraction layer

### Data Layer
- **Retrofit:** HTTP client for REST API
- **Room:** Local database for offline support
- **DataStore/SharedPreferences:** Key-value storage
- **OkHttp:** HTTP interceptors for auth/logging

### Supporting Libraries
- **Coroutines:** Async operations
- **Arrow:** Functional programming (Result type)
- **Timber:** Logging
- **Coil/Glide:** Image loading

## Rationale

1. **Separation of Concerns:** Each layer has clear responsibility
2. **Testability:** Dependencies are injected, enabling unit/integration tests
3. **Reusability:** Use cases and repositories are framework-independent
4. **Scalability:** Easy to add new features without affecting existing code
5. **Offline-First:** Local database + remote sync pattern

## Consequences

### Positive
- ✅ Clear code organization
- ✅ Easy to test (unit tests for ViewModels, domain layer)
- ✅ Parallel development possible
- ✅ Framework agnostic at domain level
- ✅ Easy onboarding for new developers

### Negative
- ❌ More boilerplate code (mappers, interfaces)
- ❌ Learning curve for less experienced developers
- ❌ Build time slightly increased due to multiple modules

## Implementation Guidelines

### File Structure

```
app/
├── src/
│   ├── main/kotlin/com/noghre/sod/
│   │   ├── ui/                      # Presentation Layer
│   │   │   ├── theme/
│   │   │   ├── components/
│   │   │   ├── screens/
│   │   │   └── viewmodels/
│   │   ├── domain/                  # Domain Layer
│   │   │   ├── entities/
│   │   │   ├── usecases/
│   │   │   └── repositories/
│   │   ├── data/                    # Data Layer
│   │   │   ├── api/
│   │   │   ├── database/
│   │   │   ├── repositories/
│   │   │   └── mappers/
│   │   ├── di/                      # Dependency Injection
│   │   ├── core/                    # Shared utilities
│   │   └── App.kt
│   └── test/
│       ├── unit/
│       └── integration/
```

### ViewModel Example

```kotlin
@HiltViewModel
class ProductViewModel @Inject constructor(
    private val getProductsUseCase: GetProductsUseCase,
    private val analyticsTracker: AnalyticsTracker
) : ViewModel() {
    
    private val _productsState = MutableStateFlow<UiState<List<Product>>>(UiState.Loading)
    val productsState: StateFlow<UiState<List<Product>>> = _productsState.asStateFlow()
    
    fun loadProducts(page: Int = 1) {
        viewModelScope.launch {
            _productsState.value = UiState.Loading
            
            getProductsUseCase(GetProductsUseCase.Params(page = page))
                .onSuccess { products ->
                    _productsState.value = UiState.Success(products)
                    analyticsTracker.trackEvent("products_loaded", mapOf("count" to products.size))
                }
                .onFailure { error ->
                    _productsState.value = UiState.Error(error)
                    analyticsTracker.trackEvent("products_load_failed", mapOf("error" to error.message))
                }
        }
    }
}

seal class UiState<T> {
    class Loading<T> : UiState<T>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error<T>(val error: Throwable) : UiState<T>()
}
```

### UseCase Example

```kotlin
@Singleton
class GetProductsUseCase @Inject constructor(
    private val productRepository: ProductRepository
) {
    suspend operator fun invoke(params: Params): Result<List<Product>> {
        return try {
            val products = productRepository.getProducts(
                page = params.page,
                pageSize = params.pageSize
            )
            Result.Success(products)
        } catch (e: Exception) {
            Result.Failure(e)
        }
    }
    
    data class Params(
        val page: Int = 1,
        val pageSize: Int = 20
    )
}

sealed class Result<T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Failure<T>(val error: Throwable) : Result<T>()
    
    fun onSuccess(block: (T) -> Unit): Result<T> {
        if (this is Success) block(data)
        return this
    }
    
    fun onFailure(block: (Throwable) -> Unit): Result<T> {
        if (this is Failure) block(error)
        return this
    }
}
```

## Related Decisions

- ADR-002: Jetpack Compose for UI
- ADR-003: Offline-First Data Sync
- ADR-004: Dependency Injection with Hilt

## References

1. [Google Android Architecture Guide](https://developer.android.com/guide/architecture)
2. [MVVM Pattern - Microsoft](https://learn.microsoft.com/en-us/archive/msdn-magazine/2009/february/patterns-wpf-apps-with-the-model-view-viewmodel-design-pattern)
3. [Clean Architecture - Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
