# ADR-0001: Centralized Auth Interceptor for API Requests

## Status
Accepted

## Context
The frontend application needs to make authenticated API requests to the backend. Each request must include a JWT token in the Authorization header. We need to decide how to manage this token injection consistently across all API calls without duplicating code.

## Decision
We will implement a centralized API client using fetch with an interceptor pattern that automatically attaches JWT tokens to all requests. The interceptor will:

1. Check for a valid JWT token in localStorage before each request
2. Add the Authorization header with the format "Bearer <token>" to all requests
3. Handle 401 responses by clearing the token and redirecting to the login page

## Alternatives Considered

### Option 1: Manual token attachment in each API call
- Pro: Simple to implement initially
- Con: High risk of forgetting to add tokens to some requests
- Con: Code duplication across multiple API functions
- Con: Difficult to maintain consistency

### Option 2: Axios with request/response interceptors
- Pro: Built-in interceptor support
- Pro: Good error handling capabilities
- Con: Adds another dependency (axios) when fetch is already sufficient
- Con: Slightly more complex setup

### Option 3: Centralized fetch wrapper with interceptor (Chosen)
- Pro: Uses native fetch API (no additional dependencies)
- Pro: Centralized token management
- Pro: Consistent application across all API calls
- Pro: Easy to modify behavior in one place
- Pro: Handles both request and response (401 errors)

## Consequences

### Positive
- Consistent authentication across all API calls
- Single place to manage token attachment logic
- Automatic handling of expired/invalid tokens
- Easy to modify authentication behavior
- Reduces code duplication

### Negative
- All API calls must go through the centralized client
- Adds slight abstraction layer that developers need to understand
- Potential single point of failure if the centralized client has issues

## Technical Implementation
- Create `api.ts` file with centralized API client
- Implement `apiRequest` wrapper function that handles token injection
- Add 401 response handling to clear tokens and redirect
- Export all API functions (fetchTodos, createTodo, etc.) through this centralized client

## Date
2025-12-30