# ADR 0001: Lane-Based Multi-Voice Architecture

## Status

Accepted

## Context

Lift-Boy needs to support polyphonic playback with multiple independent voices. Each voice should have its own sequencer, melody, and synthesis settings. The system should be extensible to 4+ simultaneous voices.

### Requirements

1. **Independent Sequencing**: Each voice needs independent rhythm and melody patterns
2. **Individual Mixing**: Per-voice volume, pan, and mute/solo
3. **Scalability**: Easy to add/remove voices without affecting others
4. **State Isolation**: Changes to one voice shouldn't impact others
5. **Future Extensibility**: Should support swapping sequencer/synth types per voice

### Alternatives Considered

#### Alternative 1: Monolithic Sequencer

**Approach**: Single global sequencer with channel selection.

```typescript
interface GlobalSequencer {
  steps: StepState[];
  activeChannels: boolean[];  // Which channels to trigger
  channelNotes: number[];     // Note per channel
}
```

**Pros**:
- Simpler state management
- One loop to rule them all
- Easier to keep in sync

**Cons**:
- All voices share the same rhythm pattern
- Hard to have different clock subdivisions per voice
- Mute/solo logic becomes complex
- Can't easily swap sequencer types (e.g., Euclidean vs XOX)
- Scales poorly beyond 4 channels

**Rejected**: Too inflexible for creative use.

#### Alternative 2: Voice Groups with Shared Sequencing

**Approach**: Group voices into rhythm sections that share sequencing.

```typescript
interface VoiceGroup {
  sequencer: Sequencer;
  voices: Voice[];  // Multiple voices per sequencer
}
```

**Pros**:
- Balance between flexibility and simplicity
- Natural grouping (e.g., drums vs bass vs lead)
- Efficient CPU usage

**Cons**:
- Still limits independent control
- Unclear how to handle groups (UI complexity)
- Doesn't solve the "different sequencer types" problem

**Rejected**: Adds complexity without solving core requirements.

## Decision

**Implement per-lane architecture** where each lane is a fully independent voice with its own:
- Rhythm module (sequencer)
- Melody module
- Instrument module (synth)
- Effect module
- Mixer settings (volume, pan, mode)
- Audio nodes (`Tone.Loop`, `FMSynth`, `Gain`, `Panner`)

### Architecture

```
Lane 1: [Rhythm] → [Melody] → [Instrument] → [Effect] → Mixer
Lane 2: [Rhythm] → [Melody] → [Instrument] → [Effect] → Mixer
Lane 3: [Rhythm] → [Melody] → [Instrument] → [Effect] → Mixer
Lane 4: [Rhythm] → [Melody] → [Instrument] → [Effect] → Mixer
                                                           ↓
                                                      Master Out
```

### Implementation

**Audio Engine**:
- Each lane gets a `LaneRuntime` object
- Each runtime has independent Tone.js nodes
- Each runtime has its own `Tone.Loop` (subdivision-based)
- Master `Tone.Transport` provides shared clock

**State Management**:
- Project contains array of `Lane` objects
- Each lane has `modules` object (rhythm, melody, instrument, effect)
- Each module stores its own state as JSON-serializable snapshot
- `laneModuleSync` handles bidirectional sync between editor and project

**UI**:
- LaneSelector component for switching between lanes
- Editor stores (sequencer, melody, synth) represent **current lane** only
- Switching lanes saves current state and loads new lane's state

## Rationale

### Why Per-Lane Loops?

**Independent Timing**: Different lanes can have different clock subdivisions:
- Lane 1: 16th note hi-hats
- Lane 2: 8th note bass
- Lane 3: Quarter note pads

**Mute/Solo Logic**: Simple boolean check in each loop:
```typescript
function shouldPlayLane(runtime: LaneRuntime): boolean {
  const anyLaneSolo = runtimes.some(r => r.mixer.mode === 'solo');
  if (runtime.mixer.mode === 'mute') return false;
  if (anyLaneSolo && runtime.mixer.mode !== 'solo') return false;
  return true;
}
```

