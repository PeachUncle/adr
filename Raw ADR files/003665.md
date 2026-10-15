# ADR-001: ID-Based Navigation Pattern

**Status**: Accepted
**Date**: 2025-01-17
**Decision Makers**: Development Team
**Related Issue**: OIR Singleton Anti-Pattern Remediation

## Context

During codebase review, we discovered that the OIR test module was using a singleton object (`OIRTestResultHolder`) to pass complex test result objects between screens. This anti-pattern caused several issues:

1. **Not Process-Death Safe**: State was lost on configuration changes or low memory conditions
2. **Memory Leaks**: Singleton lived forever, holding references that prevented garbage collection
3. **State Pollution**: Singleton state persisted between test runs, causing flaky tests
4. **Manual Memory Management**: Required explicit `clearResult()` calls, prone to bugs
5. **Architectural Inconsistency**: OIR was the only test module using this pattern (6 other modules used proper architecture)

Meanwhile, other test modules (TAT, WAT, SRT, PPDT, SDT, PIQ) all followed a clean pattern:
- Pass only submission ID via navigation
- Result screen fetches data from Firestore using ViewModel + Repository
- Process-death safe, testable, consistent

## Decision

**We adopt ID-Based Navigation as the MANDATORY pattern for all test modules.**

### Pattern Requirements

1. **Test screens** must pass ONLY primitive types (String, Int, Enum) via navigation callbacks
2. **Result screens** must fetch data from repository using ViewModel
3. **NO singleton state holders** - forbidden across entire codebase
4. **NO complex objects** in navigation - only IDs and minimal metadata

### Standard Flow

```
User completes test
  → TestViewModel: Save to Firestore (with full result data)
  → TestViewModel: Update UI state with submissionId
  → TestScreen: onTestComplete(submissionId, subscriptionType)
  → Navigation: Route to result screen with ID
  → ResultScreen: Load with submissionId parameter
  → ResultViewModel: Fetch from Firestore using submissionId
  → ResultScreen: Display with loading/error/success states
```

### Implementation Details

**Test Screen:**
```kotlin
@Composable
fun TestScreen(
    onTestComplete: (submissionId: String, subscriptionType: SubscriptionType) -> Unit
) {
    // Pass only ID after submission saved
    LaunchedEffect(uiState.isCompleted) {
        if (uiState.isCompleted && uiState.submissionId != null) {
            onTestComplete(uiState.submissionId!!, uiState.subscriptionType!!)
        }
    }
}
```

**Result Screen:**
```kotlin
@Composable
fun ResultScreen(
    submissionId: String,
    viewModel: ResultViewModel = hiltViewModel()
) {
    LaunchedEffect(submissionId) {
        viewModel.loadSubmission(submissionId)
    }

    when {
        uiState.isLoading -> LoadingState()
        uiState.error != null -> ErrorState(onRetry = { viewModel.retry(submissionId) })
        uiState.result != null -> SuccessState(uiState.result)
    }
}
```

**Result ViewModel:**
```kotlin
@HiltViewModel
class ResultViewModel @Inject constructor(
    private val repository: SubmissionRepository
) : ViewModel() {
    fun loadSubmission(submissionId: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            repository.getSubmission(submissionId)
                .onSuccess { data -> /* parse and update state */ }
                .onFailure { error -> /* show error with retry */ }
        }
    }
}
```

## Consequences

### Positive

✅ **Process-Death Safe**: State persists through configuration changes
✅ **Single Source of Truth**: Firestore is authority, not in-memory objects
✅ **Deep Linkable**: Can navigate directly to results with just an ID
✅ **Testable**: Easy to mock repositories and test ViewModels
✅ **Consistent**: All 7 test modules follow identical pattern
✅ **No Memory Leaks**: No singletons holding references
✅ **Clean Architecture**: Proper separation of concerns (UI → ViewModel → Repository)

### Negative

❌ **Network Dependency**: Requires Firestore fetch for each result view
   - *Mitigation*: Firestore has built-in caching and offline support
   - *Mitigation*: Loading states provide good UX during fetch

❌ **Slight Latency**: Small delay fetching from Firestore vs in-memory
   - *Mitigation*: Usually <100ms with cache, acceptable UX
   - *Mitigation*: Show skeleton/loading state during fetch

❌ **More Boilerplate**: Requires ViewModel + parsing logic
   - *Mitigation*: Boilerplate is consistent and reusable
   - *Mitigation*: Benefits far outweigh the extra code

## Alternatives Considered

### Alternative 1: SavedStateHandle with Parcelable
**Description**: Use Navigation's SavedStateHandle to pass complex objects

**Pros**:
- No network fetch required
- Data available immediately

