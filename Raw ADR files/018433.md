# Static Site Generators (2025)

ADR Started in September 2025.

Selection of Static Site Generator (SSG) for publishing technical notes.

## General information

Status   | Date       | Author
---------|------------|----------------
Proposed | 2025-09-24 | Bertrand Thomas

## Context

The [`devpro/tech-notes`](https://github.com/devpro/tech-notes) repository contains a collection of technical notes written in Markdown, stored in the `docs` folder.
The goal is to publish these notes as a static website on GitLab Pages, with the following requirements:

- **Minimal impact on existing Markdown**: The solution should require little to no changes to the existing Markdown files to maintain simplicity and avoid rework.
- **Modern and customizable design**: The website should have a professional, visually appealing look that avoids a "generic" feel, with easy customization options for unique styling.
- **Built-in search**: The site must include full-text search to allow users to quickly find content within the notes.
- **Tabbed code blocks**: The solution should support tabbed code blocks for displaying multi-language code snippets (e.g., Python vs. Bash) with syntax highlighting.
- **GitLab Pages compatibility**: The generator must integrate seamlessly with GitLab Pages for automated deployment via a `.gitlab-ci.yml` configuration.

The static site generator (SSG) must balance ease of setup, performance, and maintainability while meeting these requirements.
Several SSGs were evaluated to determine the best fit.

## Decision

We will use **Docusaurus** as the static site generator to publish the tech notes on GitLab Pages.

### Rationale

- **Minimal Markdown Impact**: Docusaurus supports plain Markdown for basic pages, directly using the `docs` folder.
For tabbed code blocks, it uses a simple `<Tabs>` component in MDX, requiring only a one-line import (`import Tabs from '@theme/Tabs';`) in files needing tabs, which is a minor change compared to rewriting Markdown.
- **Modern and Customizable Design**: Docusaurus provides a modern, React-based theme with a polished, professional look that feels distinct from the common Material Design aesthetic (e.g., MkDocs Material).
Customization via `docusaurus.config.js` and CSS allows for unique styling, addressing concerns about repetitive designs.
- **Built-in Search**: Docusaurus includes Algolia DocSearch (configurable for free tier), offering robust, client-side full-text search that is fast and user-friendly.
- **Tabbed Code Blocks**: The `<Tabs>` component supports tabbed code blocks with syntax highlighting (via Prism), allowing clean display of multi-language snippets (e.g., Python vs. Bash).
- **GitLab Pages Compatibility**: Docusaurus generates static HTML/CSS/JS, deployable with a simple `.gitlab-ci.yml` using a Node.js image, ensuring seamless integration with GitLab Pages.
- **Extensibility**: Docusaurus’ React-based ecosystem supports advanced features like versioning, blog integration, and custom components, making it future-proof for evolving tech notes.

## Consequences

### Benefits

- **Modern Design**: The default theme is professional and customizable, avoiding the "same look & feel" issue of other SSGs, with React-based flexibility for unique styling.
- **Robust Features**: Built-in Algolia search, versioning, and tabbed code blocks meet all requirements and support future growth (e.g., adding a blog or tutorials).
- **Active Community**: Docusaurus has a strong community and ecosystem, ensuring long-term support and plugins for additional functionality.
- **GitLab Pages Integration**: Simple CI setup with Node.js ensures fast deployment.

### Trade-offs

- **Minor Markdown Changes**: Using `<Tabs>` requires MDX and a one-line import for files with tabbed code blocks, slightly more intrusive than MkDocs’ zero-touch approach.
- **Build Overhead**: Node.js-based builds are slightly slower than MkDocs or VitePress, though still fast for small-to-medium doc sets.
- **Learning Curve**: Customization requires basic React/CSS knowledge, which is more involved than MkDocs’ YAML/CSS but comparable to VitePress’ Vue-based setup.

## Options Considered

### 1. MkDocs with Material for MkDocs

- **Pros**:
  - Zero changes to Markdown; uses existing `docs` folder as-is.
  - Excellent built-in search (Lunr.js) and tabbed code blocks via fenced Markdown.
  - Fast builds with Python-based tooling.
  - Simple GitLab Pages deployment with a Python image.
- **Cons**:
  - Material Design aesthetic feels "generic" across many sites, requiring CSS overrides for uniqueness.
  - Less modern tooling (no hot-reload) compared to Docusaurus.
- **Why Not Chosen**: The repetitive look & feel was a significant concern, and Docusaurus offers a more modern, extensible design with comparable ease.

### 2. VitePress

- **Pros**:
  - Near-minimal Markdown changes (uses `::: tabs` for code blocks).
  - Fresh, Vue-based default theme with modern aesthetics.
  - Fast builds (Vite-powered) and built-in search.
  - GitLab Pages-compatible with Node.js.
- **Cons**:
  - Smaller ecosystem than Docusaurus, with fewer plugins/themes.
  - Tabs require specific Markdown syntax, slightly more intrusive than MkDocs.
- **Why Not Chosen**: Docusaurus provides a more robust ecosystem (e.g., versioning, blog support) and stronger search (Algolia vs. JS index), making it better for long-term growth.

### 3. Other SSGs (Hugo, Jekyll, Sphinx, etc.)

- **Summary**: Evaluated but rejected due to:
  - Hugo: No native tabs, complex search setup.
  - Jekyll: No built-in tabs/search, Ruby-based complexity.
  - Sphinx: Overkill for Markdown, dated design.
  - All require more Markdown or setup changes than Docusaurus.

## Implementation Notes

- **Setup**: Run `npx create-docusaurus@latest tech-notes classic`, move existing `docs` folder into the generated project, and configure `docusaurus.config.js` to point to `docs`.
- **Tabbed Code Blocks**: Add `import Tabs from '@theme/Tabs'; import TabItem from '@theme/TabItem';` in Markdown files needing tabs, using `<Tabs><TabItem value="python">...</TabItem></Tabs>` syntax.
- **Deployment**: Use a `.gitlab-ci.yml` with Node.js to build and deploy to `build` folder for GitLab Pages.
- **Customization**: Adjust theme via `docusaurus.config.js` and custom CSS to ensure a unique look, leveraging Tailwind CSS if desired.
