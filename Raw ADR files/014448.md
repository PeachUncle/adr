# 1. Authentication Strategy

## Status

Accepted

Date: 2025-06-18

## Context

The food delivery platform needs a robust, scalable, and secure authentication mechanism that:

- Supports multiple user types (customers, staff, couriers) with different security requirements
- Provides stateless authentication for improved scalability
- Enables session management and token refresh capabilities
- Ensures secure communication between services
- Allows future extensibility (e.g., MFA for staff)

Current challenges include:

- Managing authentication across distributed services
- Handling different security requirements per user type
- Balancing security with user experience
- Ensuring scalability with a growing user base

## Decision

We will implement a JWT-based authentication system with refresh tokens:

1. **Authentication Flow**
    - Initial authentication via email/password
    - Returns a token pair (access token and refresh token)
    - Access token validity: 1 hour
    - Refresh token validity: 7 days
    - Separate endpoints per user type (`/v1.0/{user-type}/*`)

2. **Access Tokens (JWT)**
    - Stateless, signed with asymmetric keys (RS256)
    - Contains essential claims:
      ```json
      {
        "sub": "user-id",
        "exp": 1234567890,
        "iat": 1234567890,
        "role": "customer|staff|courier"
      }
      ```

3. **Refresh Tokens**
    - Stateful (stored in MongoDB)
    - One active refresh token per user
    - Rotation on each use (security measure)
    - Invalidation on suspected compromise
    - After first use, they will still be active for 5 seconds to prevent potential race conditions

4. **Token Management**
    - Automatic token refresh when the access token expires
    - Invalidation cascade (both tokens) on security events
    - Rate limiting on authentication endpoints

## Consequences

### Positive

- Stateless verification of access tokens
- Clear separation of authentication concerns
- Easy to extend for new user types
- Support for token revocation
- Improved security through token rotation

### Negative

- Need for refresh token storage
- Additional complexity in token management
- More complex testing requirements
- Clock synchronization requirements

### Neutral

- Regular key rotation is required
- Need for rate limiting implementation
- Monitoring requirements for security events

## Implementation Notes

1. **Authentication Flow**
   ```
   1. User -> Auth Service: POST /v1.0/{user-type}/login
   2. Auth Service: Validate credentials
   3. Auth Service: Generate token pair
   4. Auth Service -> User: Return tokens
   5. User -> Services: Use access token
   6. User -> Auth Service: Refresh when needed
   ```

2. **Token Refresh Flow**
   ```
   1. User -> Auth Service: POST /v1.0/{user-type}/refresh
   2. Auth Service: Validate refresh token
   3. Auth Service: Invalidate old refresh token
   4. Auth Service: Generate new token pair
   5. Auth Service -> User: Return new tokens
   ```

3. **Security Considerations**
    - HTTPS for all endpoints
    - Rate limiting per IP and user
    - Token blacklisting capability
    - Secure token storage guidelines

## Related Documents

- [ADR-4 User Types and Roles Structure](./../../global/0004-user-types-and-roles-structure.md)
- API Security Standards (to be created)

## Contributors

- Àlex Grau Roca