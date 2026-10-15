# ADR 011: Frontend Component Architecture

**Date:** 2025-11-02  
**Status:** ✅ Accepted  
**Deciders:** Engineering Team  
**Related:** Day 7 QA Process, Next.js 15 App Router, React Server Components

---

## Context

With Next.js 15 App Router and React Server Components (RSC), we need clear architectural patterns for component organization, data fetching, and interactivity. Current codebase shows inconsistencies in:

1. **Server vs. Client Components**: Unclear when to use each
2. **Data Fetching**: Mixed patterns (useEffect, server components, API routes)
3. **Component Organization**: Large files, unclear separation of concerns
4. **Error Handling**: Inconsistent error boundaries and error states
5. **Loading States**: Generic "Loading..." vs. branded skeletons

### Problems Observed

**Server Component Violations:**
```typescript
// ❌ Server Component with onClick handler
export default async function PromptPage() {
  return <Button onClick={() => {}}>Copy</Button>; // Build error
}
```

**Mixed Data Fetching:**
```typescript
// ❌ useEffect for data fetching
'use client';
export function PromptList() {
  const [prompts, setPrompts] = useState([]);
  useEffect(() => {
    fetch('/api/prompts').then(r => r.json()).then(setPrompts);
  }, []);
  // Should use Server Component
}
```

**Large Components:**
```typescript
// ❌ 600+ line components
// src/app/page.tsx - 417 lines
// src/app/patterns/page.tsx - 490 lines
```

---

## Decision

**Adopt Next.js 15 App Router best practices with clear component architecture patterns**

### Core Principles

1. **Server Components by Default**
   - Use Server Components for data fetching and static content
   - Only use Client Components when interactivity is required
   - Minimize client-side JavaScript bundle

2. **Clear Separation of Concerns**
   - Server Components: Data fetching, static rendering
   - Client Components: Interactivity, hooks, browser APIs
   - Shared Components: Reusable, composable UI

3. **Component Size Limits**
   - Target: < 200 lines per component
   - Extract logic to custom hooks
   - Break large components into smaller pieces

4. **Consistent Error Handling**
   - Error boundaries for Client Components
   - Try/catch for Server Components
   - Professional error UI, not generic messages

5. **Professional Loading States**
   - Branded skeleton loaders, not "Loading..."
   - Suspense boundaries for async components
   - Optimistic UI updates for mutations

---

## Architecture Patterns

### Pattern 1: Server Component → Client Component Composition

**When to Use:**
- Page needs data fetching + interactivity
- Minimize client bundle size

**Structure:**
```typescript
// ✅ Server Component (page.tsx)
export default async function PromptsPage() {
  const prompts = await fetchPrompts(); // Server-side fetch
  
  return (
    <div>
      <ServerStats stats={prompts} />
      <PromptsClient prompts={prompts} />
    </div>
  );
}

// ✅ Client Component (PromptsClient.tsx)
'use client';
export function PromptsClient({ prompts }: Props) {
  const [filter, setFilter] = useState('');
  // Interactive filtering, search, etc.
  return <PromptList prompts={filtered} />;
}
```

### Pattern 2: Data Fetching Strategy

**Server Components (Preferred):**
```typescript
// ✅ Server Component - Direct DB access
export default async function Dashboard() {
  const stats = await db.stats.find();
  return <StatsDisplay stats={stats} />;
}
```

**API Routes (When Needed):**
```typescript
// ✅ For client-side fetching or external APIs
'use client';
export function ClientStats() {
  const { data } = useSWR('/api/stats');
  return <StatsDisplay stats={data} />;
}
```

**Server Actions (Mutations):**
```typescript
// ✅ Server Actions for mutations
async function updatePrompt(formData: FormData) {
  'use server';
  await db.prompts.update(formData.get('id'));
  revalidatePath('/prompts');
}
```

### Pattern 3: Component Organization

