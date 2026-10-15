# ADR-001: Frontend Task Board Architecture

## Status
Accepted

## Context

The React/Vite frontend needs to deliver a kanban-style experience that works on desktop and mobile, supports touch-friendly drag-and-drop, and scales to large task lists served through paginated APIs. Previously the board rendered a fixed snapshot of tasks and drag interactions failed on touch devices, leading to poor UX.

Key requirements:

1. **Responsive board** – columns should expand to available width while remaining scrollable on narrow viewports.
2. **Mobile drag-and-drop** – touch users must be able to re-order tasks and move them between columns.
3. **Paginated data** – the UI must gracefully load additional pages when the backend exposes 0-based pagination.
4. **Accessible destructive actions** – deleting a task must be intentional, confirmed, and available from both the board card and the detail modal.

## Decision

1. **@dnd-kit + TouchSensor** for drag interactions on both pointer and touch devices.
2. **Responsive column layout** using flexbox, `min-w` guards, and overflow containers to support horizontal and vertical scrolling.
3. **React Query `useInfiniteQuery`** to request paginated tasks and append them through an infinite scroll sentinel plus a manual "Load more" button.
4. **Shadcn UI dialog primitives** for task deletion confirmation, re-used by the board card and the task detail modal.

## Rationale

- `@dnd-kit` already powers the board; enabling `TouchSensor` avoids rewriting drag logic and keeps accessibility features like keyboard dragging available in the future.
- Allowing columns to flex with `min-w-[280px]` widens the board on larger screens but still gives a first-class experience on mobile.
- `useInfiniteQuery` manages page cursors, caching, and optimistic updates without bespoke pagination state.
- Centralising destructive confirmation in a single dialog ensures consistent messaging, prevents accidental taps, and keeps future design tweaks contained.

## Implementation Notes

- **Sensors**: `useSensors(useSensor(PointerSensor), useSensor(TouchSensor, { delay: 150, tolerance: 8 }))` ensures drag handles can long-press on mobile without triggering taps.
- **Board Layout**: The board container is wrapped in `overflow-x-auto`; columns use `flex-1` with `min-w-[280px]` to prevent overcrowding.
- **Infinite Scroll**: An `IntersectionObserver` watches a sentinel `div` placed after the board; when intersecting, it calls `fetchNextPage()` unless a request is already in flight. A manual "Load more" button falls back for browsers without intersection observers.
- **Task detail modal**: Pulls task data via React Query, exposes edit and delete actions, and surfaces status/priority as modern pill badges.
- **Task cards**: Pass the whole `Task` object to delete handlers so parents can display metadata in the confirmation dialog without extra lookups.
- **Automated tests**: `src/hooks/__tests__/useTaskMutations.test.tsx` covers infinite-query pagination (`fetchNextPage`) and optimistic updates/removals across cached pages, guarding against regressions in the board experience.

## Consequences

- The frontend now depends on `@tanstack/react-query`'s infinite query types; tests and mocks must assert against `InfiniteData` instead of raw arrays.
- Task deletions and updates must update every cached page; the mutation hooks perform optimistic updates across all `tasks` queries.
- The confirmation dialog stack requires scroll-lock awareness; the custom dialog component keeps a global count of open modals so nested dialogs (detail + confirm) do not re-enable page scroll.
