# ADR-017: Pure State Container Store Pattern

**Date**: 2026-01-10
**Status**: Accepted
**Deciders**: MJRP, Antigravity AI Agent
**Related Sprint**: Sprint 19 (Track B)

## Context
As stores like `playlists.js` and `albumSeries.js` grew, they became "Thick Stores" containing complex business logic, Firestore CRUD, localStorage persistence, and undo/redo history. This made them difficult to maintain, led to high line counts (>400 LOC), and violated the Single Responsibility Principle.

## Decision
We decouple the Store from the Business Logic by converting Stores into **Pure State Containers**:
1.  **Stores** (`public/js/stores/`) only hold the reactive state variables and expose thin setters/getters. They no longer contain logic, API calls, or side effects.
2.  **Services** (`public/js/services/`) encapsulate all logic, computation, Firestore interaction, and persistence.
3.  **Controllers** call Services to perform operations. Services then update the Store's state via its setters.

### Files Refactored
- `public/js/stores/playlists.js` (Pure State, 132 LOC)
- `public/js/stores/albumSeries.js` (Pure State, 108 LOC)
- `public/js/services/PlaylistsService.js` (Logic Orchestrator)
- `public/js/services/SeriesService.js` (Logic Orchestrator)

## Consequences
**Positive**:
-   **Scannability**: Stores are now extremely thin and focused only on data shape.
-   **Logic Centralization**: Business rules are housed in Services, making them easier to debug and test.
-   **Maintainability**: Achieved < 150 LOC for key store files, fulfilling Sprint 19 quality metrics.

**Negative**:
-   **Indirection**: Controllers must now import both a Store (for data) and a Service (for actions).

## Alternatives Considered
1.  **Helper Modules**: (e.g., `PlaylistsHistoryManager.js`) rejected because it splits logic into too many small files; the Service class provides a more cohesive API surface.
2.  **Maintaining Thick Stores**: Rejected as it failed to meet the LOC targets and architectural goals of Sprint 19.

## Notes
This pattern complements **ADR-016 (Service Layer Extraction)** by specifically applying it to Data Stores. Future "thick" stores should follow this split.
