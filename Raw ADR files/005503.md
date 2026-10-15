# ADR-001: Technology Stack Selection

## Status
Accepted

## Context
We need to select a technology stack for building an AI-powered presentation system that:
- Generates dynamic presentations from AI agent reasoning
- Provides smooth, performant user interface with complex interactions
- Integrates AI agents with UI control tools
- Supports voice narration and speech input
- Enables fast development iteration

Key requirements:
- Modern, reactive frontend framework with excellent DX
- Strong TypeScript support for type safety
- AI agent framework with tool calling capabilities
- Browser-native speech APIs to minimize latency
- Node.js backend for seamless full-stack development

## Decision

We will use the following technology stack:

**Frontend:**
- **SvelteKit 2**: Full-stack framework with SSR and routing
- **Svelte 5 (runes)**: Fine-grained reactivity with modern API
- **Tailwind CSS 4**: Utility-first styling with excellent performance
- **TypeScript 5**: Strong typing throughout the application

**AI Agent:**
- **LangGraph.js**: Agentic workflow framework with state management
- **Claude 3.5 Sonnet**: Advanced reasoning via Anthropic API
- **Zod**: Runtime schema validation for agent outputs

**Speech:**
- **Web Speech API**: Browser-native TTS and STT

**Development:**
- **Vite 7**: Fast build tool and dev server
- **pnpm**: Fast, disk-efficient package manager
- **Playwright**: E2E testing framework

## Rationale

### Why SvelteKit + Svelte 5?

**Pros:**
- **Performance**: Compiles to vanilla JS, no virtual DOM overhead
- **Simplicity**: Less boilerplate than React/Vue
- **Svelte 5 Runes**: Modern reactivity primitives (`$state`, `$derived`, `$effect`)
- **Built-in features**: Routing, SSR, API routes in one framework
- **TypeScript**: First-class TypeScript support
- **Bundle size**: Smaller bundles than React/Vue equivalents

**Alternatives Considered:**
- **Next.js/React**: More verbose, larger bundles, React complexity
- **Nuxt/Vue**: Good option, but Svelte 5 has better DX and performance
- **Solid.js**: Excellent performance but smaller ecosystem

### Why LangGraph.js?

**Pros:**
- **Structured agents**: ReAct pattern with built-in state management
- **Tool calling**: First-class support for function calling
- **Observability**: Easy to debug agent reasoning
- **Extensible**: Custom tools and state management
- **TypeScript**: Full TypeScript support

**Alternatives Considered:**
- **Raw Anthropic SDK**: Too low-level, would need to build state management
- **LangChain.js**: More complex than needed, LangGraph is newer and simpler
- **Vercel AI SDK**: Good but less structured than LangGraph for agentic workflows

### Why Claude 3.5 Sonnet?

**Pros:**
- **Strong reasoning**: Excellent at complex multi-step planning
- **Tool use**: Best-in-class function calling accuracy
- **Fast**: Lower latency than GPT-4 Turbo
- **Context window**: 200K tokens enables conversation history

**Alternatives Considered:**
- **GPT-4**: Good but higher latency and cost
- **GPT-4o**: Fast but less reliable tool calling than Claude
- **Open-source models**: Not yet capable enough for complex reasoning

### Why Web Speech API?

**Pros:**
- **Zero latency**: Local browser synthesis, no network calls
- **Free**: No API costs for TTS
- **Browser-native**: Works in Chrome, Edge, Safari
- **Voices**: Multiple high-quality voices available

**Cons:**
- **Voice quality**: Not as natural as Eleven Labs or Azure TTS
- **Browser dependency**: Limited voice selection in some browsers

**Alternatives Considered:**
- **Eleven Labs**: Excellent quality but adds latency and cost
- **Azure TTS**: Good quality but requires API calls
- **Decision**: Start with Web Speech API, migrate to external TTS if quality becomes issue

### Why Tailwind CSS 4?

**Pros:**
- **Productivity**: Fast styling without context switching
- **Performance**: Purged CSS is tiny
- **Consistency**: Design system through configuration
- **Vite plugin**: First-class Vite integration in v4

**Alternatives Considered:**
- **CSS Modules**: More verbose, harder to maintain consistency
- **Styled Components**: Runtime overhead, doesn't fit Svelte philosophy
- **Plain CSS**: Lacks design system, harder to maintain

## Consequences

### Positive
- Fast development velocity with modern tooling
- Excellent performance with Svelte's compiler approach
- Strong type safety throughout the stack
- Smooth user experience with fine-grained reactivity
- Zero-cost TTS with browser APIs

### Negative
- Svelte 5 is relatively new (runes released 2024)
- Smaller community than React (but growing)
- Web Speech API voice quality is not premium
- LangGraph.js ecosystem is still maturing

### Risks & Mitigations
- **Risk**: Svelte 5 breaking changes
  - **Mitigation**: Lock to specific versions, follow release notes
- **Risk**: LangGraph.js bugs or breaking changes
  - **Mitigation**: Pin versions, contribute fixes upstream
- **Risk**: Claude API changes
  - **Mitigation**: Abstract LLM provider interface for future swaps

## Implementation Notes
- Use strict TypeScript configuration (`strict: true`)
- Follow Svelte 5 runes patterns (avoid legacy stores)
- Implement Zod schemas for all agent outputs
- Use Vite for fast HMR and build times
- Configure Tailwind with custom design tokens

## Related Decisions
- [ADR-002: Svelte 5 Runes Over Legacy Stores](./ADR-002-svelte-runes.md)
- [ADR-003: LangGraph ReAct Agent Pattern](./ADR-003-langgraph-agent.md)
- [ADR-004: Component-Based Presentation DSL](./ADR-004-component-dsl.md)

## Date
2024-10-15

## Author
Initial project setup
