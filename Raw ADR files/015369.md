# Frontend-Backend Domain Model Sharing Strategy

* Status: accepted
* Deciders: Platform Team, Frontend Team
* Date: 2025-12-07

## Context and Problem Statement

This monorepo will have multiple frontend applications (ecommerce-web, kiosk-web, pos-web) that consume the same backend APIs (cart-service, product-service, etc.). Currently, frontend TypeScript types are hand-written and don't match backend Java DTOs. For example:

- Backend `Product.java` has `long sku` and `String price`
- Frontend `product.ts` has `string sku` and `number price`

As we scale to 3+ frontend clients sharing the same APIs, we need a strategy that ensures type consistency, enables LLM agent productivity, provides excellent documentation, and catches API contract mismatches at build time rather than runtime.

## Decision Drivers

1. **LLM Agent Productivity** - AI coding assistants need discoverable, well-documented types to generate correct API integration code without hallucinating endpoints or field names
2. **Multi-Client Consistency** - ecommerce-web, kiosk-web, and pos-web must use identical type definitions for shared APIs to prevent subtle bugs
3. **Documentation as Code** - API contracts should be self-documenting, reducing the need for separate API documentation that drifts from implementation
4. **Compile-Time Correctness** - Type mismatches between frontend and backend should fail builds, not cause runtime errors
5. **Developer Experience** - Minimal friction for both Java backend and TypeScript frontend developers
6. **Incremental Adoption** - Must work with existing services without requiring a "big bang" migration

## Considered Options

1. **OpenAPI Code Generation (Code-First)** - Generate OpenAPI specs from annotated Spring controllers, then generate TypeScript clients (chosen)
2. **OpenAPI Code Generation (Spec-First)** - Write OpenAPI specs manually as the source of truth, generate both Java DTOs and TypeScript types
3. **Hand-Written TypeScript Types** - Continue manually defining frontend types per application
4. **Shared Runtime Schema (TypeBox/Zod)** - Define schemas in TypeScript that generate types and provide runtime validation
5. **GraphQL with Codegen** - Use GraphQL as the API layer with automatic type generation

## Decision Outcome

Chosen option: **OpenAPI Code Generation (Code-First)**

Spring Boot services annotate their controllers and DTOs with `springdoc-openapi`, which generates `/v3/api-docs` OpenAPI specifications at runtime. The existing `tools/openapi-codegen/generate.sh` script uses `@openapitools/openapi-generator-cli` to produce TypeScript clients that all frontend applications import from `libs/frontend/shared-data/api-client/`.

This approach leverages our existing Java-first development model while providing:
- A single source of truth (Java DTOs + Spring annotations)
- Automatic TypeScript generation with full type safety
- Rich OpenAPI documentation accessible via Swagger UI
- LLM-friendly API discovery through both OpenAPI specs and generated TypeScript interfaces

### Positive Consequences

- **Single Source of Truth** - Java DTOs are authoritative; TypeScript types are derived, eliminating drift
- **LLM Agent Excellence** - Generated types include JSDoc from `@Schema` annotations, giving AI assistants rich context for code generation
- **Contract Testing Ready** - OpenAPI specs can be used with tools like Pact or Schemathesis for API contract testing
- **Swagger UI** - Developers and AI agents can explore APIs interactively at `/swagger-ui.html`
- **Incremental Rollout** - Services can adopt annotations gradually; unannotated endpoints still work
- **Industry Standard** - OpenAPI is widely supported by API gateways, documentation tools, and code generators

### Negative Consequences

- **Build-Time Dependency** - TypeScript generation requires running backend services (can be mitigated with committed specs)
- **Annotation Overhead** - Developers must add `@Schema`, `@Operation` annotations to maximize generated documentation
- **Generator Quirks** - OpenAPI generators can produce awkward TypeScript (e.g., overly verbose class names); requires configuration tuning
- **Two-Step Validation** - Runtime OpenAPI docs may differ from committed specs if services change; CI must validate

