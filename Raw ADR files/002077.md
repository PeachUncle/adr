# ADR-0001: Centralized Auth Interceptor

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together.

- **Status:** Accepted
- **Date:** 2025-12-30
- **Feature:** Authentication (004-authentication)
- **Context:** The application needs to securely and consistently send JWT tokens with every API request to protected backend endpoints. Without a centralized mechanism, every component or hook would need to manually retrieve the token from storage and attach the `Authorization` header, leading to code duplication and increased risk of security omissions.

## Decision

We implemented a **Centralized Auth Interceptor** within the `frontend/lib/api.ts` fetch wrapper. This decision includes:

- **Centralized Wrapper**: Consolidated all `fetch` calls into a single `apiRequest` utility function.
- **Automatic Token Injection**: The wrapper automatically retrieves the Bearer token from `localStorage` (via `getToken()`) and injects it into the `Authorization` header if present.
- **Uniform Error Handling**: Centralized 4xx/5xx error parsing and response normalization.
- **Consistent API Base URL**: Management of the `API_BASE_URL` through environment variables in one location.

## Consequences

### Positive

- **DRY Principle**: Eliminates the need to manually attach headers in individual API calls.
- **Security Consistency**: Ensures that if a token exists, it is sent, reducing the chance of "forgotten" authentication on new endpoints.
- **Maintainability**: Changes to the authentication strategy (e.g., switching from `Bearer` to a different header or changing storage from `localStorage` to cookies) only need to be updated in one file.
- **Type Safety**: Provides a generic wrapper that ensures consistent response typing across the application.

### Negative

- **Tight Coupling**: All features are now dependent on this specific `apiRequest` implementation.
- **Debugging Complexity**: Debugging a specific request might require tracing through the centralized interceptor logic.
- **Global Side Effect**: Every request made through this wrapper will attempt to attach a token, even for public endpoints (though this is generally harmless).

## Alternatives Considered

- **Manual Header Attachment**: Passing headers in every component. (Rejected: High maintenance, error-prone).
- **Axios Interceptors**: Using Axios's built-in interceptor feature. (Rejected: User preferred standard `fetch` API for simplicity and smaller bundle size).
- **Higher-Order Functions**: Wrapping every call with an `withAuth` helper. (Rejected: More verbose than a centralized `apiRequest` utility).

## References

- Feature Spec: [specs/004-authentication/spec.md](../specs/004-authentication/spec.md)
- Implementation Plan: [specs/004-authentication/plan.md](../specs/004-authentication/plan.md)
- Related ADRs: None
- Evaluator Evidence: See implementation in `frontend/lib/api.ts`
