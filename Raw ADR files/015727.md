# ADR-0002: Zustand for State Management

## Status
Accepted

## Date
2024-12-30

## Context

The application needs client-side state management for:
- UI state (modals, sidebars, theme)
- Playground/CPR workflow state (multi-step forms, document data)
- User preferences (persisted settings)

Options considered:
1. **Redux**: Industry standard, but verbose boilerplate
2. **Zustand**: Minimal API, TypeScript-first, small bundle
3. **Jotai**: Atomic state, similar to Recoil
4. **Context API**: Built-in, but causes unnecessary re-renders

## Decision

Adopt Zustand for global client-side state management.

### Implementation

Main store in `src/store/index.ts`:

```typescript
import { create } from 'zustand'
import { persist, devtools } from 'zustand/middleware'

interface PlaygroundStore {
  // Document state
  cprType: CPRType | null
  emitter: EmitterData | null
  commodity: CommodityData | null
  guarantees: Guarantee[]

  // Actions
  setCPRType: (type: CPRType) => void
  setEmitter: (data: EmitterData) => void
  resetPlayground: () => void
}

export const usePlaygroundStore = create<PlaygroundStore>()(
  devtools(
    persist(
      (set) => ({
        cprType: null,
        emitter: null,
        commodity: null,
        guarantees: [],

        setCPRType: (type) => set({ cprType: type }),
        setEmitter: (data) => set({ emitter: data }),
        resetPlayground: () => set({
          cprType: null,
          emitter: null,
          commodity: null,
          guarantees: []
        })
      }),
      { name: 'playground-storage' }
    )
  )
)
```

### Usage Pattern

```typescript
// In components
const { cprType, setCPRType } = usePlaygroundStore()

// Selective subscription (prevents unnecessary re-renders)
const cprType = usePlaygroundStore((state) => state.cprType)
```

## Consequences

### Positive

1. **Minimal Boilerplate**: No action creators, reducers, or providers needed
2. **TypeScript Native**: Excellent type inference out of the box
3. **Small Bundle**: ~1.2KB gzipped vs ~7KB for Redux Toolkit
4. **Flexible Persistence**: Built-in `persist` middleware for localStorage
5. **DevTools Support**: Redux DevTools integration via `devtools` middleware
6. **No Provider Hell**: Direct import, no context wrapping needed
7. **Selective Subscriptions**: Components only re-render when selected state changes

### Negative

1. **Less Ecosystem**: Fewer middleware and plugins compared to Redux
2. **Manual Patterns**: No built-in patterns for async actions (use React Query instead)
3. **Learning Curve**: Different mental model from Redux for experienced Redux users
4. **Testing**: Requires store reset between tests

### Mitigations

- Use React Query for server state (async data fetching)
- Zustand only for UI/client state that doesn't need server sync
- Create test utilities for store reset

## References

- [Zustand Documentation](https://zustand-demo.pmnd.rs/)
- `src/store/index.ts` - Main store implementation
- [Why Zustand over Redux](https://docs.pmnd.rs/zustand/getting-started/comparison)
