# ADR-001: Docusaurus-Based Interactive Textbook Platform

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-08
- **Feature:** Physical AI & Humanoid Robotics Textbook
- **Context:** The project requires creating an interactive, mobile-friendly textbook for teaching Physical AI and Humanoid Robotics concepts. The platform must support rich content including text, diagrams, quizzes, code examples, and labs, while being deployable on GitHub Pages and accessible to students with varying technical backgrounds.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- Framework: Docusaurus v3.1.0 (static site generator for documentation)
- Content Format: Markdown with MDX support for interactive elements
- Deployment: GitHub Pages (static hosting)
- Styling: Built-in Docusaurus theme with custom CSS
- Navigation: Auto-generated sidebars with structured content hierarchy
- Interactive Elements: Embedded code examples, quizzes, and links to external tools

## Consequences

### Positive

- Excellent documentation-focused features out of the box
- Built-in mobile responsiveness and accessibility
- Fast loading times for static content
- Strong SEO capabilities
- Integrated search functionality
- Easy content authoring in Markdown
- GitHub integration for version control and deployment
- Active community and plugin ecosystem

### Negative

- Less flexibility for highly custom UI interactions
- Potential performance issues with very large documentation sets
- Learning curve for Docusaurus-specific features
- Dependency on React for custom components
- Limited dynamic functionality compared to full web applications
- Potential build time increases as content grows

## Alternatives Considered

Alternative Stack A: Custom React Application with Next.js
- Framework: Next.js with App Router
- Content: Dynamic content loading from CMS or API
- Deployment: Vercel or other hosting platforms
- Rejected due to increased complexity, longer development time, and unnecessary features for documentation-focused content

Alternative Stack B: Static Site Generator (Jekyll/Hugo)
- Framework: Jekyll or Hugo
- Content: Markdown with templating
- Deployment: GitHub Pages
- Rejected due to less modern tooling, limited interactive capabilities, and smaller ecosystem compared to Docusaurus

Alternative Stack C: Commercial Documentation Platform
- Platform: GitBook, Notion, or similar
- Deployment: Platform-provided hosting
- Rejected due to vendor lock-in, potential costs, and limited customization options

## References

- Feature Spec: specs/1-physical-ai-textbook/spec.md
- Implementation Plan: specs/1-physical-ai-textbook/plan.md
- Related ADRs: None
- Evaluator Evidence: spec.md requirements for interactive, mobile-friendly textbook deployed on GitHub Pages