---
status: 'accepted'
date: 2024-06-15
decision-makers: voder.ai website team
---

# ADR 0001: Use Vite as the Frontend Build Tool

## Context and Problem Statement

Our project requires a modern, fast, and extensible frontend build tool that provides:

- Instant server start and hot module replacement during development.
- Fast rebuilds and optimized production bundles.
- A plugin ecosystem for TypeScript, asset handling, and other common needs.
- Minimal configuration out of the box.

## Decision Drivers

- Development feedback loop speed.
- Production bundle performance and optimization.
- Availability and maturity of ecosystem plugins.
- Simplicity of configuration and maintenance.

## Considered Options

- Rollup
- Webpack
- Vite

## Decision Outcome

Chosen option: "Vite", because it delivers the fastest development experience via a native ESM dev server and HMR, leverages Rollup for production optimizations, and requires minimal configuration.

### Consequences

- Good, because Vite provides near-instant server start and hot-reload alongside zero-config production builds.
- Bad, because Vite is newer and may introduce breaking changes in minor releases (mitigated by lockfile pinning).

### Confirmation

- Verify `npm run dev` starts a hot-reload dev server in under 1 second.
- Verify `npm run build` produces a fully optimized `dist/` folder.

## Pros and Cons of the Options

### Rollup

- Good, because it is mature, supports tree shaking, and has a proven plugin system.
- Bad, because it lacks a built-in dev server and has slower incremental rebuilds.

### Webpack

- Good, because it is highly configurable with a rich ecosystem of loaders and plugins.
- Bad, because configuration complexity is high and rebuild speeds are slower.

### Vite

- Good, because it leverages native ESM for instant server start, offers lightning-fast HMR, and uses Rollup under the hood for production builds.
- Neutral, because it is newer and may evolve rapidly.
- Bad, because occasional breaking changes require minor version updates (mitigated by pinning).

## More Information

- Vite official documentation: <https://vitejs.dev/>
