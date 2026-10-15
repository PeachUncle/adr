# ADR-0001: Use Parallel Routes for Dynamic Header

## Status

Accepted

## Context

The application requires a header component that displays dynamic, route-specific content (project title). The header must:

- Fetch data from the database based on the current route
- Update automatically when the project data changes (via auto-save)
- Scale to support multiple route types without duplicating code

Two architectural approaches were considered:

1. **Traditional Shared Layout** - Import Header component in each page
2. **Next.js Parallel Routes** - Use `@header` slot in root layout

## Decision

We will use **Parallel Routes** (`@header` slot) to manage the header component.

## Consequences

### Positive

- **Single Definition**: Header logic defined once in `app/layout.tsx`, automatically applies to all routes
- **Scalability**: New pages inherit the header automatically without code changes
- **Route-Specific Logic**: Each route can provide its own header implementation in `@header/[route]/page.tsx`
- **Server Component Benefits**: Header fetches data server-side, maintaining SSR performance
- **Automatic Revalidation**: `revalidatePath()` in Server Actions updates the header slot without manual cache invalidation

### Negative

- **Learning Curve**: Parallel Routes are a Next.js 13+ feature requiring team familiarity
- **Folder Complexity**: Requires `@header/` directory and `default.tsx` fallback files
- **Debugging**: Slot-based routing can be less intuitive than component imports

### Alternatives Considered

- **Shared Layout Component**: Would require importing `<Header />` in every page file, creating maintenance overhead as the app scales
- **Context Provider**: Would force Header to be a Client Component, losing SSR benefits and complicating data fetching
- **Nested Layouts**: Would require prop drilling through multiple layout levels for route params

## References

- [Next.js Parallel Routes Documentation](https://nextjs.org/docs/app/building-your-application/routing/parallel-routes)
- Related: ADR-0002 (Auto-save implementation with revalidation strategy)
