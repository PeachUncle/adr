# ADR-0005: API Communication Pattern

- **Status:** Accepted
- **Date:** 2026-01-03
- **Feature:** 006-frontend-integration
- **Context:** Phase 2.4 frontend must communicate with the Phase 2.3 backend REST API for all task CRUD operations. Every API request must include a valid JWT token, and the frontend must handle authentication errors (401, 403) appropriately. We need to decide on the API communication approach, including client architecture, error handling, and state synchronization.

## Decision

We will use the following API communication pattern:

- **API Client**: Centralized fetch-based client class (`lib/api/client.ts`)
- **Authentication**: Automatic JWT attachment via `Authorization: Bearer <token>` header
- **Token Source**: Read from LocalStorage (`todo_auth_token` key)
- **Error Handling**:
  - 401 Unauthorized: Clear stored credentials, redirect to `/signin`
  - 403 Forbidden: Display user-friendly permission error
  - 404 Not Found: Display resource not found message
  - Other errors: Parse error response or show generic message
- **State Updates**: Update UI state ONLY after successful API response (no optimistic updates)
- **Hook Layer**: `useTasks` hook wraps API client, manages loading/error states

## Consequences

### Positive

- **Consistent Token Attachment**: Single point for JWT injection ensures 100% coverage
- **Centralized Error Handling**: Uniform 401/403 behavior across all API calls
- **No Dependencies**: Native fetch API requires no additional libraries
- **Predictable State**: UI always reflects actual backend state (no desync)
- **Type Safety**: TypeScript interfaces ensure request/response type correctness
- **Testable**: Client class can be mocked for component testing

### Negative

- **No Automatic Retry**: Transient failures require manual refresh
- **No Request Caching**: Each navigation fetches fresh data (acceptable for Phase 2.4)
- **Manual Deduplication**: Multiple components calling same endpoint fetch separately
- **Waterfall Loading**: No parallel data fetching optimization
- **No Optimistic UI**: Perceived latency higher than optimistic approach

## Alternatives Considered

**Alternative A: Axios with Interceptors**
- Pros: Built-in retry, interceptors, request/response transformation
- Rejected: Adds dependency; fetch API sufficient for current scope; similar interceptor pattern achievable

**Alternative B: React Query / TanStack Query**
- Pros: Caching, deduplication, background refetch, optimistic updates
- Rejected: Adds significant dependency; overkill for Phase 2.4 scope; increases learning curve

**Alternative C: SWR (Stale-While-Revalidate)**
- Pros: Lightweight caching, Next.js integration, simple API
- Rejected: Adds dependency; current scope doesn't require caching sophistication

**Alternative D: Optimistic UI Updates**
- Pros: Better perceived performance; immediate feedback
- Rejected: Phase 2.4 spec explicitly states "update state ONLY after successful API response"

**Alternative E: GraphQL + Apollo Client**
- Pros: Type-safe queries, automatic caching, fragments
- Rejected: Backend is REST; would require backend changes; overcomplicated for CRUD operations

## References

- Feature Spec: [specs/006-frontend-integration/spec.md](../../specs/006-frontend-integration/spec.md)
- Implementation Plan: [specs/006-frontend-integration/plan.md](../../specs/006-frontend-integration/plan.md)
- Backend API: [backend/app/routers/tasks.py](../../backend/app/routers/tasks.py)
- Related ADRs: [ADR-0003](./0003-frontend-technology-stack.md), [ADR-0004](./0004-frontend-authentication-architecture.md)
- Research: [specs/006-frontend-integration/research.md](../../specs/006-frontend-integration/research.md)
