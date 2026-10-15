# ADR 0005: Progressive Immersion Levels

## Status
Accepted

## Context
visionOS supports a spectrum of immersion from standard windows to fully immersive environments. Users have different comfort levels and use cases:
- Quick data checks → standard windows
- Focused analysis → reduced passthrough
- Presentations → fully immersive

We needed a system that:
- Provides smooth transitions between immersion levels
- Respects user comfort preferences
- Adapts visual complexity appropriately
- Maintains consistent UX across levels

## Decision
We implemented an `ImmersionManager` with six discrete levels:

| Level | Passthrough | Use Case |
|-------|-------------|----------|
| None (0) | 100% | Standard window mode |
| Minimal (1) | 95% | Subtle spatial elements |
| Partial (2) | 70% | Mixed reality overlays |
| Focused (3) | 40% | Reduced distractions |
| Full (4) | 15% | Immersive workspace |
| Complete (5) | 0% | Virtual environment |

### Core API:
```swift
@Observable
final class ImmersionManager {
    private(set) var currentLevel: ImmersionLevel = .none
    var maximumAllowedLevel: ImmersionLevel = .complete

    func setLevel(_ level: ImmersionLevel, animated: Bool = true) async
    func increaseImmersion() async
    func decreaseImmersion() async
}
```

### Environment Configuration:
Each level has associated environment settings:
```swift
struct EnvironmentConfiguration {
    let skyboxOpacity: Float
    let groundPlaneEnabled: Bool
    let ambientLightIntensity: Float
    let fogEnabled: Bool
    let spatialAudioEnabled: Bool
}
```

### SwiftUI Integration:
```swift
// Only show at certain immersion levels
someView.visibleAt(immersionLevel: .partial)

// Fade based on immersion
overlay.immersionOpacity(min: .none, max: .focused, inverted: true)
```

## Consequences

### Positive
- Smooth, animated transitions between levels
- User control over comfort and focus
- Consistent experience across the app
- Easy to add new levels if needed

### Negative
- More complex than binary immersive/windowed
- Need to design UI for multiple immersion states
- Some features only available at certain levels

### User Preferences
- `maximumAllowedLevel`: Users can set their comfort limit
- System remembers last used level per context
- Audio cues for level transitions

## Related Decisions
- ADR 0006: Spatial Audio Design
