# ADR-025: Client-Side Routing

## Status

Accepted

## Context

The application requires client-side routing to manage navigation between
different views and URL paths. Key requirements include dynamic route matching,
nested routing support, route guards, and seamless integration with React and
its component model. The solution should be flexible enough to support modern
SPA and MPA patterns, work well with lazy loading, and align with React's
declarative paradigm.

Several routing libraries were evaluated, including React Router, Next.js App
Router, Wouter, and Reach Router.

## Decision

We decided to use **React Router** (`react-router-dom`) as the client-side
routing solution for the project.

## Reasons

1. **Mature and Stable**:
   - React Router is the most widely used routing library in the React
     ecosystem, with a proven track record and active maintenance.

2. **Nested Routing Support**:
   - Built-in support for nested layouts and nested route components aligns with
     modern app structures and promotes modular routing definitions.

3. **Declarative and Component-Driven**:
   - Routes are defined using JSX, allowing routes and components to be
     co-located and configured declaratively.

4. **Dynamic Routing and Params**:
   - Supports route parameters, wildcard segments, optional params, and dynamic
     segments, which are essential for building flexible navigation systems.

5. **Data Loading and Loader APIs**:
   - The `react-router-dom` v6.4+ loader and action APIs allow for co-located
     data fetching and mutation logic, reducing boilerplate.

6. **Code Splitting and Lazy Loading**:
   - Works well with `React.lazy` and `Suspense` for route-based code splitting
     and performance optimization.

7. **Community and Ecosystem**:
   - A large community, extensive documentation, and third-party integrations
     (e.g. for auth, breadcrumbs, transitions) make React Router reliable for
     long-term use.

## Consequences

1. **Initial Setup Complexity**:
   - Proper configuration of layouts, nested routes, and loaders may take time
     to understand and set up.

2. **Opinionated Patterns**:
   - Adopting React Router's newer APIs (e.g., loaders, actions) may require
     adjustments in state management and data-fetching strategies.

3. **Non-trivial Migration from Other Solutions**:
   - Migrating from another framework like Next.js App Router or custom routing
     setup may require a structural overhaul.

## Alternatives Considered

### Wouter:

- **Pros**: Minimalistic, tiny bundle size.
- **Cons**: Limited features, no nested routes or data loading built-in.

### Next.js App Router:

- **Pros**: File-based routing, powerful conventions, SSR-ready.
- **Cons**: Tightly coupled with Next.js; not usable in custom Vite/React
  setups.

### Reach Router:

- **Pros**: Simple, accessibility-focused.
- **Cons**: Deprecated in favor of React Router after merging with its core
  team.
