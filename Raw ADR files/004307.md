# ADR-001: MVP Pattern Adoption

## Status

Accepted

Date: 2024-01

## Context

ToneForge started as a monolithic Android application with large Activity and Fragment classes containing mixed concerns: UI logic, business logic, audio processing coordination, and data management. As the application grew to support multiple effects, preset management, MIDI control, and real-time audio processing, the codebase became difficult to maintain and test.

### Problems Identified
- **Tight coupling**: UI logic mixed with business logic in fragments
- **Difficult testing**: Cannot test business logic without Android framework
- **Code duplication**: Similar patterns repeated across fragments
- **Unclear responsibilities**: Fragments doing too much
- **Poor separation**: Hard to identify what code belongs where

### Requirements
- Clear separation between UI and business logic
- Testable code without Android framework dependencies
- Familiar pattern for Android developers
- Support for coroutines and async operations
- Compatible with existing Clean Architecture principles

### Constraints
- Must work with existing codebase (gradual migration)
- Should leverage Kotlin coroutines
- Must support audio processing use cases (low latency critical)
- Team already familiar with MVP from previous projects

## Decision

We will adopt the **MVP (Model-View-Presenter)** pattern as the standard presentation layer pattern for ToneForge.

### MVP Structure

**View Interface** (Implemented by Fragment/Activity)
- Handles UI updates only
- Forwards user interactions to Presenter
- No business logic
- Passive (doesn't make decisions)

```kotlin
interface View {
    fun showLoading()
    fun hideLoading()
    fun displayData(data: Model)
    fun showError(message: String)
}
```

**Presenter** (Pure Kotlin)
- Coordinates business logic via Use Cases
- Transforms domain data for view
- Handles user actions
- Manages view lifecycle
- Uses coroutines for async operations

```kotlin
class Presenter(private val useCase: UseCase) {
    private var view: View? = null

    fun attachView(view: View)
    fun detachView()
    fun loadData()
}
```

**Contract Interface**
- Defines View, Presenter, and Model interfaces
- Documents the contract between components
- Named `*Contract.kt`

### Naming Conventions
- Contracts: `*Contract.kt` (e.g., `EffectsContract.kt`)
- Presenters: `*Presenter.kt` (e.g., `EffectsPresenter.kt`)
- Views: `*FragmentRefactored.kt` (e.g., `EffectsFragmentRefactored.kt`)

### Implementation Rules
1. All new features MUST use MVP pattern
2. Use `*FragmentRefactored` suffix for new MVP fragments
3. Legacy fragments remain for compatibility during migration
4. Presenters MUST NOT have Android dependencies
5. Views MUST only handle UI, no business logic
6. Use Constructor Injection for Presenter dependencies
7. Use Coroutines with proper dispatchers (IO for background, Main for UI)

## Alternatives Considered

### MVVM (Model-View-ViewModel)
**Pros:**
- Native support via Android Architecture Components
- Data binding reduces boilerplate
- ViewModel survives configuration changes automatically

**Cons:**
- ViewModels can become complex "god objects"
- Data binding harder to debug
- Team less familiar with pattern
- ViewModel lifecycle different from traditional Android

**Why Rejected:** Team expertise with MVP, better testability without data binding complexity, clearer separation of concerns.

### MVI (Model-View-Intent)
**Pros:**
- Unidirectional data flow
- Predictable state management
- Works well with reactive programming

**Cons:**
- Steep learning curve
- More boilerplate code
- Overkill for current app complexity
- Not familiar to team

**Why Rejected:** Too complex for current needs, would require significant rework, team not experienced with pattern.

### No Pattern (Continue Current Approach)
**Pros:**
- No refactoring needed
- No learning curve

**Cons:**
- Testing remains difficult
- Code continues to be unmaintainable
- Technical debt grows
- Onboarding new developers harder

**Why Rejected:** Maintenance pain outweighs migration cost, testability critical for audio processing features.

## Consequences

### Positive Consequences

1. **Improved Testability**
   - Presenters can be unit tested without Android framework
   - Business logic isolated from UI framework
   - Mock views easily for presenter tests

2. **Clear Separation of Concerns**
   - UI code clearly separated in View
   - Business logic in Presenter
   - Data/domain logic in Use Cases and Repositories

3. **Better Maintainability**
   - Smaller, focused classes
   - Clear responsibilities
   - Easier to locate code

4. **Familiar Pattern**
   - Team already knows MVP
   - Abundant resources and examples
   - Common in Android community

5. **Gradual Migration**
   - Can migrate one fragment at a time
   - `*FragmentRefactored` naming shows migration progress
   - Legacy code remains functional

### Negative Consequences

1. **More Boilerplate**
   - Three files per feature (Contract, Presenter, Fragment)
   - More interfaces to maintain
   - More code overall

2. **Manual Lifecycle Management**
   - Must attach/detach view manually
   - Must manage coroutine scope in presenter
   - Memory leak risk if not done correctly

3. **Migration Effort**
   - 8+ fragments to migrate
   - Testing migration takes time
   - Need to maintain both patterns during transition

4. **Not "Modern" Android**
   - Google recommends MVVM with ViewModel
   - Newer Android samples use MVVM
   - May seem dated to some developers

### Neutral Consequences

1. **Templates Needed**
   - Created templates in `.claude/templates/`
   - Provides consistency
   - Speeds up development

2. **Documentation Updates**
   - Updated CLAUDE.md
   - Created checklists
   - Training materials needed

## Implementation Notes

### Migration Strategy

**Phase 1: Template Creation** ✅ Completed
- Create MVP templates
- Document pattern in CLAUDE.md
- Create example fragments

**Phase 2: Critical Fragments** ✅ Completed
- HomeFragmentRefactored
- EffectsFragmentRefactored
- TunerFragmentRefactored
- LooperFragmentRefactored

**Phase 3: Remaining Fragments** ✅ Completed
- MetronomeFragmentRefactored
- RecorderFragmentRefactored
- SettingsFragmentRefactored
- LoopLibraryFragmentRefactored

**Phase 4: Cleanup** (Future)
- Remove legacy fragments
- Clean up unused code
- Update navigation to use new fragments only

### Code Example

```kotlin
// EffectsContract.kt
interface EffectsContract {
    interface View {
        fun showEffectsList(effects: List<Effect>)
        fun showError(message: String)
    }

    interface Presenter {
        fun loadEffects()
        fun onEffectToggled(effect: Effect)
    }
}

// EffectsPresenter.kt
class EffectsPresenter(
    private val audioRepository: AudioRepository
) : EffectsContract.Presenter {

    private var view: EffectsContract.View? = null
    private val scope = CoroutineScope(Dispatchers.Main + SupervisorJob())

    override fun loadEffects() {
        scope.launch {
            val effects = withContext(Dispatchers.IO) {
                audioRepository.getEffects()
            }
            view?.showEffectsList(effects)
        }
    }
}

// EffectsFragmentRefactored.kt
class EffectsFragmentRefactored : BaseFragment(), EffectsContract.View {
    private lateinit var presenter: EffectsPresenter

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        presenter = EffectsPresenter(AudioRepository())
        presenter.attachView(this)
        presenter.loadEffects()
    }

    override fun showEffectsList(effects: List<Effect>) {
        // Update RecyclerView
    }
}
```

### Testing Example

```kotlin
@Test
fun `loadEffects displays effects in view`() = runTest {
    // Given
    val mockEffects = listOf(Effect.DISTORTION, Effect.DELAY)
    `when`(mockRepository.getEffects()).thenReturn(mockEffects)

    // When
    presenter.loadEffects()
    advanceUntilIdle()

    // Then
    verify(mockView).showEffectsList(mockEffects)
}
```

## References

- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Android Clean Architecture](https://github.com/android10/Android-CleanArchitecture)
- [MVP for Android](https://github.com/googlesamples/android-architecture/tree/todo-mvp/)
- ToneForge CLAUDE.md - Architecture Section
- ToneForge Templates: `.claude/templates/`

## Notes

- This decision aligns with our Clean Architecture adoption (ADR-002)
- Consider ViewModel for simple, read-only screens in future
- May revisit if we adopt Jetpack Compose (declarative UI changes the game)
- Templates ensure consistency across implementations
- Testing strategy documented in test templates

---

## Metadata

- **Author**: ToneForge Team
- **Status**: Implemented and in active use
- **Last Review**: 2024-11
- **Next Review**: When considering Jetpack Compose migration
