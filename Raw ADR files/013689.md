# ADR-0004: Use Tailwind CSS v4

**Status:** Accepted  
**Date:** 2026-01-XX  
**Deciders:** Architecture Team  
**Context:** POC-1

---

## Context

POC-1 requires a styling solution. Requirements:
- Latest version (future-proof)
- Fast builds
- Modern CSS features
- Simplified setup
- Production-ready
- Excellent developer experience

**Note:** Tailwind CSS v4 was released in January 2025 and is production-ready. It provides 5x faster full builds and 100x+ faster incremental builds compared to v3.

## Decision

Use Tailwind CSS 4.0+ for styling in POC-1.

## Alternatives Considered

### Option 1: Tailwind CSS v3

- **Pros:**
  - Mature, battle-tested
  - Large ecosystem
  - Extensive documentation
  - Widely used
- **Cons:**
  - Older version (v4 is available)
  - Slower builds (5x slower full builds, 100x+ slower incremental builds)
  - Missing modern CSS features
  - More complex setup
- **Why Not:** v4 is available and provides significantly better performance. v3 is legacy.

### Option 2: CSS Modules

- **Pros:**
  - Simple
  - No dependencies
  - Good TypeScript support
- **Cons:**
  - No utility classes
  - More verbose
  - Less developer productivity
  - Need to write more CSS
- **Why Not:** Tailwind CSS provides better developer productivity with utility classes. CSS Modules require more code.

### Option 3: Styled Components

- **Pros:**
  - CSS-in-JS
  - Good TypeScript support
  - Dynamic styling
- **Cons:**
  - Runtime overhead
  - Larger bundle size
  - More complex setup
  - Less performant than utility classes
- **Why Not:** Tailwind CSS provides better performance with utility classes. Styled Components adds runtime overhead.

### Option 4: Tailwind CSS v4 (Chosen)

- **Pros:**
  - Latest version (released January 2025, production-ready)
  - 5x faster full builds, 100x+ faster incremental builds
  - Modern CSS features (cascade layers, `color-mix()`, container queries)
  - Simplified setup (zero configuration, fewer dependencies)
  - Future-proof (latest version with long-term support)
  - Production-ready
  - Excellent developer experience
- **Cons:**
  - Newer than v3 (but production-ready)
- **Why Chosen:** Best balance of performance, modern features, and developer experience. Provides all required features with excellent performance.

## Trade-offs

- **Pros:**
  - Excellent performance (fast builds)
  - Modern CSS features
  - Simplified setup
  - Future-proof
- **Cons:**
  - Newer than v3 (but production-ready)
  - May need to create more documentation/examples
- **Risks:**
  - Low risk - Tailwind CSS v4 is production-ready
  - Ecosystem may still be catching up (but sufficient)

## Consequences

- **Positive:**
  - Fast builds (5x faster full builds, 100x+ faster incremental builds)
  - Modern CSS features available
  - Simplified setup
  - Future-proof (latest version)
- **Negative:**
  - May need to create more documentation/examples
  - Fewer community examples than v3
- **Neutral:**
  - Can migrate to other styling solutions if needed (unlikely)

## Related Decisions

- `docs/mfe-poc1-architecture.md` - Section 7.4 Tailwind CSS v4
- `docs/mfe-poc1-tech-stack.md` - Tailwind CSS 4.0+ details
- `docs/tailwind-nativewind-compatibility-analysis.md` - Compatibility analysis (for universal MFE)

---

**Last Updated:** 2026-01-XX

