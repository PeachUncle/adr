# ADR 003: Zustand for Client State Management

**Status:** Rejected (Not Implemented)

**Date:** 2025-10-18

**Context:**

WCAG Explorer needs to manage several types of client-side state:

- User preferences (theme, view mode, announcement settings)
- Favorites collection
- UI state (modals, expanded sections, filter visibility)
- Filter state (search query, selected versions, levels, guidelines)

We needed to decide on an approach for managing this state across the application. The state could be:
- Local to individual components
- Shared across multiple components
- Persisted to localStorage
- Synchronized with URL parameters

**Decision:**

We decided **NOT to use Zustand** (or any global state management library) and instead manage state with:

1. **React useState/useReducer** - For local component state and cross-component state (via props)
2. **URL parameters** - As the source of truth for filters and routing
3. **localStorage utilities** - For user preferences and persistence
4. **Context API** - Not currently used, but available if needed

**Consequences:**

### Positive (of Not Using Zustand)

1. **Simplicity:**
   - No additional state management library to learn
   - Straightforward React patterns familiar to all developers
   - Clear component boundaries and data flow

2. **URL as Source of Truth:**
   - Filters live in URL, making state shareable and bookmarkable
   - No synchronization issues between URL and global state
   - Browser back/forward work naturally

3. **Minimal Dependencies:**
   - One less library to maintain and update
   - Smaller bundle size (~3KB saved)
   - No external state management patterns to understand

4. **Explicit Data Flow:**
   - Props drilling is minimal and intentional
   - Easy to trace where state comes from and where it goes
   - Component composition makes state passing clear

5. **Colocation:**
   - State lives close to where it's used
   - Easier to understand component dependencies
   - Simpler to refactor individual components

6. **localStorage Abstraction:**
   - Dedicated utility modules for persistence (lib/favorites.ts, lib/filterState.ts, lib/themes.ts)
   - Type-safe helpers for reading/writing preferences
   - Consistent persistence patterns across the app

### Negative (of Not Using Zustand)

1. **Props Drilling:**
   - Some state (favorites, theme) passed through multiple levels
   - App.tsx contains a lot of state management logic
   - Changes to state shape affect multiple components

2. **No Global State:**
   - Can't easily access favorites or theme from deeply nested components
   - Need to pass callbacks down for state updates
   - Some components receive props they only pass through

3. **State Updates Can Be Verbose:**
   - Manual state setting and callback passing
   - Need to lift state up to common ancestor
   - More code than `useStore()` hook

4. **Potential Duplication:**
   - Similar patterns repeated (localStorage read/write, state initialization)
   - Could benefit from shared hooks (useFavorites, useTheme)
   - Manual synchronization between localStorage and state

5. **Scalability Concerns:**
   - As app grows, prop drilling may become unwieldy
   - Adding new shared state requires touching multiple files
   - Testing requires setting up more component hierarchies

### Current Implementation

```typescript
// App.tsx - Main state container
const [favorites, setFavorites] = useState<Set<string>>(() => getFavorites());
const [viewMode, setViewMode] = useState<ViewMode>('card');
const [filters, setFilters] = useState<QueryFilters>(getDefaultFilters());

// Pass down to children
<CriterionCard
  criterion={c}
  isFavorite={favorites.has(c.id)}
  onToggleFavorite={() => handleToggleFavorite(c.id)}
/>

// Utility functions handle persistence
const handleToggleFavorite = (id: string) => {
  const newFavorites = toggleFavorite(id); // Updates localStorage
  setFavorites(newFavorites);
};
```

**Alternatives Considered:**

### Zustand
- **Pros:**
  - Minimal boilerplate, simple API
  - Easy to create slices for different state domains
  - Built-in persistence middleware for localStorage
  - Good TypeScript support
  - Small bundle size (~1KB)
- **Cons:**
  - Another library to maintain
  - Global state could lead to less intentional architecture
  - Doesn't solve URL synchronization
  - May encourage bypassing prop drilling too eagerly
- **Reason for rejection:** Application state is simple enough that React's built-in tools suffice. URL state handles most of the complexity, and localStorage utilities provide sufficient persistence.

### Redux Toolkit
- **Pros:**
  - Industry standard, well-documented
  - Powerful DevTools
  - Strong patterns and middleware ecosystem
  - Excellent TypeScript support
- **Cons:**
  - Much more boilerplate than Zustand
  - Larger bundle size (~15KB)
  - Overkill for this application's needs
  - Steeper learning curve
- **Reason for rejection:** Too heavy and complex for our relatively simple state management needs.

### React Context API
- **Pros:**
  - Built into React, no dependencies
  - Can avoid props drilling
  - Good for theme and user preferences
- **Cons:**
  - Can cause unnecessary re-renders if not optimized
  - More verbose than Zustand
  - Multiple contexts can get messy
  - Still need to handle persistence manually
- **Reason for rejection:** Adds complexity without solving our main problem (URL state sync). Could be added later for specific use cases without major refactoring.

### Jotai or Recoil (Atomic State)
- **Pros:**
  - Fine-grained reactivity
  - Minimal re-renders
  - Modern patterns
- **Cons:**
  - Different mental model than traditional state
  - Smaller communities
  - Overkill for our use case
- **Reason for rejection:** Unnecessary complexity for our state structure.

### Valtio (Proxy-based State)
- **Pros:**
  - Mutable syntax feels natural
  - Small and fast
  - Simple API
- **Cons:**
  - Magic behavior with proxies
  - Less predictable than immutable approaches
  - Smaller ecosystem
- **Reason for rejection:** Prefer explicit immutable updates for clarity.

**When to Reconsider:**

This decision should be revisited if:

1. **Props Drilling Becomes Painful:** 5+ levels of prop passing for common state
2. **Multiple Consumers:** Many components need access to same global state
3. **Complex State Logic:** State updates become difficult to reason about
4. **Team Scaling:** Multiple developers working on state-heavy features simultaneously
5. **Performance Issues:** Re-renders from lifted state cause slowdowns

**Potential Migration Path:**

If we need global state in the future:

1. **Custom Hooks First:** Extract localStorage logic to hooks (useTheme, useFavorites)
2. **Context for Preferences:** Move theme/announcements to Context API
3. **Zustand if Needed:** Adopt Zustand for truly global state (favorites, user prefs)
4. **Keep URL State:** URL remains source of truth for filters, Zustand handles UI prefs

**Notes:**

- Current architecture keeps state management intentional and visible
- URL state is more valuable than global state for this application (shareability, bookmarkability)
- Most state is either local to a component or derived from URL
- Persistence layer (localStorage) is well-abstracted already
- App.tsx acts as the natural "state container" - acceptable for this application size
