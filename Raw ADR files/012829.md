# ADR-007: State Management

## Status

Accepted

## Context

We need a state management solution for the Vue 3 frontend to handle:

- **Server state**: API data (inquiries, bookings, performers, etc.)
- **UI state**: Current user, sidebar open/closed, modal state
- **Complex workflows**: Inquiry → Booking conversion (Phase 2: possibly XState)

The application is an admin dashboard with typical CRUD operations plus some workflow logic.

## Decision Drivers

- **Simplicity**: Solo developer needs maintainable patterns
- **DX**: Good developer experience with Vue 3 Composition API
- **TypeScript support**: Full type safety
- **Caching**: Avoid unnecessary API calls
- **Vue ecosystem fit**: Native Vue solutions preferred
- **Future complexity**: May need state machines later (Phase 2)

## Options Considered

### Option A: Pinia Colada (Accepted for Phase 1)

**What is it?**

Pinia Colada is a new library by Eduardo (creator of Pinia) that combines:

- Data fetching (like TanStack Query)
- Global state management (like Pinia)
- All in one simple API

**Pros:**

- ✅ **One library** - handles both server state and UI state
- ✅ **Built for Vue** - created by Pinia's author (Eduardo)
- ✅ **Modern API** - clean, intuitive Composition API
- ✅ **Automatic caching** - smart request deduplication
- ✅ **TypeScript-first** - excellent type inference
- ✅ **Lighter than TanStack Query** - less bundle size
- ✅ **Simpler mental model** - fewer concepts to learn

**Cons:**

- ⚠️ **Newer library** - smaller ecosystem than TanStack Query
- ⚠️ **Less documentation** - but growing rapidly

**Example:**

```tsx
import { useQuery, useMutation } from '@pinia/colada'

// Server state - auto-cached, auto-refetched
const {
  data: bookings,
  isLoading,
  error,
} = useQuery({
  key: ['bookings'],
  query: () => api.getBookings(),
})

// Mutations with auto-invalidation
const { mutate: createBooking } = useMutation({
  mutation: (data) => api.createBooking(data),
  onSuccess: () => {
    // Auto-invalidate bookings list
    queryClient.invalidateQueries(['bookings'])
  },
})

// UI state - same store pattern
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = computed(() => user.value !== null)
  return { user, isLoggedIn }
})
```

### Option B: TanStack Query + Pinia

**Pros:**

- ✅ **Battle-tested** - massive adoption, proven at scale
- ✅ **Rich ecosystem** - devtools, plugins, examples
- ✅ **Comprehensive docs** - every edge case covered

**Cons:**

- ❌ **Two libraries** - TanStack Query + Pinia for UI state
- ❌ **More complex** - more concepts (queryClient, hydration, etc.)
- ❌ **Larger bundle** - TanStack Query is heavier
- ❌ **Not Vue-native** - React-first design

### Option C: XState for Everything

**Pros:**

- ✅ **Predictable** - state machines prevent impossible states
- ✅ **Visualization** - can visualize all state transitions
- ✅ **Great for complex workflows** - inquiry → booking flow

**Cons:**

- ❌ **Overkill** - most of the app is simple CRUD
- ❌ **Steep learning curve** - state machines are conceptually complex
- ❌ **Doesn't handle data fetching** - still need something else
- ❌ **More boilerplate** - defining machines for everything is verbose

## Decision

**Phase 1: Use Pinia + Pinia Colada for state management.**

- **Pinia**: Global UI state (auth, sidebar, modals)
- **Pinia Colada**: Server state / data fetching (bookings, inquiries, etc.)

**Phase 2: Add XState only if needed for complex workflows.**

### Rationale

1. **Start simple**: Pinia Colada handles 90% of use cases elegantly
2. **One library**: Simpler to learn and maintain
3. **Vue-native**: Built by Eduardo specifically for Vue 3
4. **Good enough**: Most CRUD operations don't need state machines
5. **Defer complexity**: Add XState only when workflow complexity proves it necessary

### When to Add XState (Phase 2)

Consider XState if:

- Inquiry → Booking conversion has too many edge cases
- Multi-step wizards need robust validation at each step
- State transitions become hard to debug
- Visual state machine diagrams would help team understanding

**Important**: XState is **additive**, not a replacement. You'd use XState for specific complex flows while keeping Pinia Colada for everything else.

### Implementation Plan

**Phase 1 (Now):**

```tsx
// Server state with Pinia Colada
useQuery({ key: ['inquiries'], query: api.getInquiries })
useQuery({ key: ['bookings'], query: api.getBookings })
useMutation({ mutation: api.createInquiry })

// UI state with Pinia
const authStore = useAuthStore() // User session, token
const uiStore = useUIStore() // Sidebar open, modal state
```

**Phase 2 (If Needed):**

```tsx
// Wrap complex flow in XState machine
const inquiryMachine = createMachine({
  initial: 'new',
  states: {
    new: { on: { QUOTE: 'quoted' } },
    quoted: { on: { CONFIRM: 'confirmed', LOSE: 'lost' } },
    confirmed: { on: { CREATE_BOOKING: 'booked' } },
    // ...
  },
})

// Use machine for inquiry conversion flow only
const { state, send } = useMachine(inquiryMachine)
```

## Consequences

### Positive

- Simple, maintainable state management
- One library to learn instead of two (Pinia Colada vs TanStack Query + Pinia)
- Automatic caching reduces unnecessary API calls
- Good TypeScript support throughout
- Smaller bundle size than alternatives
- Can add XState later without refactoring existing code

### Negative

- Newer ecosystem means fewer Stack Overflow answers
- Might need to read source code occasionally
- If we later need XState, will have two state patterns (acceptable)

### Risks

- **Pinia Colada immaturity**: Library could have breaking changes
  - _Mitigation_: Eduardo (creator) is reliable; API is stable; worst case migrate to TanStack Query
- **Workflow complexity**: What if simple state isn't enough?
  - _Mitigation_: Can add XState for specific flows in Phase 2 without rewriting everything

## Follow-up Actions

- [ ] Install Pinia Colada: `pnpm add @pinia/colada`
- [ ] Set up Pinia Colada plugin in main.ts
- [ ] Create query hooks for API endpoints (inquiries, bookings, etc.)
- [ ] Create Pinia stores for UI state (auth, sidebar, modals)
- [ ] Document state management patterns in frontend README
- [ ] Defer XState decision - revisit after Phase 1 MVP
