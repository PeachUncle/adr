# ADR: Spotify API Client

> Date: 2025-12-20
> Status: **Adopted**

## Context

musix.js needs a Spotify API client to implement the Spotify adapter. The client must support Client Credentials Flow authentication, track/album/artist/playlist retrieval, search functionality, and automatic token refresh. It must work with the Bun runtime.

## Decision Drivers

- TypeScript-first with excellent type definitions
- Support for Client Credentials Flow
- Automatic token refresh
- Minimal dependencies for security and bundle size
- Active maintenance and official support preferred

## Options Considered

- **Option 1:** @spotify/web-api-ts-sdk (Official Spotify SDK)
- **Option 2:** Direct API (Native fetch with manual implementation)
- **Option 3:** @ekwoka/spotify-api
- **Option 4:** spotify-web-api-node

## Evaluation

See `evaluation-criteria.md` for criteria definitions.

| Criterion | Weight | Official SDK | Direct API | @ekwoka | web-api-node |
|-----------|--------|--------------|------------|---------|--------------|
| Functional Fit | 25% | 4 (1.00) | 4 (1.00) | 2 (0.50) | 4 (1.00) |
| TypeScript Support | 20% | 5 (1.00) | 3 (0.60) | 5 (1.00) | 3 (0.60) |
| Lightweight | 15% | 2 (0.30) | 5 (0.75) | 5 (0.75) | 1 (0.15) |
| Security | 15% | 4 (0.60) | 2 (0.30) | 2 (0.30) | 3 (0.45) |
| Documentation | 15% | 3 (0.45) | 5 (0.75) | 3 (0.45) | 3 (0.45) |
| Ecosystem | 10% | 3 (0.30) | 3 (0.30) | 1 (0.10) | 2 (0.20) |
| **Total** | 100% | **3.65** | **3.70** | **3.10** | **2.85** |

## Decision

Adopt **@spotify/web-api-ts-sdk** (Official Spotify SDK).

## Rationale

Although Direct API scored slightly higher (3.70 vs 3.65), the Official SDK was chosen for the following reasons:

1. **Official Support**: Maintained by Spotify, ensuring alignment with API changes
2. **TypeScript Excellence**: TS-first design with embedded types, no @types package needed
3. **Zero Dependencies**: No transitive vulnerability risks
4. **Built-in Token Refresh**: Automatic token management reduces implementation complexity
5. **Lower Risk**: Direct API approach requires OAuth expertise to implement securely

The Direct API approach would require significant development effort and carries security risks from manual OAuth implementation.

## Consequences

**Positive:**
- Complete TypeScript type coverage out of the box
- No external HTTP library dependencies
- Automatic token refresh reduces adapter complexity
- Official SDK ensures compatibility with Spotify API updates

**Negative:**
- Bundle size is larger than minimal custom implementation
- Limited tree-shaking due to class-based architecture
- Last update was 2 years ago (maintenance concern)

**Risks:**
- Maintenance stall: Monitor GitHub activity; fallback to Direct API if SDK becomes incompatible with Spotify API changes
- Bun compatibility: Not explicitly tested; verify during implementation

## Confirmation

- Spotify adapter passes all acceptance criteria in spec
- No TypeScript errors in adapter implementation
- Token refresh works correctly in integration tests

## Related Decisions

- [20251204-development-toolchain.md](./20251204-development-toolchain.md) - Bun runtime
- [20251202-api-design.md](./20251202-api-design.md) - Error handling patterns

## Resources

| Option | Documentation | Repository |
|--------|---------------|------------|
| @spotify/web-api-ts-sdk | [Blog](https://developer.spotify.com/blog/2023-07-03-typescript-sdk) | [GitHub](https://github.com/spotify/spotify-web-api-ts-sdk) |
| Direct API | [Spotify Docs](https://developer.spotify.com/documentation/web-api) | N/A |
| @ekwoka/spotify-api | [Docs](https://thekwoka.net/packages/spotify-api) | [GitHub](https://github.com/ekwoka/spotify-api) |
| spotify-web-api-node | [Docs](http://thelinmichael.github.io/spotify-web-api-node/) | [GitHub](https://github.com/thelinmichael/spotify-web-api-node) |

## Sources

- [Introducing the TypeScript SDK | Spotify for Developers](https://developer.spotify.com/blog/2023-07-03-typescript-sdk)
- [spotify-web-api-ts-sdk - npm](https://www.npmjs.com/package/@spotify/web-api-ts-sdk)
- [GitHub - spotify/spotify-web-api-ts-sdk](https://github.com/spotify/spotify-web-api-ts-sdk)
- [Client Credentials Flow | Spotify for Developers](https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow)
