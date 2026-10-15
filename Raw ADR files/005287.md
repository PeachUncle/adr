# ADR-003: Use tRPC for Type-Safe API

## Status

✅ **Accepted**

**Date:** 27. Oktober 2025

## Context

Die AI-Freelancer-Plattform braucht eine API für:

- Frontend ↔ Backend Kommunikation
- CRUD Operations (Users, Projects, Bookings)
- Complex Workflows (Trial Period, Matching, Payments)
- Real-time Features (Messaging, später)

**Requirements:**

- Type Safety (Frontend ↔ Backend)
- Gute DX (Developer Experience)
- Easy to maintain (Solo-Developer)
- Performance (Low Latency)
- Security (Authentication, Authorization)

**Constraint:**

- Full-Stack TypeScript (Next.js Frontend + Backend)
- Nicht-öffentliche API (nur für eigene Frontend)

## Decision

Ich verwende **tRPC (TypeScript Remote Procedure Call)** für die API.

### Was ist tRPC?

tRPC ermöglicht **end-to-end type-safe APIs** ohne Code-Generation:

- Backend definiert Procedures (Queries + Mutations)
- Frontend importiert Backend-Types automatisch
- Auto-Completion, Type-Checking im Frontend
- Kein REST-Boilerplate (Endpoints, HTTP-Methoden, Validierung dupliziert)

## Rationale

### Warum tRPC?

**1. End-to-End Type Safety**

```typescript
// Backend: src/server/routers/projects.ts
export const projectsRouter = router({
  create: protectedProcedure
    .input(
      z.object({
        name: z.string(),
        skills: z.array(z.string()),
        budgetRange: z.enum(['LESS_10K', 'RANGE_10_20K' /* ... */]),
      })
    )
    .mutation(async ({ input, ctx }) => {
      return await ctx.prisma.project.create({ data: input });
    }),
});

// Frontend: src/components/CreateProjectForm.tsx
const mutation = trpc.projects.create.useMutation();

// ✅ TypeScript weiß exakt, was `input` braucht:
mutation.mutate({
  name: 'AI Chatbot',
  skills: ['langchain', 'python'],
  budgetRange: 'RANGE_10_20K', // Auto-Completion!
});

// ❌ Fehler, falls falscher Type:
mutation.mutate({
  name: 123, // Error: Type 'number' is not assignable to type 'string'
});
```

**2. Kein Boilerplate**

```typescript
// ❌ REST API (viel Boilerplate):

// Backend:
app.post('/api/projects', async (req, res) => {
  // Validation
  const schema = z.object({ name: z.string(), /* ... */ });
  const validated = schema.parse(req.body); // Manual

  // Business Logic
  const project = await prisma.project.create({ data: validated });

  res.json({ project });
});

// Frontend:
const response = await fetch('/api/projects', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name, skills, budgetRange }),
});
const data = await response.json(); // ❌ `data` ist `any`, kein Type Safety

// ✅ tRPC (weniger Boilerplate):

// Backend:
create: protectedProcedure
  .input(z.object({ name: z.string(), /* ... */ }))
  .mutation(async ({ input, ctx }) => {
    return await ctx.prisma.project.create({ data: input });
  }),

// Frontend:
const project = await trpc.projects.create.mutate({ name, skills, budgetRange });
// ✅ `project` ist type-safe!
```

**3. Optimiert für Full-Stack TypeScript**

- Kein Swagger/OpenAPI nötig
- Keine Code-Generation (GraphQL CodeGen)
- Types werden automatisch geshared

**4. Great DX (Developer Experience)**

- Auto-Completion überall
- Refactoring: Backend ändern → Frontend zeigt sofort Errors
- Weniger Runtime-Errors (Catch @ Compile-Time)

## Alternatives Considered

### Alternative 1: REST API

**Pros:**

- ✅ Standard (jeder kennt REST)
- ✅ HTTP-Caching möglich
- ✅ Öffentliche API möglich
- ✅ Framework-agnostic

**Cons:**

- ❌ **Kein Type Safety** (Frontend ↔ Backend)
- ❌ Viel Boilerplate (Endpoints, Validation, Serialization)
- ❌ API-Docs notwendig (Swagger/OpenAPI)
- ❌ Validation dupliziert (Backend + Frontend)

