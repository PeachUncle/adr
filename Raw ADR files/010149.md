# ADR 003: Use localStorage for Persistence

## Status
Accepted

## Context
We needed a simple persistence mechanism for storing todos, application state, and user preferences without requiring a backend server.

## Decision
We will use the browser's localStorage API for all data persistence, accessed through a `StorageService` abstraction.

## Rationale
- **Zero dependencies**: Built into all modern browsers
- **Synchronous API**: Simple read/write without async complexity
- **Sufficient capacity**: 5-10MB storage per origin
- **User privacy**: Data stays on user's device, no server needed
- **Perfect for MVP**: Todo app doesn't need cloud sync or collaboration
- **Fast access**: Reading/writing is instant

## Implementation
Created `StorageService` class with:
- `save(key, value)`: Stores any JSON-serializable data
- `load(key, defaultValue)`: Retrieves data with fallback
- `remove(key)`: Deletes specific key
- `clear()`: Removes all app data
- Error handling for storage quota and parse errors
- Namespace prefix (`'todoApp_'`) to avoid conflicts

## What We Store
- `todos`: Array of all todo items
- `nextId`: Auto-increment ID counter
- `filter`: Current filter selection (all/active/completed)
- `darkMode`: Theme preference (true/false)

## Consequences

### Positive
- No backend required, works offline by default
- Instant load times (no network requests)
- Simple implementation with full test coverage (17 tests)
- User data persists across browser sessions
- Easy to clear/debug via DevTools

### Negative
- Data tied to single device/browser
- No cross-device sync
- 5-10MB storage limit (sufficient for ~50,000 todos)
- Can be cleared by user/browser
- Synchronous API can block UI for very large datasets

## Alternatives Considered
- **IndexedDB**: More complex API, overkill for simple key-value storage
- **sessionStorage**: Data lost on tab close, not suitable for todos
- **Backend API**: Requires server infrastructure, authentication, networking
- **Service Worker + Cache API**: Overcomplicated for this use case
