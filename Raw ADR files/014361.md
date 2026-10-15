---
title: 'ADR-0009: Enable React Compiler for Portfolio App'
description: 'Decision to enable the experimental React Compiler (React 19) for the Portfolio App to optimize performance and adopt modern React patterns.'
sidebar_position: 9
tags: [architecture, adr, portfolio-app, react, performance, optimization]
---

## Purpose

Record the decision to enable the **React Compiler** (experimental React 19 feature) in the Portfolio App's Next.js configuration.

## Scope

### In scope

- React Compiler enablement and configuration
- Performance optimization rationale
- Build and runtime implications
- Validation and rollback criteria

### Out of scope

- Detailed compiler internals (refer to React documentation)
- Manual optimization techniques that the compiler obviates

## Prereqs / Inputs

- Decision owner(s): Portfolio maintainer
- Date: 2026-01-13
- Status: Implemented (enabled in `next.config.ts`)
- Related artifacts:
  - Portfolio App architecture: `docs/60-projects/portfolio-app/architecture.md`
  - Stack ADR: ADR-0005 (Next.js + TypeScript)

## Decision Record

### Title

ADR-0009: Enable React Compiler for Portfolio App

### Context

React 19 introduces an experimental compiler that automatically optimizes React components by:

- Memoizing components and hooks intelligently
- Reducing manual `useMemo` and `useCallback` boilerplate
- Improving runtime performance for interactive UI

The Portfolio App is a public-facing demonstration of modern web engineering practices. Enabling the React Compiler:

- Signals awareness of cutting-edge React ecosystem developments
- Provides measurable performance benefits (reduced re-renders, optimized bundles)
- Aligns with the "modern full-stack" narrative in the portfolio

Next.js 15+ supports React Compiler via the `reactCompiler` configuration option.

### Decision

Enable the React Compiler in the Portfolio App:

- Configuration: `next.config.ts` → `reactCompiler: true`
- Dependency: `babel-plugin-react-compiler` in `devDependencies`
- Scope: All React components in the app

Constraints:

- Monitor build performance and output size
- Treat compiler regressions as high-priority defects
- Document any compiler-specific workarounds or patterns

### Alternatives considered

1. **Manual optimization with useMemo/useCallback**
   - Pros: Explicit control, well-understood patterns
   - Cons: Boilerplate, maintenance overhead, easy to miss optimization opportunities
   - Not chosen: Compiler provides more comprehensive and consistent optimization

2. **Defer compiler adoption until stable**
   - Pros: Lower risk, fewer edge cases
   - Cons: Misses opportunity to demonstrate modern React adoption; performance remains suboptimal
   - Not chosen: Portfolio benefits from early adoption signal and performance gains outweigh experimental risk

3. **Selective compiler adoption (opt-in per component)**
   - Pros: Gradual rollout, isolated risk
   - Cons: Increased configuration complexity, inconsistent optimization
   - Not chosen: Full enablement is simpler and aligns with modern defaults

### Consequences

#### Positive consequences

- Improved runtime performance (fewer unnecessary re-renders)
- Reduced manual optimization code (cleaner components)
- Modern React ecosystem alignment (demonstrates awareness of latest patterns)
- Better developer experience (less cognitive overhead for optimization)

#### Negative consequences / tradeoffs

- Experimental feature risk (potential compiler bugs or edge cases)
- Build complexity (additional Babel transformation step)
- Debugging complexity (compiler-generated code may be harder to trace)
- Future migration risk if compiler API changes

#### Operational impact

- CI build times may increase slightly due to compilation step
- Must validate that builds remain deterministic and reproducible
- Compiler errors/warnings should be treated as CI failures

#### Security impact

- No direct security impact
- Supply chain: `babel-plugin-react-compiler` is an additional dependency (covered by Dependabot)

### Implementation notes

Configuration in `next.config.ts`:

```typescript
const nextConfig: NextConfig = {
  reactCompiler: true,
};
```

Dependency in `package.json`:

```json
{
  "devDependencies": {
    "babel-plugin-react-compiler": "1.0.0"
  }
}
```

No component-level changes required; compiler optimizes automatically.

## Validation / Expected outcomes

- Build succeeds locally and in CI
- No runtime regressions in preview or production
- Performance improvements measurable via:
  - React DevTools Profiler (reduced re-renders)
  - Bundle size analysis (optimized output)
  - Lighthouse/PageSpeed scores (maintained or improved)

Rollback criteria:

- Critical build failures attributable to compiler
- Performance regressions in production
- Unresolvable compiler bugs blocking releases

Rollback action:

- Set `reactCompiler: false` in `next.config.ts`
- Remove `babel-plugin-react-compiler` from devDependencies
- Document reason in this ADR's "Status" section

## Failure modes / Troubleshooting

- **Build fails with compiler errors:**
  - Check component patterns for compiler incompatibilities
  - Review compiler warnings/errors in build logs
  - Consult React Compiler documentation for workarounds
  - If unresolvable: disable compiler and file upstream issue

- **Runtime regressions after compiler enablement:**
  - Profile with React DevTools to identify problematic components
  - Validate build artifacts for unexpected transformations
  - If severe: rollback and investigate offline

- **Increased build times:**
  - Monitor CI job duration; acceptable if < 20% increase
  - If excessive: consider selective compiler adoption or investigate build caching

## References

- React Compiler documentation: https://react.dev/learn/react-compiler
- Next.js configuration: https://nextjs.org/docs/app/api-reference/next-config-js/reactCompiler
- Portfolio App architecture: `docs/60-projects/portfolio-app/architecture.md`
- Stack ADR: `docs/10-architecture/adr/adr-0005-portfolio-app-stack-nextjs-ts.md`
