# ADR-003: GlobalScope Usage in Leak Verification Helper

## Status
**Accepted** (with constraints)

## Date
2024-11-20

## Context
The `LeakVerificationHelper` utility class in SSBMax uses Kotlin's `GlobalScope` to intentionally create memory leak scenarios for testing and debugging purposes with Android Profiler.

`GlobalScope` is generally considered an anti-pattern in production code because:
- Coroutines launched in `GlobalScope` have no structured concurrency
- They survive ViewModel/Activity lifecycle, causing memory leaks
- Difficult to cancel or manage lifecycle
- Can cause resource exhaustion

However, `LeakVerificationHelper` is a **test-only utility** that requires `GlobalScope` to:
1. Simulate memory leak conditions that survive ViewModel destruction
2. Test memory leak detection in Android Profiler
3. Verify proper cleanup mechanisms in production ViewModels
4. Demonstrate correct vs. incorrect coroutine scope usage

## Decision
We **ALLOW** `GlobalScope` usage in `LeakVerificationHelper.kt` ONLY, subject to the following constraints:

### Allowed Usage
- **File**: `core/data/src/main/kotlin/com/ssbmax/core/data/util/LeakVerificationHelper.kt`
- **Purpose**: Test-only memory leak simulation for profiler verification
- **Required Annotations**: All `GlobalScope` uses MUST be marked with `@OptIn(DelicateCoroutinesApi::class)`
- **Documentation**: Class-level KDoc MUST warn against production use

### Forbidden Usage
- **Production Code**: NEVER use `GlobalScope` in ViewModels, Repositories, or UI components
- **New Files**: Creating new files with `GlobalScope` requires architecture team approval
- **Test Files**: Unit/UI tests should use `TestScope`, not `GlobalScope`

## Enforcement Mechanisms

### 1. Code Documentation
```kotlin
/**
 * Utility for creating intentional memory leaks to test Android Profiler.
 *
 * ⚠️ WARNING: Uses GlobalScope intentionally for leak simulation.
 * NEVER use GlobalScope in production code - always use viewModelScope!
 *
 * This helper is for development/debugging ONLY.
 */
@OptIn(DelicateCoroutinesApi::class)
object LeakVerificationHelper {
    fun createLeak() {
        GlobalScope.launch { /* intentional leak */ }
    }
}
```

### 2. Custom Lint Rules
**Rule**: `NoGlobalScopeDetector` (ERROR severity)
- **Location**: `custom-lint/src/main/kotlin/com/ssbmax/lint/NoGlobalScopeDetector.kt`
- **Behavior**: Fails build if `GlobalScope` detected outside whitelist
- **Whitelist**: `LeakVerificationHelper.kt` only

### 3. Pre-Commit Hooks
**Script**: `.git/hooks/pre-commit`
- Blocks commits containing `GlobalScope` outside whitelist
- Provides helpful error message with this ADR link

### 4. CI/CD Pipeline
- Runs `./gradle.sh lint` on every PR
- No `continue-on-error` - violations block merge
- Architecture test validates whitelist compliance

## Consequences

### Positive
- ✅ Can test memory leak prevention in production ViewModels
- ✅ Provides real leak scenarios for Android Profiler training
- ✅ Clear documentation prevents accidental misuse
- ✅ Automated enforcement prevents anti-pattern spread

### Negative
- ⚠️ Risk of developers copying code without understanding context
- ⚠️ Could be misunderstood by new team members

### Mitigations
1. **Clear warnings in code comments** (implemented)
2. **Architecture tests enforce whitelist** (implemented)
3. **This ADR document for team reference** (you're reading it!)
4. **Code review checklist includes GlobalScope check**
5. **Onboarding docs explain proper coroutine scope usage**

## Alternatives Considered

### Alternative 1: Remove LeakVerificationHelper Entirely
- **Pros**: Eliminates `GlobalScope` usage completely
- **Cons**: Loses ability to test leak detection, valuable debugging tool
- **Decision**: Rejected - testing value outweighs risk with proper safeguards

### Alternative 2: Use TestScope with Infinite Timeout
- **Pros**: Structured concurrency maintained
- **Cons**: Doesn't simulate real memory leak conditions (cancels on scope cleanup)
- **Decision**: Rejected - defeats purpose of leak simulation

### Alternative 3: Separate Test Module
- **Pros**: Complete isolation from production code
- **Cons**: Overhead of separate module, same risk if copied
- **Decision**: Deferred - current safeguards sufficient, revisit if issues arise

## References
- [Kotlin Coroutines: GlobalScope Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-global-scope/)
- [Android Architecture: ViewModel Scopes](https://developer.android.com/topic/libraries/architecture/coroutines)
- SSBMax CLAUDE.md: Navigation & State Management Rules
- Implementation: `core/data/src/main/kotlin/com/ssbmax/core/data/util/LeakVerificationHelper.kt`

## Review and Maintenance
- **Review Date**: 2025-Q2 (6 months from creation)
- **Owner**: Architecture Team
- **Trigger for Review**:
  - Any new `GlobalScope` usage request
  - Memory leak production incidents
  - Team member questions about coroutine scopes

## Examples

### ✅ CORRECT: ViewModel with Proper Scope
```kotlin
@HiltViewModel
class TATTestViewModel @Inject constructor() : ViewModel() {
    fun loadTest() {
        viewModelScope.launch {  // ✅ Cancels when ViewModel cleared
            repository.getTest()
        }
    }

    override fun onCleared() {
        super.onCleared()
        // viewModelScope automatically cancels all jobs
    }
}
```

### ❌ WRONG: ViewModel with GlobalScope (Memory Leak!)
```kotlin
@HiltViewModel
class TATTestViewModel @Inject constructor() : ViewModel() {
    fun loadTest() {
        GlobalScope.launch {  // ❌ NEVER cancels, leaks ViewModel!
            repository.getTest()
        }
    }
}
```

### ✅ ALLOWED: Test Helper with GlobalScope
```kotlin
/**
 * Test utility for memory leak detection
 * ⚠️ WARNING: Uses GlobalScope intentionally - DO NOT use in production!
 */
@OptIn(DelicateCoroutinesApi::class)
object LeakVerificationHelper {
    fun createIntentionalLeak() {
        GlobalScope.launch {  // ✅ Allowed here ONLY for testing
            // Simulate leak scenario
        }
    }
}
```

## Decision Authority
- **Approved by**: Architecture Team
- **Date**: 2024-11-20
- **Status**: Active
- **Supersedes**: None
