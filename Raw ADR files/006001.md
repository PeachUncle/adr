# ADR: Adding Swagger/OpenAPI Documentation to API

## Status

Pending

## Context

Our API currently lacks comprehensive, interactive documentation that would benefit both internal development and external API consumers. The challenges we face include:

1. **Current State**: No standardized API documentation exists
2. **Architecture**: Domain-driven design with 8 domains (auth, tournament, match, league, guess, member, dashboard, admin)
3. **API Versioning**: Supporting both v1 and v2 endpoints
4. **Existing Validation**: Already using Zod schemas for request validation
5. **TypeScript Stack**: Express.js with TypeScript
6. **Deployment**: Railway platform for staging, demo, and production environments
7. **Documentation Drift Risk**: Manual documentation can easily become outdated
8. **Developer Experience**: Need interactive API testing capabilities
9. **Type Safety**: Want to maintain end-to-end type safety
10. **Integration Overhead**: Solution should minimize refactoring of existing codebase

## Options Considered

### Option 1: Zod-to-OpenAPI Integration (RECOMMENDED)

Leverage existing Zod schemas to auto-generate OpenAPI documentation.

**Libraries:**
- `@astahmer/zod-to-openapi` or `@hono/zod-openapi`
- `swagger-ui-express` for interactive UI
- `express-openapi-validator` (optional runtime validation)

**Implementation Approach:**
```typescript
import { extendZodWithOpenApi } from '@astahmer/zod-to-openapi';
import { OpenAPIRegistry, OpenApiGeneratorV3 } from '@astahmer/zod-to-openapi';

// Extend existing Zod schemas
const authenticateUserSchema = z.object({
  publicId: z.string().min(1).openapi({
    description: 'Unique public identifier for the user',
    example: 'usr_abc123'
  })
});

// Register routes
const registry = new OpenAPIRegistry();
registry.registerPath({
  method: 'post',
  path: '/api/v2/auth',
  request: {
    body: {
      content: {
        'application/json': { schema: authenticateUserSchema }
      }
    }
  },
  responses: { ... }
});
```

**Pros:**
- ✅ Minimal refactoring - leverages existing Zod schemas
- ✅ Single source of truth - schema = validation + documentation
- ✅ Type-safe - TypeScript infers types from Zod
- ✅ DRY principle - no duplicate documentation
- ✅ Runtime validation matches documentation exactly
- ✅ Low learning curve - team already knows Zod

**Cons:**
- ⚠️ Requires manually registering each route in OpenAPI registry
- ⚠️ Initial setup time to extend all existing schemas
- ⚠️ Need to define response schemas (may not exist yet)

**Effort Estimate:** 2-4 days
**Maintenance:** Low

---

### Option 2: tsoa (Decorator-Based)

Complete framework that generates both routes and OpenAPI docs from TypeScript decorators.

**Library:**
- `tsoa` (handles routing + OpenAPI generation)

**Implementation Approach:**
```typescript
@Route('api/v2/auth')
export class AuthController extends Controller {
  @Post('/')
  @Response<ErrorResponse>(404, 'User not found')
  @Response<ValidationError>(400, 'Validation failed')
  public async authenticateUser(
    @Body() requestBody: AuthenticateRequest
  ): Promise<AuthToken> {
    // Logic here
  }
}
```

**Pros:**
- ✅ Comprehensive solution - routes + validation + docs
- ✅ Battle-tested - production-ready
- ✅ Automatic OpenAPI generation
- ✅ Type-safe end-to-end
- ✅ Excellent documentation

**Cons:**
- ❌ Major refactoring required - rewrite all route handlers
- ❌ Abandons domain-driven structure
- ❌ Cannot reuse existing Zod schemas
- ❌ Learning curve - decorator syntax
- ❌ Build step required - tsoa CLI
- ❌ Breaks existing patterns

**Effort Estimate:** 1-2 weeks
**Maintenance:** Medium

---

### Option 3: swagger-jsdoc + swagger-ui-express (Traditional)

Add JSDoc comments above routes to generate OpenAPI documentation.

**Libraries:**
- `swagger-jsdoc` (parses JSDoc → OpenAPI)
- `swagger-ui-express` (serves Swagger UI)

**Implementation Approach:**
```typescript
/**
 * @openapi
 * /api/v2/auth:
 *   post:
 *     summary: Authenticate user
 *     tags: [Authentication]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - publicId
 *             properties:
 *               publicId:
 *                 type: string
 *     responses:
 *       200:
 *         description: JWT token
 */
router.post('/', API_AUTH.authenticateUser);
```

