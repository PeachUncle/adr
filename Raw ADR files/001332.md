# ADR-013: Jetpack Compose for Ground UI

**Status:** Accepted
**Date:** 2024-10
**Updated:** 2025-11-11
**Deciders:** Android Development Team
**Related Issues:** #10, #20
**Related Views:** `view-logical.md`

---

## Context

Ground-Side Android UI must:
1. Display 15+ camera properties (sliders, dropdowns)
2. Real-time updates (5Hz status from Air-Side)
3. Touch-optimized for 10.1" H16 tablet
4. Modern UX (Material Design 3)
5. Easy to maintain and extend

**Technology Choice:** What UI framework for Android?

---

## Decision

**UI Framework: Jetpack Compose (Declarative UI)**

**Rationale:**
1. **Reactive:** StateFlow → collectAsState() → automatic recomposition
2. **Modern:** Google's recommended approach (XML views deprecated)
3. **Less Boilerplate:** No findViewById, no XML layouts
4. **Composable Functions:** Reusable UI components
5. **Material Design 3:** Built-in support

---

## Alternatives Considered

### Alternative 1: XML Layouts + View Binding

**Approach:** Traditional Android XML layouts

**Pros:**
- Mature, well-documented
- Team familiar with XML

**Cons:**
- ❌ **Boilerplate:** findViewById, ViewBinding setup, observers
- ❌ **Not Reactive:** Manual UI updates when data changes
- ❌ **Deprecated:** Google recommends Compose for new projects
- ❌ **Hard to Test:** UI tests require instrumentation

**Rejection:** Compose is future of Android UI, better investment

---

### Alternative 2: Flutter

**Approach:** Cross-platform UI framework

**Pros:**
- Cross-platform (iOS + Android from single codebase)
- Declarative UI (similar to Compose)

**Cons:**
- ❌ **No iOS Requirement:** Only targeting Android (H16 tablet)
- ❌ **Dart Language:** Team knows Kotlin, not Dart
- ❌ **Android Interop:** Accessing Android APIs requires platform channels
- ❌ **Binary Size:** Flutter apps larger (~20MB vs ~5MB native)

**Rejection:** Cross-platform not needed, native Android APIs preferred

---

### Alternative 3: React Native

**Approach:** JavaScript-based cross-platform UI

**Pros:**
- Cross-platform
- Web developers can contribute

**Cons:**
- ❌ **JavaScript Performance:** Slower than native Kotlin
- ❌ **Bridge Overhead:** JS ↔ Native communication latency
- ❌ **No iOS Requirement:** Only targeting Android
- ❌ **Team Expertise:** Team knows Kotlin, not JavaScript/React

**Rejection:** Native performance preferred, team expertise in Kotlin

---

## Consequences

### Positive

✅ **Reactive UI:** StateFlow changes automatically recompose UI
```kotlin
@Composable
fun IsoDisplay(viewModel: CameraViewModel) {
    val iso by viewModel.uiState.collectAsState()
    Text("ISO: ${iso.iso}") // Auto-updates when iso changes
}
```

✅ **Reusable Components:**
```kotlin
@Composable
fun PropertySlider(label: String, value: Float, onValueChange: (Float) -> Unit) {
    Column {
        Text(label)
        Slider(value = value, onValueChange = onValueChange)
    }
}

// Use everywhere:
PropertySlider("ISO", iso, { viewModel.setIso(it) })
PropertySlider("Aperture", aperture, { viewModel.setAperture(it) })
```

✅ **Less Code:** ~30% less code than XML + ViewBinding
✅ **Better Testing:** Preview composables in IDE (no emulator)
✅ **Material 3:** Modern design system built-in

### Negative

⚠️ **Learning Curve:** Team had to learn Compose (1-2 weeks)
- Mitigation: Comprehensive training, documentation

⚠️ **Jetpack Compose Min SDK:** Requires API 21+ (Android 5.0)
- Acceptable: H16 runs Android 7.0+ (API 24)

⚠️ **Immature Ecosystem:** Some libraries not Compose-ready yet
- Mitigation: Most libraries now support Compose (2025)

---

## Real-World Success

### Issue #10: Focus Distance Display

**Implementation:** 20-line Composable
```kotlin
@Composable
fun FocusDistanceDisplay(viewModel: CameraViewModel) {
    val uiState by viewModel.uiState.collectAsState()

    Text(
        text = "Focus: ${uiState.focusDistance}",
        style = MaterialTheme.typography.bodyLarge
    )
}
```

**Result:** Instant updates when UDP status received (5Hz)

---

### Issue #20: Quick Diagnostics Screen

**Implementation:** 50-line Composable with LazyColumn
```kotlin
@Composable
fun DiagnosticsScreen(viewModel: DiagnosticsViewModel) {
    val state by viewModel.uiState.collectAsState()

    LazyColumn {
        item { ConnectionStatus(state.isConnected) }
        item { PacketRate(state.packetsPerSecond) }
        item { ErrorLog(state.errors) }
    }
}
```

**Result:** New screen added in 1 hour (vs ~4 hours with XML)

---

## Compose Best Practices

1. **Stateless Composables:** Hoist state to ViewModel
2. **Remember Expensive Operations:** Use `remember` for calculations
3. **Immutable State:** Use data classes, never mutate in Composable
4. **Preview Composables:** Use `@Preview` for rapid iteration

---

## Related Decisions

- **ADR-001:** Three-Domain Architecture (Ground-Side as Android domain)
- **ADR-005:** MVVM Pattern (Compose is natural fit for MVVM)

---

## References

- Logical View: `view-logical.md` (Ground-Side UI layer)
- Jetpack Compose Docs: https://developer.android.com/jetpack/compose
- Material 3: https://m3.material.io
