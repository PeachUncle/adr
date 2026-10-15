# ADR-004: Client-Side Only Architecture

## Status

Accepted

## Context

We need to decide whether the Markdown Docs Viewer should support server-side rendering (SSR), require a backend service, or be purely client-side. This decision impacts deployment complexity, performance, and usage scenarios.

## Decision

We will build the Markdown Docs Viewer as a purely client-side library with no server dependencies.

## Consequences

### Positive

- **Simple Deployment**: Just static files, works on any web server
- **CDN Friendly**: Can be served from CDNs globally
- **No Backend**: No server maintenance or scaling concerns
- **Offline Capable**: Works with local files or cached content
- **Privacy**: All processing happens in user's browser
- **Cost**: No server costs for processing

### Negative

- **Initial Load**: All processing happens after page load
- **SEO**: No server-side rendering for search engines
- **Large Files**: Memory constraints in browser
- **CORS**: Subject to browser CORS restrictions
- **No Preprocessing**: Can't optimize markdown at build time

### Neutral

- **Performance**: Depends on client device capabilities
- **Caching**: Must implement client-side caching
- **Search**: Client-side search indexing

## Implementation

### Architecture Principles

1. **Zero Backend Dependencies**: No API calls to custom servers
2. **Browser APIs Only**: Use native browser capabilities
3. **Progressive Enhancement**: Features degrade gracefully
4. **Lazy Loading**: Load resources as needed

### Key Design Decisions

```javascript
// All processing in browser
const viewer = createViewer({
  container: '#docs',
  source: { type: 'local', basePath: '/docs' },
});

// No server calls for:
// - Markdown parsing
// - Search indexing
// - Theme switching
// - Navigation
```

### External Services

Only optional external services are used:

- GitHub API (when using github source)
- CDN for remote markdown files
- No custom backend required

## Alternatives Considered

### Server-Side Rendering (SSR)

- ✅ Better SEO
- ✅ Faster initial render
- ❌ Complex deployment
- ❌ Server costs
- ❌ Framework specific

### Hybrid Approach

- ✅ Best of both worlds
- ❌ Most complex
- ❌ Two codebases
- ❌ Synchronization issues

### API-Based

- ✅ Preprocessing possible
- ✅ Advanced search
- ❌ Requires backend
- ❌ Latency concerns
- ❌ Availability dependencies

## Migration Path

If server-side support is needed in the future:

1. Core library remains client-side
2. Add optional SSR adapter packages
3. Implement hydration for SSR content
4. Keep client-only mode as default

## References

- [JAMstack Architecture](https://jamstack.org/)
- [Client-Side vs Server-Side Rendering](https://web.dev/rendering-on-the-web/)