**Pros:**
- ✅ Zero refactoring - add comments to existing code
- ✅ Familiar syntax - JSDoc is widely known
- ✅ Flexible - works with any Express architecture
- ✅ Quick to start - incremental implementation

**Cons:**
- ❌ No type safety - documentation can drift from code
- ❌ Violates DRY - duplicate Zod schemas in JSDoc
- ❌ Verbose - large comment blocks clutter code
- ❌ TypeScript transpilation issues
- ❌ Manual maintenance - easy to forget updates
- ❌ No runtime validation - docs and validation are separate

**Effort Estimate:** 1-2 days initial, ongoing maintenance
**Maintenance:** High

---

### Option 4: express-zod-api (Framework Alternative)

Purpose-built framework combining Express + Zod + OpenAPI generation.

**Library:**
- `express-zod-api` (replaces vanilla Express routing)

**Implementation Approach:**
```typescript
import { createServer } from 'express-zod-api';

const authenticateEndpoint = {
  method: 'post',
  input: z.object({
    publicId: z.string().min(1)
  }),
  output: z.object({
    token: z.string()
  }),
  handler: async ({ input }) => {
    return { token: 'jwt_token' };
  }
};
```

**Pros:**
- ✅ Perfect Zod integration
- ✅ Automatic OpenAPI generation
- ✅ Type-safe
- ✅ Client generation capability
- ✅ Modern approach

**Cons:**
- ❌ Framework lock-in - replaces Express routing
- ❌ Major migration - rewrite all routes
- ❌ Less mature - smaller community
- ❌ Loses middleware flexibility

**Effort Estimate:** 2-3 weeks
**Maintenance:** Low (but locked into framework)

---

## Comparison Matrix

| Criteria | Zod-to-OpenAPI | tsoa | swagger-jsdoc | express-zod-api |
|----------|----------------|------|---------------|-----------------|
| **Refactoring Required** | Medium | High | Minimal | Very High |
| **Leverages Existing Zod** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Type Safety** | ✅ Excellent | ✅ Excellent | ❌ None | ✅ Excellent |
| **Learning Curve** | Low | Medium | Low | Medium |
| **Maintenance Burden** | Low | Medium | High | Low |
| **Community Support** | Medium | High | High | Low |
| **Fits Current Architecture** | ✅ Yes | ❌ No | ✅ Yes | ❌ No |
| **Implementation Time** | 2-4 days | 1-2 weeks | 1-2 days | 2-3 weeks |

## Decision

**Selected: Option 1 - Zod-to-OpenAPI Integration**

**Rationale:**
1. Leverages existing Zod investment - we already have validation schemas
2. Maintains domain-driven architecture without major restructuring
3. Single source of truth prevents documentation drift
4. Moderate effort with long-term maintainability benefits
5. Can implement incrementally (domain by domain)
6. Type safety and runtime validation remain aligned
7. Team has minimal learning curve

## Technical Implementation

### Phase 1: Foundation Setup
1. Install dependencies:
   - `@astahmer/zod-to-openapi`
   - `swagger-ui-express`
   - `@types/swagger-ui-express`

2. Create OpenAPI registry initialization:
   - Configure base OpenAPI spec (title, version, servers)
   - Set up Swagger UI endpoint at `/api-docs`
   - Add environment-based protection (disable in production if needed)

### Phase 2: Schema Enhancement
1. Extend Zod schemas with OpenAPI metadata:
   - Add `.openapi()` calls to existing schemas
   - Include descriptions, examples, and constraints
   - Define response schemas where missing

2. Create reusable schema components:
   - Common error responses
   - Pagination schemas
   - Authentication headers

### Phase 3: Route Registration
1. Register routes in OpenAPI registry per domain:
   - Start with `auth` domain (smallest)
   - Document request/response schemas
   - Add tags for grouping
   - Include security requirements

2. Repeat for remaining domains:
   - tournament
   - match
   - league
   - guess
   - member
   - dashboard
   - admin

### Phase 4: Testing & Deployment
1. Verify generated OpenAPI spec:
   - Test Swagger UI functionality
   - Validate request/response schemas
   - Ensure examples are accurate

2. Deploy:
   - Add `/api-docs` route to staging first
   - Verify with team
   - Deploy to demo and production

### Security Configuration

```typescript
// Only expose Swagger in non-production environments
if (env.NODE_ENV !== 'production') {
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(openApiSpec));
}

// Alternative: Add authentication to Swagger UI
app.use('/api-docs', AuthMiddleware, swaggerUi.serve, swaggerUi.setup(openApiSpec));
```

### Implementation Example

