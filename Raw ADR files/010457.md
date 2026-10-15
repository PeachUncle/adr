# ADR 0003: Store-Based State Management

## Status

Accepted

## Context

Lift-Boy needs reactive state management for:
- Real-time UI updates (step grid, waveform display, playback indicators)
- Audio engine synchronization
- Multi-component coordination (keyboard controls, sequencer, synth editor)
- Project persistence

The application is built with Svelte, which provides a built-in store system.

### Requirements

1. **Reactivity**: UI should auto-update when state changes
2. **Centralized**: Avoid prop-drilling through deep component trees
3. **Testable**: State logic should be testable without components
4. **Type-Safe**: TypeScript support
5. **Debuggable**: Easy to inspect current state
6. **Minimal Dependencies**: Use framework features when possible

### Alternatives Considered

#### Alternative 1: Component-Local State

**Approach**: Keep state in component `let` variables.

```svelte
<script>
  let steps = [...];
  let selectedStep = 0;

  function toggleStep(index) {
    steps[index].active = !steps[index].active;
    steps = steps;  // Trigger reactivity
  }
</script>
```

**Pros**:
- Simple, no extra concepts
- Svelte's built-in reactivity
- Fast for small components

**Cons**:
- Hard to share state between components
- Keyboard handler can't access component state
- Audio engine can't subscribe to changes
- Testing requires component mounting
- Prop-drilling for deep hierarchies

**Rejected**: Can't share state across components/modules.

#### Alternative 2: Redux

**Approach**: Use Redux for state management.

```typescript
const store = createStore(rootReducer);

store.dispatch({ type: 'TOGGLE_STEP', index: 0 });
```

**Pros**:
- Well-established pattern
- Excellent debugging tools (Redux DevTools)
- Time-travel debugging
- Middleware support

**Cons**:
- Heavy boilerplate (actions, reducers, selectors)
- Extra dependency
- Svelte's stores are lighter and native
- Overkill for this scale
- Redux DevTools require browser extension

**Rejected**: Too much boilerplate for this use case.

#### Alternative 3: MobX

**Approach**: Observable-based state management.

```typescript
class SequencerStore {
  @observable steps = [];
  @observable selectedStep = 0;

  @action toggleStep(index) {
    this.steps[index].active = !this.steps[index].active;
  }
}
```

**Pros**:
- Less boilerplate than Redux
- Automatic dependency tracking
- Computed values

**Cons**:
- Extra dependency
- Decorators require build configuration
- Svelte stores provide similar features
- Another paradigm to learn

**Rejected**: Svelte stores are simpler and native.

#### Alternative 4: Context API

**Approach**: Svelte's context API for state sharing.

```svelte
<!-- App.svelte -->
<script>
  import { setContext } from 'svelte';
  const state = { steps: [...] };
  setContext('sequencer', state);
</script>

<!-- Child.svelte -->
<script>
  import { getContext } from 'svelte';
  const sequencer = getContext('sequencer');
</script>
```

**Pros**:
- Built into Svelte
- No extra dependencies
- Scoped to component tree

**Cons**:
- Not reactive by default (need writable stores anyway)
- Harder to access from non-components (audio engine, keyboard)
- Context is parent-to-child only
- Testing requires component tree setup

**Rejected**: Doesn't solve reactivity, still need stores.

## Decision

**Use Svelte's writable and derived stores** for all application state.

### Store Organization

```
stores/
├── sequencer.ts       # XOX step sequencer state
├── melody.ts          # Bar sequencer state
├── synth.ts           # FM synth parameters
├── transport.ts       # BPM control
├── playback.ts        # Playback indicators (UI only)
├── navigation.ts      # UI scroll state
├── lanes.ts           # Lane selection
├── projects.ts        # Project persistence
└── laneModuleSync.ts  # Sync layer
```

### Store Patterns

**Writable Stores**:
```typescript
// stores/sequencer.ts
export const steps = writable<StepState[]>([...]);
export const selectedStep = writable<number>(0);
```

**Derived Stores**:
```typescript
export const activeStep = derived(
  [steps, selectedStep],
  ([$steps, $selected]) => $steps[$selected]
);
```

