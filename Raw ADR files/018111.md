# ADR-0003: TanStack Start Over Next.js as Fullstack Framework

**Status:** Accepted
**Date:** 2025-10-22
**Deciders:** Project maintainers

## Context

The super-claude project needs to recommend a fullstack framework for building complete applications with frontend and backend in a single codebase.

Requirements:

- End-to-end type safety (frontend ↔ backend)
- Modern React patterns (Server Components, Suspense)
- File-based routing
- API/RPC patterns
- Good developer experience
- Strong TypeScript support
- Integration with TanStack ecosystem (Query, Router, Form, Table)

The fullstack framework choice affects:

- tanstack-plugin skills (start-wizard, query-helper, router-helper, form-helper)
- Project scaffolding patterns
- Type safety patterns
- Learning curve for users

## Decision

**Adopt TanStack Start as the primary recommended fullstack framework.**

All fullstack-related skills will:

- Use TanStack Start for project initialization
- Integrate TanStack Router, Query, Form, and Table
- Leverage file-based routing patterns
- Use TanStack RPC for type-safe server functions
- Target modern React (Server Components, Streaming)

## Alternatives Considered

### Option 1: Next.js

**Description:**
Vercel's React framework, industry standard for fullstack React applications.

**Pros:**

- Most popular React framework (huge ecosystem)
- Production-proven at massive scale
- Excellent documentation and learning resources
- Large community and job market relevance
- App Router with Server Components
- Built-in optimizations (image, font, etc.)
- Vercel deployment integration

**Cons:**

- Vercel-specific patterns and lock-in
- Less explicit type safety (RSC/Actions patterns still evolving)
- Mixing React Server Components with client patterns is complex
- TanStack integration requires additional setup
- Opinionated about hosting (Vercel is optimal)
- RPC patterns less type-safe than TanStack RPC

**Decision:** ❌ Rejected

**Rationale:** While Next.js is battle-tested and popular, it doesn't align with our TanStack ecosystem focus. The Vercel lock-in and less explicit type safety (compared to TanStack RPC) make it less suitable for our goals of maximum type safety and TanStack integration.

### Option 2: Remix

**Description:**
Full stack web framework focused on web standards and progressive enhancement.

**Pros:**

- Web standards-focused (forms, HTTP)
- Excellent data loading patterns
- Good TypeScript support
- Server/client patterns well-defined
- Strong focus on performance

**Cons:**

- Less aligned with TanStack ecosystem
- Different routing patterns vs TanStack Router
- RPC less type-safe than TanStack RPC
- Smaller ecosystem than Next.js
- Separate TanStack integration needed

**Decision:** ❌ Rejected

**Rationale:** Remix is excellent but doesn't integrate with the TanStack ecosystem as well as TanStack Start. Our focus on TanStack Suite makes TanStack Start the more logical choice.

### Option 3: TanStack Start

**Description:**
TanStack's fullstack React framework built on TanStack Router with end-to-end type safety.

**Pros:**

- Perfect integration with TanStack Router, Query, Form, Table
- Maximum end-to-end type safety (TanStack RPC)
- Modern React patterns (Server Components, Streaming)
- File-based routing with type inference
- Single ecosystem (consistency across tools)
- Designed for type safety from the ground up
- No vendor lock-in (deploy anywhere)
- Modern architecture (latest React features)

**Cons:**

- Newer/less proven in production (smaller ecosystem)
- Fewer learning resources than Next.js
- Smaller community
- Less job market relevance (currently)
- Still evolving (potential breaking changes)

**Decision:** ✅ Selected

**Rationale:** TanStack Start's perfect integration with the TanStack ecosystem and focus on end-to-end type safety align with our goals. The type-safe RPC and Router patterns are superior to Next.js. While newer, TanStack's track record (Query, Table, Router) gives confidence in Start's future.

### Option 4: Monorepo (Vite + Hono/Elysia)

