# Architecture Decisions Log

## 1. Use Vue 3 with TypeScript
* **Status:** Accepted
* **Context:** We need a modern, performant frontend framework with strong typing support for a maintainable codebase.
* **Decision:** Use Vue 3 with the Composition API (`<script setup>`) and TypeScript.
* **Consequences:** 
  * Better type safety and developer experience.
  * Access to modern Vue features and performance improvements.

## 2. Custom State Management via Provide/Inject
* **Status:** Accepted
* **Context:** The application needs global state to manage TV show lists (Drama, Thriller, etc.) across components. The requirement was to avoid external libraries like Pinia.
* **Decision:** Implement a custom store pattern using Vue's native `reactive`, `provide`, and `inject` APIs.
* **Consequences:**
  * Zero external dependencies for state management.
  * Simplified data flow for this specific application scale.
  * Requires manual management of injection keys (`showsStoreKey`).

## 3. Centralized Data Fetching
* **Status:** Accepted
* **Context:** The application interacts with the TVMaze API. We need to handle loading states, errors, and avoid redundant network requests when navigating.
* **Decision:** Create a generic `useGetApi` composable.
* **Consequences:**
  * Consistent handling of `loading` and `error` states across views.
  * Decoupled API logic from UI components.

## 4. CSS-First Styling Strategy
* **Status:** Accepted
* **Context:** The application requires a bespoke, Netflix-like dark theme with specific responsive behaviors.
* **Decision:** Use standard CSS with Vue's Scoped Styles. Layouts utilize CSS Grid and Flexbox.
* **Consequences:**
  * No dependency on heavy CSS frameworks (Tailwind, Bootstrap).
  * Granular control over responsiveness (Desktop, Tablet, Mobile) via custom `@media` queries.
  * "Carousel" behavior implemented with native CSS scroll snapping.

## 5. Search State Synchronization
* **Status:** Accepted
* **Context:** Users expect search results to be shareable and persistent across reloads.
* **Decision:** Synchronize the search input state with the URL query parameters (`?q=...`) using Vue Router.
* **Consequences:**
  * Search results are bookmarkable and shareable.
  * Requires debouncing to prevent excessive history state updates and API calls.

## 6. Testing Strategy
* **Status:** Accepted
* **Context:** To ensure application reliability and prevent regressions, we need a robust testing strategy covering both individual units and end-to-end user flows.
* **Decision:** 
  * Use **Vitest** for Unit Testing: It integrates natively with Vite, offering fast execution and a Jest-compatible API.
  * Use **Playwright** for End-to-End (E2E) Testing: It provides reliable cross-browser testing and powerful debugging tools for user interactions.
* **Consequences:**
  * **Unit Tests**: Cover critical logic in stores, composables, and components (e.g., `useShowsStore`, `useGetApi`, `ShowCard`).
  * **E2E Tests**: Verify critical user journeys (Home page load, Search functionality, Navigation) in a real browser environment.
  * CI/CD pipelines can now enforce quality gates.


