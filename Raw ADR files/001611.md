# ADR-20251015-client-side-search-with-normalization

## Status
Accepted

## Context
ExvoRed users need to search across exvotos, SEMs, catalogs, and divinities using full-text search. Spanish language content includes accented characters (á, é, í, ó, ú, ñ, ü) that users often do not type when searching (e.g., searching "santuario" should match "santuário"). SQLite's default LIKE operator is accent-sensitive, requiring exact matches. SQLite's FTS5 (Full-Text Search) extension supports accent-insensitive search but requires configuring custom tokenizers and is complex to set up.

The current dataset size is approximately 500-2000 records per entity type, growing to an estimated 5000-10000 records over 2-3 years. Search must work across related tables (e.g., searching exvotos should also match on offering SEM name, conservation SEM name). Users expect instant search results (<100ms) as they type, similar to spreadsheet filtering. The application already loads all entity data into React state for table display, making client-side filtering feasible.

Search results must highlight matched terms in the table, with result counters ("3 of 15 results") and prev/next navigation. The search must be case-insensitive and ignore accents.

## Decision
Implement client-side search with text normalization. Fetch all entity records from the API on page load and store in React state. When users type in the SearchBar, normalize both the search query and all searchable fields using `String.normalize('NFD').replace(/[\u0300-\u036f]/g, '')` to remove diacritical marks. Filter the in-memory dataset based on normalized string matching. For exvoto search, also fetch related SEM names and include them in the searchable text. Use the `highlightText()` utility to wrap matching substrings in `<mark className="bg-yellow-200">` tags for visual highlighting.

## Consequences

### Positive
- Instant results: No network latency; search results appear immediately (<50ms) as users type
- Accent-insensitive: "santuario", "santuário", and "SANTUÁRIO" all match correctly; no user training required
- Cross-table search: Can easily search exvotos by offering SEM name or conservation SEM name by joining data in JavaScript
- Simple implementation: No database configuration, no FTS5 setup, no server-side search indexing
- Highlighting with context: Can show highlighted matches in table cells with surrounding context
- No additional backend logic: API endpoints remain simple CRUD operations without search parameters

### Negative
- Entire dataset loaded to client: All records (500-10000) must be fetched and stored in browser memory; approximately 5-20MB of JSON data
- Does not scale beyond 10000 records: Filtering 50000+ records in JavaScript introduces noticeable lag (500ms+)
- Increased initial page load: Must fetch all entities before displaying table; 200-500ms delay on initial page load for large datasets
- No pagination: All records displayed in table (or filtered); cannot implement server-side pagination without refactoring search
- Memory usage: Keeping all entities in React state consumes 10-50MB of browser memory depending on dataset size
- Limited search operators: No support for boolean operators (AND, OR, NOT), phrase matching, or fuzzy search

### Neutral
- Migration path exists: If dataset grows beyond 10000 records, can migrate to server-side search with SQLite FTS5 or PostgreSQL full-text search without changing frontend API
- Performance acceptable for target use case: Academic research teams working with 5000-10000 records see no performance issues

## Alternatives Considered

### Alternative 1: SQLite FTS5 Full-Text Search
**Rejected because:** SQLite FTS5 requires creating separate full-text search tables, configuring custom tokenizers for accent-insensitive search (non-trivial in SQLite), and rebuilding indexes whenever data changes. FTS5 adds complexity to migrations (must maintain both main table and FTS5 shadow table). Query syntax is more complex (e.g., `MATCH` operator instead of `LIKE`). FTS5 is powerful for 100000+ records but overkill for ExvoRed's 5000-10000 record target. Cross-table search (exvotos with SEM names) requires complex joins or denormalized FTS5 tables.

### Alternative 2: Server-Side Pagination with Search Parameters
**Rejected because:** Server-side pagination adds API complexity (offset/limit parameters, total count queries) and increases network latency (every search keystroke requires an API call). Implementing accent-insensitive search server-side still requires SQLite FTS5 or custom normalization logic in SQL queries (e.g., `LOWER(REPLACE(REPLACE(...)))` for each accent). Highlighting matched terms requires returning match positions from server or re-matching on client. Pagination breaks Excel-like table navigation (users expect to see all records and scroll). For datasets under 10000 records, server-side pagination adds complexity without performance benefit.

### Alternative 3: External Search Engine (Elasticsearch, Meilisearch)
**Rejected because:** External search engines are massive overkill for ExvoRed's use case. Elasticsearch requires a separate Java server, multi-gigabyte memory allocation, and complex cluster management. Meilisearch is lighter but still requires a separate service, API keys, and synchronization logic to keep search index updated with database changes. Both solutions add significant operational complexity (deployment, monitoring, backups) and cost (server resources). Data synchronization introduces consistency issues (database and search index may be out of sync). For 5000-10000 records, the added complexity cannot be justified.

## References
- Text normalization utility: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/src/utils/highlightText.tsx`
- SearchBar component: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/src/components/SearchBar.tsx`
- Unicode normalization: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/normalize
- SQLite FTS5 documentation: https://www.sqlite.org/fts5.html
