# ADR: Controller Structure for JWT and API Token Secured Endpoints

- **Status**: accepted
- **Date**: 2025-11-02

## Context

The backend API includes endpoints secured by two different authentication mechanisms: JWT for user-authenticated access and API key tokens for public or semi-public access such as from the landing page. The development team faced a choice on whether to mix both authentication types within the same controllers or separate the endpoints into different controllers corresponding to their auth schemes.

## Decision

The chosen solution is to **separate controllers by authentication type**, grouping JWT-secured endpoints within dedicated controllers under `JwtProtectedModule` and API key secured or public endpoints within other controllers under `ApiKeyProtectedModule`. This improves codebase clarity, security management, and testing by keeping different auth flows isolated.

## Options Considered

1. **Single controllers mixing JWT and API Key endpoints**
   - Pros:
     - Fewer files and potentially less boilerplate.
     - Easier to overview related features in one place.
   - Cons:
     - Mixing auth flows can confuse separation of concerns.
     - Harder to apply module-level guards and documentation filters.
     - Risk of accidental auth misconfiguration.

2. **Separate controllers by auth type (Chosen)**
   - Pros:
     - Clear separation of authentication mechanisms.
     - Simplifies module imports and Swagger docs filtering by module.
     - Easier to maintain, test, and audit.
   - Cons:
     - More files and slightly higher initial setup overhead.

## Consequences

- Clear modularization of code reflecting real-life auth boundaries.
- Improves maintainability and helps generate separated Swagger documentation.
- Facilitates independent security policies and middlewares per auth type.
- Slightly more project structure complexity and boilerplate.

## References (if any)

- NestJS Module & Controller documentation
- Internal team discussions on authentication architecture
