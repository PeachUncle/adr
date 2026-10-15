# ADR 0003: Routing and Layouts Strategy

## Status

Accepted

## Date

2026-01-12

## Context

We need to define the routing structure and layout composition strategy for the dashboard application. Key requirements:

1. **Separate layouts** - Auth pages and dashboard pages need different layouts
2. **Nested layouts** - Settings should be nested within dashboard
3. **URL structure** - Clean, semantic URLs
4. **Route protection** - Dashboard routes require authentication
5. **Code organization** - Clear file structure

### Options Considered

#### Option A: Flat Route Structure

```
app/
├── auth/
│   └── login/page.tsx
├── dashboard/page.tsx
├── settings/page.tsx
```

**Pros:** Simple
**Cons:** Layout duplication, no grouping

#### Option B: Route Groups (Selected)

```
app/
├── (auth)/auth/...
├── (dashboard)/dashboard/...
```

**Pros:** Layout isolation, logical grouping
**Cons:** Slightly more complex folder structure

#### Option C: Parallel Routes

Using slots like `@auth` and `@dashboard`

**Pros:** Advanced composition
**Cons:** Overkill for this use case

## Decision

We choose **Route Groups** with nested layouts.

## Rationale

1. **Layout Isolation**: Route groups `(auth)` and `(dashboard)` allow completely different layouts without URL impact.

2. **Clean URLs**: 
   - `/auth/login` not `/(auth)/auth/login`
   - `/dashboard` not `/(dashboard)/dashboard`

3. **Nested Layouts**: Settings lives under dashboard layout, inheriting the shell.

4. **Protection Strategy**: Layout-based auth check is cleaner than page-level.

5. **Future Proof**: Easy to add more route groups (marketing, onboarding, etc.)

## Implementation

### Folder Structure

```
app/
├── layout.tsx                      # Root: providers, global styles
├── page.tsx                        # "/" - redirect based on auth
│
├── (auth)/                         # Route group (no URL impact)
│   └── auth/
│       ├── layout.tsx              # Auth layout: centered, card
│       ├── login/
│       │   └── page.tsx
│       ├── forgot-password/
│       │   └── page.tsx
│       └── register/
│           └── page.tsx
│
├── (dashboard)/                    # Route group
│   └── dashboard/
│       ├── layout.tsx              # Dashboard layout: AppShell
│       ├── page.tsx                # /dashboard - home
│       ├── users/
│       │   └── page.tsx            # /dashboard/users
│       └── settings/
│           ├── layout.tsx          # Settings sub-layout: tabs
│           ├── page.tsx            # Redirect to /profile
│           ├── profile/
│           │   └── page.tsx
│           ├── account/
│           │   └── page.tsx
│           └── appearance/
│               └── page.tsx
│
└── api/                            # API routes
    ├── auth/
    │   ├── login/route.ts
    │   ├── logout/route.ts
    │   └── me/route.ts
    └── users/
        └── route.ts
```

### Layout Composition

```
Root Layout (providers, fonts)
│
├── Auth Layout (centered card)
│   ├── Login Page
│   ├── Forgot Password Page
│   └── Register Page
│
└── Dashboard Layout (AppShell: sidebar + topbar)
    ├── Dashboard Home
    ├── Users Page
    └── Settings Layout (tabs navigation)
        ├── Profile Page
        ├── Account Page
        └── Appearance Page
```

### Root Layout

```tsx
// app/layout.tsx
import { ThemeProvider } from '@/components/providers/theme-provider';
import './globals.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### Auth Layout

```tsx
// app/(auth)/auth/layout.tsx
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/40">
      <div className="w-full max-w-md p-6">
        {children}
      </div>
    </div>
  );
}
```

### Dashboard Layout (with Auth Protection)

```tsx
// app/(dashboard)/dashboard/layout.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth/auth.store';
import { AppShell } from '@/components/layout/app-shell';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return <div>Loading...</div>; // Or skeleton
  }

  if (!isAuthenticated) {
    return null; // Will redirect
  }

  return <AppShell>{children}</AppShell>;
}
```

### Settings Layout

```tsx
// app/(dashboard)/dashboard/settings/layout.tsx
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Link from 'next/link';

const settingsTabs = [
  { value: 'profile', label: 'Profile', href: '/dashboard/settings/profile' },
  { value: 'account', label: 'Account', href: '/dashboard/settings/account' },
  { value: 'appearance', label: 'Appearance', href: '/dashboard/settings/appearance' },
];

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Manage your account settings.</p>
      </div>
      
      <nav className="flex gap-4 border-b">
        {settingsTabs.map((tab) => (
          <Link
            key={tab.value}
            href={tab.href}
            className="pb-2 text-sm font-medium hover:text-primary"
          >
            {tab.label}
          </Link>
        ))}
      </nav>
      
      <div>{children}</div>
    </div>
  );
}
```

### Root Page (Redirect Logic)

```tsx
// app/page.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth/auth.store';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.replace('/dashboard');
      } else {
        router.replace('/auth/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
    </div>
  );
}
```

## Route Protection Strategy

### Current: Layout-Based (Client-Side)

- Dashboard layout checks `isAuthenticated`
- Redirects to login if not authenticated
- Simple, works for most cases

### Production Enhancement: Proxy

For better security, add Next.js proxy (formerly middleware in Next.js 15 and earlier):

```typescript
// proxy.ts (Next.js 16+)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const isAuthPage = request.nextUrl.pathname.startsWith('/auth');
  const isDashboard = request.nextUrl.pathname.startsWith('/dashboard');

  if (isDashboard && !token) {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }

  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/auth/:path*'],
};
```

**Note:** Middleware requires httpOnly cookie storage (not localStorage).

## URL Structure

| URL | Page | Layout Chain |
|-----|------|--------------|
| `/` | Redirect | Root |
| `/auth/login` | Login | Root → Auth |
| `/auth/forgot-password` | Forgot Password | Root → Auth |
| `/auth/register` | Register | Root → Auth |
| `/dashboard` | Dashboard Home | Root → Dashboard |
| `/dashboard/users` | Users Table | Root → Dashboard |
| `/dashboard/settings` | Redirect | Root → Dashboard → Settings |
| `/dashboard/settings/profile` | Profile Form | Root → Dashboard → Settings |
| `/dashboard/settings/account` | Account Form | Root → Dashboard → Settings |
| `/dashboard/settings/appearance` | Theme Toggle | Root → Dashboard → Settings |

## Consequences

### Positive

- Clean separation of auth and dashboard
- Reusable layouts
- Clear URL structure
- Easy to add new sections
- Settings properly nested under dashboard

### Negative

- Deep nesting can be confusing initially
- Route group naming requires convention
- Client-side protection has flash potential

### Mitigations

- Document folder structure clearly
- Use consistent naming (`(groupName)`)
- Add loading states to prevent flash
- Document middleware upgrade path

## References

- [Next.js Route Groups](https://nextjs.org/docs/app/building-your-application/routing/route-groups)
- [Next.js Layouts](https://nextjs.org/docs/app/building-your-application/routing/layouts-and-templates)
- [Next.js Middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware)
