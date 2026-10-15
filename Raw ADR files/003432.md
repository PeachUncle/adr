# ADR-0004: State Management Strategy

## Status
Accepted

## Context
We need to manage different types of state in the application:
- Global UI state (auth, theme, notifications)
- Server state (API responses, caching)
- Form state (user inputs, validation)
- Local component state (UI toggles, selections)

## Decision
We will use a multi-strategy approach for state management:

### 1. Context API for Global UI State
- **Auth State**: `AuthContext` - user authentication, login/logout
- **Theme State**: `ThemeContext` - light/dark/system theme
- **Notifications**: `NotificationContext` - toast notifications

### 2. TanStack Query (React Query) for Server State
- API calls and caching
- Synchronization with server
- Background refetching
- Optimistic updates
- tRPC integration

### 3. React Hook Form for Form State
- Form inputs and validation
- Error handling
- Zod schema validation (from shared package)
- Performance optimization (uncontrolled components)

### 4. useState/useReducer for Local Component State
- UI toggles (modals, dropdowns)
- Temporary selections
- Component-specific state

### 5. localStorage for Persistence
- Theme preferences
- Auth tokens
- Chat history
- User preferences

## Rationale

### Context API
- Simple and built-in
- Sufficient for global UI state
- No additional dependencies
- Easy to understand and maintain

### TanStack Query
- Excellent for server state management
- Built-in caching and synchronization
- Reduces boilerplate code
- Works seamlessly with tRPC

### React Hook Form
- High performance (uncontrolled components)
- Minimal re-renders
- Excellent TypeScript support
- Integrates well with Zod validation

### localStorage
- Simple persistence for user preferences
- No backend required
- Fast and reliable
- Works offline

## Consequences

### Positive
- Right tool for each job
- Minimal dependencies
- Easy to understand and maintain
- Good performance characteristics
- Type-safe throughout

### Negative
- Multiple state management approaches to learn
- Need to understand when to use which approach
- Some duplication (Context API boilerplate)

## Alternatives Considered

1. **Redux**: Rejected - overkill for this application
2. **Zustand**: Considered but rejected - Context API sufficient
3. **SWR**: Considered but TanStack Query chosen for better tRPC integration
4. **Controlled forms**: Rejected - React Hook Form provides better performance

## Migration Path

If we outgrow this approach:
1. Context API → Consider Zustand or Jotai
2. TanStack Query → Already industry standard
3. React Hook Form → Already optimal for forms
4. localStorage → Can migrate to IndexedDB or backend storage

