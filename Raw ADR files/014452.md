# 3. Authentication and Authorization

## Status

Accepted

Date: 2025-06-18

## Context

As our system grows with multiple services and user roles (customers, staff, and couriers), we need a clear strategy for
handling authentication and authorization across the entire system. We need to ensure secure access control while
maintaining scalability, performance, and reliability.

## Decision

1. **Authentication Domain Responsibilities**
    - User registration and login
    - JWT token issuance (access and refresh tokens)
    - Token refresh handling
    - Management of signing keys
    - Optional token revocation

2. **Individual Domains Responsibilities**
    - Independent JWT validation using shared signing keys
    - Domain-specific authorization rules
    - No direct calls to the auth domain for token validation

3. **Common Authentication Library**
    - Shared JWT validation middleware
    - Standard claims processing
    - Authorization helpers

## Consequences

### Positive

- Improved system performance (no network calls for validation)
- Better service availability (no auth service dependency)
- Increased scalability (auth service isn't a bottleneck)
- Consistent security implementation across services
- Clear separation of authentication and authorization concerns

### Negative

- Need for a secure key distribution mechanism
- Additional complexity in key rotation (if needed)
- Services must maintain a synchronized clock for token validation
- More complex token revocation (if needed)

### Neutral

- Services need to implement shared authentication middleware
- Each service maintains its own authorization rules
- Need for proper security monitoring and logging

## Implementation Notes

1. **Key Management**
    - Use asymmetric key pairs (public/private)
    - Store private key only in auth service
    - Distribute public key to all services
    - Implement automated key rotation

2. **Token Structure**
    - Include standard claims (sub, exp, iat)
    - Add custom claims (role, user_type)
    - Keep the payload minimal for performance

3. **Validation Process**
    - Verify signature using a public key
    - Check token expiration
    - Validate required claims
    - Apply domain-specific authorization

## Related Documents

- Authentication Service Design Doc (to be created)
- Security Standards Doc (to be created)
- Key Management Process Doc (to be created)

## Contributors

- Àlex Grau Roca