**Helper Functions**:
```typescript
export function toggleStepActive(index?: number) {
  const targetIndex = index ?? get(selectedStep);
  steps.update(s => s.map((step, i) =>
    i === targetIndex ? { ...step, active: !step.active } : step
  ));
}
```

### Component Usage

```svelte
<script>
  import { steps, toggleStepActive } from '$lib/stores/sequencer';
</script>

{#each $steps as step, i}
  <button
    class:active={step.active}
    on:click={() => toggleStepActive(i)}
  >
    {i + 1}
  </button>
{/each}
```

## Rationale

### Why Svelte Stores?

**Native to Framework**: Built into Svelte, no extra dependencies.

**Auto-Subscriptions**: `$store` syntax auto-subscribes/unsubscribes:
```svelte
<div>BPM: {$bpm}</div>
<!-- Automatically subscribes on mount, unsubscribes on unmount -->
```

**Type-Safe**: Works seamlessly with TypeScript:
```typescript
const steps = writable<StepState[]>([]);
// TypeScript knows $steps is StepState[]
```

**Debuggable**: Easy to inspect in console:
```javascript
import { get } from 'svelte/store';
import { steps } from './stores/sequencer';
console.log(get(steps));
```

**Testable**: Can test without components:
```typescript
test('toggleStepActive', () => {
  toggleStepActive(0);
  expect(get(steps)[0].active).toBe(true);
});
```

**Accessible Everywhere**: Stores work in:
- Components (via `$store`)
- Functions (via `get(store)`)
- Audio engine (via `subscribe()`)
- Keyboard handler (via `subscribe()`)

### Why Separate Stores?

**Single Responsibility**: Each store has one concern:
- `sequencer.ts`: Step pattern editing
- `melody.ts`: Bar sequence editing
- `synth.ts`: Synth parameters

**Performance**: Svelte only re-renders components that subscribe to changed stores.

**Clarity**: Import only what you need:
```typescript
import { steps } from './stores/sequencer';  // Not entire state tree
```

### Why Derived Stores?

**Computed Values**: Recalculate only when dependencies change:
```typescript
export const activeStep = derived(
  [steps, selectedStep],
  ([$steps, $selected]) => $steps[$selected]
);
// Only recalculates when steps or selectedStep change
```

**No Redundant State**: Avoid storing computed values:
```typescript
// BAD: Redundant
const steps = writable([...]);
const activeStep = writable(steps[0]);  // Must manually sync!

// GOOD: Derived
const activeStep = derived([steps, selectedStep], ...);  // Auto-syncs
```

### Why Helper Functions?

**Encapsulation**: Hide update logic:
```typescript
// Without helpers
steps.update(s => s.map((step, i) =>
  i === index ? { ...step, active: !step.active } : step
));

// With helpers
toggleStepActive(index);
```

**Type Safety**: Functions can enforce constraints:
```typescript
export function setPatternLength(length: number) {
  const clamped = clamp(length, 1, 64);  // Enforce valid range
  sequencerSettings.update(s => ({ ...s, length: clamped }));
}
```

**Testability**: Test business logic independently:
```typescript
test('setPatternLength clamps to valid range', () => {
  setPatternLength(100);
  expect(get(sequencerSettings).length).toBe(64);
});
```

## Consequences

### Positive

✅ **Reactive**: UI auto-updates on state changes
✅ **Minimal Boilerplate**: No actions, reducers, or selectors
✅ **Type-Safe**: Full TypeScript support
✅ **Testable**: Pure functions, no component mounting needed
✅ **Debuggable**: Simple to inspect in console
✅ **Performant**: Fine-grained reactivity (only affected components re-render)
✅ **Ecosystem**: Works with Svelte's built-in features

### Negative

❌ **No Time-Travel**: Unlike Redux, no built-in undo/redo
❌ **No DevTools**: No browser extension for store inspection
❌ **Manual Sync**: Need `laneModuleSync` to keep editor/project in sync
❌ **Global State**: Stores are singletons (hard to test in parallel)

### Neutral

