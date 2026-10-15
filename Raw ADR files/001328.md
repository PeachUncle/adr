# ADR-005: MVVM Pattern for Ground-Side Android

**Status:** Accepted
**Date:** 2024-10 (Ground-Side architecture)
**Updated:** 2025-11-11
**Deciders:** Android Development Team
**Related Issues:** #10 (Focus distance UI), #20 (Quick Diagnostics), #22 (Manual focus)
**Related Views:** `view-logical.md`

---

## Context

Ground-Side Android application must:

1. **Display real-time camera status** (ISO, shutter, aperture, focus distance, battery)
2. **Handle user input** (sliders, buttons, dropdowns)
3. **Communicate with Air-Side** (send commands via TCP, receive status via UDP)
4. **Survive configuration changes** (screen rotation, app backgrounding)
5. **React to data changes** (update UI immediately when status received)
6. **Maintain clean separation** between UI, business logic, and data

**Technology Constraints:**
- Android platform (H16 tablet)
- Jetpack Compose for declarative UI
- Kotlin language (type-safe, coroutine support)
- Target API 24-36 (Android 7.0 to 14+)

**UI Complexity:**
- 15+ camera properties (each with slider/dropdown)
- Real-time status updates (5Hz UDP broadcast)
- Multiple screens (Dashboard, Settings, Diagnostics)
- Optimistic UI updates (don't wait for Air-Side confirmation)

**Design Question:** How to structure Android app for clean architecture, testability, and maintainability?

---

## Decision

**We will adopt the MVVM (Model-View-ViewModel) pattern** with Jetpack Architecture Components:

### Layer 1: View (UI Layer) - Jetpack Compose Composables

**Technology:** Jetpack Compose (declarative UI)

**Responsibilities:**
- Render UI based on state
- Capture user interactions
- **No business logic** (only UI logic like "show dropdown when clicked")

**Example:**
```kotlin
@Composable
fun CameraDashboard(viewModel: CameraViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    Column {
        Text("ISO: ${uiState.iso}")
        Slider(
            value = uiState.iso.toFloat(),
            onValueChange = { viewModel.setIso(it.toInt()) }
        )
    }
}
```

**Key Principle:** Stateless composables, state hoisted to ViewModel

---

### Layer 2: ViewModel (Presentation Logic Layer)

**Technology:** AndroidX Lifecycle ViewModel

**Responsibilities:**
- Hold UI state (`StateFlow<UiState>`)
- Expose functions for UI actions
- Orchestrate repository calls
- Survive configuration changes (screen rotation)
- Transform domain data to UI data

**Example:**
```kotlin
class CameraViewModel(
    private val repository: CameraRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(CameraUiState())
    val uiState: StateFlow<CameraUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            repository.statusFlow.collect { status ->
                _uiState.update { it.copy(
                    iso = status.camera.iso,
                    aperture = status.camera.aperture,
                    shutterSpeed = status.camera.shutterSpeed
                )}
            }
        }
    }

    fun setIso(value: Int) {
        viewModelScope.launch {
            // Optimistic UI update
            _uiState.update { it.copy(iso = value.toString()) }

            // Send command to Air-Side
            val result = repository.setProperty("iso", value.toString())
            if (result.isFailure) {
                // Revert on error
                _uiState.update { it.copy(iso = _previousIso) }
            }
        }
    }
}
```

**Key Features:**
- Lifecycle-aware (survives rotation)
- Coroutine scope tied to lifecycle
- Reactive state updates (StateFlow)

---

### Layer 3: Repository (Data Abstraction Layer)

**Technology:** Kotlin coroutines

**Responsibilities:**
- Abstract data sources (network, local storage)
- Coordinate TcpClient and UdpListener
- Cache data where appropriate
- Transform network models to domain models
- Handle errors and retries

**Example:**
```kotlin
class CameraRepository(
    private val tcpClient: TcpCommandClient,
    private val udpListener: UdpStatusListener,
    private val propertyLoader: PropertyLoader
) {

    private val _statusFlow = MutableStateFlow(CameraStatus())
    val statusFlow: StateFlow<CameraStatus> = _statusFlow.asStateFlow()

    init {
        // Collect UDP status updates
        CoroutineScope(Dispatchers.IO).launch {
            udpListener.statusFlow.collect { udpStatus ->
                _statusFlow.value = udpStatus
            }
        }
    }

    suspend fun setProperty(name: String, value: String): Result<Unit> {
        val command = CommandMessage(
            command = "camera.set_property",
            parameters = mapOf("property" to name, "value" to value)
        )
        return tcpClient.sendCommand(command)
    }
}
```

**Key Features:**
- Single source of truth for data
- Hides network complexity from ViewModel
- Suspending functions for async operations

---

### Layer 4: Network Layer (Data Sources)

**Technology:** Kotlin coroutines + Java sockets

**Components:**
- **TcpCommandClient:** Send commands, receive responses (TCP port 5000)
- **UdpStatusListener:** Receive status broadcasts (UDP port 5001)
- **HeartbeatClient:** Bidirectional heartbeat (UDP port 5002)
- **NetworkMonitor:** Connection health, auto-reconnect

**Example:**
```kotlin
class TcpCommandClient(private val airSideIp: String, private val port: Int = 5000) {

    private var socket: Socket? = null
    private val sequenceId = AtomicInteger(0)

    suspend fun sendCommand(command: CommandMessage): Result<ResponseMessage> = withContext(Dispatchers.IO) {
        try {
            val request = command.copy(sequenceId = sequenceId.incrementAndGet())
            val json = Json.encodeToString(request)

            socket?.getOutputStream()?.write(json.toByteArray())

            val response = socket?.getInputStream()?.readBytes()
            val responseMsg = Json.decodeFromString<ResponseMessage>(response.decodeToString())

            if (responseMsg.payload.status == "success") {
                Result.success(responseMsg)
            } else {
                Result.failure(Exception(responseMsg.payload.errorMessage))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

---

### Layer 5: Data Layer (Local Storage & Specs)

**Components:**
- **PropertyLoader:** Load camera property specs from JSON (ADR-002)
- **MessageSerializer:** JSON serialization (Gson/Kotlinx.serialization)
- **DataStore:** Persistent key-value storage (user settings)

---

## Alternatives Considered

### Alternative 1: MVC (Model-View-Controller)

**Approach:** Traditional MVC with Activities as Controllers

**Structure:**
- Model: Data classes + network clients
- View: XML layouts + Activities
- Controller: Activities handle logic

**Pros:**
- Familiar to developers from pre-Android-Architecture-Components era
- Simple for small apps

**Cons:**
- ❌ **Activity God Object:** Activity becomes massive (UI + logic + data)
- ❌ **No Lifecycle Handling:** Configuration changes (rotation) destroy Activity
  - Must save/restore state manually
  - Network requests can leak Activity references
- ❌ **Hard to Test:** Activity tied to Android framework (requires instrumented tests)
- ❌ **No Reactive Updates:** Must manually update UI when data changes

**Rejection Reason:** Modern Android best practices recommend MVVM with Architecture Components. MVC is legacy pattern.

---

### Alternative 2: MVP (Model-View-Presenter)

**Approach:** MVP with Presenters handling logic

**Structure:**
- Model: Data classes + repositories
- View: Activities/Fragments implementing View interface
- Presenter: Plain Kotlin classes orchestrating logic

**Pros:**
- Testable (Presenter is plain Kotlin, no Android dependencies)
- Separation of concerns

**Cons:**
- ❌ **Boilerplate:** Must define View interface, implement in Activity
  - Example: `interface CameraView { fun showIso(value: String) }`
- ❌ **Lifecycle Complexity:** Presenter must be manually attached/detached
- ❌ **No Built-In Reactivity:** Must implement observer pattern manually
- ❌ **Configuration Changes:** Still need to handle rotation (save Presenter state)

**Rejection Reason:** MVVM with ViewModel solves same problems with less boilerplate (Jetpack libraries handle lifecycle automatically)

---

### Alternative 3: MVI (Model-View-Intent)

**Approach:** Unidirectional data flow with single state stream

**Structure:**
- Model: Single state object (`sealed class State`)
- View: Composables rendering state
- Intent: User actions as sealed classes

**Example:**
```kotlin
sealed class CameraIntent {
    data class SetIso(val value: Int) : CameraIntent()
    data class SetAperture(val value: String) : CameraIntent()
}

data class CameraState(
    val iso: String,
    val aperture: String,
    val isLoading: Boolean,
    val error: String?
)
```

**Pros:**
- Predictable state management (Redux-like)
- Easy to debug (state history)
- Strong guarantees (single state tree)

**Cons:**
- ⚠️ **Boilerplate:** Every action requires Intent class definition
- ⚠️ **Complexity:** State reducer function becomes large
- ⚠️ **Overkill:** 15+ properties × multiple screens = 50+ Intent classes
- ⚠️ **Learning Curve:** Team not familiar with MVI pattern

**Partial Rejection:** MVI principles adopted (unidirectional flow, single state) but without full Intent system. MVVM with StateFlow achieves 80% of MVI benefits with less complexity.

---

### Alternative 4: Compose-Only (No ViewModel)

**Approach:** State hoisting within Composables, no ViewModel layer

**Example:**
```kotlin
@Composable
fun CameraDashboard() {
    var iso by remember { mutableStateOf("400") }

    LaunchedEffect(Unit) {
        // Directly call repository from Composable
        repository.statusFlow.collect { status ->
            iso = status.camera.iso
        }
    }

    Slider(value = iso.toFloat(), onValueChange = { iso = it.toString() })
}
```

**Pros:**
- Simpler (no ViewModel layer)
- Less boilerplate

**Cons:**
- ❌ **Configuration Changes:** State lost on rotation (unless `rememberSaveable`)
- ❌ **No Separation:** Business logic mixed with UI
- ❌ **Hard to Test:** Can't test logic without Compose runtime
- ❌ **State Duplication:** Each screen manages own state (no shared state)

**Rejection Reason:** Android best practices recommend ViewModel for state that survives configuration changes. Real-world app (Issue #10, #20) showed need for shared state across screens.

---

## Consequences

### Positive

✅ **Configuration Change Handling:** ViewModel survives screen rotation
- User rotates screen → UI rebuilds → ViewModel survives → State preserved
- No need to save/restore state manually
- Network requests continue across rotation

✅ **Testability:** Each layer tested independently
- ViewModel: Unit tests with mocked Repository
- Repository: Unit tests with mocked Network clients
- UI: Compose UI tests with fake ViewModel

**Example Test:**
```kotlin
@Test
fun `setIso updates state and calls repository`() = runTest {
    val fakeRepo = FakeRepository()
    val viewModel = CameraViewModel(fakeRepo)

    viewModel.setIso(800)

    assertEquals("800", viewModel.uiState.value.iso)
    assertEquals("iso", fakeRepo.lastProperty)
}
```

✅ **Reactive UI:** StateFlow automatically updates Composables
- UDP status received → Repository updates StateFlow → ViewModel updates uiState → Composable recomposes
- No manual UI update calls required

✅ **Separation of Concerns:** Clear boundaries between layers
- UI: Only rendering and user input
- ViewModel: Presentation logic and state management
- Repository: Data operations and business logic
- Network: Communication protocols

✅ **Coroutine Integration:** ViewModel has viewModelScope
- Cancelled when ViewModel cleared → no leaks
- Structured concurrency (parent-child coroutine hierarchy)

✅ **Optimistic Updates:** ViewModel can update UI before Air-Side confirms
- User sets ISO → UI updates immediately → Command sent → Revert if error
- Perceived responsiveness improved

✅ **Jetpack Compose Compatibility:** MVVM is natural fit for Compose
- StateFlow maps directly to `collectAsState()`
- Composables are simple functions consuming state

---

### Negative

⚠️ **Learning Curve:** Team must understand MVVM, StateFlow, coroutines
- **Mitigation:** Comprehensive documentation in `android/docs/`
- **Mitigation:** Code examples for common patterns
- **Reality:** One-time investment, now team proficient

⚠️ **Boilerplate:** StateFlow, uiState data classes, copy() for updates
- **Example:** `_uiState.update { it.copy(iso = newIso) }`
- **Mitigation:** Kotlin data classes minimize boilerplate
- **Mitigation:** IDE code generation (live templates)

⚠️ **State Synchronization:** UI state and network state can diverge
- **Example:** Optimistic update fails, must revert UI
- **Mitigation:** Repository is single source of truth
- **Mitigation:** ViewModel applies optimistic updates, reverts on error

⚠️ **ViewModel Lifetime Complexity:** Must understand when ViewModel cleared
- **Activity-scoped:** Survives rotation, cleared on Activity finish
- **Fragment-scoped:** Survives rotation within fragment, cleared on fragment destroy
- **Mitigation:** Android documentation clear on lifecycle

---

## Real-World Validation

### Issue #10: Focus Distance Display

**Challenge:** Display focus distance from UDP status in UI

**MVVM Implementation:**
1. **Repository:** Collect UDP status, extract `focal_distance_meters`
2. **ViewModel:** Map to UI string (e.g., "2.5m" or "∞")
3. **UI:** Display in Composable with LiveData observer

**Result:** Clean implementation, no issues. Took ~30 minutes.

**MVVM Benefit:** Clear data flow made implementation straightforward.

---

### Issue #20: Quick Diagnostics Screen

**Challenge:** New screen showing connection status, packet rates, errors

**MVVM Implementation:**
1. **ViewModel:** DiagnosticsViewModel with connection state, packet stats
2. **Repository:** NetworkMonitor provides connection status
3. **UI:** DiagnosticsScreen Composable rendering state

**Result:** New screen added without modifying existing screens. MVVM enabled modular development.

---

### Issue #22: Manual Focus Commands Not Reaching Air-Side

**Challenge:** Commands sent from UI but not arriving at Air-Side

**MVVM Debugging:**
1. **UI Layer:** Verified button clicked (log in Composable)
2. **ViewModel:** Verified function called (log in setFocusDistance())
3. **Repository:** Verified command constructed (log in sendCommand())
4. **Network:** Found bug - TcpClient filtering commands incorrectly

**MVVM Benefit:** Clear layer boundaries made debugging systematic. Found bug in Network layer without touching UI/ViewModel code.

---

## Implementation Notes

### StateFlow vs. LiveData

**Decision:** Use StateFlow (not LiveData)

**Rationale:**
- StateFlow is Kotlin Coroutines-native (LiveData is Android-specific)
- StateFlow has simpler API (no postValue vs. setValue confusion)
- StateFlow better for Compose (`collectAsState()` extension)
- StateFlow can be used in shared Kotlin modules (multiplatform ready)

---

### UI State Design

**Pattern:** Single `UiState` data class per screen

```kotlin
data class CameraDashboardUiState(
    val iso: String = "400",
    val aperture: String = "5.6",
    val shutterSpeed: String = "1/250",
    val focusDistance: String = "∞",
    val isConnected: Boolean = false,
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)
```

**Benefits:**
- Single source of truth for screen state
- Easy to save/restore (single object)
- Clear snapshot of UI at any time

---

### ViewModel Injection

**Pattern:** Hilt dependency injection (future) or manual factory

**Current (Manual):**
```kotlin
val viewModel: CameraViewModel = viewModel(
    factory = CameraViewModelFactory(repository)
)
```

**Future (Hilt):**
```kotlin
@HiltViewModel
class CameraViewModel @Inject constructor(
    private val repository: CameraRepository
) : ViewModel()

// In Composable:
val viewModel: CameraViewModel = hiltViewModel()
```

---

## Future Enhancements

**Considered for Phase 2:**
- **Offline Mode:** Cache last known state when Air-Side disconnected
- **State Persistence:** Save UI state to DataStore (survive app kill)
- **Multi-Module:** Extract ViewModel into separate Gradle module (shared logic)
- **MVI Refactor:** Full MVI with Intent system if complexity grows

---

## Related Decisions

- **ADR-001:** Three-Domain Architecture (Ground-Side as independent UI domain)
- **ADR-002:** Specification-First (PropertyLoader used in Repository layer)
- **ADR-013:** Jetpack Compose for Ground UI (View layer technology choice)

---

## References

- Logical View: `docs/architecture/view-logical.md` (Ground-Side MVVM layers section)
- C4 Component Diagram: `docs/architecture/c4-level3-ground-side-components.puml`
- Android Best Practices: https://developer.android.com/topic/architecture
- Jetpack Compose: https://developer.android.com/jetpack/compose
- Issue #10: Focus distance implementation
- Issue #20: Quick diagnostics screen
- Issue #22: Manual focus debugging
