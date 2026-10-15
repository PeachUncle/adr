# ADR-0006: Migrate to Rspack Bundler

**Status:** Accepted (Implemented)  
**Date:** 2026-01-XX  
**Deciders:** Architecture Team  
**Context:** POC-1 - Rspack Migration  
**Supersedes:** ADR-0002 (Use Vite Bundler) for POC-1+

---

## Context

POC-1 requires Hot Module Replacement (HMR) with Module Federation v2 in development mode. The initial decision to use Vite (ADR-0002) was made for POC-0, but during POC-1 implementation, we discovered:

- **Vite + Module Federation v2 limitation:** HMR does not work with Module Federation v2 in dev mode
- **Workflow impact:** Required build → preview → manual refresh cycle, significantly impacting developer experience
- **Primary goal:** Enable HMR with Module Federation v2 for fast development cycles

**Requirements:**

- HMR with Module Federation v2 in dev mode (PRIMARY GOAL)
- Fast dev server startup
- Fast production builds
- TypeScript support
- Module Federation v2 support
- Production-ready
- Excellent developer experience

---

## Decision

Migrate from Vite 6.x to Rspack as the bundler for the MFE platform, starting with POC-1.

**Rationale:**

- Rspack supports HMR with Module Federation v2 (primary requirement)
- Rust-based performance (2-5x faster builds than Vite)
- Webpack-compatible API (easier migration path)
- Production-ready and actively maintained
- Better ecosystem compatibility for Module Federation

---

## Alternatives Considered

### Option 1: Stay with Vite

- **Pros:**
  - Already implemented in POC-0
  - Excellent ecosystem
  - Fast dev server
- **Cons:**
  - ❌ **HMR does not work with Module Federation v2** (blocking issue)
  - Requires build → preview → refresh workflow
  - Poor developer experience for Module Federation development
- **Why Not:** Cannot meet primary requirement (HMR with Module Federation v2)

### Option 2: Webpack 5

- **Pros:**
  - Mature, battle-tested
  - Module Federation v2 support
  - HMR support
  - Large ecosystem
- **Cons:**
  - Slower than Rspack (JavaScript-based)
  - More complex configuration
  - Slower dev server startup
  - Slower HMR updates
- **Why Not:** Rspack provides better performance with Webpack compatibility

### Option 3: Rspack (Chosen)

- **Pros:**
  - ✅ **HMR works with Module Federation v2** (meets primary requirement)
  - Very fast (Rust-based, 2-5x faster than Vite)
  - Webpack-compatible API (easier migration)
  - Module Federation v2 support
  - Production-ready
  - Active maintenance by ByteDance
  - Good TypeScript support
  - Nx integration available (@nx/rspack)
- **Cons:**
  - Newer than Vite (but mature enough)
  - Smaller ecosystem than Vite (but sufficient)
  - Requires migration effort
- **Why Chosen:** Only option that meets the primary requirement (HMR with Module Federation v2) while providing excellent performance.

---

## Trade-offs

### Positive

- ✅ HMR with Module Federation v2 enabled (primary goal achieved)
- ✅ Faster production builds (2-5x faster than Vite)
- ✅ Faster HMR updates
- ✅ Better developer experience for Module Federation development
- ✅ Production-ready and actively maintained

### Negative

- Migration effort required (6 phases, 9-13 days)
- Testing framework migration required (Vitest → Jest)
- Smaller ecosystem than Vite (but sufficient for our needs)
- Team needs to learn Rspack-specific concepts

### Risks

- **Low-Medium Risk:** Migration complexity, but well-documented and manageable
- **Low Risk:** Rspack is production-ready and actively maintained
- **Low Risk:** Webpack-compatible API reduces learning curve

---

## Consequences

### Positive

- ✅ **HMR with Module Federation v2 working** (primary goal achieved)
- Faster development cycles
- Better developer experience
- Faster production builds
- Production-ready solution

### Negative

- Migration effort (completed in Phase 1-5)
- Testing framework migration (Vitest → Jest, completed in Phase 5)
- Configuration changes across all apps and libraries

### Neutral

- Can continue using Rspack for future phases
- Migration is complete and documented

---

## Implementation

**Migration Status:** ✅ Complete (Phase 1-5)

**Migration Details:**

- See `docs/Rspack-Migration/` for complete migration documentation
- All apps and libraries migrated to Rspack
- Testing framework migrated to Jest
- HMR verified working with Module Federation v2

**Key Changes:**

- Bundler: Vite 6.x → Rspack
- Testing: Vitest 4.0 → Jest 30.x
- Config files: `vite.config.mts` → `rspack.config.js`
- Build times: ~37-40s per app (acceptable)
- Bundle sizes: < 500 KB per app (good)

---

## Related Decisions

- **Supersedes:** ADR-0002 (Use Vite Bundler) - Vite remains valid for POC-0, but Rspack is used for POC-1+
- **Related:** ADR-0004 (Use Vitest for Testing) - Superseded by Jest migration for Rspack compatibility
- `docs/Rspack-Migration/rspack-migration-plan.md` - Complete migration plan
- `docs/Rspack-Migration/task-list.md` - Migration progress tracking
- `docs/References/mfe-poc1-tech-stack.md` - Updated tech stack
- `docs/References/mfe-poc1-architecture.md` - Updated architecture

---

## Migration Summary

**Completed:** 2026-01-XX  
**Phases:** 6 phases (1-5 complete, 6 in progress)  
**Status:** ✅ Core migration complete, verification in progress  
**Test Status:** 48 tests verified passing, 3 projects have test discovery issues (needs investigation)

---

**Last Updated:** 2026-01-XX
