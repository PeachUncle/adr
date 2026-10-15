# ADR-002: Clean Architecture Layers

## Status

Accepted

Date: 2024-01

## Context

ToneForge initially had a flat package structure where all components were mixed together: UI code, business logic, data access, audio processing, MIDI handling, and utilities all lived in poorly organized packages. This made it difficult to:

- Understand component dependencies
- Test business logic independently
- Reuse code across features
- Identify layer boundaries
- Enforce separation of concerns

As the app grew to support multiple effects, preset management, MIDI control, looper functionality, and background audio processing, the need for clear architectural layers became critical.

### Requirements
- Clear separation of concerns across layers
- Testable business logic without Android dependencies
- Reusable domain logic
- Flexible infrastructure (can swap implementations)
- Support for both UI and background audio processing

### Constraints
- Must work with existing Android app structure
- Native C++ audio processing via JNI
- Real-time audio requirements (low latency)
- Gradual migration from existing codebase

## Decision

We will organize ToneForge following **Clean Architecture** principles with three distinct layers:

### 1. Domain Layer (`domain/`)

**Purpose:** Pure business logic and domain models, completely independent of frameworks.

**Contains:**
- `interfaces/` - Contracts for repositories and services
  - `AudioEngineInterface` - Audio processing contract
  - `PermissionInterface` - Permission management contract

- `models/` - Domain entities and value objects
  - `AudioState` - Audio pipeline state
  - `EffectParameters` - Effect parameter models
  - `PedalEffect` - Effect definitions

- `usecases/` - Application business rules
  - `StartAudioPipelineUseCase` - Audio pipeline initialization
  - Each use case has single responsibility

**Rules:**
- ❌ NO Android framework dependencies (no `android.*` imports)
- ❌ NO infrastructure dependencies
- ✅ Pure Kotlin only
- ✅ Interfaces for all external dependencies
- ✅ Can depend on other domain classes
- ✅ Should be highly testable with pure unit tests

### 2. Infrastructure Layer (`infrastructure/`)

**Purpose:** Implementations of domain interfaces, framework-specific code, and external integrations.

**Contains:**
- `adapters/` - Implement domain interfaces
  - `AudioEngineAdapter` - Implements AudioEngineInterface
  - `PermissionManagerAdapter` - Implements PermissionInterface

- `audio/` - Audio subsystem
  - `AudioEngine` - JNI bridge to native code
  - `PipelineManager` - Audio pipeline lifecycle
  - `AudioStateManager` - State management

- `midi/` - MIDI subsystem
  - `ToneForgeMidiManager` - MIDI device integration

- `presets/` - Preset management
  - `PresetManager` - Save/load presets
  - `FavoritesManager` - Favorites functionality

- `permissions/` - Android permissions
  - `PermissionManager` - Runtime permission handling

- `services/` - Background services
  - `AudioBackgroundService` - Background audio processing

**Rules:**
- ✅ CAN depend on domain layer
- ✅ CAN have Android dependencies
- ✅ CAN integrate with external libraries
- ✅ Implements domain interfaces
- ❌ Should NOT depend on UI layer
- ✅ Should be mockable for testing

### 3. UI Layer (`ui/`)

**Purpose:** User interface and presentation logic following MVP pattern.

**Contains:**
- `activities/` - Android activities
  - `MainActivity` - Main entry point
  - `BaseActivity` - Shared activity functionality

- `base/` - MVP base classes
  - `BaseFragment` - Common fragment functionality
  - `BasePresenter` - Presenter base class
  - `BaseView` - View interface

- `fragments/` - Feature fragments (MVP)
  - `EffectsFragmentRefactored` - Effects UI
  - `TunerFragmentRefactored` - Tuner UI
  - `LooperFragmentRefactored` - Looper UI
  - etc.

- `components/` - Reusable UI components
  - `SystemStatusController` - Status UI
  - `AudioInitializer` - Audio initialization UI

- `navigation/` - Navigation logic
  - `NavigationController` - Fragment navigation

**Rules:**
- ✅ CAN depend on domain layer
- ✅ CAN depend on infrastructure layer (via dependency injection)
- ✅ Follows MVP pattern (see ADR-001)
- ✅ Fragments implement View interfaces
- ✅ Presenters coordinate use cases
- ❌ NO business logic in views

### Dependency Rule

**Dependencies only point inward:**

```
UI Layer → Infrastructure Layer → Domain Layer
   ↓              ↓                    ↑
   └──────────────┴────────────────────┘
        (via interfaces)
```

- UI can depend on Infrastructure and Domain
- Infrastructure can depend on Domain only
- Domain depends on nothing (pure Kotlin)

### Package Structure

```
com.example.toneforge/
├── domain/
│   ├── interfaces/
│   │   ├── AudioEngineInterface.kt
│   │   └── PermissionInterface.kt
│   ├── models/
│   │   ├── AudioState.kt
│   │   ├── EffectParameters.kt
│   │   └── PedalEffect.kt
│   └── usecases/
│       └── StartAudioPipelineUseCase.kt
│
├── infrastructure/
│   ├── adapters/
│   │   ├── AudioEngineAdapter.kt
│   │   └── PermissionManagerAdapter.kt
│   ├── audio/
│   │   ├── AudioEngine.kt
│   │   ├── PipelineManager.kt
│   │   └── AudioStateManager.kt
│   ├── midi/
│   │   └── ToneForgeMidiManager.kt
│   ├── presets/
│   │   ├── PresetManager.kt
│   │   └── FavoritesManager.kt
│   ├── permissions/
│   │   └── PermissionManager.kt
│   └── services/
│       └── AudioBackgroundService.kt
│
└── ui/
    ├── activities/
    │   ├── MainActivity.kt
    │   └── BaseActivity.kt
    ├── base/
    │   ├── BaseFragment.kt
    │   ├── BasePresenter.kt
    │   └── BaseView.kt
    ├── fragments/
    │   ├── effects/
    │   ├── tuner/
    │   ├── looper/
    │   └── ...
    ├── components/
    │   ├── SystemStatusController.kt
    │   └── AudioInitializer.kt
    └── navigation/
        └── NavigationController.kt
```

