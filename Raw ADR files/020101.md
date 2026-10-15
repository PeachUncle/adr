# ADR 007: URL as Source of Truth for Application State

**Status:** Accepted

**Date:** 2025-10-18

**Context:**

WCAG Explorer is a filtering and search application where users can:
- Search for criteria by text
- Filter by version (2.0, 2.1, 2.2)
- Filter by level (A, AA, AAA)
- Filter by principle and guideline
- Filter by tags
- View favorites
- Navigate between pages of results

These filters create application state that needs to be:
- Shareable (send link to colleague)
- Bookmarkable (save for later reference)
- Navigable (browser back/forward buttons work)
- Persistent (survives page refresh)
- Restorable (deep linking to specific views)

We needed to decide where this state should live:
1. **Component state** (useState) - Lost on refresh
2. **Global state** (Redux, Zustand) - Not shareable via URL
3. **localStorage** - Not shareable, not in address bar
4. **URL parameters** - Shareable, bookmarkable, navigable

**Decision:**

We will use the **URL as the source of truth** for all filter and search state.

Implementation approach:
- Filter state is encoded in URL pathname and query string
- URL is parsed on mount and on navigation
- State changes update the URL via History API
- Browser back/forward naturally work
- URLs are shareable and bookmarkable

**Consequences:**

### Positive

1. **Shareability:**
   - Users can copy URL and send to others
   - Recipients see exact same filters and results
   - No "session state" issues
   - Works across devices and browsers

```
https://wcag-explorer.com/version:2-2/level:a+aa/?q=color
// Everyone who opens this sees WCAG 2.2, Level A+AA, searching "color"
```

2. **Bookmarkability:**
   - Users can bookmark specific views
   - Bookmarks always work (no session dependencies)
   - Can organize bookmarks by filter combinations
   - Professional researchers can save common queries

3. **Browser Navigation:**
   - Back button naturally returns to previous filters
   - Forward button restores filters
   - History works as expected
   - No need to implement custom history

4. **Deep Linking:**
   - Direct links to specific criteria with filters
   - Email links work correctly
   - Social media sharing shows right content
   - Documentation can link to specific views

5. **No State Synchronization:**
   - Single source of truth (URL)
   - No disconnect between URL and state
   - Refresh button always works correctly
   - No stale state issues

6. **Analytics and Debugging:**
   - Can see exact user state in analytics
   - Bug reports include full state in URL
   - Easy to reproduce issues
   - Can analyze common filter patterns

7. **Progressive Enhancement:**
   - App works without JavaScript (initial HTML)
   - Could render server-side with same URLs
   - Stateless server (no session management)
   - CDN-friendly (no cookies or sessions)

8. **Accessibility:**
   - Screen reader users can share links
   - ARIA live announcements match visible state
   - Keyboard navigation works with browser history
   - No hidden state

### Negative

1. **URL Length:**
   - Complex filters create long URLs
   - Multiple tags can make URLs unwieldy
   - URL length limits (2000 chars) could be hit
   - Not aesthetically pleasing

```
/version:2-0+2-1+2-2/level:a+aa+aaa/principle:p+o/tags:1+5+12+18+23/?q=keyboard
// Functional but long
```

2. **URL Encoding Complexity:**
   - Custom encoding scheme needed (dots → dashes)
   - Must handle special characters
   - Need to encode/decode consistently
   - Validation and error handling required

3. **User Experience Friction:**
   - URL changes frequently as users filter
   - History can fill up with similar states
   - Hard to describe "clean" URLs for marketing

4. **State Parsing Overhead:**
   - Must parse URL on every navigation
   - Need to handle malformed URLs gracefully
   - Validation logic for each parameter
   - Default fallbacks for missing values

5. **Limited State Capacity:**
   - Can't store complex objects in URL
   - No nested data structures
   - Must serialize everything to strings
   - Type information lost

6. **Security Considerations:**
   - URL parameters visible in browser history
   - Could be logged by proxies/analytics
   - Sensitive filters exposed
   - (Not an issue for WCAG Explorer - public data)

7. **Complexity of Synchronization:**
   - Need to prevent update loops
   - URL → State → URL requires careful coordination
   - Browser back/forward needs special handling
   - `isUpdatingFromURL` flag needed

```typescript
// Complexity to prevent loops
const isUpdatingFromURL = useRef(false);

useEffect(() => {
  if (isUpdatingFromURL.current) {
    isUpdatingFromURL.current = false;
    return; // Don't update URL when loading from URL
  }
  const newURL = buildURL(filters);
  window.history.pushState({}, '', newURL);
}, [filters]);
```

### Implementation Details

**URL Format:**
```
/[segment]/[segment]/...?query#hash

Segments:
  version:2-2           (WCAG versions, + separated)
  level:a+aa            (Conformance levels)
  principle:p+o+u+r     (Principles: perceivable, operable, etc.)
  guideline:1-2         (Guideline number, dots → dashes)
  tag:1                 (Legacy single tag)
  tags:1+2+3            (Multiple tags)

Query:
  ?q=search+terms       (Search query)

Hash:
  #sc-1-1-1             (Scroll to criterion)

Examples:
  /                                    → Defaults (WCAG 2.2, A+AA)
  /version:2-2/level:aaa/              → WCAG 2.2, Level AAA
  /principle:p/guideline:1-3/?q=alt    → Perceivable, GL 1.3, "alt"
```

