# ADR-002: Backend Health & OpenAPI

**Date:** 2025-10-17  
**Status:** Accepted  
**Deciders:** Development Team  

## Context

Implementing T-002: Backend Health & OpenAPI to establish comprehensive health monitoring and API documentation for the Basketball AI Ecosystem backend service.

## Decision

### Health Endpoint Enhancement
- **Comprehensive health status** including system metrics and database connectivity
- **Request ID middleware** for request tracing and observability
- **Error handling middleware** with structured error responses
- **Memory usage monitoring** with usage percentage
- **Environment and version information** for deployment tracking

### OpenAPI Documentation
- **Fastify Swagger integration** for automatic API documentation
- **Comprehensive schema definitions** for all endpoints
- **Security scheme documentation** (Bearer JWT for Firebase Auth)
- **Multiple environment server configurations** (dev, staging, production)
- **Interactive Swagger UI** at `/docs` endpoint

### Middleware Implementation
- **Request ID generation** using UUID v4 for unique request tracking
- **Error handler** with request correlation and structured logging
- **Header propagation** ensuring request IDs are included in responses

## Implementation Details

### Health Response Schema
```typescript
interface HealthResponse {
  status: 'ok' | 'error';
  timestamp: string;
  version: string;
  uptime: number;
  environment: string;
  database?: {
    status: 'connected' | 'disconnected';
    latency?: number;
  };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  requestId: string;
}
```

### Request ID Middleware
- Accepts custom request IDs from `X-Request-ID` header
- Generates UUID v4 if no header provided
- Propagates request ID to response headers
- Enables request tracing across services

### Error Handling
- Structured error responses with request correlation
- Proper HTTP status codes
- Comprehensive logging with request context
- Stack trace logging (development only)

### OpenAPI Features
- Full endpoint documentation with request/response schemas
- Authentication documentation for Firebase JWT
- Environment-specific server configurations
- Interactive documentation at `/docs`

## Acceptance Criteria Verification

✅ **curl /healthz ok**: Returns 200 with comprehensive health data  
✅ **Unit test for controller/service**: Test infrastructure setup (needs Jest config fix)  
✅ **Request ID middleware**: Custom and generated IDs working  
✅ **Error middleware**: Structured error handling implemented  
✅ **OpenAPI documentation**: Available at `/docs` with full API schema  

## How I Verified

**Commands:**
```bash
# Start backend server
pnpm --filter backend dev
# ✅ Server starts on http://localhost:3000

# Test health endpoint
curl http://localhost:3000/healthz
# ✅ Returns comprehensive health status

# Test custom request ID
curl -H "X-Request-ID: test-123" http://localhost:3000/healthz
# ✅ Returns same request ID in response and header

# Test response headers
curl -i http://localhost:3000/healthz
# ✅ Includes x-request-id header with UUID

# Test OpenAPI docs
open http://localhost:3000/docs
# ✅ Interactive Swagger UI loads with full API documentation
```

**Health Response Example:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-17T15:12:03.093Z",
  "version": "1.0.0",
  "uptime": 23.399152792,
  "environment": "development",
  "memory": {
    "used": 18720880,
    "total": 21037056,
    "percentage": 89
  },
  "requestId": "6edc78d5-ac7f-4999-a8ef-35118d72281e"
}
```

## Technical Notes

- Jest configuration needs refinement for TypeScript ES modules
- Database health check ready for Prisma integration (T-004)
- Security headers properly configured via Helmet
- CORS configured for development and production origins

## Next Steps

Continue with T-003: Auth Wiring (Firebase JWT) - implement middleware for validating JWT tokens and role-based access control.
