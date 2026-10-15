# ADR-002: Dual Independent Audio Output Buses

## Status

Accepted

## Date

2026-01-04

## Context

The soundboard needs to output audio to two destinations simultaneously:
- **Monitor**: User's speakers/headphones (so they hear what they're playing)
- **Inject**: Virtual audio device (routed into Discord/Teams/streaming software)

We needed to decide how to architect this dual-output capability.

## Decision

We implement two completely independent audio buses, each with its own:
- `WasapiOut` stream connected to a separate audio device
- `MixingSampleProvider` for voice mixing
- Voice instances (each sound creates a `VoicePair` containing two `Voice` objects)

The `AudioBuffer` (decoded PCM data) is shared read-only between both voices to avoid memory duplication.

## Alternatives Considered

| Approach | Pros | Cons |
|----------|------|------|
| **Dual independent buses (chosen)** | Per-device volume control, no external software for routing, independent fade control | Voice state duplicated, potential clock drift between devices |
| **Single bus + external routing** | Guaranteed sync, simpler code, single Voice per sound | Requires Voicemeeter/VB-Cable setup, no per-device volume control in app |
| **Single bus with code splitter** | Single Voice instance | ISampleProvider contract prevents sharing; would need circular buffer adding complexity without solving sync |
| **Windows audio session routing** | Native Windows API | Can't route one session to two outputs natively; still needs Voicemeeter |

## Rationale

1. **User experience**: Per-device volume control (Monitor vs. Inject) is valuable for balancing what the user hears vs. what goes into calls.

2. **Independence from external software**: While Voicemeeter is still needed for mic routing (see ADR-001), the app can function without it for basic dual-output use cases.

3. **Acceptable overhead**: Memory overhead is ~200 bytes per active sound (Voice metadata only; AudioBuffer is shared). CPU overhead is negligible (~0.0001% for 4 simultaneous sounds).

4. **Clock drift is acceptable for intended use**: Two independent WASAPI streams can drift over time (devices have slightly different sample clocks). However, the app is designed for short SFX (typically 3-10 seconds), where drift is sub-audible. Over 10 seconds at 0.01% drift = 1ms, which is imperceptible.

## Consequences

### Positive
- Per-device volume control works naturally
- Fade-out applies to both outputs simultaneously via `VoicePair.BeginFadeOut()`
- No additional external software required for the dual-output feature itself
- Clean separation of concerns between buses

### Negative
- Voice state is duplicated (two `FadeEnvelope` instances, two position pointers per sound)
- Clock drift between outputs could become audible for long-duration playback (> 60 seconds)
- Architecture doesn't scale cleanly to 3+ output devices (would need refactoring)

### Technical Debt
- **Long-duration audio**: If ambient/background tracks (minutes long) are added, implement clock synchronization or document the limitation
- **Third output**: Would require refactoring `VoicePair` to support N outputs rather than hardcoded pair

## Implementation Notes

```
AudioBuffer (shared, decoded once)
        ↓
    VoicePair
    ├── MonitorVoice → MonitorBus → MixingSampleProvider → WasapiOut → Monitor Device
    └── InjectVoice  → InjectBus  → MixingSampleProvider → WasapiOut → Inject Device
```

Key files:
- `Services/AudioEngine.cs` - Creates and manages both buses and voice pairs
- `Audio/OutputBus.cs` - Single bus implementation (instantiated twice)
- `Audio/Voice.cs` - Individual voice with position tracking and fade envelope
