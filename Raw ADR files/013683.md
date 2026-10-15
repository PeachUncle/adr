# ADR 0005: API Gateway Proxy Implementation

**Status:** Accepted  
**Date:** 2026-12-10  
**Decision Makers:** Architecture Team  
**Category:** Backend Infrastructure

---

## Context

In POC-2, the API Gateway proxy functionality was deferred due to issues with `http-proxy-middleware` v3.x. The proxy was unable to correctly forward request bodies for POST/PUT/PATCH requests, resulting in `400 Bad Request` errors from downstream services.

### Problem Statement

Frontend applications are currently calling backend services directly (bypassing the API Gateway), which:

1. Exposes internal service URLs to clients
2. Complicates CORS configuration
3. Prevents centralized request logging
4. Makes it harder to implement rate limiting
5. Bypasses potential security middleware

### Previous Attempts (POC-2)

1. **http-proxy-middleware v3.x** - Path rewriting issues, body not forwarded
2. **Body parser order changes** - Partial success, still issues with large bodies
3. **Custom axios proxy** - Request abort issues, timeout problems

---

## Decision

Implement a custom streaming HTTP proxy using Node.js native `http` module with direct stream piping.

### Approach: Native HTTP Streaming Proxy

```typescript
import { IncomingMessage, ServerResponse, request as httpRequest } from 'http';
import { request as httpsRequest } from 'https';

function createProxyMiddleware(targetUrl: string) {
  const target = new URL(targetUrl);

  return (req: IncomingMessage, res: ServerResponse) => {
    const requestFn = target.protocol === 'https:' ? httpsRequest : httpRequest;

    const proxyReq = requestFn(
      {
        hostname: target.hostname,
        port: target.port,
        path: req.url,
        method: req.method,
        headers: {
          ...req.headers,
          host: target.host,
          'x-forwarded-for': req.socket.remoteAddress,
          'x-forwarded-proto': 'https',
        },
      },
      proxyRes => {
        res.writeHead(proxyRes.statusCode!, proxyRes.headers);
        proxyRes.pipe(res);
      }
    );

    // Stream request body directly (no buffering)
    req.pipe(proxyReq);

    proxyReq.on('error', err => {
      res.writeHead(502);
      res.end('Bad Gateway');
    });
  };
}
```

### Key Implementation Details

1. **No Body Buffering** - Request body streams directly to target
2. **Header Forwarding** - All headers forwarded, plus X-Forwarded-* headers
3. **Stream Piping** - Both request and response piped as streams
4. **Error Handling** - Connection errors return 502, timeouts return 504

---

## Alternatives Considered

### Option 1: http-proxy Library (node-http-proxy)

**Pros:**

- Well-maintained, widely used
- Built-in WebSocket support
- Lower-level than http-proxy-middleware

**Cons:**

- Still requires configuration
- May have same body forwarding issues
- Additional dependency

### Option 2: express-http-proxy

**Pros:**

- Simple Express middleware
- Good documentation

**Cons:**

- May buffer request body
- Less control over streaming

### Option 3: Keep Direct Service URLs

**Pros:**

- Already working
- No additional implementation needed

**Cons:**

- Exposes internal URLs
- CORS complexity
- No centralized logging
- Security concerns

---

## Consequences

### Positive

1. **Full Control** - Complete control over request/response handling
2. **No Buffering** - Stream-based approach handles large payloads
3. **Minimal Dependencies** - Uses Node.js built-in modules
4. **Predictable Behavior** - Simple, well-understood implementation

### Negative

1. **Manual Implementation** - More code to maintain
2. **Feature Parity** - Must implement features like WebSocket support manually
3. **Testing Burden** - Need comprehensive tests for edge cases

### Neutral

1. **Performance** - Similar to library-based solutions
2. **Complexity** - Moderate complexity, well-documented

---

## Implementation Plan

1. Create proxy module in API Gateway
2. Implement streaming request/response handling
3. Add path rewriting for service routing
4. Add header manipulation (X-Forwarded-*, CORS)
5. Add error handling (502, 503, 504)
6. Add request timeout handling
7. Write comprehensive tests
8. Update frontend to use API Gateway URL

---

## Verification

- [ ] POST requests with JSON body work
- [ ] PUT/PATCH requests work
- [ ] Large file uploads work
- [ ] Headers forwarded correctly
- [ ] Authentication tokens forwarded
- [ ] Error responses correct (502, 503, 504)
- [ ] Request timeouts handled
- [ ] All existing tests pass

---

## References

- [POC-2 Proxy Investigation](../../POC-3-Planning/api-gateway-proxy-implementation.md)
- [Node.js HTTP Module](https://nodejs.org/api/http.html)
- [Stream Piping](https://nodejs.org/api/stream.html#stream_readable_pipe_destination_options)