**Directory Structure:**
```
src/
├── app/                    # Next.js pages (Server Components)
│   ├── prompts/
│   │   ├── page.tsx        # Server Component (data fetching)
│   │   └── [id]/
│   │       └── page.tsx
├── components/
│   ├── ui/                 # shadcn/ui primitives
│   ├── features/          # Feature-specific components
│   │   ├── PromptCard.tsx         # Client Component (interactive)
│   │   ├── PromptList.tsx        # Client Component (filtering)
│   │   └── PromptActions.tsx     # Client Component (buttons)
│   └── layout/            # Layout components
│       ├── Header.tsx
│       └── Footer.tsx
└── hooks/                  # Custom React hooks
    ├── usePrompts.ts
    └── useFavorites.ts
```

### Pattern 4: Error Boundaries

**Client Components:**
```typescript
// ✅ Error boundary wrapper
'use client';
export function PromptCardWithErrorBoundary({ prompt }: Props) {
  return (
    <ErrorBoundary fallback={<PromptCardError />}>
      <PromptCard prompt={prompt} />
    </ErrorBoundary>
  );
}
```

**Server Components:**
```typescript
// ✅ Try/catch with error handling
export default async function PromptsPage() {
  try {
    const prompts = await fetchPrompts();
    return <PromptList prompts={prompts} />;
  } catch (error) {
    return <ErrorPage error={error} />;
  }
}
```

### Pattern 5: Loading States

**Suspense Boundaries:**
```typescript
// ✅ Suspense with skeleton
export default function PromptsPage() {
  return (
    <Suspense fallback={<PromptsSkeleton />}>
      <PromptsList />
    </Suspense>
  );
}
```

**Optimistic Updates:**
```typescript
// ✅ Optimistic UI for mutations
'use client';
export function FavoriteButton({ promptId }: Props) {
  const { favorites, toggleFavorite } = useFavorites();
  const isFavorite = favorites.includes(promptId);
  
  const handleClick = async () => {
    // Optimistic update
    toggleFavorite(promptId, { optimistic: true });
    
    try {
      await fetch('/api/favorites', { method: 'POST', body: { promptId } });
    } catch (error) {
      // Rollback on error
      toggleFavorite(promptId, { optimistic: false });
    }
  };
  
  return <HeartButton filled={isFavorite} onClick={handleClick} />;
}
```

---

## Component Guidelines

### Server Components

**Use When:**
- ✅ Fetching data from database
- ✅ Accessing backend resources
- ✅ Sensitive data (API keys, tokens)
- ✅ Heavy dependencies (reduce bundle size)
- ✅ Static content

**Don't Use When:**
- ❌ Need interactivity (onClick, onChange)
- ❌ Need browser APIs (localStorage, window)
- ❌ Need React hooks (useState, useEffect)
- ❌ Need event listeners

**Example:**
```typescript
// ✅ Server Component
export default async function PromptsPage() {
  const prompts = await db.prompts.find();
  return (
    <div>
      <h1>Prompts</h1>
      <PromptsClient prompts={prompts} />
    </div>
  );
}
```

### Client Components

**Use When:**
- ✅ Interactive elements (buttons, forms, inputs)
- ✅ State management (useState, useReducer)
- ✅ Effects (useEffect, useLayoutEffect)
- ✅ Browser APIs
- ✅ Third-party libraries (charts, animations)

**Don't Use When:**
- ❌ Data fetching (use Server Component)
- ❌ Static content (use Server Component)
- ❌ Can be done server-side

**Example:**
```typescript
// ✅ Client Component
'use client';
export function PromptActions({ prompt }: Props) {
  const { copyToClipboard } = useClipboard();
  const [copied, setCopied] = useState(false);
  
  return (
    <Button onClick={() => {
      copyToClipboard(prompt.content);
      setCopied(true);
    }}>
      {copied ? 'Copied!' : 'Copy'}
    </Button>
  );
}
```

### Component Size Limits

**Guidelines:**
- **Target:** < 200 lines per component
- **Large Components (> 300 lines):** Extract sub-components
- **Logic Extraction:** Move to custom hooks
- **Data Fetching:** Move to Server Component or hook