## Pros and Cons of the Options

### 1. OpenAPI Code Generation (Code-First) - CHOSEN

Java controllers and DTOs are annotated with springdoc-openapi. At build/runtime, services expose `/v3/api-docs`. A codegen script produces TypeScript clients.

**Implementation:**
```java
// Product.java
@Schema(description = "Product with pricing and availability")
public record Product(
    @Schema(description = "Stock Keeping Unit", example = "SKU-12345")
    long sku,
    @Schema(description = "Product display name")
    String description,
    @Schema(description = "Current price in USD", example = "29.99")
    String price,
    @Schema(description = "Available inventory count")
    int availableQuantity
) {}
```

```java
// ProductController.java
@Operation(summary = "Get product by SKU",
           description = "Returns product details including current price and availability")
@ApiResponse(responseCode = "200", description = "Product found")
@ApiResponse(responseCode = "404", description = "Product not found")
@GetMapping("/products/{sku}")
public Mono<Product> getProduct(@PathVariable long sku) { ... }
```

Generated TypeScript:
```typescript
/** Product with pricing and availability */
export interface Product {
  /** Stock Keeping Unit */
  sku: number;
  /** Product display name */
  description: string;
  /** Current price in USD */
  price: string;
  /** Available inventory count */
  availableQuantity: number;
}
```

**Good**
- Java developers work in familiar territory; TypeScript is auto-generated
- `@Schema` descriptions become JSDoc comments, excellent for LLM context
- Swagger UI provides interactive API exploration for developers and AI agents
- OpenAPI specs can be committed to git for offline generation and contract testing
- Mature ecosystem: springdoc-openapi, openapi-generator-cli, Redoc
- Generated fetch clients handle serialization, headers, error responses
- Supports all REST patterns (pagination, HATEOAS, file uploads)

**Bad**
- Requires backend service running for live spec generation (mitigated by committing specs)
- `openapi-generator-cli` output can be verbose; needs `--additional-properties` tuning
- Reactive types (Mono/Flux) require springdoc configuration to unwrap correctly
- Annotations add boilerplate to Java code
- Generated TypeScript may not match project code style (fixable with prettier post-processing)

**LLM Agent Considerations**
- Excellent: Generated types with JSDoc are highly discoverable
- Agents can fetch `/v3/api-docs` JSON to understand all endpoints
- Swagger UI at `/swagger-ui.html` provides human-readable exploration
- Committed OpenAPI specs in repo are directly readable by agents

### 2. OpenAPI Code Generation (Spec-First)

OpenAPI YAML/JSON files are written manually as the source of truth. Both Java DTOs and TypeScript clients are generated from specs.

**Good**
- API design happens before implementation, encouraging thoughtful contracts
- Perfect parity between Java and TypeScript - both are generated
- Specs can be reviewed/approved before implementation
- Works without running services
- Enables parallel frontend/backend development from shared spec

**Bad**
- Requires developers to learn OpenAPI specification syntax
- Generated Java code may not match Spring conventions or project patterns
- Two sources of truth (specs and implementation) can drift
- Additional tooling for Java generation (openapi-generator for Spring, or custom templates)
- Friction: developers must edit YAML, regenerate code, then customize
- Generated Java records/classes may lack custom validation logic

**LLM Agent Considerations**
- Good: Specs are directly readable and often included in project context
- Risk: Agents may edit spec but forget to regenerate, causing inconsistency
- Requires clear documentation that spec → generated code relationship

### 3. Hand-Written TypeScript Types

Continue the current approach: frontend teams manually define TypeScript interfaces in each application or shared library.

**Current State:**
```typescript
// apps/ecommerce-web/src/features/products/types/product.ts
export interface Product {
  sku: string;        // Backend uses long!
  name: string;       // Backend calls this "description"!
  price: number;      // Backend uses String!
  imageUrl: string;   // Doesn't exist in backend!
}
```

