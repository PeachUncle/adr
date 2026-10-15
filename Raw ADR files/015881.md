# ADR-002: Routing Solution

## Status

Accepted

## Context

Rule Bound is a web application that will serve RPG rules content across multiple pages/views. Users need to:

- Navigate between different rule sections
- Deep link to specific rules
- Use browser back/forward buttons
- Have accessible navigation with proper focus management
- Experience smooth transitions on mobile devices

We need a routing solution that supports:

- Client-side routing (SPA experience)
- TypeScript support
- Accessibility features (focus management, announcements)
- Code splitting for performance
- Mobile-friendly navigation patterns

## Options Considered

### 1. React Router v6

- **Pros:**
  - Industry standard for React routing
  - Strong TypeScript support
  - Built-in accessibility features (focus management)
  - Excellent documentation
  - Active maintenance
  - Supports code splitting
  - Declarative routing API
  - Nested routes support
  - Data loading patterns
- **Cons:**
  - Slightly larger bundle size (but tree-shakeable)
  - API changes between major versions

### 2. TanStack Router

- **Pros:**
  - Excellent TypeScript support (type-safe routes)
  - Modern, innovative features
  - Built-in data loading
  - Powerful type inference
- **Cons:**
  - Newer, smaller community
  - Less battle-tested
  - More complex for simple use cases
  - Steeper learning curve

### 3. Wouter

- **Pros:**
  - Very lightweight (~1.5KB)
  - Simple API
  - Hooks-based
- **Cons:**
  - Limited features compared to React Router
  - Smaller ecosystem
  - Less comprehensive accessibility features
  - May need additional solutions for complex routing

### 4. Next.js (Framework)

- **Pros:**
  - File-based routing
  - SSR/SSG capabilities
  - Great developer experience
- **Cons:**
  - Full framework (overkill for our needs)
  - Server-side complexity not needed for rules reference app
  - Less flexibility for client-only app
  - Heavier deployment requirements

## Decision

We will use **React Router v6** as the routing solution.

**Key reasons:**

1. **Accessibility**: Built-in focus management and screen reader announcements
2. **Battle-Tested**: Proven in production across thousands of apps
3. **TypeScript Support**: Good type definitions and type safety
4. **Documentation**: Comprehensive docs and large community
5. **Features**: All needed features (code splitting, nested routes, navigation)
6. **Mobile-Friendly**: Works excellently on mobile browsers
7. **Future-Proof**: Active development and long-term support

## Consequences

### Positive

- Standardized routing patterns familiar to React developers
- Built-in accessibility features reduce custom implementation
- Code splitting at route level for better performance
- Excellent error boundaries integration
- Strong community support for troubleshooting

### Negative

- Bundle size slightly larger than minimal alternatives (~10KB gzipped)
- Need to learn React Router API (though it's well-documented)

### Neutral

- Will use declarative `<Routes>` and `<Route>` components
- Route definitions will be centralized for maintainability
- Focus management handled automatically by library

### Implementation Notes

- Use lazy loading with `React.lazy()` for route-based code splitting
- Implement proper loading states during route transitions
- Ensure all navigation elements have proper ARIA labels
- Use `useNavigate` hook for programmatic navigation
- Implement scroll restoration for better UX
