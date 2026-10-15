# ADR 0002: User Authentication and Login Implementation

## Status
Accepted

## Context
This ADR documents the design and implementation decisions for user authentication and login in the banking application. Secure authentication is critical for protecting user accounts and sensitive operations. The system uses JWT (JSON Web Tokens) for stateless authentication and bcrypt for password hashing. The implementation covers token creation, validation, and middleware for protected routes.

## Decision
### Authentication Flow
- Users authenticate by providing their username and password to the `/api/v1/user/login` endpoint.
- Passwords are hashed using bcrypt before storage and compared using bcrypt's secure comparison.
- Upon successful login, a JWT is issued containing the username and standard claims (issuer, subject, audience, issued at, expiration, etc.).
- The JWT is signed with a secret key (minimum 32 characters, loaded from environment variable `JWT_SECRET_KEY`).
- The JWT is returned to the client and must be included in the `Authorization: Bearer <token>` header for protected endpoints.

### Implementation Details
- **JWT Creation**: Implemented in `internal/auth/jwt.go` using the `github.com/golang-jwt/jwt/v5` library. The `JWTMaker` struct handles token creation and verification. The payload includes standard claims and a unique token ID.
- **Password Hashing**: Implemented in `internal/auth/password.go` using bcrypt. Passwords are never stored or compared in plaintext.
- **Token Payload**: Defined in `internal/auth/types.go` as the `Payload` struct, which embeds JWT claims and provides validation logic.
- **Middleware**: The `BearerMiddleware` in `internal/auth/middleware.go` validates the JWT on incoming requests, extracts the payload, and attaches it to the Gin context for downstream handlers.
- **Login Endpoint**: The controller validates credentials, issues a JWT, and returns user info and the token in a structured response. Errors are handled with appropriate HTTP status codes and messages.

### Security Considerations
- The JWT secret key must be kept secure and never hardcoded in the codebase.
- Passwords are always hashed and never logged or returned in API responses.
- JWTs have a configurable expiration (default: 24 hours) to limit the window of misuse if compromised.
- The middleware ensures that only requests with valid, non-expired tokens can access protected resources.

## Consequences
- Stateless authentication with JWT enables scalable, distributed deployments without server-side session storage.
- The use of bcrypt and secure token handling mitigates common authentication vulnerabilities.
- The design is extensible for future features such as refresh tokens, multi-factor authentication, or role-based access control.

## References
- [JWT (RFC 7519)](https://datatracker.ietf.org/doc/html/rfc7519)
- [bcrypt Password Hashing](https://pkg.go.dev/golang.org/x/crypto/bcrypt)
- [Golang JWT Library](https://github.com/golang-jwt/jwt) 