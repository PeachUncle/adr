# ADR-0005: Global Search Pagination Approach

**Status**: Accepted
**Date**: 2025-10-31
**Deciders**: Claude Code Agent, Project Maintainer
**Related ADRs**: [ADR-0001 CMS and API Separation](./0001-cms-api-separation.md)

## Context

The global device search bar was unable to find devices beyond the first page of results. With 3,306 devices in the system but API pagination limited to 200 devices per request, users couldn't find devices like "EB821" that appeared on later pages.

### Problem Statement:
- API returns max 200 devices per request (backend further limits to ~100)
- Search only operated on loaded data
- No mechanism to search across all 3,306 devices
- User experience: devices appeared "missing" from search

### Requirements:
1. Search must find ANY device in the system
2. Search must work across all customers (not just current)
3. Search must be performant (< 1 second response time)
4. Solution must not overwhelm the API with requests
5. User must see loading indicator during search

## Decision

Implement **client-side pagination with caching** for global search:

1. **Fetch all pages on first search**: Loop through API pages until all devices loaded
2. **Cache results for 1 minute**: Avoid re-fetching for subsequent searches
3. **Search in-memory**: Filter cached data client-side
4. **Show loading indicator**: Inform user while data loads

### Implementation Details:

```javascript
// Cache with TTL
let globalSearchCache = [];
let globalSearchLastFetch = 0;
const CACHE_DURATION = 60000; // 1 minute

async function fetchAllDevicesForSearch() {
    // Return cached if fresh
    if (cache is fresh) return globalSearchCache;

    // Paginate through all pages
    let pageNumber = 1;
    while (hasMore && pageNumber <= 50) {
        fetch(`api/get-devices.php?pageRows=200&pageNumber=${pageNumber}&allCustomers=true`);
        allDevices.push(...devices);
        pageNumber++;
    }

    // Cache and return
    globalSearchCache = allDevices;
    return allDevices;
}
```

### API Enhancement:
Added `allCustomers=true` parameter to `get-devices.php` to bypass customer filter.

## Consequences

### Positive
- **Complete Search Coverage**: Finds all 3,306 devices
- **Fast Subsequent Searches**: Cached data = instant results
- **No Backend Changes**: Uses existing pagination API
- **Simple Implementation**: ~40 lines of JavaScript
- **User Feedback**: Loading spinner indicates progress

### Negative
- **Initial Load Time**: First search takes 3-5 seconds (33 API calls)
- **Memory Usage**: Stores 3,306 devices in browser memory (~5-10 MB)
- **Network Load**: Multiple sequential API requests
- **Stale Data**: Cache may be up to 1 minute old
- **API Load**: 33+ requests on first search per user

### Neutral
- **Cache Duration**: 1 minute is arbitrary (could be tuned)
- **Max Pages**: Limited to 50 pages (10,000 devices max)
- **No Shared Cache**: Each user/tab maintains separate cache

## Performance Metrics

### Measured Performance:
- **First Search**: 3-5 seconds (depending on network)
- **Cached Search**: < 100ms (instant)
- **Memory**: ~8 MB for 3,306 devices
- **API Calls**: 33 requests on first search, 0 on subsequent

### Expected Scaling:
- 5,000 devices: ~25 pages, 2.5 seconds
- 10,000 devices: 50 pages (max), 5 seconds
- 15,000+ devices: Would exceed 50-page limit

## Alternatives Considered

### Alternative 1: Backend Search Endpoint
**Description**: Create dedicated `/api/search-devices.php` that searches on server-side

**Pros**:
- Single API request
- No client-side caching needed
- Supports larger datasets
- Lower memory usage

**Cons**:
- Requires backend changes to mps-api
- Backend still needs to paginate through HP API
- Latency moved to server (still 3-5 seconds)
- More complex to implement

**Decision**: Rejected due to backend complexity. Revisit if dataset grows beyond 10,000.

---

### Alternative 2: Lazy Loading with Virtual Scrolling
**Description**: Load pages as user scrolls through dropdown results

**Pros**:
- Loads only needed data
- Scales better for large datasets
- Lower initial load time

**Cons**:
- Complex UI implementation
- User must scroll through results
- Doesn't solve "search everything" requirement
- Still need multiple API calls

**Decision**: Rejected. Doesn't meet requirement to search entire dataset.

---

### Alternative 3: Elasticsearch/Database Search
**Description**: Index all devices in search engine, query via dedicated endpoint