➖ **Convention-Based**: No enforced patterns (team must agree on conventions)
➖ **Subscriptions**: Must manually unsubscribe in non-component code

## Implementation Notes

### Store Creation Pattern

```typescript
// stores/sequencer.ts
import { writable, derived, get } from 'svelte/store';

// State
export const steps = writable<StepState[]>(createDefaultSteps());
export const selectedStep = writable<number>(0);

// Derived
export const activeStep = derived(
  [steps, selectedStep],
  ([$steps, $selected]) => $steps[$selected]
);

// Actions
export function toggleStepActive(index?: number) {
  const targetIndex = index ?? get(selectedStep);
  steps.update(s => s.map((step, i) =>
    i === targetIndex ? { ...step, active: !step.active } : step
  ));
}

// Snapshot functions
export function getSequencerSnapshot(): SequencerSnapshot { /* ... */ }
export function loadSequencerSnapshot(snapshot?: SequencerSnapshot) { /* ... */ }
```

### Subscription Pattern

**In Components** (auto-unsubscribe):
```svelte
<script>
  import { steps } from '$lib/stores/sequencer';
  // $steps automatically subscribes/unsubscribes
</script>

{#each $steps as step}
  ...
{/each}
```

**In Functions** (manual unsubscribe):
```typescript
import { steps } from '$lib/stores/sequencer';

const unsubscribe = steps.subscribe(value => {
  console.log('Steps changed:', value);
});

// Later...
unsubscribe();
```

### Immutable Updates

**Always use `.update()` or `.set()`**:
```typescript
// GOOD: Immutable
steps.update(s => s.map((step, i) =>
  i === 5 ? { ...step, active: true } : step
));

// BAD: Mutates store value
const current = get(steps);
current[5].active = true;  // ❌ Doesn't trigger reactivity!
```

### Multi-Store Updates

```typescript
export function setPatternLength(length: number) {
  sequencerSettings.update(s => ({ ...s, length }));

  // Clear selection if out of range
  if (get(selectedStep) >= length) {
    selectedStep.set(0);
  }
}
```

## Related Decisions

- [ADR 0001: Lane-Based Architecture](0001-lane-architecture.md) - Lanes use stores for state
- [ADR 0002: Snapshot Serialization](0002-snapshot-serialization.md) - How stores persist

## Future Considerations

### Undo/Redo

Implement history tracking:
```typescript
const history = writable({
  past: [] as SequencerSnapshot[],
  present: createSequencerSnapshot(),
  future: [] as SequencerSnapshot[]
});

export function undo() {
  history.update(h => {
    if (h.past.length === 0) return h;
    const previous = h.past[h.past.length - 1];
    return {
      past: h.past.slice(0, -1),
      present: previous,
      future: [h.present, ...h.future]
    };
  });
}
```

### Store DevTools

Create custom devtools panel:
```typescript
// Store inspector
const storeRegistry = new Map();

export function debugStore(name, store) {
  storeRegistry.set(name, store);
  store.subscribe(value => {
    console.log(`[${name}]`, value);
  });
}

// In stores
debugStore('steps', steps);
debugStore('melody', bars);
```

### Store Persistence Plugin

Auto-save stores to localStorage:
```typescript
function persistentStore<T>(key: string, initial: T) {
  const stored = localStorage.getItem(key);
  const store = writable<T>(stored ? JSON.parse(stored) : initial);

  store.subscribe(value => {
    localStorage.setItem(key, JSON.stringify(value));
  });

  return store;
}

// Usage
const bpm = persistentStore('bpm', 120);
```

### Async Stores

For data fetching:
```typescript
function asyncReadable<T>(
  initial: T,
  fetch: () => Promise<T>
) {
  const { subscribe, set } = writable<T>(initial);

  fetch().then(set);

  return { subscribe };
}

// Usage
const presets = asyncReadable([], fetchPresets);
```

## References

- [Svelte Stores Documentation](https://svelte.dev/docs#run-time-svelte-store)
- [State Management Documentation](../STATE_MANAGEMENT.md)
- [Architecture Overview](../ARCHITECTURE.md)

## Date

2025-01-15
