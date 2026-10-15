# ADR-0005: Next.js App Router Architecture

## Status
Accepted

## Date
2024-12-30

## Context

The application was initially built with Next.js Pages Router. With Next.js 13+, the App Router offers:

- React Server Components (RSC)
- Nested layouts
- Improved data fetching patterns
- Streaming and Suspense
- Route groups and parallel routes

Decision needed: Migrate to App Router or stay with Pages Router?

## Decision

Migrate fully to Next.js App Router (`src/app/`) architecture.

### Directory Structure

```
src/app/
├── (auth)/                    # Route group for auth pages
│   ├── login/page.tsx
│   ├── signup/page.tsx
│   ├── forgot-password/page.tsx
│   └── reset-password/page.tsx
├── (dashboard)/               # Route group for authenticated pages
│   ├── layout.tsx             # Shared dashboard layout with sidebar
│   └── settings/
│       ├── page.tsx
│       ├── team/page.tsx
│       └── organization/page.tsx
├── api/                       # API routes (BFF)
│   ├── auth/
│   ├── cpr/
│   ├── documents/
│   └── ...
├── chat/
│   ├── page.tsx
│   └── [sessionId]/page.tsx
├── cpr/
│   ├── analise/page.tsx
│   ├── simulator/page.tsx
│   └── wizard/page.tsx
├── layout.tsx                 # Root layout
├── page.tsx                   # Landing page
└── globals.css
```

### Layout Composition

```typescript
// src/app/layout.tsx (Root)
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}

// src/app/(dashboard)/layout.tsx
export default function DashboardLayout({ children }) {
  return (
    <div className="flex">
      <Sidebar />
      <main>{children}</main>
    </div>
  )
}
```

### Client vs Server Components

```typescript
// Server Component (default) - runs on server
export default async function Page() {
  const data = await fetchData() // Direct data fetching
  return <ClientComponent data={data} />
}

// Client Component - marked with 'use client'
'use client'
export function ClientComponent({ data }) {
  const [state, setState] = useState()
  return <Interactive data={data} />
}
```

### Current Usage

Most pages are Client Components (`'use client'`) due to:
- Heavy interactivity (forms, wizards)
- Authentication context usage
- Real-time updates and polling

## Consequences

### Positive

1. **Nested Layouts**: Dashboard layout shared across settings pages
2. **Route Groups**: `(auth)` and `(dashboard)` organize without affecting URLs
3. **Colocation**: API routes, components, and pages in same directory
4. **Future-Proof**: Access to streaming, parallel routes when needed
5. **Loading States**: `loading.tsx` convention for Suspense fallbacks
6. **Error Boundaries**: `error.tsx` convention for error handling

### Negative

1. **Learning Curve**: RSC mental model differs from traditional React
2. **Client Component Friction**: Need `'use client'` directive for interactivity
3. **Hydration Issues**: Server/client mismatch can cause errors
4. **Bundle Complexity**: Need to understand what runs where

### Migration Notes

- All interactive pages marked `'use client'`
- API routes remain unchanged (Route Handlers)
- Layouts wrap content without re-mounting on navigation
- `useRouter` from `next/navigation` (not `next/router`)

## File Conventions

| File | Purpose |
|------|---------|
| `page.tsx` | Route UI |
| `layout.tsx` | Shared layout wrapper |
| `loading.tsx` | Loading UI (Suspense fallback) |
| `error.tsx` | Error UI (Error Boundary) |
| `not-found.tsx` | 404 UI |
| `route.ts` | API endpoint |

## References

- [Next.js App Router Documentation](https://nextjs.org/docs/app)
- [React Server Components](https://react.dev/blog/2023/03/22/react-labs-what-we-have-been-working-on-march-2023#react-server-components)
- `src/app/layout.tsx` - Root layout
- `src/app/(dashboard)/layout.tsx` - Dashboard layout
