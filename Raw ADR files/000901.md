# 004: Browser LocalStorage for User Data Persistence

## Status

Accepted

## Date

2025-12-15

## Context

The application needed to persist user data across sessions for features like reading lists, rating history, and saved recommendations. Several storage approaches were considered:

Alternatives:
1. **Browser LocalStorage** - Client-side storage
   - ✅ No backend required
   - ✅ Instant access
   - ✅ Privacy-friendly (data stays local)
   - ✅ Simple JavaScript API
   - ❌ Limited to single browser/device
   - ❌ No sync across devices

2. **Backend Database (PostgreSQL/SQLite)** - Server storage
   - ✅ Persistent across devices
   - ✅ Centralized data
   - ❌ Requires backend infrastructure
   - ❌ User accounts needed
   - ❌ Privacy concerns
   - ❌ Deployment complexity

3. **File-based storage** - JSON files on disk
   - ✅ Simple for local use
   - ❌ Not web-accessible
   - ❌ Harder to share/deploy

4. **Gradio State only** - In-memory session state
   - ✅ Built-in to Gradio
   - ❌ Lost on page refresh
   - ❌ Not persistent

## Decision

Use **browser LocalStorage** for client-side persistence of user data.

Data stored:
- **Reading List**: Last 20 saved recommendations
- **Ratings**: User feedback on recommendation quality
- **Session History**: In-memory (Gradio State) for current session

Data format:
```javascript
// Reading List
localStorage.setItem('readingList', JSON.stringify([
  {
    query: "solarpunk with found family",
    recommendations: "...",
    timestamp: "2025-12-15T12:00:00Z",
    id: 1734264000000
  },
  ...
]))

// Ratings
localStorage.setItem('ratings', JSON.stringify([
  {
    rating: 5,
    query: "hopeful sci-fi",
    timestamp: "2025-12-15T12:00:00Z"
  },
  ...
]))
```

Features:
- Automatic pruning (keep last 20 reading list items)
- Display in sidebar on page load
- Visual feedback on save/rate actions
- No user accounts required

## Consequences

### Positive
- **Zero backend**: No database, no user auth, no hosting costs
- **Privacy**: Data never leaves user's browser
- **Speed**: Instant read/write, no network latency
- **Simplicity**: Just JavaScript, no backend code
- **Deployment**: Works in any environment
- **No accounts**: Frictionless UX, no signup required

### Negative
- **Single device**: Data doesn't sync across browsers/devices
- **Storage limits**: 5-10MB typical limit (not an issue for text)
- **No backup**: User clears cache = data lost
- **Security**: Readable by any script on same origin
- **Sharing**: Can't share reading lists with others

### Neutral
- Users accustomed to local-only data in many apps
- Clear in UI that data is stored locally

### Risks
- **Data loss**: User clears browser data
  - Mitigation: Export feature to save as JSON/PDF
- **Privacy misunderstanding**: Users may think it's synced
  - Mitigation: UI copy clarifies "Your Reading List" (local)
- **Storage overflow**: Very active users hit limits
  - Mitigation: Prune to last 20 items automatically

## Implementation Notes

LocalStorage operations:
```javascript
// Save to reading list
const item = { query, recommendations, timestamp: new Date().toISOString(), id: Date.now() };
let list = JSON.parse(localStorage.getItem('readingList') || '[]');
list.unshift(item);
list = list.slice(0, 20); // Keep last 20
localStorage.setItem('readingList', JSON.stringify(list));

// Load on page init
setTimeout(() => {
  const list = JSON.parse(localStorage.getItem('readingList') || '[]');
  displayReadingList(list);
}, 500);
```

Analytics fallback:
- For overall usage stats, also implemented file-based analytics
- Stored in `~/.book_recommender_analytics.json`
- Separate from user-facing reading list
- Used for developer insights, not user features

Key files:
- `src/book_recommender/ui.py`: JavaScript for LocalStorage operations
- `src/book_recommender/analytics.py`: Separate analytics tracking

## References

- [MDN LocalStorage API](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage)
- [LocalStorage Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API/Using_the_Web_Storage_API)
- [Privacy-First Design](https://www.smashingmagazine.com/2017/07/privacy-by-design-framework/)
