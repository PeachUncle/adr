# ADR-025: HTTP Client Integration via Dependency Injection

## Status

**Proposed** - January 9, 2026  
**Extends:** [ADR-022: Building-Blocks Architecture](./ADR-022-building-blocks-no-http-client.md)

## Context

ADR-022 established that this library provides **building blocks**, not a complete HTTP client. However, consumer feedback indicates that while they appreciate the flexibility, they want **less friction** when integrating their chosen HTTP client.

### Current State (ADR-022)

```typescript
// Consumer must wire everything manually
import { endpoints, validateRequest, validateResponse } from '@engraph/castr';
import createClient from 'openapi-fetch';

const client = createClient<paths>({ baseUrl: 'https://api.example.com' });

// Manual: find endpoint, validate request, make call, validate response
const endpoint = endpoints.find((e) => e.operationId === 'getUser');
validateRequest(endpoint, { pathParams: { id: '123' } });
const { data } = await client.GET('/users/{id}', { params: { path: { id: '123' } } });
validateResponse(endpoint, 200, data);
```

### Desired State

```typescript
// Castr provides typed interface; consumer injects their client
import { createTypedClient } from '@engraph/castr';
import { fetchAdapter } from '@engraph/castr/adapters/fetch'; // or axios, ky, etc.

const api = createTypedClient({
  baseUrl: 'https://api.example.com',
  adapter: fetchAdapter, // DI: consumer provides their HTTP client
  schemas: generatedSchemas,
});

// Type-safe, validated API calls
const user = await api.request('getUser', { path: { id: '123' } });
// ^ Typed from OpenAPI, validated by Zod, using consumer's HTTP client
```

## Decision

**Extend ADR-022 with a Dependency Injection pattern for HTTP clients.**

Castr will provide:

1. **`CastrHttpAdapter` interface** - Contract that any HTTP client must implement
2. **`createTypedClient()` factory** - Creates type-safe client from adapter + schemas
3. **Optional adapter packages** - Pre-built adapters for common clients (fetch, axios, ky)

Castr will NOT provide:

- ❌ Default/bundled HTTP client (per ADR-022)
- ❌ Adapter dependencies in core package
- ❌ HTTP client-specific configuration

## Implementation

### Core Interface

```typescript
/**
 * Contract for HTTP adapters. Consumers implement this for their HTTP client.
 */
export interface CastrHttpAdapter {
  request<TResponse>(
    method: HttpMethod,
    url: string,
    options: AdapterRequestOptions,
  ): Promise<AdapterResponse<TResponse>>;
}

interface AdapterRequestOptions {
  headers?: Record<string, string>;
  body?: unknown;
  signal?: AbortSignal;
}

interface AdapterResponse<T> {
  status: number;
  data: T;
  headers: Headers;
}
```

### Factory Function

```typescript
/**
 * Create a type-safe API client with DI'd HTTP adapter.
 */
export function createTypedClient<TOperations>(config: {
  baseUrl: string;
  adapter: CastrHttpAdapter;
  schemas: GeneratedSchemas<TOperations>;
}): TypedApiClient<TOperations>;
```

### Adapter Packages (Optional)

Separate packages, not bundled in core:

| Package                                | Adapter       | Notes                    |
| -------------------------------------- | ------------- | ------------------------ |
| `@engraph/castr-adapter-fetch`         | Native fetch  | Zero dependencies        |
| `@engraph/castr-adapter-axios`         | Axios         | For interceptor users    |
| `@engraph/castr-adapter-ky`            | Ky            | Modern, lightweight      |
| `@engraph/castr-adapter-openapi-fetch` | openapi-fetch | Type-safe OpenAPI client |

## Rationale

### 1. Maintains ADR-022 Philosophy

- **No bundled HTTP client** - Consumer still chooses
- **Building blocks** - Interface is another building block
- **Composition** - Adapters are separate, optional packages

### 2. Reduces Friction

- **One factory call** instead of manual wiring
- **Type inference** flows through automatically
- **Validation built-in** (optional, configurable)

### 3. Testability (from RULES.md)

```typescript
// Easy to mock for testing
const mockAdapter: CastrHttpAdapter = {
  request: vi.fn().mockResolvedValue({ status: 200, data: mockUser }),
};

const api = createTypedClient({
  baseUrl: 'http://test',
  adapter: mockAdapter,
  schemas,
});
```

### 4. Ecosystem Evolution

- New HTTP clients can implement interface
- Community can contribute adapters
- No core package updates needed for new clients

## Consequences

### Positive

✅ **Keep ADR-022 benefits** - Consumer choice, no lock-in  
✅ **Reduce friction** - Easy integration path  
✅ **Type safety** - Full TypeScript inference  
✅ **Testable** - Easy to mock adapter  
✅ **Extensible** - New adapters without core changes  
✅ **Optional** - Building blocks still work without client

### Negative

⚠️ **API surface increase** - New interface and factory  
⚠️ **Adapter maintenance** - Pre-built adapters need updates

### Mitigation

- **API increase**: Well-documented, intuitive API
- **Adapter maintenance**: Community-driven, versioned independently

## Timeline

| Phase    | Work                                    | Target  |
| -------- | --------------------------------------- | ------- |
| Design   | Interface definition, factory signature | Phase 4 |
| Core     | `createTypedClient`, `CastrHttpAdapter` | Phase 5 |
| Adapters | fetch, axios adapters                   | Phase 5 |
| Docs     | Integration guide, examples             | Phase 5 |

## Related Decisions

- [ADR-022](./ADR-022-building-blocks-no-http-client.md) - Foundation: no bundled HTTP client
- [RULES.md](../../.agent/RULES.md) - Dependency Injection for Testability

## Success Criteria

- [ ] `CastrHttpAdapter` interface defined and exported
- [ ] `createTypedClient` factory implemented
- [ ] fetch adapter package published
- [ ] Integration guide with examples
- [ ] Unit tests with mocked adapter
