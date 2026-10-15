# ADR: API Design Patterns

> **Warning:** This ADR was migrated from pre-documentation-standards decisions. Do not use as a template for new ADRs. See `TEMPLATE.md` instead.

> Date: 2025-12-02
> Status: **Adopted**

## Context

musix.js needs consistent API patterns across all adapters. These patterns must handle authentication, asynchronous operations, errors, and pagination in a way that is intuitive for TypeScript developers while remaining flexible enough to accommodate different music service APIs.

## Decision Drivers

- TypeScript developer familiarity
- Memory efficiency for large datasets
- Clear error handling patterns
- Flexibility for different service behaviors
- Simple getting-started experience

## Options Considered

### Initial Service
- **Option 1:** Spotify
- **Option 2:** Apple Music
- **Option 3:** YouTube Music

### Authentication Flow
- **Option 1:** Library handles full OAuth flow
- **Option 2:** Accept tokens only

### Async Pattern
- **Option 1:** Promise only
- **Option 2:** AsyncIterator only
- **Option 3:** Observable (RxJS)
- **Option 4:** Promise + AsyncIterator

### Error Handling
- **Option 1:** Custom error classes
- **Option 2:** Result type (Ok/Err)
- **Option 3:** Standard exceptions

### Pagination
- **Option 1:** Cursor-based
- **Option 2:** Offset-based
- **Option 3:** AsyncIterator
- **Option 4:** AsyncIterator + Cursor

## Decisions

| Category | Decision |
|----------|----------|
| Initial Service | **Spotify** |
| Authentication | **Token only** |
| Async Pattern | **Promise + AsyncIterator** |
| Error Handling | **Custom error classes** |
| Pagination | **AsyncIterator + Cursor** |

## Rationale

### Initial Service: Spotify

- Official TypeScript SDK available for reference
- Free tier available for development
- Core features accessible (search, playlists, playback control)
- November 2024 API restrictions (Recommendations, etc.) are documented and understood
- Good baseline for designing the common interface

### Authentication: Token Only

Library accepts access tokens; users handle OAuth externally.

```typescript
const adapter = new SpotifyAdapter({ accessToken: 'xxx' });
```

Benefits:
- Simple to start
- Environment-agnostic (browser, Node, edge)
- Clear separation of concerns
- Users can use existing auth libraries

Future: May add optional auth helpers to reduce user burden.

### Async Pattern: Promise + AsyncIterator

- Single resources → Promise
- Collections → AsyncIterator

```typescript
// Single resource
const track = await adapter.getTrack('id');

// Collection (lazy iteration)
for await (const track of adapter.getPlaylistTracks('id')) {
  console.log(track.name);
}
```

Benefits:
- Intuitive for different use cases
- Memory efficient for large playlists
- No external dependencies (unlike Observable)
- Native language support

### Error Handling: Custom Error Classes

```typescript
try {
  await adapter.getTrack('id');
} catch (error) {
  if (error instanceof NotFoundError) {
    // Handle 404
  } else if (error instanceof RateLimitError) {
    // Handle rate limit
  }
}
```

Benefits:
- Familiar `instanceof` pattern
- IDE autocomplete for error types
- Stack traces preserved
- TypeScript developers expect this pattern

### Pagination: AsyncIterator + Cursor

High-level API uses AsyncIterator for simplicity:

```typescript
for await (const track of adapter.getPlaylistTracks('id')) {
  // Automatically fetches next pages
}
```

Low-level API exposes cursor for fine control:

```typescript
const page = await adapter.getPlaylistTracksPage('id', { cursor: 'abc' });
console.log(page.items, page.nextCursor);
```

Benefits:
- Simple default experience
- Power users can optimize pagination
- Memory efficient
- Handles service-specific pagination internally

## Consequences

**Positive:**
- Familiar patterns for TypeScript developers
- No external dependencies for core functionality
- Flexible enough for different use cases
- Good developer experience

**Negative:**
- Users must handle OAuth themselves initially
- AsyncIterator requires ES2018+ or polyfill

**Risks:**
- Token-only auth may frustrate users wanting turnkey OAuth - Mitigated by documenting recommended auth libraries and potentially adding helpers later

## Related Decisions

- [20251204-package-design.md](./20251204-package-design.md)