**Warum nicht gewählt:**
Für eine interne API (nur eigenes Frontend) ist Type Safety wichtiger als REST-Standards. tRPC ist produktiver.

**Wann REST?**

- Öffentliche API (für Partner)
- Multi-Platform (iOS, Android, Web)
- → Später, wenn nötig

### Alternative 2: GraphQL

**Pros:**

- ✅ Flexible Queries (Client wählt Felder)
- ✅ Single Endpoint
- ✅ Type Safety (mit CodeGen)
- ✅ Gut für komplexe Daten-Fetching

**Cons:**

- ❌ **Viel Setup-Aufwand** (Schema, Resolvers, CodeGen)
- ❌ Steile Lernkurve
- ❌ Over-Engineering für MVP
- ❌ Performance: N+1 Problem (Dataloader nötig)
- ❌ Code-Generation notwendig (extra Build-Step)

**Warum nicht gewählt:**
GraphQL ist Overkill für dieses Projekt. tRPC ist einfacher, schneller zu entwickeln, und bietet ähnliche Type Safety.

**Wann GraphQL?**

- Komplexe, verschachtelte Daten
- Viele verschiedene Clients
- → Nicht nötig für MVP

### Alternative 3: Next.js Server Actions

**Pros:**

- ✅ Native Next.js (kein Extra-Framework)
- ✅ Type-safe
- ✅ Einfach für Mutations

**Cons:**

- ❌ Nur Mutations (keine Queries mit Server Actions)
- ❌ Weniger Flexibilität als tRPC
- ❌ Noch relativ neu (App Router Feature)

**Warum nicht gewählt:**
Server Actions sind gut für einfache Mutations, aber tRPC ist besser für komplexe APIs (Queries + Mutations, Middleware, Error Handling).

**Kombination:**

- tRPC für API (Queries + Mutations)
- Server Actions für UI-Interactions (später, optional)

### Alternative 4: gRPC

**Pros:**

- ✅ Sehr performant (Binary Protocol)
- ✅ Type-safe (Protobuf)
- ✅ Gut für Microservices

**Cons:**

- ❌ Nicht web-native (braucht Proxy für Browser)
- ❌ Viel Setup
- ❌ Over-Engineering für Monolith

**Warum nicht gewählt:**
gRPC ist für Microservices, nicht für Full-Stack Web-Apps. tRPC ist besser für Next.js.

## Trade-offs

### Pros (tRPC)

1. **Type Safety** → Weniger Runtime-Errors
2. **Produktivität** → Weniger Boilerplate, schnellere Development
3. **DX** → Auto-Completion, Refactoring einfach
4. **Einfach** → Kein Swagger, kein CodeGen

### Cons (tRPC)

1. **Vendor Lock-in**
   - tRPC funktioniert nur mit TypeScript
   - Migration zu REST/GraphQL wäre aufwendig
   - **Mitigation:** Akzeptabel für internes Projekt

2. **Keine öffentliche API**
   - tRPC ist nicht für externe Clients geeignet
   - **Mitigation:** Später REST-Endpoints für Partner (wenn nötig)

3. **Weniger bekannt als REST**
   - Team-Mitglieder müssten tRPC lernen
   - **Mitigation:** Solo-Dev, kein Team

## Implementation Notes

### tRPC Setup

```typescript
// src/server/trpc.ts
import { initTRPC, TRPCError } from '@trpc/server';
import { Context } from './context';

const t = initTRPC.context<Context>().create();

export const router = t.router;
export const publicProcedure = t.procedure;

// Protected Procedure (requires auth)
export const protectedProcedure = t.procedure.use(async ({ ctx, next }) => {
  if (!ctx.session || !ctx.session.user) {
    throw new TRPCError({ code: 'UNAUTHORIZED' });
  }
  return next({
    ctx: {
      session: ctx.session,
    },
  });
});
```

### Router Structure

