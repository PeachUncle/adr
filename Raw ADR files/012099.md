# ADR: Package Design

> **Warning:** This ADR was migrated from pre-documentation-standards decisions. Do not use as a template for new ADRs. See `TEMPLATE.md` instead.

> Date: 2025-12-04
> Status: **Adopted**

## Context

musix.js needs a clear package structure that supports multiple music service adapters while maintaining a clean, tree-shakeable architecture. The design should allow consumers to import only what they need.

## Decision Drivers

- Tree-shaking support for minimal bundle size
- Clear separation between adapters
- Intuitive import paths for consumers
- Minimal external dependencies
- Extensible architecture for future adapters

## Options Considered

### Package Name
- **Option 1:** `musix.js`
- **Option 2:** `musix`
- **Option 3:** `@musix/core`

### Entry Point Strategy
- **Option 1:** Single entry point
- **Option 2:** Subpath exports

### Dependency Policy
- **Option 1:** Minimize dependencies
- **Option 2:** Prioritize convenience

### Directory Structure
- **Option 1:** Flat structure
- **Option 2:** Feature-based structure
- **Option 3:** Adapter-centric structure

## Decisions

| Category | Decision |
|----------|----------|
| Package Name | **musix** |
| Public Scope | **public** (npm) |
| Entry Points | **Subpath exports** |
| Dependency Policy | **Minimize** |
| Directory Structure | **Adapter-centric** |

## Rationale

### Package Name: musix

- Simple and memorable
- Available on npm
- No scope prefix needed for a standalone library

### Entry Points: Subpath Exports

Enables selective imports:
```typescript
import { SpotifyAdapter } from 'musix/spotify';
import { AppleMusicAdapter } from 'musix/apple-music';
```

Benefits:
- Consumers only bundle adapters they use
- Dependencies isolated per adapter
- Clear mental model for users

### Dependency Policy: Minimize

- Keep the library lightweight
- Reduce security surface area
- Avoid dependency conflicts in consumer projects
- Easier to maintain long-term

### Directory Structure: Adapter-Centric

```
src/
├── core/           # Shared types, errors, interfaces
└── adapters/       # Service adapters
    ├── spotify/
    ├── apple-music/
    └── youtube-music/
```

Benefits:
- Clear ownership of code per adapter
- Easy to add new adapters
- Shared code in `core/` prevents duplication
- Maps directly to subpath exports

## Consequences

**Positive:**
- Minimal bundle size for consumers
- Clear separation of concerns
- Easy to add new adapters independently
- No dependency bloat

**Negative:**
- More complex package.json exports configuration
- Consumers must import from specific subpaths

**Risks:**
- Subpath exports require Node.js 12.7+ or bundler support - Acceptable as the target audience uses modern tooling

## Related Decisions

- [20251204-development-toolchain.md](./20251204-development-toolchain.md)
- [20251202-api-design.md](./20251202-api-design.md)
