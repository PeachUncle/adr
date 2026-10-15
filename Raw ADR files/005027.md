# ADR-003: React 18 + Vite + TanStack Query for Dashboard

**Status:** Accepted
**Date:** 2025-11-14
**Deciders:** Alice (Architect), Charlie (Developer), Diana (UX Designer)
**Technical Story:** Epic 6 - Story 6-4 (React Dashboard Foundation & API Integration)

## Context and Problem Statement

The Agent Orchestrator needs an interactive dashboard for remote monitoring and management. We need to choose a frontend stack that provides excellent developer experience, fast build times, efficient state management for server data, and React 18's concurrent features.

## Decision Drivers

* Fast development iteration (Hot Module Replacement)
* Efficient server state management (caching, refetching)
* Modern React features (React 18 concurrent rendering)
* Build performance (development and production)
* Type safety with TypeScript
* Developer experience and productivity
* Bundle size optimization

## Considered Options

* **Option 1:** React 18 + Vite + TanStack Query + Zustand
* **Option 2:** React 18 + Create React App + Redux Toolkit + RTK Query
* **Option 3:** Next.js 14 with App Router
* **Option 4:** Vue 3 + Vite + Pinia

## Decision Outcome

**Chosen option:** "React 18 + Vite + TanStack Query + Zustand", because it provides the fastest development experience (Vite HMR), best-in-class server state management (TanStack Query), minimal boilerplate, and full control over build configuration.

### Positive Consequences

* **Vite:** 10x faster dev server startup (instant HMR, <1s cold start)
* **TanStack Query:** Automatic caching, background refetching, optimistic updates, reduces API calls by ~60%
* **Zustand:** Minimal boilerplate for client state (100 lines vs 500+ with Redux)
* **React 18:** Concurrent rendering, automatic batching, Suspense for data fetching
* Full build configuration control (no ejection needed)
* Excellent TypeScript integration
* Smaller bundle size than Redux-based alternatives

### Negative Consequences

* Team needs to learn TanStack Query patterns (minor learning curve)
* Vite ecosystem is newer than webpack (but rapidly maturing)
* Less opinionated than Next.js (more decisions to make)

## Pros and Cons of the Options

### Option 1: React 18 + Vite + TanStack Query + Zustand

Modern, lightweight stack optimized for developer experience and performance.

**Pros:**
* **Vite:** Instant HMR, <1s cold start, 10x faster than CRA
* **TanStack Query:** Best-in-class server state management, automatic caching
* **Zustand:** Minimal boilerplate (3x less code than Redux)
* **React 18:** Latest features (concurrent rendering, automatic batching)
* Full control over build config
* Smaller bundle size
* Excellent TypeScript support

**Cons:**
* Vite ecosystem newer than webpack
* Team learning curve for TanStack Query
* More setup decisions required

### Option 2: Create React App + Redux Toolkit + RTK Query

Traditional, well-established React stack with Redux ecosystem.

**Pros:**
* Well-known patterns (Redux)
* Large community and resources
* Official Redux Toolkit simplifies Redux
* RTK Query handles API state

**Cons:**
* **CRA is deprecated** (no longer maintained by React team)
* Slow build times (webpack-based)
* Redux boilerplate (even with Redux Toolkit)
* Larger bundle size
* Eject required for build customization
* Slower HMR than Vite

### Option 3: Next.js 14 with App Router

Full-stack React framework with server components and routing.

**Pros:**
* Server-side rendering out of the box
* File-based routing
* Server components (React 18 feature)
* Excellent production optimizations
* Opinionated (fewer decisions)

**Cons:**
* **Overkill for our needs** (we don't need SSR)
* More complex deployment
* Opinionated file structure
* Server components add complexity
* Larger initial bundle
* Dashboard is client-side only (no SEO needs)

### Option 4: Vue 3 + Vite + Pinia

Modern Vue stack with Composition API.

**Pros:**
* Excellent developer experience
* Fast build times with Vite
* Pinia is clean state management
* Good TypeScript support
* Smaller learning curve than React

**Cons:**
* **Team expertise is in React**
* Smaller ecosystem than React
* Less suitable for complex dashboards
* Component library options more limited
* Not worth switching from React

## Links

* [Vite Documentation](https://vitejs.dev/)
* [TanStack Query Documentation](https://tanstack.com/query/latest)
* [React 18 Release Notes](https://react.dev/blog/2022/03/29/react-v18)
* [Zustand Documentation](https://github.com/pmndrs/zustand)
* [Epic 6 Retrospective](../epics/epic-6-retrospective.md)
* Implementation: `dashboard/` directory

## Implementation Notes

### Stack Versions
- React: 18.3.1
- Vite: 5.4.3
- TanStack Query: 5.56.2
- Zustand: 4.5.5
- TypeScript: 5.5.4

### TanStack Query Setup
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000, // 30 seconds
      gcTime: 5 * 60 * 1000, // 5 minutes
      retry: 3,
      refetchOnWindowFocus: true,
    },
  },
});
```

### State Management Strategy
- **Server State:** TanStack Query (projects, stories, escalations, etc.)
- **Client State:** Zustand (theme, sidebar state, filters)
- **Form State:** React Hook Form (not Redux)

### Performance Results from Epic 6
- **Dev server start:** <1s (Vite) vs ~30s (CRA)
- **HMR:** <100ms (Vite) vs 2-5s (CRA)
- **API call reduction:** ~60% fewer API calls (TanStack Query caching)
- **Bundle size:** 280KB gzipped (vs 350KB with Redux)
- **First load:** 1.2s (Production, 3G connection)

### Key Learnings from Epic 6
- TanStack Query's cache invalidation on WebSocket events works brilliantly
- Zustand reduced boilerplate by 70% compared to previous Redux implementations
- Vite's dev experience improved team velocity significantly
- React 18's automatic batching reduced re-renders

## Review and Update History

| Date | Reviewer | Change |
|------|----------|--------|
| 2025-11-14 | Alice, Charlie, Diana | Initial decision (Story 6-4) |
| 2025-11-16 | Bob | Documented in ADR with Epic 6 metrics |
