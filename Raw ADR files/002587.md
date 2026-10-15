# ADR-018: Fine-Grained Service Modularization

**Date**: 2026-01-10
**Status**: Proposed
**Deciders**: MJRP, Antigravity AI Agent
**Related Sprint**: Sprint 19 (Track C)

## Context
Sprint 19 Track B successfully extracted business logic from stores into `PlaylistsService` and `SeriesService`. However, `PlaylistsService` (360 LOC) is already accumulating disparate responsibilities (Undo/Redo, Track Ops, Stats, Persistence, Mode Management). To prevent these from becoming "God Services," we need a pattern for further decomposition.

## Decision
We adopt the **Fine-Grained Service** pattern:
1.  **Orchestrator Services**: High-level services (like the current `PlaylistsService`) act as facades or orchestrators.
2.  **Specialized Sub-Services**: Complex logic blocks are moved to focused sub-services.
3.  **Horizontal Sharing**: Logic used by multiple services (e.g., Persistence/LocalStorage) is extracted into a shared infrastructure service.

### Target Refactoring for Track C
-   **`PlaylistHistoryService`**: Extract undo/redo versioning logic from `PlaylistsService`.
-   **`StorageService`**: Create a unified wrapper for `localStorage` side-effects.
-   **`UserMigrationService`**: Extract guest-to-user sync logic from `SeriesService`.

## Consequences
**Positive**:
-   **Granular Testing**: Each sub-service can be unit-tested for a single domain of responsibility.
-   **Boilerplate Reduction**: Shared services (Storage) remove redundant try-catch blocks across multiple services.
-   **Scannability**: Orchestrators return to < 200 LOC.

**Negative**:
-   **Dependency Depth**: Increased complexity in the dependency graph (Orchestrator -> Sub-Service).

## Alternatives Considered
1.  **Mixin Pattern**: Rejected as it makes the "this" context confusing in Vanilla JS.
2.  **Keeping Monolithic Services**: Rejected as it eventually recreates the "God File" problem at the service layer.

## Notes
The naming convention should reflect specialization: `[Domain][Responsibility]Service` (e.g., `PlaylistHistoryService`).
