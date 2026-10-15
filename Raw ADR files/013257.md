# ADR 0012: Frontend Structure

## Status

Accepted

## Context

Currently, there are no established guidelines for the structure of the frontend codebase. To ensure consistency, maintainability, and adherence to best practices, a clear structure needs to be defined.

## Decision

The following guidelines will be adopted for the frontend structure:

1. **Source Code Location**
   - All frontend source code will reside in the `src` folder.

2. **Component Design**
   - Components will follow the Single Responsibility Principle (SRP), ensuring each component has a single, well-defined purpose.

3. **UI Components**
   - Components that are solely responsible for rendering design based on the values and functions passed via `Props` will be placed in the `src/ui` folder.

4. **API Management**
   - All API-related logic will be placed in the `src/api` folder.
   - API clients should be designed to be reusable and testable.

5. **Styling**
   - Tailwind CSS will be the primary styling framework for the project.
   - Component-specific styles should be colocated with the component files.

6. **Utility Functions**
   - Reusable utility functions will be placed in the `src/utils` folder.

7. **Testing**
   - Each component or module should have a corresponding test file, named with the `.test.tsx` or `.test.ts` suffix.
   - Test files should be colocated with the components or modules they test, or alternatively, organized under a `src/tests` folder.

8. **Component Catalog with Storybook**
   - Storybook will be used to manage and maintain a catalog of all components.
   - Catalog files for Storybook will be colocated with their respective components in the same folder.
   - This approach will improve maintainability and provide a centralized way to preview and test components.

## Consequences

- Adopting this structure will improve code readability and maintainability.
- Developers will have a clear understanding of where to place and find specific types of components.
- Following SRP will make components easier to test and reuse.
