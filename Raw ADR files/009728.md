# ADR-005: Client State Management

## Status

**Accepted** - 2026-01-01

## Context

The game client needs to manage multiple state domains:
- **Auth state**: Current user, session, guest status
- **Room state**: Players, settings, ready status
- **Game state**: Tiles, turns, scores, actions
- **Chat state**: Messages, reactions
- **Voice state**: Peers, mute status, speaking indicators
- **UI state**: Modals, loading states, errors

State must sync with server in real-time and persist appropriately.

## Decision Drivers

- **Performance**: Avoid unnecessary re-renders
- **Developer Experience**: Simple, intuitive API
- **TypeScript**: Strong typing support
- **React Compatibility**: Works with Server Components
- **Bundle Size**: Minimal overhead
- **Testing**: Easy to test in isolation

## Considered Options

### Option 1: Zustand (Selected)

**Pros**:
- Minimal boilerplate
- Works with React Server Components
- Easy store splitting by domain
- Built-in devtools support
- Small bundle (~1KB)
- TypeScript-first

**Cons**:
- Less structure than Redux
- No built-in async patterns
- Fewer middleware options

### Option 2: Redux Toolkit

**Pros**:
- Well-established patterns
- Rich middleware ecosystem
- DevTools integration
- Built-in async handling (createAsyncThunk)

**Cons**:
- More boilerplate
- Larger bundle
- Steeper learning curve
- Overkill for this scale

### Option 3: Jotai

**Pros**:
- Atomic state model
- Minimal boilerplate
- Good for fine-grained updates

**Cons**:
- Different mental model
- Less suited for complex, interconnected state
- Fewer patterns for large state

### Option 4: React Context + useReducer

**Pros**:
- No external dependencies
- Built into React
- Familiar patterns

**Cons**:
- Re-render issues without memoization
- Boilerplate for multiple contexts
- No devtools

## Decision

**We will use Zustand with domain-separated stores.**

### Store Structure

```
src/stores/
├── auth.ts      # User session, guest status
├── room.ts      # Room state, players, settings
├── game.ts      # Game state, tiles, turns
├── chat.ts      # Messages, reactions
├── voice.ts     # Peer connections, mute states
└── ui.ts        # Modals, loading, errors
```

### Implementation Pattern

```typescript
// src/stores/game.ts
import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';

interface GameState {
  gameId: string | null;
  phase: 'waiting' | 'playing' | 'finished';
  currentTurn: number;
  hand: Tile[];
  opponents: OpponentState[];
  discards: Tile[];
  melds: Meld[];
  score: number;

  // Actions
  setGame: (game: GameData) => void;
  updateFromServer: (delta: GameDelta) => void;
  selectTile: (tileId: string) => void;
  clearSelection: () => void;
}

export const useGameStore = create<GameState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      gameId: null,
      phase: 'waiting',
      currentTurn: 0,
      hand: [],
      opponents: [],
      discards: [],
      melds: [],
      score: 0,

      setGame: (game) => set({
        gameId: game.id,
        phase: game.phase,
        currentTurn: game.currentTurn,
        hand: game.hand,
        opponents: game.opponents,
        discards: game.discards,
        melds: game.melds,
        score: game.score,
      }),

      updateFromServer: (delta) => set((state) => ({
        ...state,
        ...delta,
      })),

      selectTile: (tileId) => set((state) => ({
        hand: state.hand.map(t => ({
          ...t,
          selected: t.id === tileId
        }))
      })),

      clearSelection: () => set((state) => ({
        hand: state.hand.map(t => ({ ...t, selected: false }))
      })),
    })),
    { name: 'game-store' }
  )
);
```

### Selector Pattern

```typescript
// Prevent unnecessary re-renders
const hand = useGameStore((state) => state.hand);
const phase = useGameStore((state) => state.phase);

// Derived selectors
const isMyTurn = useGameStore((state) =>
  state.currentTurn === state.mySeat
);
```

## Rationale

1. **Simplicity**: Zustand's API is minimal. No providers, no boilerplate.

2. **Performance**: `subscribeWithSelector` middleware enables fine-grained subscriptions.

3. **Server Components**: Zustand works outside React context, compatible with Next.js App Router.

4. **Domain Separation**: Multiple stores prevent monolithic state, improve testability.

5. **TypeScript**: First-class TypeScript support with inference.

## Consequences

### Positive
- Clean, readable store code
- Easy testing (stores are just functions)
- Minimal bundle impact
- DevTools for debugging
- Works with SSR/RSC

### Negative
- No enforced patterns (freedom = potential inconsistency)
- Async logic not built-in (use standard promises)
- Less ecosystem than Redux

### Patterns to Follow

| Pattern | Implementation |
|---------|----------------|
| Async actions | `async` functions in store |
| Derived state | Selectors with useMemo if needed |
| Side effects | `subscribeWithSelector` for reactions |
| Persistence | `persist` middleware for local storage |
| Reset | `resetters` pattern for store clearing |

## State Sync with Server

```typescript
// Real-time sync pattern
useEffect(() => {
  const channel = supabase.channel(`room:${roomId}`);

  channel.on('broadcast', { event: 'game_update' }, (payload) => {
    useGameStore.getState().updateFromServer(payload.delta);
  });

  channel.subscribe();

  return () => { channel.unsubscribe(); };
}, [roomId]);
```

## Related Decisions

- ADR-001: Real-time Architecture (state sync source)
- ADR-003: Game Logic Location (server as source of truth)
