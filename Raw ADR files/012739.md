# ADR 001: Refactor Project Folder Structure

## Status

Accepted

## Context

The current project folder structure is not efficiently organized, leading to confusion among team members, especially with the growing complexity of the application. The components are intermingled with pages, and there isn't a clear distinction between global and page-specific components. This has started to hinder our development speed and makes the onboarding process for new developers more complicated than necessary.

## Decision

We will refactor our project folder structure to:

- Separate global reusable components from page-specific components.
- Create a dedicated layout folder for components that are part of our page layouts but not reused elsewhere.
- Use a `components` subfolder within page folders for components that are only used within that page.

Here's an example of the new structure:

pages/
|-- Home/
|-- Home.tsx
|-- home-title/
| `-- HomeTitle.tsx
    |-- product-carousel/
        |-- ProductCarousel.tsx
        |-- components/
        |   `-- ProductCarouselCard/
| `-- ProductCarouselCard.tsx
        |-- data/
        |   `-- ... (data for carrousel)
|-- test/
| `-- ... (test for carousel)
        `-- types/
`-- ... (types of carousel)

## Consequences

- The refactoring will result in a clear, maintainable structure that separates concerns appropriately.
- All components that are not globally reused will be placed within the specific page folder, making it evident that they are part of that page's unique functionality.
- Global components will reside in the `components` folder at the `src` root, promoting reuse across pages.
- This change will require updating import paths and potentially some adjustments in component scoping.
- There will be a short-term decrease in development speed as the team adapts to the new structure, but we expect an overall increase in productivity once the transition is complete.

We believe this decision will support our scaling efforts and help maintain a clean codebase as our application grows.
