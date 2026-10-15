# ADR-004: Frontend State Management Strategy

## Status
Accepted

## Context
The ESRI App Finder & Builder Assistant requires managing several categories of state:
- **Server State**: Chat messages, app recommendations, Living Atlas datasets, web map configurations
- **Client State**: UI state (sidebar open/closed, active tab), selected app, current map view
- **Form State**: User inputs, filters, search queries
- **Cache State**: Previously fetched data to reduce API calls

We need a state management solution that:
- Handles async data fetching with caching
- Provides optimistic updates for better UX
- Avoids boilerplate code
- Supports TypeScript well
- Is easy to learn and maintain
- Performs well with frequent updates

## Decision
We will use a **hybrid state management approach**:
- **React Query (TanStack Query)** for server state management
- **Zustand** for client/UI state management
- **React Hook Form** for form state (if complex forms needed in future)

### Architecture
```
┌─────────────────────────────────────────┐
│  React Components                        │
├─────────────────────────────────────────┤
│  React Query Hooks    │  Zustand Store  │
│  (Server State)       │  (Client State) │
├───────────────────────┴─────────────────┤
│  API Services Layer                      │
└─────────────────────────────────────────┘
```

## Consequences

### Positive
1. **Separation of Concerns**: Clear distinction between server and client state
2. **Less Boilerplate**: React Query eliminates manual loading/error states
3. **Automatic Caching**: React Query caches API responses intelligently
4. **Optimistic Updates**: Easy to implement for better UX
5. **TypeScript Support**: Both libraries have excellent TypeScript support
6. **Developer Experience**: Simple APIs, easy to learn
7. **Performance**: Zustand is extremely lightweight (~1KB)
8. **No Context Hell**: Avoid deeply nested context providers
9. **Devtools**: React Query Devtools for debugging server state
10. **Future-Proof**: Easy to add Redux later if needed

### Negative
1. **Learning Curve**: Team needs to learn two state management patterns
2. **Dual State Sources**: Need to coordinate between React Query and Zustand
3. **Query Key Management**: React Query keys need careful planning
4. **Not a "Standard" Pattern**: Less common than Redux in enterprise

## Alternatives Considered

### 1. **Redux Toolkit**
- **Pros**:
  - Industry standard
  - Predictable state updates
  - Excellent devtools
  - Large ecosystem
- **Cons**:
  - Significant boilerplate even with toolkit
  - Overkill for our complexity level
  - Harder to learn for new developers
  - Doesn't solve server state caching
- **Why Rejected**: Too heavy for our needs. React Query handles server state better.

### 2. **React Context + useReducer**
- **Pros**:
  - Built into React
  - No dependencies
  - Simple for small apps
- **Cons**:
  - Performance issues with frequent updates
  - Context hell with many providers
  - No built-in caching or async handling
  - Manual loading/error state management
- **Why Rejected**: Not sufficient for complex async data management.

### 3. **Zustand Only**
- **Pros**:
  - Single state management solution
  - Very simple API
  - Good TypeScript support
- **Cons**:
  - No built-in async/caching support
  - Would need to implement our own data fetching logic
  - Manual cache invalidation
- **Why Rejected**: Zustand alone doesn't handle server state well.

### 4. **React Query Only**
- **Pros**:
  - Excellent for server state
  - Can store client state in URL params
  - Less to learn
- **Cons**:
  - Awkward for pure client state (UI toggles, etc.)
  - Query keys for client state feels wrong
  - Not designed for synchronous local state
- **Why Rejected**: Not ideal for UI state management.

### 5. **Jotai or Recoil**
- **Pros**:
  - Atomic state management
  - Modern React patterns
  - Good TypeScript support
- **Cons**:
  - Less mature than alternatives
  - Smaller community
  - Still need separate server state solution
- **Why Rejected**: Less battle-tested than Zustand. React Query + Zustand is simpler.

## Implementation Details

### React Query Setup

#### Configuration
```typescript
// src/config/react-query.config.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true
    },
    mutations: {
      retry: 0
    }
  }
});
```

#### Provider Setup
```typescript
// src/App.tsx
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './config/react-query.config';

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

#### Custom Hooks
```typescript
// src/hooks/useChat.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { chatService } from '../services/chat.service';

export function useChat(sessionId: string) {
  const queryClient = useQueryClient();

  const sendMessage = useMutation({
    mutationFn: (message: string) => 
      chatService.sendMessage({ message, sessionId }),
    onSuccess: (data) => {
      // Invalidate and refetch any related queries
      queryClient.invalidateQueries(['chat', sessionId]);
    }
  });

  return {
    sendMessage: sendMessage.mutate,
    isLoading: sendMessage.isPending,
    error: sendMessage.error
  };
}
```

```typescript
// src/hooks/useLivingAtlas.ts
import { useQuery } from '@tanstack/react-query';
import { atlasService } from '../services/atlas.service';

export function useLivingAtlasSearch(query: string, filters: any) {
  return useQuery({
    queryKey: ['living-atlas', query, filters],
    queryFn: () => atlasService.search({ query, ...filters }),
    enabled: query.length > 2, // Only search if query is 3+ chars
    staleTime: 5 * 60 * 1000 // Cache for 5 minutes
  });
}
```

### Zustand Setup

#### Store Definition
```typescript
// src/store/appStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface AppState {
  // UI State
  sidebarOpen: boolean;
  activeTab: 'chat' | 'map' | 'atlas' | 'preview';
  
  // App Selection
  selectedApp: string | null;
  selectedDatasets: string[];
  
  // Map Configuration
  currentWebMapId: string | null;
  mapExtent: any | null;
  
  // Actions
  setSidebarOpen: (open: boolean) => void;
  setActiveTab: (tab: AppState['activeTab']) => void;
  setSelectedApp: (appId: string | null) => void;
  addDataset: (datasetId: string) => void;
  removeDataset: (datasetId: string) => void;
  setCurrentWebMapId: (mapId: string | null) => void;
  setMapExtent: (extent: any) => void;
  reset: () => void;
}