**Good**
- Maximum flexibility for frontend-specific shapes
- No build tooling or generation steps
- Frontend can evolve independently of backend changes
- Simple to understand and modify

**Bad**
- Types drift from backend reality (already happening - see current state)
- Each frontend app may define types differently
- No compile-time guarantee that types match API responses
- Runtime errors when backend changes break assumptions
- LLM agents will generate code against stale/incorrect types
- Duplicated effort across ecommerce-web, kiosk-web, pos-web

**LLM Agent Considerations**
- Poor: Agents have no way to verify types match actual API
- High risk of generating incorrect integration code
- Types lack descriptions/documentation for context

### 4. Shared Runtime Schema (TypeBox/Zod)

Define schemas in TypeScript using a library like TypeBox or Zod. Schemas provide runtime validation and static type inference.

**Implementation:**
```typescript
// libs/frontend/shared-data/schemas/product.ts
import { Type, Static } from '@sinclair/typebox';

export const ProductSchema = Type.Object({
  sku: Type.Number({ description: 'Stock Keeping Unit' }),
  description: Type.String(),
  price: Type.String({ pattern: '^\\d+\\.\\d{2}$' }),
  availableQuantity: Type.Integer({ minimum: 0 })
});

export type Product = Static<typeof ProductSchema>;

// Runtime validation
import Ajv from 'ajv';
const ajv = new Ajv();
const validate = ajv.compile(ProductSchema);

function parseProduct(data: unknown): Product {
  if (!validate(data)) throw new ValidationError(validate.errors);
  return data as Product;
}
```

**Good**
- Runtime validation catches API mismatches immediately with clear errors
- Single definition for type + validation (DRY)
- JSON Schema export for documentation
- TypeBox schemas can generate OpenAPI components
- Works without backend changes

**Bad**
- Backend remains the "real" source of truth; schemas are still manually synchronized
- Runtime overhead for validation on every API response
- TypeScript-centric: Java backend doesn't benefit
- Requires discipline to update schemas when backend changes
- Bundle size increase from schema/validation libraries

**LLM Agent Considerations**
- Moderate: Schemas are more descriptive than bare interfaces
- Agents still can't verify schemas match actual backend
- JSON Schema export could be compared against backend OpenAPI

### 5. GraphQL with Codegen

Use GraphQL as the API layer. Schema-first design with automatic type generation for both server and client.

**Current State:** order-service already has GraphQL support (`@Operation(summary = "Get orders (GraphQL)")`).

**Implementation:**
```graphql
# schema.graphql
type Product {
  """Stock Keeping Unit"""
  sku: ID!
  """Product display name"""
  description: String!
  """Current price in USD format"""
  price: String!
  """Available inventory count"""
  availableQuantity: Int!
}

type Query {
  product(sku: ID!): Product
  products(search: String, first: Int): ProductConnection!
}
```

```typescript
// Generated by graphql-codegen
export type Product = {
  __typename?: 'Product';
  /** Stock Keeping Unit */
  sku: Scalars['ID'];
  /** Product display name */
  description: Scalars['String'];
  /** Current price in USD format */
  price: Scalars['String'];
  /** Available inventory count */
  availableQuantity: Scalars['Int'];
};

// Generated hook
export function useProductQuery(sku: string) {
  return useQuery(ProductDocument, { variables: { sku } });
}
```

**Good**
- Schema is the single source of truth for both server and client
- Excellent developer experience with generated hooks and types
- Introspection enables powerful tooling (GraphiQL, IDE plugins)
- Clients request exactly the fields they need (no over-fetching)
- Subscriptions for real-time updates
- Strong typing with nullability and custom scalars

**Bad**
- Significant migration effort from existing REST APIs
- GraphQL learning curve for backend developers
- Need to implement resolvers for all existing REST endpoints
- Potential N+1 query issues require DataLoader patterns
- Caching is more complex than REST (no HTTP caching)
- WebFlux + GraphQL integration requires careful setup

