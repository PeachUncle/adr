# ADR: Development Toolchain

> **Warning:** This ADR was migrated from pre-documentation-standards decisions. Do not use as a template for new ADRs. See `TEMPLATE.md` instead.

> Date: 2025-12-04
> Status: **Adopted**

## Context

musix.js requires a modern development toolchain that supports TypeScript-first development, fast iteration cycles, and produces high-quality outputs for both ESM and CommonJS consumers.

## Decision Drivers

- Fast development cycle (build, test, lint)
- Native TypeScript support without extra configuration
- ESM and CommonJS dual output support
- Modern tooling with active maintenance
- Minimal configuration complexity

## Options Considered

### Runtime
- **Option 1:** Node.js
- **Option 2:** Bun

### Bundler
- **Option 1:** tsup
- **Option 2:** tsdown
- **Option 3:** Rollup
- **Option 4:** esbuild
- **Option 5:** Bunup

### Test Framework
- **Option 1:** Vitest
- **Option 2:** Bun Test

### Linter/Formatter
- **Option 1:** ESLint + Prettier
- **Option 2:** Biome

## Decisions

| Category | Decision |
|----------|----------|
| Runtime | **Bun** |
| Bundler | **tsdown** |
| Module Format | **Dual (ESM + CommonJS)** |
| TypeScript Target | **ESNext** |
| Test Framework | **Bun Test** |
| Linter/Formatter | **Biome** |

## Rationale

### Runtime: Bun

- Development environment only (does not affect end users)
- Significantly faster than Node.js for development tasks
- Native TypeScript support without transpilation
- NAPI-RS nearly fully supported (required for tsdown's Rolldown backend)

### Bundler: tsdown

- Backed by VoidZero (Vite/Rolldown maintainers)
- Rolldown-based for high performance
- tsup-compatible API for easy migration if needed
- Actively maintained with growing adoption
- Experimental on Bun but technically feasible via NAPI-RS compatibility

### Test Framework: Bun Test

- Fast execution in Bun environment
- Unified tooling with the runtime
- API mocking (our primary use case) is well-supported
- Fake timers incomplete but not needed for this library
- Migration to Vitest possible if requirements change

### Linter/Formatter: Biome

- Single tool for both linting and formatting
- Significantly faster than ESLint + Prettier
- Simple configuration
- TypeScript-first design

### Module Format: Dual

- ESM for modern consumers
- CommonJS for legacy compatibility
- Broader ecosystem support

### TypeScript Target: ESNext

- Can be adjusted later if needed
- Allows use of latest language features
- Bundler handles downleveling for outputs

## Consequences

**Positive:**
- Fast development feedback loop
- Minimal configuration files
- Modern, actively maintained tools
- Unified tooling reduces context switching

**Negative:**
- Bun ecosystem less mature than Node.js
- tsdown is newer with smaller community
- Some Bun-specific quirks may require workarounds

**Risks:**
- tsdown experimental status on Bun - Mitigated by NAPI-RS compatibility and tsup fallback option
- Bun Test limitations - Mitigated by straightforward migration path to Vitest if needed

## Related Decisions

- [20251204-package-design.md](./20251204-package-design.md)
- [20251204-development-process.md](./20251204-development-process.md)
