# ADR-002: Svelte 5 Runes Over Legacy Stores

## Status
Accepted

## Context
Svelte 5 introduces a new reactivity system based on "runes" (`$state`, `$derived`, `$effect`) that replaces the previous reactive declarations (`$:`) and stores (`writable`, `readable`, `derived`).

We need to decide whether to:
1. Use Svelte 5 runes throughout the application
2. Continue using legacy stores and reactive declarations
3. Mix both approaches

Key considerations:
- **Performance**: Fine-grained reactivity vs. coarse-grained
- **Developer Experience**: Modern API vs. familiar patterns
- **Maintainability**: Consistency across codebase
- **Future-proofing**: Svelte's direction going forward

## Decision

We will use **Svelte 5 runes exclusively** throughout the codebase, avoiding legacy stores and reactive declarations.

**What this means:**
- All reactive state uses `$state()`
- All computed values use `$derived()`
- All side effects use `$effect()`
- No `writable()`, `readable()`, or `derived()` stores
- No `$:` reactive declarations

**Exception:** External libraries that export stores can still be used, but we'll wrap them if needed.

## Rationale

### Performance Benefits

**Fine-Grained Reactivity**:
```svelte
<script lang="ts">
  let user = $state({ name: 'Alice', age: 30 })
  let doubled = $derived(user.age * 2)
</script>

<p>{user.name}</p>  <!-- Only updates when name changes -->
<p>{doubled}</p>    <!-- Only updates when age changes -->
```

**Legacy Approach** (coarser):
```svelte
<script lang="ts">
  let user = { name: 'Alice', age: 30 }
  $: doubled = user.age * 2  // Re-runs when ANY part of user changes
</script>
```

### Developer Experience

**Runes are more intuitive:**
- `$state()` clearly indicates mutable state
- `$derived()` explicitly shows computed values
- `$effect()` makes side effects obvious
- No confusion about `$:` placement and ordering

**Better TypeScript integration:**
```typescript
let count = $state(0)           // Type inferred as number
let items = $state<Item[]>([])  // Explicit generic type
```

### Consistency

Using runes exclusively means:
- Single mental model for reactivity
- No mixing of patterns
- Easier onboarding for new developers
- More predictable behavior

### Future-Proofing

Svelte team has indicated:
- Runes are the future of Svelte
- Legacy stores will be maintained but not actively developed
- New features will leverage runes
- Performance improvements will focus on runes

## Examples

### State Management

**Runes (our approach):**
```typescript
// stores/presentation.svelte.ts
class PresentationStore {
  components = $state(new Map())
  timeline = $state([])

  isPlaying = $derived(this.timeline.length > 0)

  addComponent(id: string, component: Component) {
    this.components.set(id, component)
  }
}

export const presentationStore = new PresentationStore()
```

**Legacy stores (avoid):**
```typescript
import { writable, derived } from 'svelte/store'

const components = writable(new Map())
const timeline = writable([])

export const isPlaying = derived(timeline, $timeline => $timeline.length > 0)

export function addComponent(id: string, component: Component) {
  components.update($c => {
    $c.set(id, component)
    return $c
  })
}
```

### Computed Values

**Runes:**
```svelte
<script lang="ts">
  let count = $state(0)
  let doubled = $derived(count * 2)
  let message = $derived(`Count is ${count}`)
</script>
```

**Legacy (avoid):**
```svelte
<script lang="ts">
  let count = 0
  $: doubled = count * 2
  $: message = `Count is ${count}`
</script>
```

### Side Effects

**Runes:**
```svelte
<script lang="ts">
  let sessionId = $state<string>()

  $effect(() => {
    if (sessionId) {
      fetch(`/api/sessions/${sessionId}`)
        .then(r => r.json())
        .then(data => console.log(data))
    }
  })
</script>
```

**Legacy (avoid):**
```svelte
<script lang="ts">
  let sessionId: string

  $: if (sessionId) {
    fetch(`/api/sessions/${sessionId}`)
      .then(r => r.json())
      .then(data => console.log(data))
  }
</script>
```

## Migration Strategy

For existing code using legacy patterns:

1. **Component-level state**: Replace `let x` with `let x = $state()`
2. **Reactive declarations**: Replace `$: y = ...` with `let y = $derived(...)`
3. **Side effects**: Replace `$: { ... }` with `$effect(() => { ... })`
4. **Stores**: Replace with class-based runes stores (see example above)

## Consequences

### Positive
- Improved performance with fine-grained reactivity
- Better developer experience with clear, explicit API
- Stronger TypeScript integration
- Future-proof as Svelte evolves
- Consistent patterns across entire codebase

### Negative
- Learning curve for developers familiar with legacy Svelte
- Less resources/examples online (as of 2024)
- Some Svelte ecosystem libraries still use stores
- Can't easily copy-paste old Svelte code

### Risks & Mitigations
- **Risk**: Breaking changes in Svelte 5 runes
  - **Mitigation**: Pin Svelte version, test thoroughly before upgrading
- **Risk**: Team unfamiliarity with runes
  - **Mitigation**: Comprehensive documentation and code examples
- **Risk**: Third-party stores integration
  - **Mitigation**: Create wrapper utilities to convert stores to runes

## Implementation Guidelines

### DO:
```svelte
<script lang="ts">
  let count = $state(0)
  let doubled = $derived(count * 2)

  $effect(() => {
    console.log('Count changed:', count)
  })
</script>
```

### DON'T:
```svelte
<script lang="ts">
  let count = 0  // Not reactive!
  $: doubled = count * 2  // Legacy syntax

  $: {  // Legacy side effect
    console.log('Count changed:', count)
  }
</script>
```

### Module-Level State:
```typescript
// ✅ Correct - class with runes
class CounterStore {
  count = $state(0)
  doubled = $derived(this.count * 2)
}
export const counter = new CounterStore()

// ❌ Avoid - legacy store
import { writable } from 'svelte/store'
export const counter = writable(0)
```

## Testing Implications

Runes work seamlessly with Testing Library:

```typescript
import { render, screen } from '@testing-library/svelte'
import Counter from './Counter.svelte'

it('updates count on click', async () => {
  const { component } = render(Counter)

  // State updates work as expected
  await userEvent.click(screen.getByRole('button'))

  expect(screen.getByText('Count: 1')).toBeInTheDocument()
})
```

## Related Decisions
- [ADR-001: Technology Stack](./ADR-001-technology-stack.md)
- [ADR-004: Component-Based Presentation DSL](./ADR-004-component-dsl.md)

## References
- [Svelte 5 Runes Documentation](https://svelte-5-preview.vercel.app/docs/runes)
- [Svelte 5 Migration Guide](https://svelte.dev/docs/v5-migration-guide)

## Date
2024-10-15

## Author
Initial project setup
