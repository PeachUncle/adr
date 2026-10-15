# ADR 0002 – Data Fetching & Offline-First Strategy

## Status
Accepted

## Context
The challenge requires handling:
- unstable or slow internet connections,
- automatic re-execution of failed requests,
- caching to improve re-visit performance,
- search filtering with debouncing,
- and clear UX feedback on loading or connection issues.

These requirements define not only *which* tool to use, but *how* the data layer should behave.
An offline-first approach is needed, ensuring resilience and smooth user experience even under poor network conditions.

## Decision
Adopt an **offline-first data fetching strategy built around SWR**, leveraging its revalidation model and event-driven behavior.

Key aspects:

### 1. **Stale-While-Revalidate (SWR) as the core strategy**
- Show cached data immediately for responsiveness.
- Revalidate in background to fetch up-to-date data.
- Maintain UI responsiveness even under slow networks.

### 2. **Automatic retry and reconnection behavior**
- Enable `revalidateOnReconnect` to automatically refetch when internet is restored.
- Use `errorRetryCount` and `errorRetryInterval` for controlled retries.

### 3. **Dynamic search queries**
- Use `useSWR` with conditional keys:
  - `null` → skip fetching when the input is empty.
  - `posts?userId=X` → fetch only when stable search input is ready (after debounce).

### 4. **Debouncing outside SWR**
- Debounce input at the component level to avoid unnecessary requests.
- After debounce → update SWR key → revalidate automatically.

### 5. **Slow connection detection**
- Use SWR callbacks:
  - `onLoadingSlow` → show “slow connection” UI message.
  - `onSuccess` or `onError` → remove the warning.

### 6. **Clear UI states**
Explicit UI states will be shown for:
- loading (`isLoading`)
- validating (`isValidating`)
- connection slow
- error and retry events

## Consequences

### Positive
- Predictable, resilient data layer.
- Smooth UX even under unstable network conditions.
- Minimal custom logic thanks to SWR’s built-in revalidation behavior.
- Scalable pattern for additional API endpoints.

### Negative
- Slightly more concepts to learn (stale-while-revalidate, conditional keys).
- SWR abstracts part of the control, so fine-grained manual handling is limited.

## Alternatives Considered
- **Manual fetch + useEffect**: Rejected due to lack of caching, reconnection awareness, and higher code complexity.
- **React Query**: Powerful but unnecessary overhead for the challenge’s scope.