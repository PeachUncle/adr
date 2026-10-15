# ADR 0001: Docusaurus-based Technical Book Architecture

## Status
Accepted

## Date
2025-12-10

## Context
We need to build a comprehensive technical book on Physical AI and Humanoid Robotics for a 13-week graduate course. The solution must accommodate 40,000-60,000 words of content across 4 modules, support rich technical content including code examples and diagrams, and be deployable on GitHub Pages with full search functionality and SEO optimization.

## Decision
We will use Docusaurus v3.x as the static site generator with the following architectural components:

1. **Technology Stack**:
   - Docusaurus v3.x with React
   - JavaScript/TypeScript with Node.js v18+
   - GitHub Pages for deployment
   - GitHub Actions for CI/CD

2. **Content Structure**:
   - Hierarchical organization by 4 modules and 13+ chapters
   - Metadata-rich Markdown files with standardized frontmatter
   - Supporting documents (glossary.md, notation.md)

3. **Deployment Strategy**:
   - Static site deployment to GitHub Pages
   - GitHub Actions for automated builds and deployment
   - SEO optimization with sitemaps and robots.txt

## Alternatives Considered
1. GitBook: Good for books but lacks modern extensibility and customization options
2. Hugo: Powerful but steeper learning curve for non-web developers, potentially difficult for content creators
3. Sphinx: Excellent for Python projects but limited language support for the diverse technologies in the book
4. Custom React application: More flexibility but significantly more development and maintenance overhead

## Consequences
### Positive
- Leverages mature, well-documented static site generator
- Strong support for technical documentation with syntax highlighting, math rendering, and search
- Responsive design out-of-the-box
- SEO-friendly with built-in sitemap generation
- Easy for content creators to work with Markdown
- Integrates well with GitHub workflow

### Negative
- Requires learning curve for non-web developers
- Limited interactivity compared to custom web application
- Potential performance concerns with large content volume
- Static site limitations for real-time content updates