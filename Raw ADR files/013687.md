# ADR-0001: Use React Router 7

**Status:** Accepted  
**Date:** 2026-01-XX  
**Deciders:** Architecture Team  
**Context:** POC-1

---

## Context

POC-1 requires routing for authentication and payments flows. Requirements:
- TypeScript support
- Route protection/guards
- Production-ready
- Modern features
- Good ecosystem
- Data loading APIs
- Lazy loading support

## Decision

Use React Router 7.x for routing in POC-1.

## Alternatives Considered

### Option 1: React Router 6

- **Pros:**
  - Stable, mature ecosystem
  - Extensive documentation
  - Widely used
  - Proven in production
- **Cons:**
  - Missing modern features (data loaders, etc.)
  - Not the latest version
  - Less TypeScript support than v7
- **Why Not:** Missing modern features that React Router 7 provides. v7 is the future.

### Option 2: TanStack Router

- **Pros:**
  - Excellent TypeScript support
  - Modern architecture
  - Type-safe routing
  - Good performance
- **Cons:**
  - Newer, smaller ecosystem
  - Less documentation
  - Learning curve
  - Less mature than React Router
- **Why Not:** Smaller ecosystem and less mature than React Router. React Router 7 provides similar features with better ecosystem.

### Option 3: Next.js Routing

- **Pros:**
  - File-based routing
  - Excellent DX
  - Built-in optimizations
- **Cons:**
  - Requires Next.js framework
  - Not compatible with Module Federation
  - Overkill for our use case
- **Why Not:** Requires Next.js framework, not compatible with our MFE architecture.

### Option 4: React Router 7 (Chosen)

- **Pros:**
  - Latest version with modern features
  - Excellent TypeScript support
  - Route protection built-in
  - Data loading APIs
  - Production-ready
  - Large ecosystem
  - Used by major companies
- **Cons:**
  - Newer version (less ecosystem maturity than v6)
- **Why Chosen:** Best balance of modern features, TypeScript support, and ecosystem maturity.

## Trade-offs

- **Pros:**
  - Modern routing patterns available
  - Type-safe routing
  - Production-ready
  - Large ecosystem
- **Cons:**
  - Newer version may have fewer community examples
  - Ecosystem may still be catching up
- **Risks:**
  - Low risk - React Router 7 is production-ready
  - Ecosystem maturity may require more documentation creation

## Consequences

- **Positive:**
  - Modern routing patterns available from the start
  - Type-safe routing improves developer experience
  - Future-proof (latest version)
  - Large ecosystem for support
- **Negative:**
  - May need to create more documentation/examples
  - Fewer community examples than React Router 6
- **Neutral:**
  - Migration path exists if needed (unlikely)

## Related Decisions

- `docs/mfe-poc1-architecture.md` - Section 7.1 React Router 7
- `docs/mfe-poc1-tech-stack.md` - React Router 7.x details

---

**Last Updated:** 2026-01-XX