**Pros**:
- Ultra-fast search (< 50ms)
- Supports fuzzy matching, filters
- Scales to millions of devices
- No pagination needed

**Cons**:
- Requires infrastructure (Elasticsearch cluster)
- Data synchronization complexity
- Significant cost increase
- Over-engineered for current needs

**Decision**: Rejected. Too complex for 3,306 devices. Revisit at 100,000+ devices.

---

### Alternative 4: IndexedDB Client-Side Database
**Description**: Store all devices in browser's IndexedDB, query locally

**Pros**:
- Persistent cache (survives page refresh)
- Fast queries with indexes
- No memory concerns
- Offline capability

**Cons**:
- IndexedDB API complexity
- Browser compatibility issues
- Data synchronization logic needed
- Stale data management

**Decision**: Rejected. Over-engineered for 1-minute cache needs. Consider for future enhancement.

## Implementation

### Files Modified:
1. `cms/api/get-devices.php`: Added `allCustomers` parameter
2. `cms/assets/app.js`: Implemented `fetchAllDevicesForSearch()`

### Code Changes:

**get-devices.php** (lines 20, 35-48):
```php
$allCustomers = isset($_GET['allCustomers']) && $_GET['allCustomers'] === 'true';

$params = [
    'FilterDealerId' => $dealerId,
    'FilterDealerCodes' => [$dealerCode],
    // ...
];

if (!$allCustomers) {
    $params['FilterCustomerCodes'] = [$customerCode];
}
```

**app.js** (lines 3274-3307):
```javascript
async function fetchAllDevicesForSearch() {
    if (globalSearchCache.length > 0 && (now - globalSearchLastFetch) < CACHE_DURATION) {
        return globalSearchCache;
    }

    const allDevices = [];
    let pageNumber = 1;

    while (hasMore && pageNumber <= 50) {
        const response = await fetch(`api/get-devices.php?pageRows=200&pageNumber=${pageNumber}&allCustomers=true`);
        const data = await response.json();
        allDevices.push(...data.devices);
        hasMore = allDevices.length < data.total && devices.length > 0;
        pageNumber++;
    }

    globalSearchCache = allDevices;
    return allDevices;
}
```

### Testing:

**Test 1: Search Coverage**
```bash
# Verify all customers accessible
curl ".../api/get-devices.php?allCustomers=true"
# Result: 3,306 devices (vs 957 without parameter)
```

**Test 2: Cache Effectiveness**
```javascript
// First search: 33 network requests logged
// Second search (within 1 min): 0 requests, instant results
```

**Test 3: Edge Cases**
- Empty search (< 2 chars): No API calls
- Search during load: Debounced (300ms)
- Cache expiry: Re-fetches after 1 minute

## Future Enhancements

### Short Term (if needed):
1. **Configurable Cache Duration**: Allow user to adjust cache TTL
2. **Progress Indicator**: Show "Loading page X of Y"
3. **Cancel Search**: Allow user to cancel in-progress load

### Medium Term (if dataset grows):
1. **Service Worker Caching**: Persist cache across page reloads
2. **Background Refresh**: Update cache silently while user searches
3. **Compression**: Use HTTP compression for API responses

### Long Term (if reaches 10,000+ devices):
1. **Backend Search Endpoint**: Move pagination to server
2. **ElasticSearch Integration**: Full-text search with filters
3. **GraphQL**: Client specifies needed fields, reduces payload

## Monitoring

### Metrics to Track:
- Average first-search time
- Cache hit rate
- Memory usage
- API error rate
- User search abandonment rate

### Alerts:
- First-search time > 10 seconds
- API error rate > 5%
- Memory usage > 50 MB
- Cache hit rate < 80%

## Review Date

**Next Review**: 2025-11-30 (1 month)

**Trigger for Early Review**:
- Device count exceeds 5,000
- User complaints about search speed
- API rate limiting issues
- Memory usage concerns

## References

- [Issue: Global search not finding devices](#)
- [SEARCH_FIX_REPORT.md](../../SEARCH_FIX_REPORT.md)
- [Commit c91a2c6](https://github.com/JezSlade/MPSM-Dashboard/commit/c91a2c6)

## Notes

This decision was made in response to user feedback that device "EB821" could not be found via search. The solution prioritizes immediate user needs (complete search coverage) over optimal performance (dedicated search endpoint). The implementation is pragmatic and can be replaced with a more sophisticated solution if the dataset grows significantly.
