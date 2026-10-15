# ADR-0003: React Query for Data Fetching

## Status
Accepted

## Date
2024-12-30

## Context

The application has extensive data fetching requirements:
- User authentication state
- Document lists and details
- CPR analysis workflows
- Compliance verification results
- Organization and team data
- Real-time status polling

Challenges:
1. **Cache Management**: Avoid redundant fetches for the same data
2. **Loading/Error States**: Consistent handling across components
3. **Stale Data**: Balance freshness with performance
4. **Mutations**: Handle optimistic updates and cache invalidation
5. **Polling**: Support real-time status updates for async workflows

## Decision

Use TanStack Query (React Query v5) as the primary data fetching and caching layer.

### Implementation

Provider setup in `src/providers/QueryProvider.tsx`:

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 10,   // 10 minutes (formerly cacheTime)
      retry: 1,
      refetchOnWindowFocus: false
    }
  }
})
```

### Query Patterns

Standard query hook pattern (`src/hooks/useDocuments.ts`):

```typescript
export function useDocuments(sessionId?: string) {
  const queryClient = useQueryClient()

  const {
    data: documents = [],
    isLoading: loading,
    error: queryError,
    refetch
  } = useQuery({
    queryKey: ['documents', 'user', sessionId],
    queryFn: () => fetchDocumentsAPI(sessionId),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10
  })

  const deleteMutation = useMutation({
    mutationFn: deleteDocumentAPI,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] })
    }
  })

  return { documents, loading, error, removeDocument: deleteMutation.mutateAsync }
}
```

### Polling for Async Workflows

Used in CPR analysis status polling:

```typescript
const { data: status } = useQuery({
  queryKey: ['cpr', 'status', sessionId],
  queryFn: () => fetchCPRStatus(sessionId),
  refetchInterval: (data) =>
    data?.status === 'completed' ? false : 3000, // Poll every 3s until done
  enabled: !!sessionId
})
```

### Key Files

- `src/providers/QueryProvider.tsx` - Client configuration
- `src/hooks/useDocuments.ts` - Document fetching
- `src/hooks/useCPRAnalysis.ts` - CPR workflow with polling
- `src/hooks/useAdminUsers.ts` - Admin user management
- `src/hooks/useOrganization.ts` - Organization data

## Consequences

### Positive

1. **Automatic Caching**: Queries with same key share cached data
2. **Stale-While-Revalidate**: Shows cached data while fetching fresh
3. **Built-in States**: `isLoading`, `isError`, `data` standardized
4. **Smart Refetching**: Configurable on focus, interval, or manual
5. **Optimistic Updates**: Mutations can update cache before server confirms
6. **DevTools**: Excellent debugging with React Query DevTools
7. **Type Safety**: Full TypeScript support with generics

### Negative

1. **Bundle Size**: ~13KB gzipped (acceptable trade-off)
2. **Learning Curve**: Query keys and invalidation patterns take time to master
3. **Over-caching Risk**: Need to properly invalidate on mutations
4. **Provider Required**: Must wrap app in QueryClientProvider

### Query Key Conventions

```typescript
// Entity lists
['documents', 'user', sessionId]
['sessions', 'list']
['admin', 'users', { page, limit }]

// Single entities
['documents', 'detail', documentId]
['cpr', 'status', sessionId]

// Actions
['cpr', 'analysis', 'result']
```

## References

- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [Query Keys Best Practices](https://tanstack.com/query/latest/docs/react/guides/query-keys)
- `src/providers/QueryProvider.tsx` - Configuration
