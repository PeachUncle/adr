# ADR-006 API Standards (N/A for Docusaurus Content Site)

## Status

Accepted (Decision: Not Applicable)

## Context

The Physical AI Book project is focused on generating a static website to present academic content. The architectural decision (ADR-003) to use Docusaurus as a Static Site Generator (SSG) implies that the primary output is a collection of static HTML, CSS, and JavaScript files served directly to the client. This type of architecture typically does not involve exposing an API for content delivery or interaction.

## Decision

The project **will not define or implement any external APIs** for content consumption or interaction. Given the static nature of the Docusaurus site, content is delivered directly via HTTP as pre-rendered HTML. There are no backend services that would expose a programmatic interface.

## Consequences

*   **Positive**:
    *   **Simplicity**: Eliminates the complexity of designing, implementing, securing, and maintaining an API layer.
    *   **Reduced Attack Surface**: No API means no API-related security vulnerabilities.
    *   **Lower Development Cost**: No resources are spent on API development or documentation.
*   **Negative**:
    *   **No Programmatic Content Access**: External applications or services cannot programmatically fetch content from the book site via a structured API. Content can only be accessed by scraping the HTML, which is not a robust method.
    *   **Limited Integration Points**: Difficult to integrate the book's content with other systems that rely on APIs for data exchange.

## Alternatives Considered

*   **Implementing a GraphQL or REST API for content**: Rejected because it would necessitate a backend server and a database, contradicting the core architectural decision to remain static and headless. The complexity and cost would be disproportionate to the project's content delivery goals.
*   **Utilizing Docusaurus's internal client-side search index API**: While Docusaurus can build a client-side search index (e.g., as a JSON file), this is primarily for the site's internal search functionality and not intended as a public API for external consumption. The structure and stability of this internal API are not guaranteed for external use.