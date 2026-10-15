# ADR-002: Dual Build Modes

**Status**: Accepted
**Date**: 2026-01-03

## Context

QuizzMe serves two distinct user segments:

1. **Offline-first users**: Need full functionality without server dependency (privacy-conscious, poor connectivity, self-hosted)
2. **Full-feature users**: Want cloud storage, auth, and compute-intensive astro calculations

A single deployment model cannot satisfy both. Static export breaks server features; server-only deployment excludes offline users.

## Decision

Support **two deployment modes** from the same codebase:

### Mode A: Static Export ("Buffet")

```bash
npm run build:static
```

- Output: Pure HTML/JS/CSS, deployable to any CDN
- No API routes bundled
- Storage: LocalStorage only
- Astro features: Disabled/hidden
- Auth: Not available

### Mode B: Server Deploy ("A-la-carte")

```bash
npm run build:server && npm run start
```

- Output: Next.js server with API routes
- Full API route availability
- Storage: Supabase
- Astro features: Full compute via Cosmic Bridge
- Auth: Supabase Auth

### Implementation

1. **Environment detection**: `process.env.NEXT_PUBLIC_BUILD_MODE`
2. **Feature flags**: Derive UI state from build mode
3. **Conditional exports**: API routes excluded from static build
4. **Graceful degradation**: UI hides unavailable features, never shows broken links

```typescript
// Example feature detection
const isServerMode = process.env.NEXT_PUBLIC_BUILD_MODE === 'server';
const features = {
  astroCompute: isServerMode,
  cloudSync: isServerMode,
  auth: isServerMode,
};
```

## Consequences

### Positive

- **Wider adoption**: Serve both offline and cloud users
- **Progressive enhancement**: Start static, upgrade to server
- **CDN deployment**: Static build works on Netlify, Vercel, GitHub Pages
- **Development parity**: Same codebase, different feature sets

### Negative

- **Testing burden**: Must test both modes in CI
- **Conditional complexity**: Components must handle both states
- **Documentation overhead**: Two deployment paths to explain

### Risks

- **Silent failures**: If mode detection fails, features may break silently
- **Mitigation**: CI static build check ensures no API route dependencies

## CI Validation

```yaml
# Required CI checks
- name: Static Build Check
  run: npm run build:static

- name: Server Build Check
  run: npm run build:server
```

## References

- [Next.js Static Export](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