**LLM Agent Considerations**
- Excellent: GraphQL schema is highly structured and self-documenting
- Introspection query returns full schema for agent consumption
- Generated types include full documentation
- Risk: Agents familiar with REST may generate incorrect patterns

## Comparison Matrix

| Criterion | Code-First OpenAPI | Spec-First OpenAPI | Hand-Written | TypeBox/Zod | GraphQL |
|-----------|-------------------|-------------------|--------------|-------------|---------|
| Single Source of Truth | Java DTOs | YAML Specs | None | TS Schemas | GraphQL Schema |
| LLM Agent Friendliness | Excellent | Good | Poor | Moderate | Excellent |
| Multi-Client Consistency | Automatic | Automatic | Manual | Manual | Automatic |
| Compile-Time Safety | Generated | Generated | None | Inferred | Generated |
| Documentation | Swagger UI | Redoc/Swagger | Manual | JSON Schema | GraphiQL |
| Migration Effort | Low | Medium | None | Low | High |
| Java Developer Experience | Native | Foreign | N/A | N/A | Learning Curve |
| TS Developer Experience | Consume Only | Consume Only | Full Control | Full Control | Consume + Schema |

## Hybrid REST + GraphQL Services

Services like order-service and cart-service expose both REST and GraphQL APIs from the same domain models. This requires a unified approach to type generation that handles both protocols.

### Current Architecture (order-service and cart-service)

Both order-service and cart-service implement the hybrid pattern, exposing the same domain models via both REST and GraphQL.

```
┌─────────────────────────────────────────────────────────────────┐
│                     Java Domain Model                            │
│            Order.java / Cart.java (domain aggregate)            │
│   (Single Source of Truth - all fields including nested types)  │
└─────────────────────┬───────────────────────┬───────────────────┘
                      │                       │
                      ▼                       ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│     REST Controller         │   │    GraphQL Controller        │
│   OrderController.java      │   │  OrderQueryController.java   │
│   @GetMapping("/orders")    │   │  @QueryMapping order()       │
│          │                  │   │          │                   │
│          ▼                  │   │          ▼                   │
│   springdoc-openapi         │   │   schema.graphqls            │
│   /v3/api-docs              │   │   (23 exposed fields)        │
└─────────────────────────────┘   └─────────────────────────────┘
                      │                       │
                      ▼                       ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│   openapi-generator-cli     │   │    graphql-codegen           │
│   typescript-fetch          │   │    typescript-operations     │
└─────────────────────────────┘   └─────────────────────────────┘
                      │                       │
                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                libs/frontend/shared-data/api-client/             │
│  ├── generated/rest/order-service/        (OpenAPI types)       │
│  └── generated/graphql/order-service/     (GraphQL types)       │
└─────────────────────────────────────────────────────────────────┘
```

### Why This Works

1. **Java Record is the source of truth**: `Order.java` defines all 33 fields
2. **GraphQL schema is a view**: `schema.graphqls` exposes 23 fields (hides internal fields like `reservationId`, `sessionId`)
3. **OpenAPI is another view**: REST may expose different fields or transformations
4. **Both generate compatible types**: Since both derive from the same Java model

### Generated Type Organization

```
libs/frontend/shared-data/api-client/src/
├── generated/
│   ├── rest/
│   │   ├── product-service/     # REST-only service
│   │   │   ├── models/
│   │   │   │   └── Product.ts
│   │   │   └── api/
│   │   │       └── ProductApi.ts
│   │   ├── cart-service/        # Hybrid service (REST types)
│   │   │   ├── models/
│   │   │   │   └── Cart.ts
│   │   │   └── api/
│   │   │       └── CartApi.ts
│   │   └── order-service/       # Hybrid service (REST types)
│   │       └── ...
│   └── graphql/
│       ├── cart-service/        # Hybrid service (GraphQL types)
│       │   ├── types.ts
│       │   └── hooks.ts         # useCartQuery, useAddToCartMutation
│       └── order-service/       # Hybrid service (GraphQL types)
│           ├── types.ts
│           └── hooks.ts         # useOrderQuery, useOrdersQuery
└── index.ts                     # Re-exports for consumers
```

