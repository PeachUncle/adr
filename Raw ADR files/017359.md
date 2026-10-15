# ADR-011: OpenAPI 3.0 for API Documentation

**Date**: 2025-10-27
**Status**: Accepted
**Epic**: Epic 005 - Backend Service Refactoring
**Related ADRs**: [ADR-009 (Zod Validation)](./ADR-009-zod-validation.md), [ADR-010 (Express.js)](./ADR-010-expressjs-api-server.md)

## Context

API documentation was manually maintained and often out of sync with actual API:
- Markdown docs outdated within weeks
- No interactive API playground
- Client developers had to read code to understand API
- No automated API client generation
- Breaking changes not clearly documented

## Decision

We will use **OpenAPI 3.0** specification for all API documentation with automated generation from code.

**Implementation**:
```typescript
// openapi.yaml (generated from code)
openapi: 3.0.0
info:
  title: Sovren API
  version: 1.0.0
  description: Creator monetization platform API

paths:
  /api/payments/invoice:
    post:
      summary: Create Lightning invoice
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                amount:
                  type: number
                  description: Amount in satoshis
                description:
                  type: string
      responses:
        200:
          description: Invoice created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Invoice'
```

**Tools**:
- **Swagger UI**: Interactive API documentation
- **OpenAPI Generator**: Auto-generate client SDKs
- **zod-to-openapi**: Generate OpenAPI from Zod schemas
- **swagger-jsdoc**: Extract OpenAPI from JSDoc comments

## Consequences

### Positive

1. **Always Up-to-Date**: Generated from code, can't drift
2. **Interactive Docs**: Swagger UI for testing endpoints
3. **Client Generation**: Auto-generate TypeScript/Python/etc clients
4. **Validation**: OpenAPI spec validates request/response formats
5. **Standardized**: Industry-standard format

### Negative

1. **Setup Complexity**: Initial setup requires configuration
2. **Maintenance**: Need to update OpenAPI annotations
3. **Build Time**: Spec generation adds to build process

## Alternatives Considered

- **GraphQL Schema**: Different paradigm, requires rewrite - Rejected
- **API Blueprint**: Less popular, smaller tooling - Rejected
- **RAML**: Deprecated in favor of OpenAPI - Rejected
- **Manual Markdown**: Always outdated - Rejected

## Implementation

```typescript
import { generateOpenAPISpec } from './utils/openapi';

// Generate spec on startup
const spec = generateOpenAPISpec({
  routes: app._router.stack,
  schemas: zodSchemas,
});

// Serve Swagger UI
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(spec));
```

## Related Documentation

- [OpenAPI Specification](https://swagger.io/specification/)
- [API Documentation](/docs/api/README.md)
- [Generated API Spec](/docs/api/openapi.yaml)

## Revision History

- **2025-10-27**: Initial decision documented for Epic 005
