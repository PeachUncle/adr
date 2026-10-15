# ADR-004: Next.js with App Router for Frontend

## Status
**Accepted**

## Date
2025-01-XX

## Context

MyUglyRocks needs a frontend framework that:
- Provides excellent developer experience
- Supports SEO for public pages (gallery, specimens, materials)
- Handles authenticated user experiences smoothly
- Integrates well with our ASP.NET Core backend
- Deploys easily with good performance

### Requirements
1. **SEO**: Public gallery and reference pages need to be indexable
2. **Performance**: Fast initial load, especially for image-heavy pages
3. **TypeScript**: First-class TypeScript support
4. **Component Library**: Compatible with modern UI libraries (shadcn/ui)
5. **Deployment**: Easy deployment with preview environments
6. **Developer Experience**: Hot reload, good error messages, modern tooling

### Options Considered

#### Option A: Next.js (App Router)
- React-based with server components
- Built-in SSR/SSG/ISR
- File-based routing
- Railway deployment (Vercel as backup)

#### Option B: Next.js (Pages Router)
- Mature, stable
- Well-documented
- Being superseded by App Router

#### Option C: Remix
- Server-first React framework
- Excellent data loading patterns
- Smaller ecosystem than Next.js

#### Option D: Vite + React (SPA)
- Simple, fast development
- No built-in SSR
- Would need separate SSR solution for SEO

#### Option E: Blazor WebAssembly
- .NET everywhere
- Larger bundle size
- Smaller ecosystem for UI components

#### Option F: Angular
- Enterprise-grade
- Steeper learning curve
- Less ecosystem momentum

## Decision

**Use Next.js 14+ with App Router for the frontend.**

### Rationale

1. **React Server Components (RSC)**: Reduce JavaScript sent to client for read-heavy pages. Gallery browsing, specimen lookup, and public profiles can be server-rendered with minimal JS.

2. **Hybrid Rendering**:
   - Static generation for reference pages (specimens, materials)
   - Server-side rendering for gallery (fresh content)
   - Client-side for interactive features (cycle management)

3. **Railway Deployment**:
   - Single platform for frontend + backend + database
   - Simplified infrastructure management
   - Preview environments available
   - Vercel available as backup if needed

4. **shadcn/ui Compatibility**: The most popular component library for Next.js, giving us beautiful, accessible components.

5. **Industry Standard**: Next.js is the most popular React framework, ensuring:
   - Easy to find developers
   - Extensive documentation and tutorials
   - Active community support

6. **App Router Benefits**:
   - Nested layouts (perfect for settings sidebar, dashboard)
   - Loading and error states per route segment
   - Parallel routes for complex UIs
   - Server Actions (future optimization)

### Rendering Strategy by Page

| Page | Rendering | Rationale |
|------|-----------|-----------|
| Landing `/` | Static (SSG) | Marketing content, rarely changes |
| Gallery `/gallery` | Server (SSR) | Fresh content, SEO important |
| Post Detail `/gallery/:id` | Server (SSR) | SEO, dynamic content |
| Specimens `/specimens` | Static (ISR) | Reference data, update daily |
| Materials `/materials` | Static (ISR) | Reference data, update daily |
| Dashboard `/dashboard` | Client (CSR) | Private, interactive |
| Cycles `/cycles` | Client (CSR) | Private, heavy interaction |
| Settings `/settings` | Client (CSR) | Private, forms |
| Auth pages | Server (SSR) | Simple forms, SEO not needed |

### Project Structure

```
src/
├── app/                          # App Router
│   ├── (auth)/                   # Auth pages (login, register)
│   ├── (public)/                 # Public pages (landing, gallery)
│   ├── (protected)/              # Auth-required pages
│   │   ├── layout.tsx            # Auth check wrapper
│   │   ├── dashboard/
│   │   ├── cycles/
│   │   └── settings/
│   └── api/                      # API routes (if needed)
│
├── components/
│   ├── ui/                       # shadcn/ui components
│   └── shared/                   # Domain components
│
├── lib/
│   ├── api/                      # API client
│   └── hooks/                    # Custom hooks
│
└── providers/                    # Context providers
```

### API Integration Pattern

The frontend calls the ASP.NET backend directly (not through Next.js API routes):

