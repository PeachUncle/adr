# ADR-001: Folder Structure

**Created:** 2025-03-10
**Updated:** 2025-03-10

## Status

✅ Accepted || ⚠️ Pending || ‼️ Declined || 🕐 In Progress

## Context

This application will serve as a bare bones example of how a bigger application will be (in some aspects only). The project is a React + TypeScript application. A clear folder structure has been proposed to separate components, pages, hooks, assets, mocks and stories. This structure aims to convey an understanding of how applications can be structured for good organization but doesn't dismiss the possibility of other options existing, as projects need to adapt to their particular needs.

## Decision

Adopt the following folder structure with a standardized layout for each module type:

- **assets**

  - Contains media such as fonts, images, etc. organized by type.

- **components**

  - Contains reusable UI elements (e.g., `Button`) with:
    - Main component file (e.g., `Button.tsx`).
    - Scoped styling (e.g., `Button.css`).
    - Stories files for StoryBook (e.g., `Button.stories.ts`)
    - Testing files (e.g., `Button.test.tsx`)
    - Supporting files if needed: `types.ts`, `constants.ts`, `utils.ts`.

- **hooks:**

  - Custom React hooks (e.g., `useMockFetch`) following a similar pattern:
    - Main hook file, along with `types.ts`, `constants.ts`, `utils.ts`, and tests in `__tests__`.

- **contexts:**

  - There will be no contexts in this application as it's only for an interview process, but if there were:
    - Global state management providers (e.g., `RootContext`, `AuthContext`) with their own component, types, constants, utils, and tests.

- **pages:**

  - Feature views (e.g., `Introduction Page`) with a similar structure to components.
  - Pages may include nested specific sub-components (e.g., `Playground`) as needed.

- **utils:**
  - General-purpose utilities (e.g., analytics, datetime, sort) and shared test helpers, each with its own `__tests__`.

## Consequences

This structure promotes modularity and clarity. It may require additional initial setup, but it will significantly improve maintainability and streamline onboarding for new team members.