**Cons**:
- 1MB transaction size limit (results can be large)
- Must make all classes Parcelable (lots of boilerplate)
- Still not truly process-death safe (SavedState has limits)
- Tight coupling between screens

**Decision**: ❌ Rejected - Size limits and coupling issues

### Alternative 2: Shared ViewModel Scope
**Description**: Share ViewModel between test screen and result screen

**Pros**:
- No network fetch
- Data available immediately

**Cons**:
- Different from other modules (inconsistent)
- ViewModels should be screen-scoped for proper lifecycle
- State management becomes complex
- Not deep-linkable

**Decision**: ❌ Rejected - Architectural inconsistency

### Alternative 3: Keep Singleton Pattern (Status Quo)
**Description**: Continue using `OIRTestResultHolder`

**Pros**:
- No changes required
- Data available immediately

**Cons**:
- Not process-death safe
- Memory leaks
- State pollution
- Architectural anti-pattern
- Inconsistent with other modules

**Decision**: ❌ Rejected - Too many serious issues

## Enforcement

To prevent regression, we implemented multiple enforcement layers:

### 1. Custom Lint Rules (ERROR Severity)
- `SingletonMutableStateDetector`: Catches singletons with mutable state
- `NavigationComplexObjectDetector`: Catches complex object navigation
- `ViewModelLifecycleDetector`: Ensures proper cleanup

Location: `/lint/src/main/kotlin/com/ssbmax/lint/`

### 2. Pre-Commit Hooks
Blocks commits that:
- Add `*Holder.kt` files
- Create singleton objects with mutable state
- Pass complex objects via navigation callbacks

Location: `/.git/hooks/pre-commit`

### 3. Architecture Tests
Automated tests that validate:
- All test screens use ID-based navigation
- No singleton mutable state exists
- All result screens have ViewModels

Location: `/app/src/test/kotlin/com/ssbmax/testing/ArchitectureTest.kt`

### 4. CI/CD Pipeline
- Lint checks fail build on violations
- Architecture tests fail build on violations
- No `continue-on-error` allowed

Location: `/.github/workflows/ci.yml`

### 5. Documentation
Comprehensive guidelines in:
- `CLAUDE.md` - Main architecture rules
- This ADR - Decision rationale
- Code comments in reference implementations

## Migration

### OIR Module Migration (Completed)

**Before** (Anti-Pattern):
```kotlin
object OIRTestResultHolder {
    private var _result: OIRTestResult? = null
    fun setResult(result: OIRTestResult)
    fun getResult(): OIRTestResult?
}

// In navigation
OIRTestResultHolder.setResult(result)
navigate("result")

// In result screen
val result = OIRTestResultHolder.getResult()
```

**After** (Proper Pattern):
```kotlin
// Created OIRSubmissionResultViewModel
@HiltViewModel
class OIRSubmissionResultViewModel @Inject constructor(
    private val repository: SubmissionRepository
) : ViewModel() {
    fun loadSubmission(submissionId: String)
}

// In navigation
onTestComplete(submissionId, subscriptionType)

// In result screen
OIRTestResultScreen(submissionId = submissionId)
```

**Files Changed**:
- ✅ Created: `OIRSubmissionResultViewModel.kt`
- ✅ Modified: `OIRTestResultScreen.kt` (now uses ViewModel)
- ✅ Modified: `OIRTestScreen.kt` (passes ID not object)
- ✅ Modified: `SharedNavGraph.kt` (removed holder usage)
- ✅ Deleted: `OIRTestResultHolder.kt`

**Result**: OIR now matches TAT/WAT/SRT/PPDT/SDT/PIQ pattern exactly.

## References

- [CLAUDE.md - Navigation & State Management Rules](../../CLAUDE.md#-navigation--state-management-rules)
- [OIR Migration PR](#) (link to PR when created)
- [Google Android Architecture Guide](https://developer.android.com/topic/architecture)
- [Jetpack Navigation Best Practices](https://developer.android.com/guide/navigation/navigation-principles)

## Review History

| Date | Reviewer | Status | Notes |
|------|----------|--------|-------|
| 2025-01-17 | Development Team | Accepted | Unanimously approved |
| 2025-01-17 | Tech Lead | Accepted | Enforcement mechanisms approved |

## Future Considerations

1. **Offline-First Strategy**: If Firestore latency becomes an issue, consider:
   - Optimistic UI updates with local cache
   - Room database as primary source with Firestore sync
   - Background sync with conflict resolution

2. **Performance Monitoring**: Track metrics:
   - Time to display results (should be <200ms)
   - Cache hit rate (should be >80%)
   - User-perceived latency

3. **Pattern Evolution**: Re-evaluate if:
   - Firestore performance degrades significantly
   - New Android architecture components provide better alternatives
   - User feedback indicates unacceptable latency

---

**This decision is now the standard for all navigation in SSBMax.**