const initialState = {
  sidebarOpen: true,
  activeTab: 'chat' as const,
  selectedApp: null,
  selectedDatasets: [],
  currentWebMapId: null,
  mapExtent: null
};

export const useAppStore = create<AppState>()(
  devtools(
    (set) => ({
      ...initialState,
      
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setActiveTab: (tab) => set({ activeTab: tab }),
      setSelectedApp: (appId) => set({ selectedApp: appId }),
      
      addDataset: (datasetId) => 
        set((state) => ({
          selectedDatasets: [...state.selectedDatasets, datasetId]
        })),
      
      removeDataset: (datasetId) =>
        set((state) => ({
          selectedDatasets: state.selectedDatasets.filter(id => id !== datasetId)
        })),
      
      setCurrentWebMapId: (mapId) => set({ currentWebMapId: mapId }),
      setMapExtent: (extent) => set({ mapExtent: extent }),
      
      reset: () => set(initialState)
    }),
    { name: 'AppStore' }
  )
);
```

#### Using the Store
```typescript
// In a component
import { useAppStore } from '../store/appStore';

function Sidebar() {
  const sidebarOpen = useAppStore((state) => state.sidebarOpen);
  const setSidebarOpen = useAppStore((state) => state.setSidebarOpen);
  
  // Or select multiple values
  const { activeTab, setActiveTab } = useAppStore((state) => ({
    activeTab: state.activeTab,
    setActiveTab: state.setActiveTab
  }));

  return <div>...</div>;
}
```

### Query Key Patterns

```typescript
// src/utils/queryKeys.ts
export const queryKeys = {
  chat: (sessionId: string) => ['chat', sessionId] as const,
  recommendations: (query: string) => ['recommendations', query] as const,
  livingAtlas: {
    all: ['living-atlas'] as const,
    search: (query: string, filters: any) => 
      ['living-atlas', 'search', query, filters] as const,
    detail: (datasetId: string) => 
      ['living-atlas', 'detail', datasetId] as const,
    categories: () => ['living-atlas', 'categories'] as const
  },
  maps: {
    all: ['maps'] as const,
    detail: (mapId: string) => ['maps', mapId] as const
  }
};
```

## State Flow Examples

### Example 1: User Sends Chat Message
```
1. User types message → Component calls useChatMutation
2. React Query: Send request to /api/chat
3. Loading state automatically managed by React Query
4. Response received with recommendations
5. React Query: Cache response with key ['chat', sessionId]
6. Zustand: Update selectedApp if user picks recommendation
```

### Example 2: User Searches Living Atlas
```
1. User types search query → Component uses useLivingAtlasSearch hook
2. React Query: Debounced search (via enabled flag)
3. Cache hit? → Return cached data immediately
4. Cache miss? → Fetch from /api/living-atlas/search
5. React Query: Cache results for 5 minutes
6. User selects dataset → Zustand: Add to selectedDatasets array
```

### Example 3: User Opens/Closes Sidebar
```
1. User clicks sidebar toggle
2. Component calls useAppStore(state => state.setSidebarOpen)
3. Zustand: Update sidebarOpen state
4. All components subscribed to sidebarOpen re-render
5. No API calls needed (pure client state)
```

## Performance Considerations

### React Query Optimizations
1. **Stale-While-Revalidate**: Show cached data while fetching fresh data
2. **Prefetching**: Prefetch likely next queries
3. **Pagination**: Use `useInfiniteQuery` for Living Atlas results
4. **Optimistic Updates**: Update UI before server confirms

### Zustand Optimizations
1. **Selective Subscriptions**: Only subscribe to needed state slices
2. **Shallow Equality**: Use `shallow` for object subscriptions
3. **Computed Values**: Use selectors for derived state

## Testing Strategy

### React Query Testing
```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChat } from '../hooks/useChat';

test('should send chat message', async () => {
  const queryClient = new QueryClient();
  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  const { result } = renderHook(() => useChat('session-123'), { wrapper });
  
  result.current.sendMessage('test message');
  
  await waitFor(() => expect(result.current.isLoading).toBe(false));
  expect(result.current.error).toBeNull();
});
```

### Zustand Testing
```typescript
import { renderHook, act } from '@testing-library/react';
import { useAppStore } from '../store/appStore';

test('should toggle sidebar', () => {
  const { result } = renderHook(() => useAppStore());
  
  expect(result.current.sidebarOpen).toBe(true);
  
  act(() => {
    result.current.setSidebarOpen(false);
  });
  
  expect(result.current.sidebarOpen).toBe(false);
});
```

## Migration Path

If we need to migrate to Redux later:
1. Server state stays with React Query (no change)
2. Only client state needs migration from Zustand to Redux
3. Zustand store structure is compatible with Redux slices
4. Gradual migration possible (Zustand and Redux can coexist)

## References
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [React Query Best Practices](https://tkdodo.eu/blog/practical-react-query)

## Related ADRs
- [ADR-001: Frontend Framework Selection](./001-frontend-framework-selection.md)

---
**Date**: 2025-11-05  
**Author**: Development Team  
**Status**: Accepted
