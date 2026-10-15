# ADR-002: Lit as Frontend Framework

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template needs a frontend framework for building the user interface. Requirements include:

1. **OAuth Integration**: Must support Authorization Code flow with PKCE for secure authentication with Keycloak
2. **Type Safety**: TypeScript support for maintainable, self-documenting code
3. **Modern Tooling**: Vite compatibility for fast development and optimized production builds
4. **Component Model**: Reusable, encapsulated UI components
5. **Bundle Size**: Minimal footprint for fast initial load times
6. **Long-Term Maintainability**: Avoid framework churn and migration burden
7. **Observability**: Support for OpenTelemetry instrumentation

The frontend must communicate with the FastAPI backend, handle authentication flows, and provide a responsive user experience.

## Decision

We chose **Lit** (version 3.x) as the frontend framework.

Lit is Google's library for building Web Components - custom HTML elements that work natively in the browser. Key implementation details:

**Package Configuration** (`frontend/package.json`):
```json
{
  "dependencies": {
    "lit": "^3.1.0",
    "oidc-client-ts": "^3.0.1"
  },
  "devDependencies": {
    "vite": "^5.0.10",
    "typescript": "^5.3.3",
    "tailwindcss": "^3.4.0",
    "@playwright/test": "^1.56.1",
    "vitest": "^4.0.8"
  }
}
```

**Component Structure** (`frontend/src/components/`):
```typescript
import { LitElement, html, css } from 'lit'
import { customElement, state } from 'lit/decorators.js'

@customElement('health-check')
export class HealthCheck extends LitElement {
  static styles = css`...`

  @state()
  private healthData: HealthResponse | null = null

  render() {
    return html`<div class="container">...</div>`
  }
}
```

**OIDC Authentication** (`frontend/src/auth/`):
- `config.ts`: OIDC configuration for Keycloak integration
- `service.ts`: `AuthService` class using `oidc-client-ts` with PKCE
- `store.ts`: Reactive auth state management

**API Client** (`frontend/src/api/client.ts`):
- Type-safe HTTP client with automatic token injection
- Error handling with typed `ApiError` responses

## Consequences

### Positive

1. **Web Standards Alignment**: Lit builds standard Web Components that work in any browser without framework-specific runtime. Components are `<custom-element>` tags that can be used in vanilla HTML

2. **Minimal Bundle Size**: Lit core is ~5KB minified+gzipped. The entire framework adds minimal overhead compared to React (~40KB) or Angular (~100KB+)

3. **No Virtual DOM Overhead**: Lit uses efficient tagged template literals (`html\`...\``) with surgical DOM updates. Changes only affect the specific parts of the DOM that changed

4. **TypeScript Native**: First-class TypeScript support with decorators (`@customElement`, `@state`, `@property`) for clean component definitions

5. **Scoped Styles**: Shadow DOM encapsulation prevents style leakage between components. Each component's CSS is isolated by default

6. **Future-Proof**: Web Components are a browser standard. If Lit development stopped, components would continue working. Migration to another framework (or none) is straightforward

7. **Simple Mental Model**: No complex state management patterns required. `@state()` for internal state, `@property()` for external props, and reactive updates happen automatically

8. **Vite Integration**: Excellent development experience with Vite - fast HMR, optimized builds, and native ES module support

### Negative

1. **Smaller Ecosystem**: Fewer pre-built component libraries compared to React or Vue. More custom component development may be required

2. **Less Familiar**: Developers experienced with React/Vue may need adjustment time. Web Components concepts (Shadow DOM, slots, lifecycle) differ from virtual DOM frameworks

3. **Limited Server-Side Rendering**: SSR support exists but is less mature than Next.js or Nuxt. For this SPA application, this is not a concern

4. **Form Handling**: No built-in form libraries like Formik or React Hook Form. Form state management requires custom implementation or lighter libraries

5. **State Management**: No Redux/Vuex equivalent. For complex applications, state management patterns must be designed (though the simple reactive state is often sufficient)

### Neutral

1. **Google Backed**: Lit is developed by Google (evolved from Polymer). Provides confidence in long-term maintenance but introduces vendor considerations

2. **Shadow DOM Learning**: Developers need to understand Shadow DOM for styling and slotting. This is standard browser knowledge but often new to developers

3. **Testing Approach**: Uses `@open-wc/testing` and Vitest. Testing patterns differ slightly from React Testing Library

## Alternatives Considered

### React

**Why Not Chosen**:
- Larger bundle size (~40KB for React + ReactDOM)
- Virtual DOM overhead for applications that don't benefit from it
- Frequent ecosystem churn (class components to hooks, Redux to Context to Zustand, etc.)
- Framework lock-in: React components only work in React applications
- More complex mental model (hooks rules, closure issues, memo/callback optimization)

### Vue 3

**Why Not Chosen**:
- Similar concerns to React regarding framework lock-in
- Larger bundle than Lit
- Two-way binding patterns can lead to harder-to-debug state issues
- Template syntax requires learning Vue-specific directives

### Svelte

**Why Not Chosen**:
- Compile-time framework generates vanilla JavaScript (similar philosophy to Lit)
- Smaller community than React/Vue
- Different reactive model that requires Svelte-specific knowledge
- Less mature TypeScript support compared to Lit

### Angular

**Why Not Chosen**:
- Significantly larger bundle size and complexity
- Opinionated full framework when we only need UI components
- Steeper learning curve
- Overkill for this application's scope

### Vanilla JavaScript / No Framework

**Why Not Chosen**:
- Would require reimplementing reactive updates, component lifecycle, and templating
- Lit provides exactly these features with minimal overhead
- More boilerplate code for the same functionality

---

## Related ADRs

- [ADR-001: FastAPI as Backend Framework](./001-fastapi-backend-framework.md) - Backend API that frontend consumes
- [ADR-004: Keycloak as Identity Provider](./004-keycloak-identity-provider.md) - OAuth provider frontend authenticates with
- [ADR-013: PKCE Enforcement for Public Clients](./013-pkce-enforcement-public-clients.md) - Security pattern frontend implements

## Implementation References

- `frontend/src/components/` - Lit component implementations
- `frontend/src/auth/service.ts` - OIDC authentication service
- `frontend/src/api/client.ts` - Type-safe API client
- `frontend/package.json` - Dependencies and build scripts
- `frontend/vite.config.ts` - Vite build configuration