**Description:**
Build separate frontend (Vite) and backend (Hono/Elysia) in a monorepo.

**Pros:**

- Maximum flexibility
- Best-in-class for each layer
- Can deploy frontend/backend separately
- TypeScript types can be shared via workspace packages

**Cons:**

- More complex setup and configuration
- Need to manage two separate deployments
- Shared types require workspace setup
- More moving parts and potential issues
- Not a "fullstack framework" (manual integration)

**Decision:** ❌ Rejected

**Rationale:** While flexible, a monorepo adds complexity without the benefits of a fullstack framework. TanStack Start provides the same type safety with better DX and simpler deployment. Monorepos are still supported but not the primary recommendation.

## Consequences

### Positive

- **Maximum type safety**: TanStack RPC provides end-to-end types (frontend ↔ backend)
- **Ecosystem consistency**: All TanStack tools work together seamlessly
- **Modern patterns**: Latest React features (Server Components, Suspense, Streaming)
- **File-based routing**: Type-safe routes with automatic type inference
- **No vendor lock-in**: Deploy to any platform (Vercel, Netlify, Cloudflare, etc.)
- **Simpler skills**: tanstack-plugin can focus on one framework

### Negative

- **Smaller ecosystem**: Fewer community examples and resources than Next.js
- **Job market**: Less relevant for job-seeking developers (Next.js dominates)
- **Learning curve**: Users need to learn TanStack patterns (not Next.js)
- **Production risk**: Newer framework, less proven at scale
- **Migration overhead**: Harder to hire developers familiar with TanStack Start

### Neutral

- **Community size**: TanStack ecosystem is growing but smaller than Next.js
- **Documentation**: TanStack Start docs are good but less extensive than Next.js
- **Hosting**: Any platform works, but no Vercel-level integration out of the box

## Implementation Notes

**How will this be enforced?**

- start-wizard skill scaffolds TanStack Start projects
- query-helper, router-helper, form-helper assume TanStack Start
- Documentation and examples use TanStack Start patterns
- Skills reference TanStack Start docs

**When does this take effect?**

- Immediately for all new fullstack work
- Existing Next.js examples should note they're alternative patterns

**What needs to change to comply?**

- tanstack-plugin skills use TanStack Start
- Project scaffolding uses `create-tanstack-start`
- RPC patterns use TanStack RPC (not Next.js Server Actions)
- File routing uses TanStack Router patterns

**Recommended Stack:**

```txt
TanStack Start
├── TanStack Router (file-based routing)
├── TanStack Query (server state)
├── TanStack Form (forms + validation)
├── TanStack Table (data tables)
└── TanStack RPC (type-safe server functions)
```

## References

**Related ADRs:**

- None yet

**OpenSpec Proposals:**

- [tanstack-plugin](../../../openspec/changes/tanstack-plugin/) - Full TanStack ecosystem implementation

**External Resources:**

- [TanStack Start Documentation](https://tanstack.com/start)
- [TanStack Router Documentation](https://tanstack.com/router)
- [TanStack RPC Documentation](https://tanstack.com/query/latest/docs/framework/react/typescript#typing-the-rpcs)

## Notes

**Why TanStack Start over Next.js despite Next.js being more popular?**

1. **Type safety**: TanStack RPC is more type-safe than Next.js Server Actions
2. **Ecosystem alignment**: Using TanStack Query, Router, Form, Table together is smoother
3. **No lock-in**: TanStack Start can deploy anywhere (Next.js optimizes for Vercel)
4. **Modern architecture**: Built for latest React features from the ground up
5. **Consistency**: Single ecosystem reduces context switching

**Migration path:**

If TanStack Start doesn't gain traction or the ecosystem stalls, we can create a next-start-migrator skill to help users migrate to Next.js. The TanStack Query/Router/Form skills can still be valuable with Next.js.

**Monorepo alternative:**

For users who need separate frontend/backend deployments, we'll support Vite + Hono patterns, but won't make it the primary recommendation.
