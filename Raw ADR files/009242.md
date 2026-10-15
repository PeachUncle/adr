# ADR-001: FastAPI as Backend Framework

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template needs a Python web framework for the backend API service. The framework must support:

1. **Asynchronous Operations**: High-concurrency workloads including database queries, OAuth token validation, and external service calls (JWKS fetching, OIDC discovery)
2. **Strong Type Safety**: Runtime validation and IDE autocompletion for request/response handling
3. **Automatic API Documentation**: Self-documenting APIs for developer experience and API consumer clarity
4. **OAuth 2.0 / OIDC Integration**: JWT validation, Bearer token handling, and integration with identity providers
5. **Multi-Tenancy Support**: Middleware capabilities for tenant context extraction and propagation
6. **Database Integration**: Async SQLAlchemy support for PostgreSQL with connection pooling
7. **Production Readiness**: Mature, well-maintained framework suitable for enterprise applications

The backend handles critical security functions including JWT token validation via JWKS, rate limiting, token revocation, and Row-Level Security (RLS) tenant context management.

## Decision

We chose **FastAPI** as the backend framework.

FastAPI is a modern, high-performance Python web framework built on Starlette (ASGI) and Pydantic. Key implementation details in this project:

**Application Structure** (`backend/app/main.py`):
- Uses `asynccontextmanager` lifespan for startup/shutdown events
- Configures CORS middleware for frontend integration
- Implements `TenantResolutionMiddleware` for multi-tenant context extraction
- Structured exception handlers for HTTP, validation, and general errors

**Dependency Injection** (`backend/app/api/dependencies/`):
- `auth.py`: OAuth token validation with JWKS, rate limiting, and revocation checking
- `database.py`: Async session management with tenant context
- `tenant.py`: Tenant resolution from JWT claims
- `scopes.py`: Role-based access control using token scopes

**Pydantic Integration** (`backend/app/schemas/`):
- Request/response models with automatic validation
- `TokenPayload` for JWT claim parsing
- `AuthenticatedUser` for user context propagation
- `OIDCDiscovery`, `TokenResponse` for OAuth flows

**Async Database Support** (`backend/app/core/database.py`):
- `create_async_engine` with PostgreSQL+asyncpg
- Connection pooling (20 connections, 10 overflow)
- `AsyncSessionLocal` factory with explicit transaction control

## Consequences

### Positive

1. **Native Async Support**: All I/O operations (database queries, HTTP calls to Keycloak, Redis operations) use async/await, enabling high concurrency without thread pools

2. **Automatic OpenAPI Generation**: The `/docs` (Swagger UI) and `/redoc` endpoints are auto-generated, accurately documenting all endpoints including authentication requirements

3. **Pydantic Validation**: Request bodies, query parameters, and response models are validated at runtime with clear error messages (`HTTP 422` with field-level details)

4. **Dependency Injection**: Complex authentication flows are cleanly encapsulated:
   ```python
   async def get_current_user(
       credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
       jwks_client: Annotated[JWKSClient, Depends(get_jwks_client)],
       rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
   ) -> AuthenticatedUser:
   ```

5. **Middleware Support**: Starlette-based middleware enables tenant context extraction before route handlers execute

6. **Type Hints Throughout**: Full IDE support with `Annotated` types and `CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]`

7. **Performance**: ASGI-native framework with performance comparable to Node.js and Go for I/O-bound workloads

### Negative

1. **Learning Curve**: Developers unfamiliar with async Python or dependency injection patterns need onboarding time

2. **Async Complexity**: All database operations, HTTP clients, and Redis calls must use async variants; mixing sync/async code requires careful handling

3. **Smaller Ecosystem**: Fewer third-party packages compared to Django; some integrations require custom implementation

4. **No Built-in ORM**: Requires separate SQLAlchemy integration (vs. Django's built-in ORM)

### Neutral

1. **Python 3.10+ Required**: Uses modern Python features (`|` union types, `Annotated`, `match` statements where applicable)

2. **Starlette Foundation**: Middleware, routing, and request/response handling come from Starlette; understanding both frameworks is beneficial

## Alternatives Considered

### Flask

**Why Not Chosen**:
- Synchronous by default; async support via extensions is less mature
- No built-in request validation; requires Flask-Pydantic or Marshmallow
- Manual OpenAPI documentation or Flask-RESTX required
- Would require significant custom code for the OAuth/JWKS integration that FastAPI handles natively

### Django / Django REST Framework

**Why Not Chosen**:
- Heavier framework with batteries-included philosophy (admin, ORM, templates) that we don't need
- Async support (Django 4.1+) is newer and less battle-tested for full async stacks
- Django REST Framework adds complexity for pure API services
- Multi-tenancy typically requires django-tenant-schemas which uses schema-based isolation, not RLS

### Starlette (Direct)

**Why Not Chosen**:
- FastAPI is built on Starlette and adds exactly what we need: Pydantic integration, dependency injection, and automatic OpenAPI
- Using Starlette directly would require reimplementing these features

### Litestar (formerly Starlite)

**Why Not Chosen**:
- Smaller community and ecosystem compared to FastAPI
- Less third-party library support
- FastAPI's maturity and adoption provide more confidence for enterprise use

---

## Related ADRs

- [ADR-004: Keycloak as Identity Provider](./004-keycloak-identity-provider.md) - OAuth integration that FastAPI handles
- [ADR-005: Row-Level Security for Multi-Tenancy](./005-row-level-security-multitenancy.md) - Database pattern that FastAPI middleware supports

## Implementation References

- `backend/app/main.py` - FastAPI application initialization
- `backend/app/api/dependencies/auth.py` - OAuth token validation dependency
- `backend/app/core/config.py` - Pydantic Settings configuration
- `backend/app/schemas/` - Pydantic request/response models