```typescript
// src/services/openapi/registry.ts
import { OpenAPIRegistry, OpenApiGeneratorV3 } from '@astahmer/zod-to-openapi';
import { extendZodWithOpenApi } from '@astahmer/zod-to-openapi';
import { z } from 'zod';

extendZodWithOpenApi(z);

export const registry = new OpenAPIRegistry();

// Register common components
registry.registerComponent('ErrorResponse', z.object({
  message: z.string()
}).openapi({ description: 'Standard error response' }));

// src/domains/auth/openapi.ts
import { registry } from '@/services/openapi/registry';
import { authenticateUserSchema } from './api';

registry.registerPath({
  method: 'post',
  path: '/api/v2/auth',
  tags: ['Authentication'],
  summary: 'Authenticate user',
  request: {
    body: {
      content: {
        'application/json': {
          schema: authenticateUserSchema
        }
      }
    }
  },
  responses: {
    200: {
      description: 'JWT token',
      content: {
        'application/json': {
          schema: z.string()
        }
      }
    },
    404: {
      description: 'User not found',
      content: {
        'application/json': {
          schema: z.object({ message: z.string() })
        }
      }
    }
  }
});

// src/index.ts
import swaggerUi from 'swagger-ui-express';
import { OpenApiGeneratorV3 } from '@astahmer/zod-to-openapi';
import { registry } from '@/services/openapi/registry';

// Import all domain OpenAPI registrations
import '@/domains/auth/openapi';
import '@/domains/tournament/openapi';
// ... etc

const generator = new OpenApiGeneratorV3(registry.definitions);
const openApiSpec = generator.generateDocument({
  openapi: '3.0.0',
  info: {
    title: 'Best Shot API',
    version: env.API_VERSION || 'v2'
  },
  servers: [
    { url: 'https://api-best-shot-staging.mariobrusarosco.com', description: 'Staging' },
    { url: 'https://api-best-shot-demo.mariobrusarosco.com', description: 'Demo' },
    { url: 'https://api-best-shot.mariobrusarosco.com', description: 'Production' }
  ]
});

if (env.NODE_ENV !== 'production') {
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(openApiSpec));
}
```

## Consequences

### Positive

1. **Developer Experience**
   - Interactive API documentation with "Try it out" functionality
   - Self-documenting API reduces onboarding time
   - Clear contract for frontend-backend communication

2. **Type Safety**
   - Single source of truth for validation and documentation
   - Runtime validation matches documented schemas
   - Prevents documentation drift

3. **Maintainability**
   - Low maintenance overhead
   - Documentation updates automatically with code changes
   - Incremental implementation possible

4. **Architecture Preservation**
   - No changes to domain-driven structure
   - Existing patterns remain intact
   - Minimal refactoring required

5. **Client Generation**
   - OpenAPI spec can generate TypeScript clients
   - Potential for mobile app SDK generation
   - Third-party integration becomes easier

### Negative

1. **Initial Setup Cost**
   - 2-4 days to implement across all domains
   - Need to create response schemas (currently missing)
   - Learning curve for OpenAPI metadata

2. **Manual Route Registration**
   - Each endpoint must be manually registered
   - More verbose than decorator-based approaches
   - Requires discipline to document new endpoints

3. **Bundle Size**
   - Additional dependencies in production (swagger-ui-express)
   - Can mitigate by only loading in non-production environments

4. **Incomplete Documentation Initially**
   - Incremental rollout means partial documentation at first
   - Need to prioritize which domains to document first

### Mitigation Strategies

1. **Incremental Rollout**
   - Start with auth domain (smallest, most critical)
   - Document one domain per sprint
   - Gather team feedback and adjust approach

2. **Response Schema Creation**
   - Create response schemas alongside OpenAPI registration
   - Use existing TypeScript types as reference
   - Start simple, enhance with examples later

3. **Documentation Standards**
   - Create templates for common patterns
   - Document process in developer guide
   - Add pre-commit hook to remind about documentation

4. **Environment Protection**
   - Disable Swagger in production initially
   - Monitor performance impact
   - Consider authentication for Swagger UI

5. **Team Training**
   - Hold knowledge-sharing session on Zod OpenAPI extensions
   - Create example implementations
   - Document common patterns in wiki

## References

- [Zod to OpenAPI - GitHub](https://github.com/astahmer/zod-to-openapi)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Swagger UI Express](https://www.npmjs.com/package/swagger-ui-express)
- [Zod Documentation](https://zod.dev/)
- [Express OpenAPI Validator](https://www.npmjs.com/package/express-openapi-validator)
- [OpenAPI Best Practices](https://swagger.io/resources/articles/best-practices-in-api-documentation/)
