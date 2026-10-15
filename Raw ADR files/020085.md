# ADR-001: Server-Side Proxy for Solid Pod Access in Containerized Environments

## Status

**Accepted**

## Context

Wayfinder integrates with Solid Pods to fetch profile data directly from users' personal data stores. During development in a KASM workspace (containerized desktop environment), we discovered that:

1. The Solid Pod server runs on `localhost:3002` and is accessible from the terminal
2. The browser cannot reach `localhost:3002` due to container network isolation
3. `curl` commands succeed while browser requests fail with `ERR_CONNECTION_REFUSED`

This is a common issue in containerized environments where the browser runs in a different network namespace than the server processes.

### Options Considered

1. **Direct browser-to-Pod connection** (original approach)
   - Pros: Simple, no proxy overhead
   - Cons: Doesn't work in containerized environments

2. **Server-side proxy through Next.js API routes**
   - Pros: Works in all environments, central point for auth/caching
   - Cons: Additional request hop, requires proxy security

3. **Configure container networking to bridge namespaces**
   - Pros: No code changes
   - Cons: Infrastructure complexity, not portable, not always possible

4. **Use public Pod URLs only**
   - Pros: No proxy needed
   - Cons: Can't develop locally without internet, no offline support

## Decision

Implement a **server-side proxy** (`/api/pod-proxy`) that:

1. Accepts Pod URLs as query parameters
2. Validates that URLs point to allowed Pod servers (security)
3. Fetches the resource server-side (same network as Pod)
4. Returns the response to the browser

The `@inrupt/solid-client` library is configured with a custom fetch function that automatically routes localhost Pod requests through the proxy when running in a browser environment.

```typescript
function createProxiedFetch(): typeof fetch {
  return async (input, init) => {
    const url = typeof input === 'string' ? input : input.url;

    if (url.includes('localhost:3002') && typeof window !== 'undefined') {
      return fetch(`/api/pod-proxy?url=${encodeURIComponent(url)}`, init);
    }

    return fetch(input, init);
  };
}
```

## Consequences

### Positive

- **Works in containerized environments**: KASM, Docker, VMs all work
- **Transparent to application code**: The proxy is injected at the fetch level
- **Security boundary**: Proxy validates allowed hosts, preventing SSRF
- **Foundation for auth**: Proxy can add authentication tokens in future
- **Caching opportunity**: Server can cache Pod responses if needed

### Negative

- **Additional latency**: Extra hop through Next.js server
- **Proxy maintenance**: Another route to maintain and secure
- **Dev/Prod divergence**: Proxy only needed in certain environments

### Neutral

- **Production behavior**: In production with public Pod URLs, the proxy is bypassed (browser fetches directly)
- **Debugging**: Server-side requests appear in Next.js logs, not browser DevTools

## Implementation Notes

- Proxy is restricted to `localhost:3002` and `127.0.0.1:3002` only
- Uses environment detection (`typeof window !== 'undefined'`) to enable proxy only in browser
- Server-side rendering (SSR) fetches directly without proxy

## Related

- [solid-pod-integration.md](../patterns/solid-pod-integration.md) - Full integration patterns
- [app/src/app/api/pod-proxy/route.ts](../../../app/src/app/api/pod-proxy/route.ts) - Proxy implementation
- [app/src/lib/solid-client.ts](../../../app/src/lib/solid-client.ts) - Client with proxied fetch
