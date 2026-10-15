# ADR-005 Content Structure and Organization

## Status

Accepted

## Context

The Physical AI Book project requires a clear and consistent content structure to facilitate readability, navigation, and adherence to academic standards. The project Constitution mandates a specific division into four modules, each containing three chapters, and an overall research paper format.

## Decision

Content will be organized hierarchically within the Docusaurus `docs/` directory, mirroring the logical structure of the book:

*   A top-level `docs/` directory.
*   Sub-directories for each of the four modules (e.g., `docs/module1`, `docs/module2`).
*   Markdown files for each chapter within their respective module directories (e.g., `docs/module1/chapter1.md`).
*   `_category_.json` files will be used within module directories to define sidebar labels and positions.
*   `sidebars.ts` will explicitly define the order and nesting of modules and chapters in the navigation.

## Consequences

*   **Positive**:
    *   **Clear Hierarchy**: The file system directly reflects the logical structure of the book, making it intuitive for authors and readers.
    *   **Docusaurus Integration**: Aligns perfectly with Docusaurus's documentation plugin conventions for automatic sidebar generation and routing.
    *   **Maintainability**: Easy to locate and manage individual chapters and modules.
    *   **Scalability**: Supports future expansion of chapters or modules if required, while maintaining structure.
    *   **Version Control Friendly**: Content changes are localized to specific Markdown files, simplifying Git operations.
*   **Negative**:
    *   **Initial Setup Overhead**: Requires careful initial setup of directories and `_category_.json` files.
    *   **Strict Adherence**: Deviations from the prescribed module/chapter structure would require significant refactoring.

## Alternatives Considered

*   **Flat Structure (all chapters in one directory)**: Rejected because it would quickly become unmanageable for a book-length project and would not reflect the logical grouping of modules.
*   **Custom Content Types (e.g., using Docusaurus's blog plugin for chapters)**: Rejected because the `docs` plugin is specifically designed for hierarchical, versioned documentation, which better suits a book's structure. The blog plugin is more appropriate for chronological posts.
*   **External Content Management System**: Rejected as per ADR-001 (Database Choice) and ADR-003 (Architecture Choice), favoring a file-based, static approach.