**Extensibility**: Adding a lane is just:
1. Create new `Lane` in project
2. Create new `LaneRuntime` in audio engine
3. Start its loop

### Why Module Slots?

**Swappability**: Future modules can be hot-swapped:
```typescript
// Switch from XOX to Euclidean sequencer
lane.modules.rhythm.definitionId = 'rhythm.euclidean';
```

**Consistent Structure**: Every lane has the same shape, simplifying:
- UI rendering (same component structure per lane)
- Audio engine (same node graph per lane)
- Persistence (same schema per lane)

### Why Shared Transport?

**Sync**: All lanes stay in sync despite independent loops because they share `Tone.Transport.bpm`.

**Single BPM Control**: User changes BPM once, affects all lanes.

**Sample-Accurate**: Tone.js handles scheduling internally.

## Consequences

### Positive

✅ **Full Independence**: Each lane is a complete voice
✅ **Easy to Scale**: Add lanes by pushing to `lanes` array
✅ **Solo/Mute Trivial**: Check `runtime.mixer.mode` in loop
✅ **Extensible**: Can swap module types per lane in future
✅ **Testable**: Each lane can be tested in isolation
✅ **Clear Ownership**: No ambiguity about which lane owns which state

### Negative

❌ **Pointer Management**: Each lane has its own `stepPointer` and `melodyPointer` to track
❌ **State Duplication**: Editor stores + project stores + lane runtimes (mitigated by sync layer)
❌ **Memory Usage**: More Tone.js nodes (4 synths vs 1 polyphonic synth)
❌ **Complexity**: `laneModuleSync.ts` needs bidirectional sync with guard flag

### Neutral

➖ **12 Lane Limit**: Current implementation supports up to 12 lanes (defined in `PROJECT_LANE_LIMIT`)
➖ **CPU Usage**: Multiple loops and synths (acceptable on modern hardware)

## Implementation Notes

### LaneRuntime Structure

```typescript
interface LaneRuntime {
  laneId: string;
  laneIndex: number;

  // Audio nodes
  synth: Tone.FMSynth;
  gainNode: Tone.Gain;
  pannerNode: Tone.Panner;

  // Timing
  loop: Tone.Loop | null;
  stepPointer: number;
  melodyPointer: number;

  // State (cached from lane)
  sequencer: SequencerSnapshot;
  melody: MelodySnapshot;
  synth: SynthSnapshot;
  mixer: MixerSettings;
}
```

### Sync Pattern

**Edit → Persist**:
```
User edits step → sequencer store updates →
laneModuleSync detects change → updateModuleState() →
projects store updates → localStorage saves
```

**Switch Lane**:
```
User selects lane 2 → persistLaneState(0) →
save lane 0 to project → applyLaneState(1) →
load lane 1 from project → editor stores update
```

## Related Decisions

- [ADR 0002: Snapshot Serialization](0002-snapshot-serialization.md) - How lane state is persisted
- [ADR 0003: Store-Based State Management](0003-store-based-state.md) - How state flows through system

## Future Considerations

### Lane Chains

Allow routing lanes into each other:
```
Lane 1 (Drums) → Lane 2 (Bus FX) → Master Out
Lane 3 (Bass)  ↗
```

**Not implemented**: Current design mixes all lanes at master.

### Polyphonic Instruments

Use `Tone.PolySynth` instead of `FMSynth` for chords:
```typescript
if (instrument.definitionId === 'instrument.poly-synth') {
  runtime.synth = new Tone.PolySynth(Tone.FMSynth);
}
```

**Not implemented**: All current modules are monophonic.

### Per-Lane Tempo

Different BPM per lane (polyrhythms):
```typescript
runtime.loop.playbackRate = lane.tempoMultiplier;
```

**Not implemented**: All lanes share global BPM.

## References

- [Tone.js Loop Documentation](https://tonejs.github.io/docs/14.7.77/Loop)
- [Audio Engine Documentation](../AUDIO_ENGINE.md)
- [State Management Documentation](../STATE_MANAGEMENT.md)

## Date

2025-01-15
