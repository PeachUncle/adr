# ADR-003 Architecture Choice: Docusaurus Static Site

## Status

Accepted

## Context

The primary goal of the Physical AI Book project is to disseminate academic content effectively. A key decision involves the underlying architectural pattern for publishing this content. Options include traditional Content Management Systems (CMS), custom web applications, or static site generators. The project emphasizes academic rigor, clear structure, and ease of deployment.

## Decision

The project will adopt a **Static Site Generation (SSG) architecture using Docusaurus**. Docusaurus is specifically designed for building documentation websites, leveraging Markdown for content and React for extensible UI components. The output will be a collection of static HTML, CSS, and JavaScript files.

## Consequences

*   **Positive**:
    *   **Performance**: Generated static sites are extremely fast, offering a superior user experience and better SEO.
    *   **Security**: Minimal attack surface as there are no servers, databases, or dynamic backend components to exploit.
    *   **Scalability**: Static files can be easily cached and served from Content Delivery Networks (CDNs), handling high traffic volumes without complex infrastructure.
    *   **Developer Experience**: Content is written in Markdown/MDX, integrated with Git for version control, simplifying collaboration and content updates.
    *   **Cost-Effectiveness**: Static sites can be hosted for free or at very low cost on platforms like GitHub Pages.
    *   **Tooling**: Docusaurus provides out-of-the-box features tailored for documentation (e.g., versioning, search, internationalization).
*   **Negative**:
    *   **No Dynamic Features**: Limited ability to implement dynamic server-side functionalities (e.g., user authentication, personalized content, comments without third-party integrations).
    *   **Build Time**: Rebuilding the entire site for every content change, which can become slow for extremely large sites (though Docusaurus has optimizations).
    *   **Dependency on Docusaurus**: The project is tightly coupled with the Docusaurus ecosystem and its conventions.

## Alternatives Considered

*   **Traditional CMS (e.g., WordPress, Drupal)**: Rejected due to unnecessary complexity, higher hosting costs, increased security concerns, and over-provisioning for a content-only site. The dynamic capabilities were not required.
*   **Custom Web Application (e.g., React/Next.js with a custom backend)**: Rejected due to significant development effort, higher maintenance, and the need to reinvent documentation-specific features already provided by Docusaurus. Overkill for a content delivery platform.
*   **Other Static Site Generators (e.g., Jekyll, Hugo, Gatsby)**: While viable, Docusaurus was chosen specifically for its strong focus on documentation, active community, and features like versioning, search, and integrated theme system, which align perfectly with the project's requirements.