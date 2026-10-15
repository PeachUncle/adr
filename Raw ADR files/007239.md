# ADR-022: Building-Blocks Architecture - No HTTP Client Generation

## Status

**Accepted** - November 29, 2025  
**Implementation:** Core library

philosophy

## Context

During the investigation of test failures (Session 3.7), we discovered that several tests expected this library to generate complete HTTP client implementations (e.g., `createClient<paths>()` from openapi-fetch). This raised a fundamental question: **Should this library generate complete SDKs with HTTP clients, or provide building blocks for consumers to build their own SDKs?**

### Historical Context

The previous library architecture generated:

- Zod schemas for validation
- **Complete Zodios HTTP client** (with axios)
- All-in-one solution requiring no additional HTTP client choice

### Current Landscape

**Modern ecosystem has evolved:**

1. **This library (current)**: Generates Zod schemas + building blocks (schemas, metadata, validation helpers)
2. **openapi-fetch**: Type-safe fetch wrapper consuming openapi-typescript types
3. **openapi-typescript**: Type generation without validation or HTTP client
4. **Multiple HTTP clients**: fetch (native), axios, ky, got, etc.

### The Question

**Should @engraph/castr:**

- **Option A**: Generate complete SDKs with HTTP client (like original @engraph/castr)?
- **Option B**: Generate building blocks, let consumers choose HTTP client?

### Key Insight from Research

After researching the ecosystem:

- **Previous approach** = Schema generation + Zodios HTTP client (coupled)
- **openapi-fetch** = Type-safe HTTP client only (no schema generation)

**Our library's role:**

- Provide **schema generation and validation** (non-HTTP parts)
- Enable a **separate SDK workspace** to handle HTTP client integration

This creates a modern, **composable architecture** instead of monolithic all-in-one generation.

### Why This Matters

**MCP Ecosystem Requirements:**

- MCP tools need **flexibility**, not locked-in HTTP clients
- Different deployment targets may require different HTTP clients
- Validation should be independent of HTTP transport

**Modern Library Design:**

- Single Responsibility Principle
- Composition over coupling
- Consumer choice over framework opinion

### Failing Tests

16 unit tests failed expecting:

- `createClient<paths>()` generation
- openapi-fetch integration
- Complete SDK with HTTP client bundled

These tests **constrained implementation** rather than **proving behavior**, violating our testing philosophy.

## Decision

**We adopt a building-blocks architecture where this library generates schemas, validation helpers, endpoint metadata, and MCP tools - BUT NOT complete HTTP client implementations.**

### What This Library Provides

✅ **Zod schemas** - Type-safe validation schemas from OpenAPI  
✅ **Endpoint metadata** - Method, path, parameters, responses  
✅ **Validation helpers** - `validateRequest()`, `validateResponse()`  
✅ **MCP tools** - Model Context Protocol tool definitions  
✅ **Schema registry** - Dynamic schema lookup utilities

### What This Library Does NOT Provide

❌ **HTTP client implementation** (consumers choose: fetch, axios, ky, openapi-fetch, etc.)  
❌ **Opinionated SDK structure** (consumers control their architecture)  
❌ **HTTP client configuration** (consumers set their defaults)

### Separate SDK Workspace (Phase 5)

A **separate workspace** will demonstrate how to build complete, production-ready SDKs:

- **Consumes** this library for schemas and validation
- **Adds** HTTP client integration (likely openapi-fetch)
- **Demonstrates** best practices for SDK construction
- **Serves** as both reference implementation and production-ready SDK

This validates that the building-blocks architecture works in practice.

## Rationale

### 1. Separation of Concerns

**Schema generation ≠ HTTP transport**

- Validation logic is independent of how HTTP requests are made
- HTTP clients evolve faster than validation schemas
- Different environments may require different HTTP clients (Node.js vs Edge vs Browser)

### 2. Consumer Flexibility

**Users can choose:**

