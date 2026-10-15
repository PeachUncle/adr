# ADR-0001: Backend-for-Frontend (BFF) Pattern

## Status
Accepted

## Date
2024-12-30

## Context

The Rodrigues AI application requires communication with a Python FastAPI backend that handles:
- Authentication (JWT tokens)
- CPR document analysis and creation
- Document management
- Compliance verification
- Risk calculation

Key challenges:
1. **Security**: JWT tokens should not be exposed to client-side JavaScript
2. **CORS**: Direct client-to-backend calls require complex CORS configuration
3. **Token Refresh**: Automatic token refresh needs secure cookie handling
4. **API Versioning**: Backend API changes should not break the frontend
5. **Environment Handling**: Different backend URLs for development/staging/production

## Decision

Implement a BFF (Backend-for-Frontend) pattern using Next.js API routes (`/api/*`) as a proxy layer between the React frontend and Python backend.

### Implementation

All API routes follow this pattern:

```typescript
// src/app/api/[resource]/route.ts
export async function GET(request: NextRequest) {
  const backendUrl = process.env.BACKEND_URL
  const token = request.cookies.get('access_token')?.value

  const response = await fetch(`${backendUrl}/api/v1/resource`, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })

  return NextResponse.json(await response.json())
}
```

### Key Files

- `src/app/api/auth/*` - Authentication routes (login, logout, refresh)
- `src/app/api/cpr/*` - CPR workflow routes
- `src/app/api/documents/*` - Document management
- `src/app/api/compliance/*` - Compliance verification
- `src/lib/auth/token-refresh.ts` - Token refresh logic with `fetchWithRefresh`

## Consequences

### Positive

1. **Enhanced Security**: JWT tokens stored in httpOnly cookies, not accessible via JavaScript
2. **Simplified CORS**: Frontend and API routes share the same origin
3. **Transparent Token Refresh**: `fetchWithRefresh` wrapper handles 401 responses automatically
4. **API Abstraction**: Frontend decoupled from backend API structure changes
5. **Consistent Error Handling**: Centralized error formatting in API routes
6. **Type Safety**: API routes can validate and transform responses before forwarding

### Negative

1. **Additional Latency**: Extra network hop through Next.js server
2. **Server Load**: Next.js server handles all API traffic
3. **Deployment Complexity**: Need to ensure Next.js server can reach backend
4. **Duplicate Code**: Some request/response handling duplicated across routes

### Mitigations

- Use edge runtime for API routes where possible (lower latency)
- Implement response caching for non-sensitive endpoints
- Keep API routes thin (minimal transformation)

## References

- [Next.js API Routes](https://nextjs.org/docs/app/building-your-application/routing/route-handlers)
- [BFF Pattern by Sam Newman](https://samnewman.io/patterns/architectural/bff/)
- `src/lib/auth/token-refresh.ts` - Token refresh implementation