### Frontend Usage Pattern

```typescript
// For REST-only services (product-service)
import { Product, ProductApi } from '@reactive-platform/api-client/rest/product-service';

// For GraphQL queries (order-service)
import { useOrderQuery, Order } from '@reactive-platform/api-client/graphql/order-service';

// For hybrid services - choose based on use case:
// - GraphQL for complex queries with field selection
// - REST for simple CRUD with caching
import { Cart as RestCart, CartApi } from '@reactive-platform/api-client/rest/cart-service';
import { useCartQuery, Cart as GqlCart } from '@reactive-platform/api-client/graphql/cart-service';
```

### When to Use REST vs GraphQL

| Use Case | Protocol | Reason |
|----------|----------|--------|
| Simple CRUD | REST | HTTP caching, simpler debugging |
| Complex queries with field selection | GraphQL | Avoid over-fetching |
| Real-time updates | GraphQL | Subscriptions |
| File uploads | REST | Better multipart support |
| Public API | REST | More widely understood |
| Mobile with bandwidth constraints | GraphQL | Request only needed fields |

### Generation Script Updates

Update `tools/openapi-codegen/generate.sh` to handle both protocols:

```bash
#!/usr/bin/env bash
set -e

SERVICES=("product-service:8080" "cart-service:8081" "order-service:8088")

# Generate REST types from OpenAPI
for service_port in "${SERVICES[@]}"; do
  IFS=':' read -r service port <<< "$service_port"
  echo "Generating REST types for $service..."

  curl -s "http://localhost:$port/v3/api-docs" -o "tools/openapi-codegen/specs/$service.json"

  pnpm openapi-generator-cli generate \
    -i "tools/openapi-codegen/specs/$service.json" \
    -g typescript-fetch \
    -o "libs/frontend/shared-data/api-client/src/generated/rest/$service" \
    --additional-properties=supportsES6=true,typescriptThreePlus=true
done

# Generate GraphQL types for services with GraphQL support
GRAPHQL_SERVICES=("cart-service:8081" "order-service:8088")

for service_port in "${GRAPHQL_SERVICES[@]}"; do
  IFS=':' read -r service port <<< "$service_port"
  echo "Generating GraphQL types for $service..."

  # Fetch GraphQL schema via introspection
  pnpm graphql-codegen --config "tools/graphql-codegen/$service.yml"
done

echo "Type generation complete!"
```

### graphql-codegen Configuration

```yaml
# tools/graphql-codegen/order-service.yml
schema: http://localhost:8088/graphql
documents: apps/ecommerce-web/src/**/*.graphql
generates:
  libs/frontend/shared-data/api-client/src/generated/graphql/order-service/types.ts:
    plugins:
      - typescript
      - typescript-operations
    config:
      skipTypename: false
      enumsAsTypes: true

  libs/frontend/shared-data/api-client/src/generated/graphql/order-service/hooks.ts:
    plugins:
      - typescript-react-query
    config:
      fetcher: graphql-request
```

### LLM Agent Considerations for Hybrid Services

1. **Clear Protocol Indicators**: Generated paths (`/rest/` vs `/graphql/`) make protocol obvious
2. **Schema Discovery**: Agents can fetch both `/v3/api-docs` (REST) and introspect `/graphql` (GraphQL)
3. **Documentation Parity**: Both OpenAPI and GraphQL schemas include descriptions from Java annotations
4. **Consistent Naming**: Same entity name (`Order`) in both protocols, importable from different paths

## Committed Specs Strategy

**OpenAPI and GraphQL specs are committed to the repository** rather than only generated at runtime. This is critical for LLM agent productivity and CI reliability.

### Repository Structure

