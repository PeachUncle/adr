# ADR-002: Use LiveSvelte for Rich UI

## Status

Accepted

## Date

2024-12-30

## Context

We need rich, interactive UI components that:
- Feel native and responsive
- Work seamlessly with LiveView
- Support complex interactions (drag-drop, animations)
- Are maintainable with clear component boundaries
- Work well with AI code generation

### Options Considered

1. **Pure LiveView + Alpine.js** — Default Phoenix approach
2. **LiveSvelte** — Svelte components in LiveView
3. **LiveVue** — Vue components in LiveView
4. **Full SPA (SvelteKit)** — Separate frontend application

## Decision

Use **LiveSvelte** to embed Svelte 5 components within LiveView.

## Rationale

| Factor | Pure LiveView | LiveSvelte | LiveVue | Full SPA |
|--------|---------------|------------|---------|----------|
| Rich interactions | Limited | Excellent | Excellent | Excellent |
| Bundle size | Smallest | Small | Medium | Varies |
| Learning curve | Low | Medium | Medium | High |
| AI-friendly syntax | Good | Excellent | Good | Good |
| Server integration | Native | Good | Good | Requires API |
| PWA support | Limited | Good | Good | Excellent |

### Why Svelte over Vue

1. **Cleaner syntax** — Less boilerplate, AI generates more reliably
2. **Smaller bundles** — Compiles away, no runtime
3. **Svelte 5 runes** — Modern reactivity model
4. **Vercel backing** — Long-term investment

### Why Not Full SPA

1. **Added complexity** — Two codebases, two builds
2. **LiveView benefits** — Server-rendered, real-time updates
3. **Team familiarity** — Team knows Phoenix, not SPA architecture
4. **Incremental adoption** — Add Svelte where needed

## Implementation

### Basic Usage

```elixir
# LiveView
def render(assigns) do
  ~H"""
  <.svelte name="RichComponent" props={%{data: @data}} socket={@socket} />
  """
end
```

```svelte
<!-- Svelte component -->
<script>
  export let data = [];
  import { pushEvent } from 'live_svelte';
  export let live = null;
</script>
```

### When to Use Svelte vs Pure LiveView

| Use Svelte | Use Pure LiveView |
|------------|-------------------|
| Complex animations | Simple forms |
| Drag-and-drop | Static content |
| Rich text editors | Simple lists |
| Charts/visualizations | CRUD interfaces |
| Client-side state | Server-driven UI |

## Consequences

### Positive

- Rich interactions without full SPA
- Clean component boundaries
- Excellent developer experience
- Good AI code generation

### Negative

- Two component systems (Phoenix + Svelte)
- Additional build complexity
- LiveSvelte is community-maintained
- Learning curve for Svelte patterns

### Mitigations

- Clear guidelines on when to use each
- Document patterns in COMPONENTS.md
- Monitor LiveSvelte updates
- Svelte components are portable if needed

## References

- [LiveSvelte GitHub](https://github.com/woutdp/live_svelte)
- [Svelte Documentation](https://svelte.dev/docs)
- [Svelte 5 Runes](https://svelte.dev/blog/runes)