**URL Utilities:**
```typescript
// lib/urlUtils.ts

// Parse URL to filters
export function parseURL(pathname: string, search: string): QueryFilters {
  const filters: QueryFilters = {};

  // Parse pathname segments
  const segments = pathname.split('/').filter(Boolean);
  for (const segment of segments) {
    const [key, value] = segment.split(':');
    if (key === 'version') {
      filters.version = value.split('+').map(v => v.replace(/-/g, '.'));
    }
    // ... more parsing logic
  }

  // Parse query string
  const params = new URLSearchParams(search);
  if (params.has('q')) {
    filters.q = params.get('q')!;
  }

  return filters;
}

// Build URL from filters
export function buildURL(filters: QueryFilters, hash?: string): string {
  const segments: string[] = [];

  // Omit defaults to keep URLs clean
  if (!isDefaultVersion(filters.version)) {
    segments.push(`version:${filters.version.join('+')}`);
  }

  // ... more building logic

  const pathname = segments.length > 0 ? `/${segments.join('/')}` : '/';
  const search = filters.q ? `?q=${encodeURIComponent(filters.q)}` : '';
  const hashStr = hash || '';

  return pathname + search + hashStr;
}
```

**Synchronization Pattern:**
```typescript
// App.tsx

// 1. On mount/pathname change → URL to State
useEffect(() => {
  isUpdatingFromURL.current = true;
  const urlFilters = parseURL(window.location.pathname, window.location.search);
  const mergedFilters = mergeWithDefaults(urlFilters);
  setFilters(mergedFilters);
}, [location.pathname]);

// 2. On state change → State to URL
useEffect(() => {
  if (isUpdatingFromURL.current) {
    isUpdatingFromURL.current = false;
    return; // Prevent loop
  }

  const newURL = buildURL(filters, window.location.hash);
  window.history.pushState({}, '', newURL);
  saveFilters(filters); // Also save to localStorage as backup
}, [filters]);

// 3. Browser back/forward
useEffect(() => {
  const handlePopState = () => {
    isUpdatingFromURL.current = true;
    const urlFilters = parseURL(window.location.pathname, window.location.search);
    setFilters(mergeWithDefaults(urlFilters));
  };

  window.addEventListener('popstate', handlePopState);
  return () => window.removeEventListener('popstate', handlePopState);
}, []);
```

**Alternatives Considered:**

### localStorage as Source of Truth
- **Pros:**
  - Persists across sessions
  - No URL length limits
  - Can store complex objects
- **Cons:**
  - Not shareable
  - Not bookmarkable
  - Browser-specific
  - Can't deep link
- **Reason for rejection:** Shareability is critical feature for WCAG Explorer. Professionals need to share filter combinations.

### Query Params Only (No Pathname Segments)
```
/?version=2.2&level=A&level=AA&q=color
```
- **Pros:**
  - Standard approach
  - Easier to parse
  - Libraries like query-string handle it
- **Cons:**
  - Longer URLs
  - Less readable
  - Harder to create "pretty" URLs
- **Reason for rejection:** Pathname segments create cleaner URLs and better semantic meaning.

### Hash-Based Routing
```
/#/version:2-2/level:a+aa
```
- **Pros:**
  - No server configuration needed
  - Client-side routing
- **Cons:**
  - Ugly URLs
  - SEO issues
  - Not standard anymore
  - Hash needed for scroll-to
- **Reason for rejection:** Modern hosting supports pathname routing. Hash routing is legacy.

### State in Session Storage
- **Pros:**
  - Survives refresh
  - No URL clutter
  - Can store complex data
- **Cons:**
  - Not shareable
  - Not bookmarkable
  - Lost when browser closes
  - Tab-specific
- **Reason for rejection:** Same issues as localStorage, plus lost on browser close.

### GraphQL-Style Query in URL
```
/?query={criteria(version:"2.2",level:["A","AA"]){id,title}}
```
- **Pros:**
  - Very expressive
  - Standard with GraphQL
- **Cons:**
  - Extremely long URLs
  - Complex parsing
  - Overkill for our use case
- **Reason for rejection:** Not practical for filter-based UI.

**Best Practices:**

### 1. Keep URLs Human-Readable
```typescript
// Good
/level:a+aa/version:2-2

// Bad
/?l=1&l=2&v=3
```

### 2. Omit Defaults
```typescript
// Default is WCAG 2.2, Level A+AA
/                           // Uses defaults
/version:2-0/               // Only specify when different
```

### 3. Validate and Sanitize
```typescript
export function parseURL(pathname: string): QueryFilters {
  const filters = {};

  // Validate versions
  if (filters.version) {
    filters.version = filters.version.filter(v =>
      ['2.0', '2.1', '2.2'].includes(v)
    );
  }

  // Provide fallbacks
  return mergeWithDefaults(filters);
}
```

### 4. Use History Correctly
```typescript
// Replace state for pagination (don't clutter history)
window.history.replaceState({}, '', newURL);

// Push state for filter changes (allow back navigation)
window.history.pushState({}, '', newURL);
```

### 5. Handle Hash Separately
```typescript
// Hash is for scroll position, not app state
const newURL = buildURL(filters, window.location.hash);
```

**Notes:**

- URL state is complemented by localStorage for preferences (theme, view mode)
- Favorites use localStorage (personal, not shareable)
- URL state is for filters and search (public, shareable)
- This pattern works excellently for filter-heavy applications
- Trade-off: URL complexity vs shareability - we chose shareability
