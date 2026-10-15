# ADR-001 Database Choice

## Status

Proposed

## Context

The Physical AI Book project is envisioned as a static website hosted via Docusaurus, primarily for academic content delivery. Traditional dynamic web applications often require a database for content management, user data, or other persistent storage. The nature of a static site for a book implies that content is managed through files (Markdown) rather than a database.

## Decision

The project will **not** utilize a traditional database system for content storage or management. All book content will be stored directly as Markdown or MDX files within the Docusaurus project structure.

## Consequences

*   **Positive**:
    *   **Simplified deployment and hosting (static files can be hosted anywhere, e.g., GitHub Pages).
    *   Reduced operational overhead (no database to manage, patch, or back up).
    *   Improved security profile (no database vulnerabilities to exploit).
    *   Faster content delivery for end-users.
    *   Content version control is seamlessly integrated with Git repository.
*   **Negative**:
    *   No dynamic content generation or user interaction features requiring persistent storage.
    *   Content updates require changes to source files and a site rebuild.
    *   Complex querying or filtering of content beyond Docusaurus's built-in search capabilities is not feasible without external tools.

## Alternatives Considered

*   **Content Management System (CMS) with database backend (e.g., WordPress, Strapi)**: Rejected due to increased complexity, hosting costs, security overhead, and the desire for a lightweight, static solution suitable for a book. The benefits of a dynamic CMS (e.g., user management, rich editing interfaces) were deemed unnecessary for this project's scope.
*   **Headless CMS with API (e.g., Contentful, Sanity)**: Rejected because it introduces an external dependency and API layer that is not required for static content delivery. While offering more structured content management, it adds complexity that goes against the project's preference for a purely static, file-based approach.