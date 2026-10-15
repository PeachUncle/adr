# ADR-004: Core Frontend Stack: Docusaurus, TypeScript, and Tailwind CSS

- **Status:** Proposed
- **Date:** 2025-11-29
- **Feature:** 001-ai-native-textbook-platform
- **Context:** The project requires a static site generator for a content-heavy textbook platform that is interactive, personalizable, and easy for a content-generation agent to populate. The framework needs to support React components within Markdown for interactivity.

## Decision

The core frontend stack will be:
- **Framework:** Docusaurus v3 (with React) for its strong focus on content-driven websites and MDX support.
- **Language:** TypeScript for type safety and maintainability.
- **Styling:** Tailwind CSS to override the default Infima styles for a more modern and flexible design system.

## Consequences

### Positive

- **Content-Focused:** Docusaurus is purpose-built for documentation and educational content, providing a solid foundation for features like versioning, i18n, and search.
- **Interactive Content:** MDX allows seamlessly embedding interactive React components directly within Markdown files, which is crucial for simulations and personalized content.
- **Performance:** As a static site generator, Docusaurus produces a very fast user experience.
- **Developer Experience:** The ecosystem is mature, and the combination with TypeScript and Tailwind CSS is well-supported.

### Negative

- **Flexibility:** Docusaurus is less flexible than a full-fledged application framework like Next.js. Building complex, non-content-focused pages can be more difficult.
- **Data Fetching:** The data-fetching model is primarily build-time. Integrating real-time data or complex client-side state requires more effort than in frameworks designed for it.
- **Styling Overrides:** Overriding Docusaurus's built-in Infima styles with Tailwind CSS requires careful setup to avoid conflicts.

## Alternatives Considered

- **Next.js:** A more powerful and flexible React framework. It was rejected because its application-centric features (like advanced server-side rendering and routing) are largely unnecessary for this content-focused project, adding needless complexity.
- **Gatsby:** Another popular static site generator. It was rejected because its data layer is heavily reliant on GraphQL, which was deemed an unnecessary dependency and architectural burden for this project's needs.
- **VitePress:** A similar tool from the Vue.js ecosystem. It was rejected because the project and team are standardized on React.

## References

- Feature Spec: `specs/001-ai-native-textbook-platform/spec.md`
- Implementation Plan: `specs/001-ai-native-textbook-platform/plan.md`
- Related ADRs:
  - ADR-001: Client-Side Personalization via React Context
  - ADR-002: Better-Auth Client Integration in Docusaurus Theme Wrapper
  - ADR-003: Mermaid.js Integration via Docusaurus Theme Plugin
- Evaluator Evidence: Not available.
