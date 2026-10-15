# ADR-20251015-use-react-lazy-loading

## Status
Accepted

## Context
ExvoRed's React application consists of 10+ page components (ExvotoPage, SemPage, CatalogPage, DivinitiesPage, CharactersPage, MiraclesPage, KeybindsPage, and their corresponding detail pages). Each page component imports domain-specific logic, data fetching, and table rendering. When bundled without code splitting, Vite produces a single JavaScript bundle of approximately 500KB-1MB (before gzip), which takes 2-3 seconds to download and parse on typical academic network connections.

Users primarily work with 1-2 entity types per session (e.g., cataloging exvotos or updating SEMs), meaning most page code is unused during a typical session. The application shell (Layout, Router, navigation) is under 50KB, but loading all page components upfront delays initial render. Modern browsers support HTTP/2 multiplexing, making multiple small file downloads more efficient than one large bundle. React 19 provides built-in code splitting via `React.lazy()` and `Suspense`, eliminating the need for third-party libraries.

## Decision
Use `React.lazy()` to dynamically import all page components at route boundaries. Wrap route components in `<Suspense>` boundaries with loading fallbacks. Configure Vite to automatically split chunks at lazy import points. Each page becomes a separate chunk (e.g., `ExvotoPage-[hash].js`, `SemPage-[hash].js`), downloaded only when the user navigates to that route. The application shell and shared components (DataTable, SearchBar, Modal) remain in the main bundle since they are used across multiple pages.

## Consequences

### Positive
- Faster initial load: Main bundle size reduced from ~800KB to ~150KB; application shell loads in <1 second on typical connections
- On-demand loading: Page components download only when needed; users who never visit the Divinities page never download its code
- Improved caching: Updating one page component invalidates only that chunk, not the entire bundle; browser cache remains valid for unchanged pages
- Automatic code splitting: Vite handles chunk splitting automatically; no manual webpack configuration required
- Better mobile performance: Smaller initial bundle reduces parse time on mobile devices with limited CPU
- Parallel downloads: HTTP/2 allows browser to download multiple chunks simultaneously; no waterfall delay

### Negative
- Navigation delay on first visit: 50-200ms delay when navigating to a new page for the first time while chunk downloads; subsequent visits are instant (cached)
- Increased HTTP requests: 10+ separate JavaScript files instead of 1; without HTTP/2, this could increase latency (but all modern servers support HTTP/2)
- Suspense boundary required: Must wrap all routes in `<Suspense>` with loading fallback; adds component hierarchy complexity
- Debugging complexity: Stack traces may show chunk IDs instead of file names; requires source maps for debugging
- Build output complexity: 10+ chunk files instead of 1 main bundle; deployment scripts must copy all chunks

### Neutral
- Fallback component design: Must design loading fallback UI (spinner, skeleton screen); overly elaborate fallbacks negate performance benefits
- Chunk size optimization: Vite automatically determines chunk boundaries, but manual optimization may be needed if chunks grow too large

## Alternatives Considered

### Alternative 1: Single Bundle (No Code Splitting)
**Rejected because:** Single bundle forces users to download all page components on initial load, even if they only use 1-2 pages. This wastes bandwidth (especially on mobile/academic networks) and delays time-to-interactive. For users on slow connections (common in academic institutions in developing countries), a 800KB bundle could take 10+ seconds to download. Browser parsing time for 800KB of JavaScript is 500-1000ms on average hardware, delaying initial render. Every code change invalidates the entire bundle cache, forcing full re-download even for minor updates.

### Alternative 2: Manual Code Splitting with Webpack
**Rejected because:** Vite provides automatic code splitting at lazy import boundaries without manual configuration. Webpack requires explicit `import()` syntax with magic comments (`/* webpackChunkName: "ExvotoPage" */`) and manual `splitChunks` configuration to optimize bundle sizes. This adds build complexity and maintenance burden. Webpack's hot module replacement (HMR) is slower than Vite's native ESM HMR. Vite's automatic chunk naming based on file names is clearer than Webpack's numeric IDs.

### Alternative 3: Route-Based and Component-Based Splitting
**Rejected because:** Splitting at the component level (e.g., lazy-loading DataTable, Modal) adds excessive complexity with minimal benefit. Shared components like DataTable are used on nearly every page, so they should remain in the main bundle. Lazy-loading these shared components would cause multiple downloads of the same code across pages. This approach increases the number of HTTP requests without improving initial load performance. Debugging becomes extremely difficult when core UI components are asynchronously loaded.

## References
- React.lazy() documentation: https://react.dev/reference/react/lazy
- Vite code splitting: https://vitejs.dev/guide/features.html#code-splitting
- App router setup: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/src/App.tsx`
- Vite configuration: `/home/marcos/Documentos/Programming/JavaScript/ExvoRed/vite.config.ts`
