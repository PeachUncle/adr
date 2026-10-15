---
doc_id: "ADR-005"
tech_stack: ["react", "typescript"]
title: "ADR-005: React Router v6 Routing Strategy"
version: "1.0.0"
last_updated: "2025-12-19"
status: "accepted"
category: "Architecture Decision"
audience: ["Developers", "Architects"]
prerequisites: ["ADR-001-React-TypeScript-Stack.md"]
related_docs: ["Architecture/Frontend-Architecture.md", "Specifications/Frontend-Specification.md"]
maintainer: "Development Team"
---

# <ADR-005-React Router v6 Routing Strategy>

## Status

**Accepted** - React Router v6 is the routing solution with code splitting and lazy loading.

## Context

The MyTechPortfolio application requires a routing solution that:
- Supports client-side routing (SPA)
- Enables code splitting for performance
- Supports nested routes
- Handles protected routes (admin authentication)
- Provides good developer experience
- Integrates with React and TypeScript
- Supports route-based code splitting

### Alternatives Considered

1. **React Router v5**
   - Pros: Mature, stable, widely used
   - Cons: Older API, less intuitive, no data APIs

2. **Next.js Router**
   - Pros: File-based routing, SSR/SSG, excellent DX
   - Cons: Full framework, overkill for SPA, requires Next.js

3. **Reach Router**
   - Pros: Accessible, simple API
   - Cons: Merged into React Router v6, no longer maintained

4. **Wouter**
   - Pros: Lightweight, hooks-based
   - Cons: Smaller ecosystem, less features

5. **React Router v6**
   - Pros: Modern API, nested routes, data APIs, code splitting support
   - Cons: Breaking changes from v5, learning curve

6. **No Router (Single Page)**
   - Pros: Simplest approach
   - Cons: No navigation, poor UX, no SEO benefits

## Decision

We chose **React Router v6 ^6.23.1** with route-based code splitting.

### Rationale

1. **Modern API**
   - Hooks-based API (`useNavigate`, `useParams`, etc.)
   - More intuitive than v5
   - Better TypeScript support
   - Improved developer experience

2. **Nested Routes**
   - Native support for nested routing
   - Perfect for admin panel structure
   - Layout components with `<Outlet />`
   - Clean route organization

3. **Code Splitting**
   - Built-in support with `React.lazy()`
   - Route-based code splitting
   - Improved initial load time
   - Better performance

4. **Protected Routes**
   - Easy to implement route guards
   - Admin authentication support
   - Role-based access control
   - Custom route components

5. **TypeScript Support**
   - Excellent TypeScript integration
   - Type-safe route parameters
   - Type-safe navigation
   - Better IDE support

6. **Ecosystem**
   - Most popular React routing solution
   - Extensive documentation
   - Large community
   - Active maintenance

7. **Performance**
   - Lazy loading support
   - Code splitting
   - Optimized re-renders
   - Small bundle size

## Consequences

### Positive

- **Code Splitting**: Route-based code splitting improves performance
- **Nested Routes**: Clean organization for admin panel and complex layouts
- **Type Safety**: Full TypeScript support
- **Developer Experience**: Modern, intuitive API
- **Performance**: Lazy loading reduces initial bundle size
- **Flexibility**: Supports various routing patterns

### Negative

- **Learning Curve**: v6 has breaking changes from v5
- **Migration**: If upgrading from v5, requires refactoring
- **Bundle Size**: Adds ~10KB (gzipped) to bundle
- **Complexity**: Nested routes can become complex

### Neutral

- **SSR**: Client-side only (no SSR support, but not needed for portfolio)
- **SEO**: Client-side routing (mitigated by proper meta tags)

## Implementation Details

### Route Structure

```typescript
// App.tsx
<Routes>
  {/* Public Routes */}
  <Route path="/" element={<HomePage />} />
  <Route path="/projects" element={<ProjectsPage />} />
  <Route path="/projects/:id" element={<ProjectDetailPage />} />
  
  {/* Admin Routes (Protected) */}
  <Route path="/admin" element={
    <AdminRoute>
      <AdminLayout />
    </AdminRoute>
  }>
    <Route index element={<AdminDashboard />} />
    <Route path="projects" element={<ProjectsAdminPage />} />
    <Route path="projects/new" element={<ProjectForm mode="create" />} />
    <Route path="projects/:id/edit" element={<ProjectForm mode="edit" />} />
  </Route>
</Routes>
```

### Code Splitting Pattern

```typescript
// Lazy load components
const HomePage = lazy(() => 
  import('@pages/HomePage').then(module => ({ default: module.HomePage }))
)

const ProjectsPage = lazy(() => import('@pages/ProjectsPage'))

// Use Suspense for loading states
<Suspense fallback={<LoadingSpinner />}>
  <Routes>
    <Route path="/" element={<HomePage />} />
  </Routes>
</Suspense>
```

### Protected Routes

```typescript
// AdminRoute.tsx
function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAdminStore()
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}
```

### Navigation

```typescript
// Using hooks
import { useNavigate, useParams } from 'react-router-dom'

function MyComponent() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  
  const handleClick = () => {
    navigate('/projects/123')
  }
}
```

### Current Route Structure

```
/                           # HomePage
/projects                   # ProjectsPage
/projects/:id               # ProjectDetailPage
/academics                  # AcademicsPage
/about                      # AboutPage
/feedback                   # FeedbackPage
/login                      # LoginPage
/admin                      # AdminLayout
  ├── /                     # AdminDashboard
  ├── /projects             # ProjectsAdminPage
  ├── /projects/new         # ProjectForm (create)
  ├── /projects/:id/edit    # ProjectForm (edit)
  ├── /academics            # AcademicsAdminPage
  └── /milestones           # JourneyMilestonesAdminPage
```

## Best Practices

1. **Code Splitting**: Lazy load all route components
2. **Nested Routes**: Use for layouts (admin, public)
3. **Protected Routes**: Implement route guards for authentication
4. **Type Safety**: Use TypeScript for route parameters
5. **Loading States**: Provide Suspense fallbacks
6. **Error Handling**: Implement error boundaries for routes

## Migration Considerations

If migrating from React Router v5:
- Update route syntax (`component` → `element`)
- Update navigation (`history.push` → `navigate`)
- Update hooks (`useHistory` → `useNavigate`)
- Update route parameters handling

## Related Decisions

- [ADR-001: React + TypeScript Stack](./ADR-001-React-TypeScript-Stack.md)
- [ADR-002: Zustand State Management](./ADR-002-Zustand-State-Management.md)
- [Frontend Architecture](../Architecture/Frontend-Architecture.md)

## References

- [React Router v6 Documentation](https://reactrouter.com/)
- [React Router GitHub](https://github.com/remix-run/react-router)
- [Frontend Architecture](../Architecture/Frontend-Architecture.md)

---

**Decision Date**: 2025-11-17  
**Decided By**: Development Team  
**Review Date**: TBD (review if routing needs become significantly more complex)