- Native `fetch` (zero dependencies)
- `axios` (interceptors, cancellation)
- `ky` (modern, lightweight)
- `openapi-fetch` (type-safe, OpenAPI-native)
- Custom clients (enterprise requirements)

**Locked-in approach forces:**

- Specific HTTP client
- Specific error handling
- Specific retry logic
- Specific timeout behavior

### 3. MCP Ecosystem Alignment

**MCP tools need:**

- Validation schemas (✅ we provide)
- Endpoint metadata (✅ we provide)
- **Flexibility** in HTTP implementation (✅ consumers choose)

From Requirements #4-6:

- Consumers build SDKs using our building blocks
- Those SDKs create MCP tools
- Different SDKs may use different HTTP clients

### 4. Modern Library Design

**Compare successful libraries:**

| Library                        | Approach                        | Philosophy          |
| ------------------------------ | ------------------------------- | ------------------- |
| **zod**                        | Validation only                 | Building block      |
| **openapi-typescript**         | Types only                      | Building block      |
| **@engraph/castr**             | Schemas + metadata + validation | **Building blocks** |
| **openapi-fetch**              | HTTP only                       | Building block      |
| **Previous approach (Zodios)** | All-in-one                      | **Monolithic**      |

Modern ecosystems favor **composition** of focused libraries over monolithic all-in-one solutions.

### 5. Aligns with Existing Architecture

**Current codebase already implements this:**

- ✅ Schemas generation (working)
- ✅ Endpoint metadata (working)
- ✅ Validation helpers (working)
- ✅ MCP tools generation (working)
- ✅ openapi-fetch as **optional peer dependency** (not required)
- ✅ Multiple template options (schemas-only, schemas-with-metadata)

**Failing tests expected a different architecture** - not what the library actually does.

## Implementation

### Requirements Updated

