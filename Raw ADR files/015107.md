# ADR-0003: State Management with React Context API

## Status
Accepted

## Context
The Huda Al-Quran application requires managing complex state across multiple components:

- **Audio Player State**: Current verse, playback status, reciter selection, repeat modes
- **Location Data**: GPS coordinates, city information, prayer times calculation
- **User Preferences**: Font size, theme, reciter choices, playback speed
- **Application State**: Loading states, error handling, navigation status

The application needed a state management solution that could:

- Provide global state access across component tree
- Handle complex audio playback logic
- Manage location-based calculations
- Persist user preferences
- Support real-time updates and synchronization

## Decision
We chose React Context API for state management, implementing custom contexts for different domains rather than using external state management libraries.

### Architecture Overview

#### 1. Audio Player Context
```typescript
interface AudioPlayerState {
  isPlaying: boolean;
  currentSurahId: number | null;
  currentVerseId: number | null;
  currentReciterId: string;
  playbackSpeed: number;
  repeatMode: 'none' | 'verse' | 'surah' | 'all';
  position: number;
  duration: number;
  isLoading: boolean;
  currentReciter: Reciter | null;
  isPlayingSurah: boolean;
}
```

#### 2. Location Context
```typescript
interface LocationState {
  coordinates: Coordinates | null;
  city: string | null;
  country: string | null;
  isLoading: boolean;
  error: string | null;
  permissionGranted: boolean;
}
```

#### 3. Provider Structure
```
AudioPlayerProvider
├── LocationProvider
│   └── App Components
└── Global State Management
```

## Rationale

### Why React Context API?

#### 1. **Simplicity and Native Integration**
- Built into React, no additional dependencies
- Seamless integration with React hooks and patterns
- Natural fit for component-based architecture

#### 2. **Performance Considerations**
- Avoids prop drilling without heavy overhead
- Selective re-renders with memoized contexts
- Good performance for moderate state complexity

#### 3. **Development Experience**
- TypeScript integration out of the box
- Easy to debug with React DevTools
- Clear separation of concerns with custom contexts

#### 4. **Scalability for This Use Case**
- Audio state is centralized but bounded
- Location state is independent and simple
- User preferences can be managed separately
- No need for complex state transitions or time travel

### Why Not External Libraries?

#### Redux/Zustand Considerations
- **Overhead**: Additional bundle size and learning curve
- **Complexity**: More boilerplate for simple state needs
- **Tooling**: Requires additional middleware for async operations

#### MobX Considerations
- **Reactivity**: More complex than needed for this application
- **Learning Curve**: Observable patterns add complexity
- **Debugging**: Harder to trace state changes

## Implementation Strategy

### 1. Domain-Specific Contexts
```typescript
// Separate contexts for different concerns
const AudioPlayerContext = createContext<AudioPlayerContextType | undefined>(undefined);
const LocationContext = createContext<LocationContextType | undefined>(undefined);
```

### 2. Custom Hooks for Access
```typescript
export const useAudioPlayer = () => {
  const context = useContext(AudioPlayerContext);
  if (!context) {
    throw new Error('useAudioPlayer must be used within AudioPlayerProvider');
  }
  return context;
};
```

### 3. Optimized Re-renders
```typescript
// Memoized context value to prevent unnecessary re-renders
const value = useMemo(() => ({
  state,
  playVerse,
  playSurahFromVerse,
  togglePlayPause,
  // ... other methods
}), [state, playVerse, playSurahFromVerse, togglePlayPause]);
```

### 4. Persistent State Integration
```typescript
// Integration with storage service for persistence
const loadPreferences = useCallback(async () => {
  const preferences = await StorageService.getPreferences();
  setState(prev => ({ ...prev, ...preferences }));
}, []);
```

## Consequences

### Positive
- **Clean architecture**: Clear separation of state domains
- **Type safety**: Full TypeScript support with proper interfaces
- **Performance**: Optimized re-renders with proper memoization
- **Maintainability**: Easy to understand and modify state logic
- **Testing**: Simple to test with mock contexts

### Negative
- **Context overhead**: Large contexts can cause performance issues if not optimized
- **Provider nesting**: Multiple providers create wrapper hell
- **Debugging complexity**: State flow can be harder to trace than explicit prop passing
- **Memory usage**: Context values kept in memory for component lifecycle

### Neutral
- **Learning curve**: Team needs to understand Context API patterns
- **Boilerplate**: Custom hooks and providers add some boilerplate
- **Tooling**: Less sophisticated dev tools than Redux ecosystem

## Performance Optimizations

### 1. Context Splitting
- Separate contexts for different domains to prevent unnecessary re-renders
- Audio and location contexts are independent

### 2. Memoization
```typescript
// Prevent unnecessary re-renders with useMemo
const contextValue = useMemo(() => ({
  state,
  actions
}), [state, actions]);
```

### 3. Selective Subscriptions
- Components only subscribe to context they need
- Avoid subscribing to entire state object

### 4. Callback Optimization
```typescript
// Stable callbacks with useCallback
const playVerse = useCallback(async (surahId: number, verseId: number) => {
  // Implementation
}, [dependencies]);
```

## Testing Strategy

### 1. Context Testing
```typescript
// Test context providers with custom render function
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <AudioPlayerProvider>
      <LocationProvider>
        {component}
      </LocationProvider>
    </AudioPlayerProvider>
  );
};
```

### 2. Hook Testing
```typescript
// Test custom hooks independently
const { result } = renderHook(() => useAudioPlayer(), {
  wrapper: AudioPlayerProvider
});
```

## Future Considerations

### 1. State Complexity Growth
- Monitor context size and performance
- Consider state splitting if contexts become too large
- Evaluate external libraries if state management becomes complex

### 2. Server State Integration
- Consider React Query or SWR for API state management
- Keep client state in Context, server state in specialized libraries

### 3. Performance Monitoring
- Add performance metrics for context updates
- Monitor re-render patterns and optimize as needed

### 4. Migration Path
- Context API can be gradually migrated to other solutions
- Provider pattern allows easy swapping of implementations

## Alternatives Considered

### 1. Redux Toolkit
- **Pros**: Powerful dev tools, middleware ecosystem, time travel debugging
- **Cons**: More boilerplate, learning curve, overkill for current needs

### 2. Zustand
- **Pros**: Simple API, small bundle size, good performance
- **Cons**: Less structure, potential for state management chaos

### 3. Recoil
- **Pros**: Fine-grained reactivity, atom-based state
- **Cons**: Facebook experimental status, learning curve

### 4. Component State Only
- **Pros**: Simplest approach
- **Cons**: Prop drilling, state duplication, poor scalability

---

*Decision Date: November 2025*  
*Status: Accepted*  
*Next Review: When state complexity significantly increases or performance issues arise*
