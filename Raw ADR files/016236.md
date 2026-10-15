# ADR-006: Frontend State Management

**Status:** Approved
**Date:** 2025-11-15
**Verification Date:** 2025-11-15
**Decision Maker:** Steve

## Context

React frontend needs to manage room state, player list, roll history, connection status, and UI state.

## Decision

Use Zustand for global state management.

## Why Zustand Over Alternatives

| Library       | Pros                 | Cons                      | Verdict        |
| ------------- | -------------------- | ------------------------- | -------------- |
| Context API   | Built-in, simple     | Re-render issues, verbose | ❌ Too basic   |
| Redux Toolkit | Powerful, devtools   | Boilerplate, overkill     | ❌ Too heavy   |
| Zustand       | Minimal, hooks-based | Smaller ecosystem         | ✅ Perfect fit |
| Jotai         | Atomic, elegant      | Less mature               | ❌ Less proven |

## State Structure

```typescript
interface AppState {
  // Connection
  socket: Socket | null;
  connectionStatus: 'connected' | 'reconnecting' | 'disconnected';

  // Room
  roomCode: string | null;
  roomMode: 'open' | 'dm-led';
  currentDC: number | null;
  expiresIn: number | null; // seconds

  // Player
  playerId: string | null;
  playerName: string | null;
  isDM: boolean;
  isRoomCreator: boolean;

  // Players List
  players: Player[];

  // Roll History
  rolls: Roll[];

  // UI State
  showAdvancedRollInput: boolean;
  historyDrawerOpen: boolean;
  presets: RollPreset[];

  // Actions
  setConnectionStatus: (status) => void;
  addRoll: (roll) => void;
  updatePlayer: (playerId, updates) => void;
  // ... other actions
}
```

## Socket.io Integration

```typescript
// Store socket instance in Zustand
const useAppStore = create<AppState>((set) => ({
  socket: null,
  setSocket: (socket) => set({ socket }),

  // Socket event handlers update store
  initSocketListeners: () => {
    const socket = useAppStore.getState().socket;
    socket?.on('roll_result', (roll) => {
      set((state) => ({ rolls: [...state.rolls, roll] }));
    });
  },
}));
```

## Consequences

- **Positive:** Minimal boilerplate, easy to test
- **Positive:** No provider hell, hooks-based
- **Positive:** Works seamlessly with Socket.io
- **Negative:** Less ecosystem than Redux (acceptable)
- **Positive:** Small bundle size (~3KB)