```typescript
// lib/api/client.ts
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,  // Include cookies
});

// lib/api/cycles.ts
export async function getCycles(params: CycleFilters) {
  const response = await apiClient.get('/cycles', { params });
  return response.data;
}
```

For server components, we fetch directly:

```typescript
// app/(protected)/cycles/page.tsx
async function CyclesPage() {
  const cookies = cookies();
  const res = await fetch(`${API_URL}/cycles`, {
    headers: { Cookie: cookies.toString() },
    next: { revalidate: 0 }  // Always fresh
  });
  const data = await res.json();
  return <CyclesList cycles={data} />;
}
```

## Consequences

### Positive

- **SEO for Public Pages**: Server rendering ensures search engines can index gallery and reference content
- **Performance**: Server components reduce JavaScript bundle, improving load times
- **Developer Velocity**: File-based routing, TypeScript, and hot reload accelerate development
- **Single Platform**: Frontend, backend, and database all on Railway
- **Ecosystem**: Large library of compatible packages and examples
- **Future-Proof**: App Router is Next.js's future direction

### Negative

- **Learning Curve**: App Router and Server Components are relatively new patterns
- **Complexity**: More rendering strategies to reason about (SSR vs SSG vs CSR)
- **Not Vercel-optimized**: Some Next.js features work best on Vercel (can switch if needed)
- **Two Runtimes**: Need to understand Node.js vs Edge vs Client boundaries

### App Router Specific Considerations

| Feature | Usage in MyUglyRocks |
|---------|----------------------|
| `layout.tsx` | Auth checks, navigation, sidebars |
| `loading.tsx` | Skeleton screens per route |
| `error.tsx` | Error boundaries per route |
| `page.tsx` | Route content |
| Route groups `(name)` | Organize auth/public/protected |
| `use client` | Interactive components only |

### Authentication Flow with App Router

```typescript
// app/(protected)/layout.tsx
import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';

export default async function ProtectedLayout({
  children
}: {
  children: React.ReactNode
}) {
  const cookieStore = cookies();
  const accessToken = cookieStore.get('access_token');

  if (!accessToken) {
    redirect('/login');
  }

  // Validate token with backend
  const user = await validateToken(accessToken.value);

  if (!user) {
    redirect('/login');
  }

  return (
    <AuthProvider user={user}>
      <AppShell>{children}</AppShell>
    </AuthProvider>
  );
}
```

## Alternatives Rejected

### Next.js Pages Router
Rejected because App Router is the future of Next.js. While Pages Router is stable and well-documented, investing in App Router now means:
- Better long-term support
- Access to Server Components
- Modern patterns that will become standard

### Remix
Rejected despite excellent data loading patterns because:
- Smaller ecosystem and community
- Less compatible with shadcn/ui patterns
- Less mature than Next.js

### Vite + React SPA
Rejected because SEO is important for the gallery and reference pages. Building our own SSR solution would add significant complexity.

### Blazor
Rejected because:
- Larger initial bundle (WebAssembly)
- Smaller component library ecosystem
- Less hiring pool for frontend developers

## Implementation Notes

### Key Libraries

| Library | Purpose |
|---------|---------|
| `next` | Framework |
| `react-query` | Server state management |
| `react-hook-form` | Form handling |
| `zod` | Validation |
| `tailwindcss` | Styling |
| `shadcn/ui` | Component library |
| `lucide-react` | Icons |
| `date-fns` | Date handling |

### Environment Variables

```env
# .env.local (for K8s deployment)
# Empty = use relative URLs through ingress (recommended)
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_MEDIA_URL=https://media.myuglyrocks.com
```

## Related Decisions
- [ADR-002-auth-strategy.md](./ADR-002-auth-strategy.md) - Cookie-based auth works with SSR
- [ADR-003-image-storage.md](./ADR-003-image-storage.md) - R2 images displayed via Next.js Image
- [ADR-005-hosting-strategy.md](./ADR-005-hosting-strategy.md) - Railway as primary platform

## References
- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [React Server Components](https://react.dev/reference/rsc/server-components)
- [Railway Next.js Deployment](https://docs.railway.app/guides/nextjs)
- [shadcn/ui](https://ui.shadcn.com/)
