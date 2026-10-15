# ADR-0011: API Gateway Routing & Public API Strategy

## Status
Accepted

## Date
2025-11-17

## Context

PolyShop exposes a **Public API** to clients (web, mobile, future partner APIs).  
Internally, PolyShop consists of multiple microservices:

- Auth Service
- Product Service
- Inventory Service
- Order Service
- Payment Service
- Notification Service
- Search Service
- Analytics Service

Clients **must not** call internal services directly.  
A dedicated API Gateway must:

- Provide one unified public API
- Enforce authentication + rate limiting
- Route requests to internal services
- Hide internal network topology
- Normalize headers and trace IDs
- Provide request/response logging
- Handle global errors
- Be compatible with OpenAPI aggregation

---

# Decision

PolyShop will use a dedicated **API Gateway** (Spring Cloud Gateway) as the only public entry point.

### Responsibilities of the Gateway

1. **Route incoming requests** to internal services based on path mapping.  
2. **Validate access tokens** using Auth Service JWKS.  
3. **Inject internal service tokens** (service-to-service JWT).  
4. **Apply rate limiting** based on user identity + IP.  
5. **Attach request tracing headers**:
   - `X-Request-Id`
   - `X-User-Id`
   - Internal service JWT
6. **Perform protocol-level validations** (e.g., required headers).  
7. **Normalize error responses** using a shared model.  
8. **Aggregate OpenAPI specs** for documentation.

The gateway **must not** contain business logic.

---

# Routing Rules

Routing uses path-based rules:

| Public Path | Internal Service |
|-------------|------------------|
| `/auth/**` | Auth Service |
| `/products/**` | Product Service |
| `/inventory/**` | Inventory Service |
| `/orders/**` | Order Service |
| `/payments/**` | Payment Service |
| `/search/**` | Search Service |
| `/analytics/**` | Analytics Service (future) |

---

# Token Handling

### User Access Token
- Validated at the Gateway.
- Only forwarded to services that require user context (orders, payments, profile).

### Internal Service Token
- Gateway requests a service token from Auth Service.
- Cached with short TTL.
- Injected as header:  
  `X-Service-Token: <jwt>`

This prevents exposing internal service secrets to users.

---

# Error Standardization

All services will return errors in the shared `ErrorResponse` format (from `common.yaml`):

```

{
"timestamp": "...",
"status": 400,
"error": "Bad Request",
"code": "INVALID_INPUT",
"message": "Price must be positive",
"path": "/products",
"requestId": "..."
}

```

If a service returns a non-standard error, the Gateway normalizes it.

---

# Rate Limiting Strategy

### Local development
- Disabled.

### Production
- Requires Redis backing
- Controlled by:
  - User ID
  - IP address (for unauthenticated endpoints)
- Strategy:
  - 100 requests/minute for logged-in users
  - 30 requests/minute for unauthenticated endpoints

---

# OpenAPI Aggregation

Each internal service exposes its OpenAPI spec at:

```

/internal/openapi.yaml

```

Gateway pulls these and merges them to produce the Public API spec:

```

/openapi.yaml

```

Rules:

- Paths from internal services are included directly.
- Examples included.
- Internal-only paths excluded.
- Internal headers removed.

---

# Security Hardening

Gateway enforces:
- HTTPS only (prod)
- TLS termination
- CORS policies
- CSRF disabled (stateless API)
- IP filtering for admin endpoints

Internal services accept traffic only from Gateway (via network policies).

---

# Alternatives Considered

### Option A: No gateway
Rejected — exposes internal topology and makes token management impossible.

### Option B: Envoy + gRPC internally
Rejected — too heavy for current scope.

### Option C: API Gateway + Service Mesh
Rejected — future possibility; too complex for v1.

---

# Consequences

### Positive
- Clean separation between public and private APIs
- Stronger security posture
- Consistent tracing and error model
- Easy scaling (gateway runs horizontally)
- Unified OpenAPI documentation

### Negative
- Small performance overhead
- Requires gateway token caching
- Extra deployment component

---

# Final Decision

PolyShop adopts **Spring Cloud Gateway** as the official API Gateway, with:

- Path-based routing
- User token validation
- Service token injection
- Global error handling
- Rate limiting
- OpenAPI aggregation

This becomes a mandatory component of production deployments.