```
tools/
├── openapi-codegen/
│   ├── generate.sh              # Generation script
│   └── specs/                   # Committed OpenAPI specs (JSON)
│       ├── product-service.json
│       ├── cart-service.json
│       ├── order-service.json
│       ├── customer-service.json
│       ├── discount-service.json
│       ├── fulfillment-service.json
│       ├── checkout-service.json
│       └── audit-service.json
└── graphql-codegen/
    ├── cart-service.yml         # Codegen config
    ├── order-service.yml
    └── schemas/                 # Committed GraphQL schemas
        ├── cart-service.graphqls
        └── order-service.graphqls
```

### Benefits of Committed Specs

| Benefit | Description |
|---------|-------------|
| **LLM Agent Discovery** | Agents can read specs directly without running services |
| **Offline Generation** | TypeScript can be regenerated without backend running |
| **Contract Versioning** | Git history shows API evolution over time |
| **PR Review** | API changes are visible in diffs alongside code |
| **CI Validation** | Compare committed vs runtime specs to detect drift |
| **Documentation** | Specs serve as always-accurate API documentation |

### CI Validation Workflow

```yaml
# .github/workflows/api-contract.yml
jobs:
  validate-specs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start services
        run: docker compose up -d --wait

      - name: Validate OpenAPI specs match runtime
        run: |
          for service in product cart order customer discount fulfillment checkout audit; do
            port=$(grep "$service" tools/check-service-ports.mjs | grep -oE '[0-9]{4}')
            echo "Checking $service on port $port..."
            curl -s "http://localhost:$port/v3/api-docs" > /tmp/$service.json
            diff tools/openapi-codegen/specs/$service-service.json /tmp/$service.json \
              || (echo "DRIFT DETECTED in $service-service" && exit 1)
          done

      - name: Validate generated TypeScript is up-to-date
        run: |
          ./tools/openapi-codegen/generate.sh
          git diff --exit-code libs/frontend/shared-data/api-client/src/generated/ \
            || (echo "Generated types are out of date. Run 'pnpm generate:api'" && exit 1)
```

### Update Workflow

When backend APIs change:

```bash
# 1. Make backend changes (DTOs, controllers, GraphQL schema)

# 2. Start services locally
docker compose up -d

# 3. Regenerate and commit specs + types
pnpm generate:api

# 4. Commit everything together
git add tools/openapi-codegen/specs/
git add tools/graphql-codegen/schemas/
git add libs/frontend/shared-data/api-client/src/generated/
git commit -m "feat(api): update cart-service contract for new discount field"
```

### Generation Script with Spec Commit

```bash
#!/usr/bin/env bash
# tools/openapi-codegen/generate.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPECS_DIR="$SCRIPT_DIR/specs"
OUTPUT_DIR="$(dirname "$SCRIPT_DIR")/../libs/frontend/shared-data/api-client/src/generated"

mkdir -p "$SPECS_DIR"

declare -A SERVICES=(
  ["product-service"]=8080
  ["cart-service"]=8081
  ["customer-service"]=8083
  ["discount-service"]=8084
  ["fulfillment-service"]=8085
  ["audit-service"]=8086
  ["checkout-service"]=8087
  ["order-service"]=8088
)

echo "=== Fetching OpenAPI specs ==="
for service in "${!SERVICES[@]}"; do
  port="${SERVICES[$service]}"
  echo "Fetching $service from port $port..."
  curl -sf "http://localhost:$port/v3/api-docs" | jq '.' > "$SPECS_DIR/$service.json" \
    || echo "WARNING: $service not running on port $port"
done

echo "=== Generating TypeScript clients ==="
for service in "${!SERVICES[@]}"; do
  if [[ -f "$SPECS_DIR/$service.json" ]]; then
    echo "Generating types for $service..."
    pnpm openapi-generator-cli generate \
      -i "$SPECS_DIR/$service.json" \
      -g typescript-fetch \
      -o "$OUTPUT_DIR/rest/$service" \
      --additional-properties=supportsES6=true,typescriptThreePlus=true,withInterfaces=true \
      --skip-validate-spec
  fi
done

echo "=== Formatting generated code ==="
pnpm prettier --write "$OUTPUT_DIR/**/*.ts"

echo "=== Done ==="
echo "Specs saved to: $SPECS_DIR"
echo "Types saved to: $OUTPUT_DIR"
echo ""
echo "Don't forget to commit both specs and generated types!"
```

