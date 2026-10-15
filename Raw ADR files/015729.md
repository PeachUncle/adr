# ADR-0004: JWT Token Refresh Strategy

## Status
Accepted

## Date
2024-12-30

## Context

The application uses JWT-based authentication with the Python backend. Key requirements:

1. **Short-lived Access Tokens**: 15-30 minute expiration for security
2. **Long-lived Refresh Tokens**: 7-30 days for user convenience
3. **Seamless Experience**: Users shouldn't see auth errors during normal use
4. **Security**: Tokens must not be accessible to JavaScript (XSS protection)

Challenges:
- Access tokens expire frequently
- Users should stay logged in across page refreshes
- Multiple concurrent requests might fail simultaneously on expiration
- Need to handle refresh race conditions

## Decision

Implement transparent token refresh using httpOnly cookies and a fetch wrapper.

### Token Storage

Tokens stored in httpOnly cookies (set by API routes):

```typescript
// src/app/api/auth/login/route.ts
const response = NextResponse.json({ user })

response.cookies.set('access_token', tokens.access_token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
  maxAge: 60 * 30 // 30 minutes
})

response.cookies.set('refresh_token', tokens.refresh_token, {
  httpOnly: true,
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
  path: '/api/auth/refresh', // Only sent to refresh endpoint
  maxAge: 60 * 60 * 24 * 7 // 7 days
})
```

### Fetch Wrapper

All authenticated requests use `fetchWithRefresh`:

```typescript
// src/lib/auth/token-refresh.ts
export async function fetchWithRefresh(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  let response = await fetch(url, {
    ...options,
    credentials: 'include' // Include cookies
  })

  // If 401, try to refresh token
  if (response.status === 401) {
    const refreshed = await refreshToken()

    if (refreshed) {
      // Retry original request with new token
      response = await fetch(url, {
        ...options,
        credentials: 'include'
      })
    } else {
      // Refresh failed, redirect to login
      window.location.href = '/login'
    }
  }

  return response
}

async function refreshToken(): Promise<boolean> {
  const response = await fetch('/api/auth/refresh', {
    method: 'POST',
    credentials: 'include'
  })

  return response.ok
}
```

### Race Condition Handling

Prevent multiple simultaneous refresh attempts:

```typescript
let refreshPromise: Promise<boolean> | null = null

async function refreshToken(): Promise<boolean> {
  if (refreshPromise) {
    return refreshPromise // Return existing promise if refresh in progress
  }

  refreshPromise = doRefresh()
  const result = await refreshPromise
  refreshPromise = null

  return result
}
```

## Consequences

### Positive

1. **XSS Protection**: Tokens not accessible via `document.cookie` or JavaScript
2. **Transparent UX**: Users never see token expiration errors
3. **Secure Transport**: Cookies only sent over HTTPS in production
4. **Automatic Retry**: Failed requests automatically retried after refresh
5. **Single Refresh**: Multiple 401s trigger only one refresh attempt

### Negative

1. **CSRF Consideration**: Need SameSite cookies or CSRF tokens
2. **Cookie Size**: JWT in cookies adds to request headers (~1-2KB)
3. **Server-Side Rendering**: Tokens not available in client-side context directly
4. **Complexity**: More complex than simple localStorage approach

### Security Measures

1. **httpOnly**: Prevents XSS access to tokens
2. **Secure**: HTTPS-only in production
3. **SameSite=Lax**: Prevents CSRF on state-changing requests
4. **Path restriction**: Refresh token only sent to `/api/auth/refresh`
5. **Short expiry**: Access token expires in 30 minutes

## References

- [OWASP JWT Security](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- `src/lib/auth/token-refresh.ts` - Implementation
- `src/app/api/auth/login/route.ts` - Cookie setting
- `src/app/api/auth/refresh/route.ts` - Refresh endpoint
