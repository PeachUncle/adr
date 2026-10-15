# ADR-1: Textbook Generation and Deployment Stack

- **Status:** Proposed
- **Date:** 2025-12-06
- **Feature:** spec-physical-ai-textbook
- **Context:** The project requires the creation of an interactive, web-based textbook for "Physical AI & Humanoid Robotics". The textbook must be easily maintainable, support rich content like code blocks and diagrams, and be deployable in a straightforward manner for the hackathon. The development process is managed via the Gemini CLI for specifications and planning.

## Decision

We will use Docusaurus as the static site generator for the textbook content and deploy the final site to GitHub Pages.

- **Generation Framework**: Docusaurus
- **Content Format**: Markdown / MDX
- **Deployment Platform**: GitHub Pages

## Consequences

### Positive

- **Excellent DX**: Docusaurus is designed for content-driven sites and provides a great authoring experience with features like live reloading.
- **Rich Content**: MDX support allows for embedding interactive React components directly within markdown, which is ideal for an "AI-native, interactive textbook".
- **Integrated Tooling**: The framework comes with built-in support for theming, search, and versioning.
- **Simplified Deployment**: GitHub Pages offers a free, robust, and tightly integrated hosting solution for the static site, with a well-documented deployment process from Docusaurus.

### Negative

- **Node.js Dependency**: The development and build process requires a Node.js environment, which is an additional dependency for contributors.
- **Structured Content**: All content must conform to the Docusaurus file and directory structure, which adds some rigidity.
- **Frontend Integration**: Integrating the RAG chatbot will require creating custom React components and hooking them into the Docusaurus frontend, which may have a learning curve.

## Alternatives Considered

- **GitBook**:
  - **Pros**: Turnkey solution for creating online books with a polished UI.
  - **Cons**: Less flexible for customization and embedding complex interactive components compared to Docusaurus. Potentially a less open ecosystem.

- **Jupyter Book**:
  - **Pros**: Excellent for projects where the primary content is a series of Jupyter Notebooks. Deep integration with the Python data science ecosystem.
  - **Cons**: The desired output is a more traditional textbook format, not a collection of notebooks. While it can handle markdown, it is more notebook-centric.

- **Custom React/Next.js Site**:
  - **Pros**: Maximum flexibility to design any desired experience.
  - **Cons**: Significant overhead in building out the core functionality of a documentation site (e.g., navigation, search, theming), which Docusaurus provides out of the box. Not a practical approach for a time-constrained hackathon.

## References

- Feature Spec: `../../specs/001-spec-physical-ai-textbook/spec.md`
- Implementation Plan: `../../specs/001-spec-physical-ai-textbook/plan.md`
- Related ADRs: None
- Evaluator Evidence: `../prompts/spec-physical-ai-textbook/2-create-textbook-implementation-plan.plan.prompt.md`