## Alternatives Considered

### Single-Layer Architecture
**Why Rejected:** No separation of concerns, testing difficult, tight coupling.

### Two-Layer (UI + Data)
**Why Rejected:** Business logic mixed with either UI or data layer, not framework-independent.

### Four-Layer (Add Application Layer)
**Why Rejected:** Overkill for current app size, three layers sufficient for clear separation.

### Feature-Based Packages
**Why Rejected:** While features are grouped, layer separation takes priority for enforcing architectural boundaries.

## Consequences

### Positive Consequences

1. **Clear Boundaries**
   - Easy to see what depends on what
   - Enforces separation of concerns
   - Prevents circular dependencies

2. **Testability**
   - Domain layer testable without Android
   - Infrastructure mockable via interfaces
   - UI testable with mocked presenters

3. **Flexibility**
   - Can swap infrastructure implementations
   - Domain logic reusable across platforms
   - UI can change without affecting business logic

4. **Framework Independence**
   - Domain logic doesn't depend on Android
   - Could potentially share domain with iOS
   - Native audio processing isolated in infrastructure

5. **Easier Navigation**
   - Developers know where to find code
   - Clear place for new features
   - Consistent organization

### Negative Consequences

1. **More Folders**
   - Deeper package structure
   - More navigation in IDE
   - Initial learning curve

2. **Indirection**
   - More interfaces to maintain
   - Adapter classes add layers
   - Can feel like "ceremony" for simple features

3. **Migration Effort**
   - Existing code needs reorganization
   - Refactoring takes time
   - Must maintain during transition

4. **Potential Over-Engineering**
   - Simple features might feel complex
   - More files for simple operations
   - Balance needed with pragmatism

### Neutral Consequences

1. **Dependency Injection**
   - Need strategy for DI (currently manual)
   - Could add DI framework in future
   - Constructor injection works for now

2. **Repository Pattern**
   - Repositories straddle infrastructure/domain
   - AudioRepository is infrastructure
   - Use interfaces for testability

## Implementation Notes

### Current Status

**✅ Fully Migrated:**
- Domain layer established
- Infrastructure layer organized
- UI layer follows MVP pattern
- Most fragments refactored

**🔄 In Progress:**
- Some legacy fragments remain
- Gradual migration ongoing

### Migration Guidelines

1. **Start with Domain**
   - Extract business logic
   - Create interfaces
   - Define models

2. **Move Infrastructure**
   - Implement domain interfaces
   - Organize by subsystem
   - Isolate Android dependencies

3. **Refactor UI**
   - Apply MVP pattern
   - Use domain use cases
   - Keep views passive

4. **Write Tests**
   - Domain: pure unit tests
   - Infrastructure: integration tests
   - UI: presenter tests + Espresso

### Testing by Layer

**Domain Layer:**
```kotlin
// Pure unit test, no mocks needed
@Test
fun `AudioState starts in idle state`() {
    val state = AudioState()
    assertEquals(AudioState.IDLE, state.status)
}
```

**Infrastructure Layer:**
```kotlin
// Integration test with mocked domain interfaces
@Test
fun `AudioEngineAdapter starts pipeline`() {
    val adapter = AudioEngineAdapter(mockAudioEngine)
    adapter.startPipeline()
    verify(mockAudioEngine).start()
}
```

**UI Layer:**
```kotlin
// Presenter test with mocked view and use case
@Test
fun `presenter loads effects on initialize`() {
    presenter.initialize()
    verify(mockView).showEffectsList(any())
}
```

### Special Considerations

**Native C++ Code:**
- Lives at project root in `cpp/`
- AudioEngine (infrastructure) provides JNI bridge
- Audio processing logic hidden behind AudioEngineInterface

**Background Audio:**
- AudioBackgroundService in infrastructure
- Coordinates with PipelineManager
- UI doesn't know about service details

**MIDI Integration:**
- ToneForgeMidiManager in infrastructure
- Domain defines MIDI events/parameters
- UI receives events via presenters

## References

- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Android Clean Architecture](https://github.com/android10/Android-CleanArchitecture)
- ADR-001: MVP Pattern Adoption
- ToneForge CLAUDE.md - Architecture Section

## Notes

- This architecture supports our MVP adoption (ADR-001)
- Layer discipline enforced through code review
- Consider linting rules to prevent layer violations
- Native code is special case (not pure domain but isolated)
- Use case granularity: prefer focused, single-purpose use cases
- Repository pattern used but repositories live in infrastructure

---

## Metadata

- **Author**: ToneForge Team
- **Status**: Implemented and actively maintained
- **Last Review**: 2024-11
- **Related**: ADR-001 (MVP Pattern), ADR-003 (JNI Security)