**Refactoring Example:**
```typescript
// ❌ BEFORE: 400-line component
export default function PromptsPage() {
  // 400 lines of mixed logic
}

// ✅ AFTER: Split into smaller pieces
export default async function PromptsPage() {
  const prompts = await fetchPrompts();
  return <PromptsClient prompts={prompts} />;
}

'use client';
export function PromptsClient({ prompts }: Props) {
  const { filtered, search, filters } = usePromptFilters(prompts);
  return (
    <div>
      <PromptSearch onSearch={search} />
      <PromptFilters filters={filters} />
      <PromptList prompts={filtered} />
    </div>
  );
}
```

---

## Consequences

### ✅ Positive

1. **Performance**
   - Smaller client bundles (Server Components don't ship JS)
   - Faster initial page load
   - Better SEO (server-rendered content)

2. **Developer Experience**
   - Clear patterns reduce confusion
   - Easier to reason about data flow
   - Better TypeScript support

3. **Maintainability**
   - Smaller components easier to understand
   - Clear separation of concerns
   - Easier to test

4. **User Experience**
   - Professional loading states
   - Better error handling
   - Optimistic UI updates feel instant

### ⚠️ Negative

1. **Learning Curve**
   - Team needs to understand RSC concepts
   - More complex than pure client-side React
   - Need to know when to use each pattern

2. **Refactoring Effort**
   - Existing large components need splitting
   - Some components need Server/Client separation
   - Migration takes time

3. **Debugging Complexity**
   - Server/Client boundary can be confusing
   - Need to understand hydration issues
   - Error boundaries behave differently

### 🔄 Trade-offs

| Aspect | Mixed Approach | Structured RSC |
|--------|---------------|----------------|
| Bundle Size | ⚠️ Large | ✅ Small |
| Initial Load | ⚠️ Slow | ✅ Fast |
| SEO | ⚠️ Client-side | ✅ Server-side |
| Complexity | ⚠️ Lower | ✅ Higher |
| Maintainability | ❌ Low | ✅ High |
| Developer Clarity | ⚠️ Unclear | ✅ Clear |

**Winner:** Structured RSC (performance and maintainability outweigh complexity)

---

## Alternatives Considered

### Alternative 1: Pure Client-Side (CSR)

**Pros:**
- Simpler mental model
- No Server/Client boundary
- Traditional React patterns

**Cons:**
- Larger bundles
- Slower initial load
- Poor SEO
- Higher server costs

**Verdict:** ❌ Rejected - Performance and SEO requirements

### Alternative 2: Pages Router (Legacy)

**Pros:**
- Mature patterns
- Well-documented
- Team familiarity

**Cons:**
- Not Next.js 15 standard
- Less performant
- Missing RSC benefits

**Verdict:** ❌ Rejected - Using Next.js 15 App Router

### Alternative 3: Hybrid Approach (Current)

**Pros:**
- Flexible
- Can optimize incrementally

**Cons:**
- Inconsistent patterns
- Unclear when to use what
- Technical debt accumulation

**Verdict:** ⚠️ Acceptable - Use as migration strategy

---

## Implementation Plan

### Phase 1: Documentation & Guidelines (Day 7)

**Tasks:**
1. ✅ Create this ADR
2. ⏳ Update `.cursorrules` with component patterns
3. ⏳ Create component template examples
4. ⏳ Document common patterns

### Phase 2: Refactor Existing Components

**Priority Order:**
1. High-traffic pages (`/prompts`, `/dashboard`)
2. Large components (> 300 lines)
3. Components with mixed Server/Client logic

**Timeline:** Incremental, ongoing

### Phase 3: Prevention

**Pre-commit Hooks:**
- Check component size (< 300 lines)
- Verify 'use client' only when needed
- Ensure Server Components don't use hooks

**Code Review Checklist:**
- [ ] Component size < 200 lines (or justified)
- [ ] Server/Client separation clear
- [ ] Error boundaries for Client Components
- [ ] Loading states implemented
- [ ] No useEffect for data fetching

---

## Examples

### Example 1: Page with Data Fetching + Interactivity

**Before:**
```typescript
// ❌ Mixed Server/Client logic
export default function PromptsPage() {
  const [prompts, setPrompts] = useState([]);
  useEffect(() => {
    fetch('/api/prompts').then(r => r.json()).then(setPrompts);
  }, []);
  // ...
}
```

**After:**
```typescript
// ✅ Server Component for data
export default async function PromptsPage() {
  const prompts = await db.prompts.find();
  return <PromptsClient prompts={prompts} />;
}

// ✅ Client Component for interactivity
'use client';
export function PromptsClient({ prompts }: Props) {
  const [filter, setFilter] = useState('');
  // Interactive logic
}
```

### Example 2: Large Component Refactoring

**Before:**
```typescript
// ❌ 400-line component
export default function Dashboard() {
  // 400 lines of mixed logic
}
```

**After:**
```typescript
// ✅ Server Component - data fetching
export default async function Dashboard() {
  const stats = await fetchDashboardStats();
  return <DashboardClient stats={stats} />;
}

// ✅ Client Component - split into smaller pieces
'use client';
export function DashboardClient({ stats }: Props) {
  return (
    <div>
      <StatsPanel stats={stats} />
      <RecentActivity />
      <QuickActions />
    </div>
  );
}
```

### Example 3: Error Handling

**Before:**
```typescript
// ❌ Generic error handling
export default function Page() {
  try {
    const data = await fetchData();
  } catch (error) {
    return <div>Error: {error.message}</div>;
  }
}
```

**After:**
```typescript
// ✅ Professional error UI
export default function Page() {
  try {
    const data = await fetchData();
    return <Content data={data} />;
  } catch (error) {
    return <ErrorPage error={error} />;
  }
}

// ErrorPage component with retry, helpful message, etc.
```

---

## Success Criteria

**Phase 1 (Documentation):**
- ✅ ADR created
- ✅ Patterns documented
- ✅ Guidelines clear

**Phase 2 (Refactoring):**
- All pages follow Server/Client pattern
- Components < 300 lines
- Error boundaries implemented
- Loading states professional

**Phase 3 (Prevention):**
- Pre-commit hooks active
- Code review checklist enforced
- Team follows patterns consistently

---

## Metrics

### Before Architecture

- **Component Size:** Avg 350 lines, max 600+
- **Server/Client:** Mixed, unclear boundaries
- **Error Handling:** Generic, inconsistent
- **Loading States:** "Loading..." text

### After Architecture

- **Component Size:** Target < 200 lines
- **Server/Client:** Clear separation
- **Error Handling:** Professional error UI
- **Loading States:** Branded skeletons

---

## References

- [Next.js 15 App Router Docs](https://nextjs.org/docs/app)
- [React Server Components](https://react.dev/reference/rsc/server-components)
- [Day 7 Plan](../planning/DAY_7_QA_FRONTEND_IMPROVEMENTS.md)
- [Pattern Audit Report](../../testing/PATTERN_AUDIT_DAY7.md)
- [Code Quality Review](../../architecture/CODE_QUALITY_REVIEW.md)

---

## Related ADRs

- ADR 009: Pattern-Based Bug Fixing (similar audit approach)
- ADR 010: DRY Improvements (component reuse patterns)
- ADR 008: Favorites System (Server/Client separation example)

---

## Notes

**Future Enhancements:**
1. Component library/storybook
2. Automated component size checks
3. AST-based Server/Client boundary detection
4. Performance monitoring for component load times

**Key Principle:**
> "Server Components by default, Client Components when needed"

---

**Last Updated:** 2025-11-02  
**Review Date:** 2025-12-02 (1 month)  
**Status:** ✅ Accepted - Implementation in progress  
**Tags:** #architecture #frontend #nextjs #react #rsc #day7

