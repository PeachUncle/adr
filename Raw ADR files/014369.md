# ADR-001: Framework Choice - Astro

## Status
Accepted

## Context
Clinton's portfolio site currently uses Gatsby with two separate branches (`main` and `main-tw`) to manage engineering and technical writing portfolios. The current setup has several pain points:

- Gatsby complexity for a simple portfolio site
- Branch management overhead
- Performance issues with Gatsby's JavaScript bundle
- Maintenance burden of keeping two branches in sync

Requirements for new framework:
- Netlify deployment support
- High performance (minimal JavaScript)
- Simple content management
- Support for filtering/interactive elements without heavy framework overhead
- Easy migration path from existing JSON data structure

## Decision
We will use **Astro** as the static site generator for the new unified portfolio site.

## Rationale

### Why Astro:
1. **Performance First**: Ships zero JavaScript by default, only adds what's needed
2. **Content Focus**: Designed for content-heavy sites like portfolios
3. **Netlify Native**: First-class support and optimization for Netlify
4. **Framework Agnostic**: Can add React/Vue components only where needed
5. **Modern DX**: Great developer experience with file-based routing
6. **Static by Default**: Perfect for portfolio site requirements

### Alternatives Considered:
- **Next.js**: Overkill for static portfolio, more complex than needed
- **11ty**: More minimal but less modern tooling
- **Nuxt**: Vue-based, unnecessary complexity
- **SvelteKit**: Good option but less mature ecosystem

### Migration Benefits:
- Single codebase instead of branch management
- Significantly better performance
- Simpler build process
- Easier content management
- Better SEO out of the box

## Consequences

### Positive:
- Lighthouse scores will improve significantly
- Simplified deployment and maintenance
- Better developer experience
- Future-proof architecture

### Negative:
- Learning curve for Astro-specific patterns
- Need to rebuild existing React components in Astro
- Migration effort required

### Neutral:
- Will still need JavaScript for filtering functionality
- Content management approach remains similar (JSON-based)