```typescript
// src/server/routers/_app.ts
import { router } from '../trpc';
import { authRouter } from './auth';
import { freelancersRouter } from './freelancers';
import { projectsRouter } from './projects';
import { bookingsRouter } from './bookings';

export const appRouter = router({
  auth: authRouter,
  freelancers: freelancersRouter,
  projects: projectsRouter,
  bookings: bookingsRouter,
  // ...
});

export type AppRouter = typeof appRouter;
```

### Frontend Usage

```typescript
// src/lib/trpc.ts
import { createTRPCReact } from '@trpc/react-query';
import type { AppRouter } from '@/server/routers/_app';

export const trpc = createTRPCReact<AppRouter>();

// src/app/providers.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { httpBatchLink } from '@trpc/client';
import { trpc } from '@/lib/trpc';

const queryClient = new QueryClient();
const trpcClient = trpc.createClient({
  links: [
    httpBatchLink({
      url: '/api/trpc',
    }),
  ],
});

export function Providers({ children }) {
  return (
    <trpc.Provider client={trpcClient} queryClient={queryClient}>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </trpc.Provider>
  );
}
```

### Example: Create Project

```typescript
// Backend: src/server/routers/projects.ts
export const projectsRouter = router({
  create: companyProcedure // nur für Companies
    .input(z.object({
      name: z.string().max(100),
      description: z.string().max(5000),
      skills: z.array(z.string()).min(1).max(10),
      budgetRange: z.enum(['LESS_10K', 'RANGE_10_20K', 'RANGE_20_50K', 'RANGE_50_100K', 'MORE_100K']),
      startDate: z.date(),
    }))
    .mutation(async ({ input, ctx }) => {
      const project = await ctx.prisma.project.create({
        data: {
          ...input,
          companyId: ctx.session.user.companyProfileId,
          status: 'OPEN',
        },
      });

      // Send admin notification
      await sendEmail({
        to: 'admin@ai-match.de',
        subject: 'New Project Posted',
        // ...
      });

      return project;
    }),
});

// Frontend: src/components/CreateProjectForm.tsx
'use client';

import { trpc } from '@/lib/trpc';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  name: z.string().max(100),
  description: z.string().max(5000),
  skills: z.array(z.string()).min(1).max(10),
  budgetRange: z.enum(['LESS_10K', 'RANGE_10_20K', 'RANGE_20_50K', 'RANGE_50_100K', 'MORE_100K']),
  startDate: z.date(),
});

export function CreateProjectForm() {
  const form = useForm({
    resolver: zodResolver(schema),
  });

  const mutation = trpc.projects.create.useMutation({
    onSuccess: (project) => {
      console.log('Project created:', project);
      // Navigate to project page
    },
  });

  const onSubmit = (data) => {
    mutation.mutate(data); // ✅ Type-safe!
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* ... form fields ... */}
      <button type="submit" disabled={mutation.isLoading}>
        Create Project
      </button>
    </form>
  );
}
```

## Consequences

### Positive

1. **Weniger Bugs**
   - Type Errors werden zur Compile-Time gefangen
   - Refactoring ist sicherer

2. **Schnellere Development**
   - Weniger Boilerplate
   - Auto-Completion spart Zeit

3. **Bessere Maintainability**
   - Types sind Source of Truth
   - API-Docs nicht notwendig (Types sind Docs)

### Negative

1. **tRPC-spezifisch**
   - Funktioniert nur mit TypeScript
   - Alternative Clients (iOS, Android) nicht möglich
   - **Mitigation:** Später REST-Endpoints für externe Clients

2. **Kleineres Ecosystem als REST**
   - Weniger Tutorials
   - **Mitigation:** Gute offizielle Docs

## Follow-up Actions

- [x] tRPC installieren (`pnpm add @trpc/server @trpc/client @trpc/react-query`)
- [x] tRPC Setup (`src/server/trpc.ts`)
- [x] Router Structure definieren (`src/server/routers/`)
- [ ] Alle Procedures implementieren (auth, freelancers, projects, bookings)

## References

- [tRPC Documentation](https://trpc.io/docs)
- [tRPC with Next.js](https://trpc.io/docs/nextjs)
- [tRPC Best Practices](https://trpc.io/docs/server/introduction)

---

**Author:** Max Mustermann
**Date:** 27. Oktober 2025
**Status:** Accepted
