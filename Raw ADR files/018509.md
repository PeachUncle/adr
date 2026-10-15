# ADR-001: Use Static Site Generation

## Status

Accepted

## Context

We need to choose a rendering strategy for this Astro template. Options include:
- Static Site Generation (SSG)
- Server-Side Rendering (SSR)
- Client-Side Rendering (CSR)
- Hybrid approach

For a template focused on privacy, censorship resistance, and IPFS deployment, we need a solution that:
- Works without a server
- Can be deployed to distributed networks
- Has minimal attack surface
- Provides maximum privacy
- Is truly portable

## Decision

We will use **Static Site Generation (SSG)** exclusively.

Configuration:
```javascript
// astro.config.mjs
export default defineConfig({
  output: 'static'
});
```

## Consequences

### Positive

- **No Server Required**: Eliminates entire classes of security vulnerabilities
- **IPFS Compatible**: Static files work perfectly with content addressing
- **Maximum Privacy**: No server-side data collection possible
- **Censorship Resistant**: Static files can be mirrored easily
- **Performance**: Pre-rendered content loads instantly
- **Portability**: Works anywhere (IPFS, CDN, web server, file system)
- **Security**: Reduced attack surface (no backend to compromise)
- **Simplicity**: Easier to audit and understand

### Negative

- **No Dynamic Features**: Can't have user authentication, server-side personalization
- **Build Time**: Must rebuild to update content
- **Client-Side Only**: Any interactivity must be client-side JavaScript
- **No Server APIs**: Can't have backend endpoints (but this is a feature for privacy)

### Mitigations

For use cases requiring dynamic features:
- Use client-side JavaScript for interactivity
- Integrate with decentralized APIs if needed
- Consider Web3 solutions for authentication
- Use IPNS for mutable content pointers
- Implement progressive enhancement

## Alternatives Considered

**Server-Side Rendering (SSR)**
- Rejected: Requires server infrastructure
- Conflicts with IPFS deployment model
- Introduces privacy concerns
- Creates single point of failure

**Hybrid (SSG + SSR)**
- Rejected: Complexity doesn't match use case
- Would require conditional logic based on deployment
- Users might accidentally enable SSR

## References

- [Astro Static Site Generation](https://docs.astro.build/en/guides/content-collections/#building-for-static-output-default)
- [IPFS Documentation](https://docs.ipfs.tech/)
- [Privacy-by-Design Principles](https://en.wikipedia.org/wiki/Privacy_by_design)

## Notes

This decision is fundamental to the template's privacy and censorship-resistance goals. Changing this would require a major version bump and potentially a fork.

---

**Date**: 2025-11-12
**Deciders**: Template Maintainers
**Reviewed**: N/A