## Implementation Notes and Next Steps

### Phase 1: Enable OpenAPI Generation (Backend)

1. Add springdoc-openapi to `gradle/libs.versions.toml`:
   ```toml
   [versions]
   springdoc = "2.7.0"

   [libraries]
   springdoc-openapi-starter-webflux-ui = { module = "org.springdoc:springdoc-openapi-starter-webflux-ui", version.ref = "springdoc" }
   ```

2. Add to `libs/backend/platform/platform-bom/build.gradle.kts`:
   ```kotlin
   api(libs.springdoc.openapi.starter.webflux.ui)
   ```

3. Annotate DTOs and controllers with `@Schema` and `@Operation`

4. Configure springdoc in `application.yml`:
   ```yaml
   springdoc:
     api-docs:
       path: /v3/api-docs
     swagger-ui:
       path: /swagger-ui.html
   ```

### Phase 2: Automate TypeScript Generation

1. Update `tools/openapi-codegen/generate.sh` to fetch specs from all services
2. Configure `openapi-generator-cli` with project-appropriate options:
   ```bash
   --additional-properties=supportsES6=true,typescriptThreePlus=true,withInterfaces=true
   ```
3. Add post-generation prettier formatting
4. Create Nx target for regeneration: `pnpm nx generate:api`

### Phase 3: CI/CD Integration

1. Commit generated OpenAPI specs to `tools/openapi-codegen/specs/`
2. Add CI step to verify specs match running services
3. Fail builds if generated TypeScript differs from committed version
4. Consider Pact or Schemathesis for contract testing

### Phase 4: Frontend Migration

1. Replace hand-written types in `apps/ecommerce-web/src/features/*/types/` with imports from generated client
2. Update React Query hooks to use generated API client
3. Document shared client usage for kiosk-web and pos-web teams

## References

### Codebase
- Current frontend types (will be replaced): `apps/ecommerce-web/src/features/cart/types/cart.ts`
- Current API client wrapper: `libs/frontend/shared-data/api-client/src/lib/api-client.ts`
- Existing codegen script: `tools/openapi-codegen/generate.sh`
- Backend Product DTO: `libs/backend/shared-model/shared-model-product/src/main/java/org/example/model/product/Product.java`

**cart-service (hybrid REST + GraphQL)**
- Cart domain model: `apps/cart-service/src/main/java/org/example/cart/domain/Cart.java`
- Cart REST controller: `apps/cart-service/src/main/java/org/example/cart/controller/CartController.java`
- Cart GraphQL schema: `apps/cart-service/src/main/resources/graphql/schema.graphqls`

**order-service (hybrid REST + GraphQL)**
- Order domain model: `apps/order-service/src/main/java/org/example/order/model/Order.java`
- Order GraphQL schema: `apps/order-service/src/main/resources/graphql/schema.graphqls`
- Order GraphQL controller: `apps/order-service/src/main/java/org/example/order/graphql/OrderQueryController.java`

### Related ADRs
- [006_frontend_monorepo_strategy.md](006_frontend_monorepo_strategy.md) - established Nx + pnpm for frontend

### External Documentation
- OpenAPI Generator CLI: https://openapi-generator.tech/docs/generators/typescript-fetch
- springdoc-openapi: https://springdoc.org/
- TypeBox: https://github.com/sinclairzx81/typebox
- GraphQL Codegen: https://the-guild.dev/graphql/codegen
- Spring for GraphQL: https://docs.spring.io/spring-graphql/reference/
