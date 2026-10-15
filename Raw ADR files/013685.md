# ADR-0002: Use Vite Bundler

**Status:** Superseded (POC-1+)  
**Date:** 2026-01-XX  
**Deciders:** Architecture Team  
**Context:** POC-0  
**Superseded By:** ADR-0006 (Migrate to Rspack Bundler) for POC-1+

> **Note:** This ADR remains valid for POC-0. For POC-1+, see ADR-0006 which supersedes this decision to enable HMR with Module Federation v2.

---

## Context

POC-0 requires a bundler for web microfrontends. Requirements:

- Fast dev server (instant startup)
- Excellent HMR (near-instant updates)
- Fast production builds
- Native ESM support
- TypeScript support
- Module Federation v2 support
- Production-ready
- Excellent developer experience

**Note:** For universal MFE (web + mobile), Rspack was chosen due to React Native Web compatibility. For MFE, Vite is the better choice.

## Decision

Use Vite 6.x as the bundler for MFE platform.

## Alternatives Considered

### Option 1: Webpack 5

- **Pros:**
  - Mature, battle-tested
  - Large ecosystem
  - Extensive documentation
  - Module Federation v1.5 support
- **Cons:**
  - Slower dev server
  - Slower HMR
  - Slower production builds
  - More complex configuration
  - Module Federation v2 support is newer
- **Why Not:** Performance is significantly worse than Vite. Dev experience is slower.

### Option 2: Rspack

- **Pros:**
  - Very fast (Rust-based)
  - Webpack-compatible
  - Good performance
  - Module Federation v2 support
- **Cons:**
  - Newer, smaller ecosystem
  - Less documentation
  - Less mature than Vite
  - Primarily designed for React Native (Re.Pack)
- **Why Not:** Vite has better ecosystem, documentation, and developer experience for projects. Rspack is better suited for React Native projects.

### Option 3: esbuild

- **Pros:**
  - Extremely fast (Go-based)
  - Simple configuration
  - Good for production builds
- **Cons:**
  - No dev server (would need to build one)
  - No HMR (would need to build one)
  - Less ecosystem
  - Not production-ready as standalone bundler
- **Why Not:** esbuild is a build tool, not a complete bundler solution. Vite uses esbuild internally but provides a complete dev experience.

### Option 4: Vite (Chosen)

- **Pros:**
  - Fast dev server (instant startup)
  - Excellent HMR (near-instant updates)
  - Fast production builds (esbuild + Rollup)
  - Native ESM (modern JavaScript)
  - Excellent TypeScript support
  - Large plugin ecosystem
  - Module Federation v2 support
  - Production-ready
  - Excellent developer experience
  - Used by major companies
  - Active maintenance
- **Cons:**
  - Newer than Webpack (but mature enough)
- **Why Chosen:** Best balance of performance, developer experience, and ecosystem. Provides all required features with excellent performance.

## Trade-offs

- **Pros:**
  - Excellent performance (dev and build)
  - Excellent developer experience
  - Modern tooling (ESM, TypeScript)
  - Production-ready
- **Cons:**
  - Newer than Webpack (but mature)
- **Risks:**
  - Low risk - Vite is production-ready and widely used
  - Module Federation v2 support is newer but stable

## Consequences

- **Positive:**
  - Fast development cycles
  - Excellent developer experience
  - Modern JavaScript/TypeScript support
  - Production-ready builds
- **Negative:**
  - Team may need to learn Vite-specific concepts
- **Neutral:**
  - Can migrate to other bundlers if needed (unlikely)

## Related Decisions

- `docs/mfe-poc0-architecture.md` - Section 2.2 Technology Stack
- `docs/mfe-poc0-tech-stack.md` - Vite 6.x details
- ADR-0003: Use Module Federation v2

---

**Last Updated:** 2026-01-XX
