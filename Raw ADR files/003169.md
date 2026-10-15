# ADR-007 Documentation Versioning Strategy

## Status

Proposed

## Context

Academic works, especially in rapidly evolving fields like Physical AI and Humanoid Robotics, often undergo revisions and new editions. The project needs a strategy to manage different versions of the book's content, allowing readers to access historical versions or specific editions. Docusaurus offers built-in support for documentation versioning.

## Decision

The project will adopt **Docusaurus's built-in documentation versioning feature** to manage different editions or major revisions of the Physical AI Book. Initially, the site will serve a single, "current" version. As major revisions occur, new versions will be explicitly created.

## Consequences

*   **Positive**:
    *   **Historical Access**: Users can easily switch between different versions of the book, which is crucial for academic reference.
    *   **Clear Evolution**: Provides a clear roadmap of how the content has evolved over time.
    *   **Simplicity with Docusaurus**: Leveraging an out-of-the-box Docusaurus feature reduces custom development effort and maintenance.
    *   **Parallel Development**: Allows for development on a "next" version while an "old" version remains published.
*   **Negative**:
    *   **Increased Content Management**: Managing multiple versions of content requires discipline and a clear process for version creation and updates.
    *   **Build Complexity**: Each version adds to the overall content, potentially increasing build times and the size of the deployed site.
    *   **Initial Configuration**: Requires careful initial setup in `docusaurus.config.ts` and understanding of the versioning workflow.

## Alternatives Considered

*   **Manual Branching and Deployment**: Rejected due to significant manual overhead. Maintaining separate Git branches for each version and deploying them independently would be complex and error-prone.
*   **External Version Control System (e.g., Gitbook)**: Rejected as Docusaurus provides sufficient built-in versioning capabilities without introducing another external platform.
*   **No Versioning**: Rejected as inconsistent with academic best practices for long-form publications and detrimental to user experience for a continuously evolving topic.