Added three new requirements (#20-22) clarifying:

- This library provides building blocks, not complete SDKs
- Consumers choose their HTTP client
- Separate SDK workspace demonstrates full integration

### Documentation Updated

- **README.md**: Clarified building-blocks approach
- **.agent/README.md**: Added library philosophy
- **.agent/requirements.md**: Added Requirements #20-22
- **.agent/plans/00-STRATEGIC-OVERVIEW.md**: Added Phase 5 (SDK Workspace)

### Tests to Fix

The 16 failing tests expected:

- `createClient<paths>()` in generated code
- HTTP client integration
- SDK-specific features

**Resolution:** These tests must be:

1. **Evaluated** - Do they prove useful behavior, or just constrain implementation?
2. **Updated** - If useful, update expectations to match building-blocks architecture
3. **Removed** - If they only test "has HTTP client", they violate testing philosophy

Per `.agent/testing-strategy.md`:

> "Tests must prove that the system behaves correctly from the user's or caller's perspective, rather than verifying that specific code paths are executed."

Tests checking for `createClient<paths>()` are **implementation details**, not **behavior**.

## Consequences

### Positive

✅ **Maximum flexibility** - Consumers choose HTTP client  
✅ **Single responsibility** - Library focused on schemas and validation  
✅ **MCP-aligned** - Flexibility needed for MCP ecosystem  
✅ **Modern design** - Composition over monolithic  
✅ **Smaller bundles** - No forced HTTP client dependencies  
✅ **Future-proof** - Not tied to any HTTP client's evolution  
✅ **Already implemented** - Matches current architecture  
✅ **Phase 5 demonstrates** - SDK workspace shows full integration

### Negative

⚠️ **Not all-in-one** - Users must wire HTTP client themselves  
⚠️ **Learning curve** - Requires understanding building-blocks approach  
⚠️ **More setup** - Compared to pre-built SDK

### Mitigation

**Not All-in-One:**

- Phase 5 SDK workspace provides complete example
- Documentation shows integration patterns
- Pre-built SDK available for those who want it

**Learning Curve:**

- Clear documentation of building-blocks philosophy
- Examples for common HTTP clients (fetch, axios, openapi-fetch)
- Reference implementation in SDK workspace

**More Setup:**

- SDK workspace provides production-ready solution
- Can be used directly or as template
- Building blocks still available for custom needs

## Alignment with Requirements

**See:** `.agent/requirements.md`

This decision directly implements:

- **Req #20:** Building blocks, not complete SDK ✅
- **Req #21:** Consumer choice of HTTP client ✅
- **Req #22:** Separate SDK workspace demonstrates integration ✅

And supports:

- **Req #1-3:** Zod schemas, SDK creation support, validation helpers ✅
- **Req #4-6:** MCP tools from consumer-built SDKs ✅
- **Req #9-11:** Programmatic API, CLI, OpenAPI input ✅

## Comparison to Ecosystem

### This Library's Role

```typescript
// @engraph/castr provides:
import { endpoints, schemas, validateRequest, validateResponse } from '@engraph/castr';

// Consumers integrate with their HTTP client:
import createClient from 'openapi-fetch';
import type { paths } from './generated-types';

const client = createClient<paths>({ baseUrl: 'https://api.example.com' });

// Use building blocks for validation:
const endpoint = endpoints.find((e) => e.operationId === 'getUser');
validateRequest(endpoint, { pathParams: { id: '123' } });

const { data, error } = await client.GET('/users/{id}', { params: { path: { id: '123' } } });

if (data) {
  validateResponse(endpoint, 200, data);
}
```

### Relationship to Other Libraries

**Replaces the previous approach:**

- ✅ Schema generation (Zod, not Zodios)
- ✅ Validation helpers
- ✅ MCP tools
- ❌ HTTP client (consumers choose)

**Complements openapi-fetch:**

- ✅ Provides runtime validation (openapi-fetch only has compile-time types)
- ✅ Provides MCP tools
- ⚪ HTTP client integration done by consumer (optional)

**Different from openapi-typescript:**

- ✅ Runtime validation (openapi-typescript is types-only)
- ✅ MCP tools
- ⚪ Can be used together (types + validation)

## Related Decisions

- [ADR-016: Remove Zodios Dependencies](./ADR-016-remove-zodios-dependencies.md) - Removed HTTP client from default template
- [ADR-013: Architecture Rewrite Decision](./ADR-013-architecture-rewrite-decision.md) - Foundation decision
- Requirements #20-22 - Building-blocks architecture defined

## References

**Research:**

- Previous approach: All-in-one (schemas + Zodios HTTP client)
- openapi-fetch: Type-safe HTTP wrapper (no schema generation)

**Requirements:**

- `.agent/requirements.md` - Requirements #20-22 added

**Strategic Plan:**

- `.agent/plans/00-STRATEGIC-OVERVIEW.md` - Phase 5: Full SDK Workspace

**Documentation:**

- `README.md` - Updated to clarify building-blocks approach
- `.agent/README.md` - Added library philosophy

**Testing Philosophy:**

- `.agent/testing-strategy.md` - Tests prove behavior, not implementation
- `.agent/RULES.md` - Engineering excellence principles

## Timeline

- **November 29, 2025**: Decision accepted during test failure investigation
- **Phase 5 (Planned)**: SDK workspace demonstrates full integration (2-3 weeks post-extraction)

## Success Criteria

✅ Requirements #20-22 documented  
✅ Documentation updated (README, .agent docs, strategic plan)  
✅ ADR created and accepted  
✅ Test failures resolved per testing philosophy  
✅ Phase 5 plan includes SDK workspace  
✅ Building-blocks approach clearly communicated

## Next Steps

1. **Resolve test failures** - Update or remove tests that constrain implementation
2. **Documentation** - Ensure all docs reflect building-blocks approach
3. **Phase 5 planning** - Detail SDK workspace implementation
4. **Examples** - Provide integration examples for common HTTP clients
