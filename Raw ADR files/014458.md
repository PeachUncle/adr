# 3. Rest API Authentication and Authorization

## Status

Accepted

Date: 2025-06-19

## Context

As our API ecosystem expands, we need to establish consistent patterns for how authentication and authorization are 
handled across all RESTful APIs, focusing specifically on the transport mechanism rather than the token format or 
authentication service implementation.

Our goals are to:

- Define a standard approach for transmitting authentication information to APIs
- Ensure consistent security patterns across all services
- Maintain compatibility with industry standards and tools
- Support different client types (browser applications, mobile apps, server-to-server)
- Simplify API consumption for developers

## Decision

For authentication and authorization transport, we will adopt the following approach:

1. **HTTP Authorization Header**:
   - Use the `Authorization` header with the Bearer scheme for token transmission
   - Example: `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

2. **Token Transport Rules**:
   - Tokens MUST always be transmitted over HTTPS
   - Tokens MUST NOT be included in URL query parameters
   - Tokens MUST NOT be included in request bodies unless specifically required for token refresh operations
   - CORS headers must be properly configured for browser-based clients

3. **Public API Documentation**:
   - Use OpenAPI's security scheme definitions to document authentication requirements
   - Document token acquisition flow in API documentation
   - Clearly indicate which endpoints require authentication

4. **Error Responses**:
   - Return `401 Unauthorized` for missing or invalid authentication
   - Return `403 Forbidden` for valid authentication but insufficient permissions
   - Follow the standard error response format as defined in our Error Response Format ADR

## Consequences

### Positive

- Consistent authentication pattern across all services improves developer experience
- Aligns with HTTP standards and common industry practices
- Compatible with most API testing tools and client libraries
- Maintains clean URLs without exposing tokens in logs or bookmarks
- Supports all client types with a single authentication approach

### Negative

- Some legacy systems may struggle with HTTP header-based authentication
- Requires proper CORS configuration for browser-based applications
- May require additional client-side code to manage token storage and transmission

### Neutral

- Compatible with various token types (JWT, opaque tokens, etc.)
- Works with different authentication providers and protocols

## Implementation Notes

### OpenAPI Definition

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT  # This is informational only
      description: JWT token obtained from the login endpoint

security:
  - BearerAuth: []
```

## Related Documents

- [Global Authentication and Authorization](./../../global/0003-authentication-and-authorization.md)
- [Authentication Strategy](./../../domain/authentication/0001-authentication-strategy.md)
- [RFC 6750: OAuth 2.0 Bearer Token Usage](https://datatracker.ietf.org/doc/html/rfc6750)
- [OpenAPI Specification 3.0.3](https://spec.openapis.org/oas/v3.0.3)

## Contributors

- Àlex Grau Roca
