# ADR 002: TanStack Query for Server State Management

**Status:** Rejected (Not Implemented)

**Date:** 2025-10-18

**Context:**

WCAG Explorer fetches data from a backend API to display WCAG success criteria with various filters and metadata. The application needs to:

- Fetch and cache API responses
- Handle loading and error states
- Refetch data when filters change
- Provide a good user experience with proper loading indicators
- Manage server state separately from UI state

We evaluated whether to use a dedicated server state management library like TanStack Query (formerly React Query) or implement data fetching with native React features (useState, useEffect).

**Decision:**

We decided **NOT to use TanStack Query** and instead manage server state with **native React hooks** (useState, useEffect) and custom utility functions.

**Consequences:**

### Positive (of Not Using TanStack Query)

1. **Simplicity:**
   - Fewer dependencies to learn and maintain
   - Straightforward data flow that's easy to understand
   - Direct control over fetch logic and timing

2. **Reduced Bundle Size:**
   - No additional library weight (~13KB gzipped for TanStack Query)
   - Smaller overall application bundle

3. **Explicit Control:**
   - Full visibility into when and how data is fetched
   - Custom debouncing and caching logic tailored to our needs
   - No "magic" behavior from library abstractions

4. **URL-Based State Integration:**
   - Direct integration with URL state management
   - Simpler synchronization between URL params and API calls
   - Clear data flow: URL → State → API → Results

5. **Learning Curve:**
   - New team members only need to know React fundamentals
   - No additional patterns or APIs to learn

### Negative (of Not Using TanStack Query)

1. **Manual State Management:**
   - Manually managing loading, error, and success states
   - More boilerplate code in components
   - Need to handle edge cases ourselves (race conditions, stale data)

2. **No Built-in Caching:**
   - Every navigation refetches data even if filters haven't changed
   - No automatic cache invalidation strategies
   - No background refetching or stale-while-revalidate patterns

3. **Missing Features:**
   - No automatic retry logic for failed requests
   - No optimistic updates for mutations (future feature)
   - No request deduplication (multiple components requesting same data)
   - No prefetching capabilities

4. **Reinventing Patterns:**
   - Custom implementation of common patterns (debouncing, error handling)
   - Risk of subtle bugs in custom state management
   - Need to maintain custom utilities (lib/api.ts, lib/urlUtils.ts)

5. **Future Scalability:**
   - As app grows, may need more sophisticated caching
   - Admin features may need mutation management
   - May eventually need to adopt TanStack Query anyway

### Current Implementation

```typescript
// App.tsx
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState<string | null>(null);
const [results, setResults] = useState<PaginatedResult<Criterion>>(...);

useEffect(() => {
  const fetchResults = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getCriteria(filters);
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  fetchResults();
}, [filters]);
```

**Alternatives Considered:**

### TanStack Query (React Query)
- **Pros:**
  - Automatic caching and cache invalidation
  - Built-in loading/error states
  - Retry logic and request deduplication
  - Optimistic updates and mutations
  - DevTools for debugging
- **Cons:**
  - Additional dependency and learning curve
  - May be overkill for simple read-only application
  - Need to integrate with URL-based state
- **Reason for rejection:** Application is currently simple enough that native hooks suffice. URL state is our primary source of truth, and we fetch on every filter change, making aggressive caching less beneficial.

### SWR (Stale-While-Revalidate)
- **Pros:**
  - Lightweight alternative to TanStack Query
  - Good caching and revalidation strategies
  - Simple API
- **Cons:**
  - Still an additional dependency
  - Less feature-rich than TanStack Query
  - Same integration challenges with URL state
- **Reason for rejection:** Similar to TanStack Query but with fewer features. If we needed a library, TanStack Query would be the better choice.

### Redux Toolkit Query (RTK Query)
- **Pros:**
  - Integrated with Redux ecosystem
  - Strong typing support
  - Code generation from OpenAPI specs
- **Cons:**
  - Requires Redux infrastructure
  - More complex setup
  - Heavier bundle size
  - We don't use Redux for anything else
- **Reason for rejection:** Too heavy for our needs, and we don't use Redux for client state.

### Zustand + API Layer
- **Pros:**
  - Lightweight global state
  - Simple API
  - Could combine with API utilities
- **Cons:**
  - Still need to implement caching logic
  - Adds global state when local state works
  - Doesn't solve server state problems
- **Reason for rejection:** Doesn't provide server state benefits over native hooks.

**When to Reconsider:**

This decision should be revisited if:

1. **Performance Issues:** Users experience slow page loads due to refetching
2. **Complex Mutations:** Admin features require complex create/update/delete operations
3. **Real-time Updates:** Need to poll or sync data from server
4. **Multiple Data Sources:** App grows to fetch from many different endpoints
5. **Team Feedback:** Developers find manual state management becoming unwieldy

**Notes:**

- Current approach works well for a read-mostly application with URL-driven filters
- The API is fast enough that refetching on navigation isn't problematic
- localStorage provides persistence for favorites and preferences (not server state)
- URL state acts as a form of "cache" - bookmarked URLs restore exact filter state
