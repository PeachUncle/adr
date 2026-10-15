# ADR 010: Frontend-Backend Separation

**Status:** Accepted

**Date:** 2024-11-12

---

## Context

BuildFlow uses Laravel as primary backend (ADR-014) with potential future implementations. We must decide:
- Should frontend be coupled with backend?
- Should each backend have its own frontend?
- How to maintain consistency?

---

## Decision

**Build a single React SPA frontend that works with any backend via the API contract.**

### Architecture

```
┌─────────────────────┐
│   React Frontend    │
│   (buildflow-react) │
│   Port: 5173        │
└──────────┬──────────┘
           │ HTTP API calls
           │ (configurable backend)
           ↓
   ┌───────┴───────┐
   │               │
┌──▼──┐  ┌────▼────┐  ┌────▼────┐
│Laravel│ │ Symfony │  │ Next.js │
│ :8000 │ │  :8001  │  │  :3000  │
└───────┘ └─────────┘  └─────────┘
```

### Configuration

```typescript
// .env
VITE_API_BASE_URL=http://localhost:8000/api/v1  // Laravel
// or
VITE_API_BASE_URL=http://localhost:8001/api/v1  // Symfony
// or
VITE_API_BASE_URL=http://localhost:3000/api/v1  // Next.js
```

### Type Generation

```bash
# Generate TypeScript types from OpenAPI spec
npm run generate-types

# src/api/types.ts is auto-generated
import { Client, Quote, Project } from '@/api/types';
```

---

## Consequences

### Positive
- ✅ **Consistency**: Same UX with any backend
- ✅ **Efficiency**: Build UI once, use with all backends
- ✅ **Contract Enforcement**: Forces API consistency
- ✅ **Development Speed**: Frontend and backend teams independent
- ✅ **Testing**: Test frontend against any backend
- ✅ **Deployment**: Deploy frontend and backend separately

### Negative
- ⚠️ **No SSR Benefits**: Can't leverage backend rendering
- ⚠️ **SEO Limited**: SPA limitations (solvable with pre-rendering)
- ⚠️ **CORS Required**: Must configure CORS on backends
- ⚠️ **Two Deployments**: Frontend and backend separate

---

## Technology Choice

### React SPA
- **Framework**: React 18+ with Hooks
- **Build Tool**: Vite (fast, modern)
- **Language**: TypeScript (type safety)
- **State**: TanStack Query (React Query)
- **Routing**: React Router v6
- **UI**: Tailwind CSS + Shadcn/ui
- **Forms**: React Hook Form + Zod
- **API Client**: Axios + auto-generated from OpenAPI

### Why React?
- Modern and popular
- Excellent ecosystem
- TypeScript support
- Component reusability
- Strong tooling

### Why Not Framework-Specific?
- ❌ Laravel + Inertia → Couples to Laravel only
- ❌ Next.js SSR → Becomes another backend implementation
- ❌ Symfony + Twig → Server-rendered, not API-based

---

## API Client Structure

```typescript
// src/api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// src/api/clients.ts (generated)
export const clientsApi = {
  list: () => apiClient.get<Client[]>('/clients'),
  create: (data: ClientInput) => apiClient.post<Client>('/clients', data),
  // ... auto-generated from OpenAPI
};
```

---

## Alternatives Considered

### Alternative 1: Backend-Specific Frontends
**Description:** Each backend has its own frontend (Laravel Blade, Symfony Twig, Next.js React)

**Why rejected:** 
- Duplicate UI development
- Inconsistent UX
- More maintenance
- Doesn't showcase React skills

### Alternative 2: Next.js as Frontend + Backend
**Description:** Use Next.js for both API and frontend

**Why rejected:**
- Becomes single implementation
- Loses multi-backend showcase
- No longer language-agnostic
- Couples frontend to Node.js

### Alternative 3: Monorepo with Shared Components
**Description:** Keep frontends separate but share components

**Why rejected:**
- Still duplicate app logic
- Complex dependency management
- Doesn't solve consistency problem

---

## Mobile Strategy (Future)

Same approach applies to mobile:
- **buildflow-android**: Native Android, consumes API
- **buildflow-ios**: Native iOS, consumes API
- Both work with any backend
- Share API contract with web frontend

---

**Related:** 
- ADR-001 (Multi-repo enables this)
- ADR-002 (API-first makes this possible)
- ADR-008 (Contract tests ensure compatibility)
