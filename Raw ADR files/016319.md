# Migration from Next.js to Astro with 8-Bit Castle Theme

- Status: accepted
- Date: 2025-01-15

## Context and Problem Statement

The Securing the Realm website was built using Next.js but needed a complete rebuild to:
1. Introduce an interactive 8-bit castle navigation metaphor
2. Improve performance for a content-heavy static site
3. Simplify content management with a better content collections system
4. Reduce JavaScript bundle size and improve lighthouse scores
5. Better align with the site's branding as a fantasy-themed tech education platform

Next.js, while powerful, was overengineered for our primarily static content needs. We needed a framework that excels at static site generation, provides excellent developer experience, and allows us to ship minimal JavaScript to users.

## Decision Drivers

- **Performance**: Target LCP ≤ 2.5s, total JS ≤ 80KB, CLS ≤ 0.1
- **Developer Experience**: Strong TypeScript support, intuitive content management
- **Content-First**: Built-in content collections with schema validation
- **Static Generation**: Excellent static site generation capabilities
- **SEO**: Built-in sitemap, RSS, and metadata management
- **Brand Alignment**: Flexibility to implement custom 8-bit castle UI without fighting framework conventions
- **Build Time**: Fast builds for frequent content updates (daily YouTube feed checks)
- **Maintainability**: Reduced complexity, less boilerplate

## Considered Options

### Option 1: Continue with Next.js

- Description: Keep the existing Next.js setup with static export
- Pros:
  - No migration effort required
  - Familiar to many developers
  - Rich ecosystem
  - Can add server features if needed later
- Cons:
  - Overkill for static content
  - Larger JavaScript bundle
  - More complex data fetching patterns
  - Harder to implement custom themed UI without heavy client-side JS
  - Static export mode doesn't leverage Next.js strengths

### Option 2: Migrate to Astro

- Description: Rebuild the site using Astro with content collections
- Pros:
  - Built for content-heavy static sites
  - Near-zero JavaScript by default
  - Excellent TypeScript support with strict mode
  - Built-in content collections with Zod schema validation
  - Component islands architecture for selective interactivity
  - Fast build times
  - Built-in integrations (MDX, sitemap, image optimization)
  - File-based routing
  - Easy to implement custom themed UI
- Cons:
  - Requires complete rebuild (migration effort)
  - Smaller ecosystem than Next.js
  - Need to learn new framework conventions
  - Less suitable if server-side features needed later

### Option 3: Migrate to Gatsby

- Description: Use Gatsby with GraphQL for content management
- Pros:
  - Mature static site generator
  - Rich plugin ecosystem
  - Good TypeScript support
- Cons:
  - GraphQL layer adds complexity for simple content
  - Slower build times
  - More complex configuration
  - Heavier than needed for our use case
  - Community momentum has shifted to other tools

## Decision Outcome

Chosen option: "Migrate to Astro"

Justification:

- **Perfect Fit for Content**: Astro's content collections provide type-safe content management with Zod schemas, exactly what we need for blog posts, talks, and projects
- **Performance Excellence**: Ships near-zero JavaScript by default, achieving our performance targets easily
- **Developer Experience**: Astro's component syntax is intuitive, TypeScript support is excellent, and file-based routing is straightforward
- **Theme Implementation**: The component islands architecture makes it easy to add interactive castle elements while keeping the rest static
- **Build Speed**: Fast builds support our daily deployment workflow
- **Future-Proof**: Can add interactive islands where needed without rehydrating entire page

The migration effort is justified by:
1. Significant performance improvements
2. Better content authoring experience
3. Easier maintenance going forward
4. Better alignment with site goals (content-focused, fast, fantasy-themed)

## Consequences

### Positive

- **Dramatic Performance Improvement**: Lighthouse scores expected to exceed targets (≥90)
- **Smaller Bundle**: JavaScript reduced from ~200KB to <20KB
- **Faster Builds**: Build times reduced from ~45s to ~20s
- **Type Safety**: Content collections provide compile-time validation of all content
- **Simpler Code**: Less boilerplate, more straightforward patterns
- **Better DX**: Hot module replacement is faster, errors are clearer
- **SEO Benefits**: Built-in sitemap, better metadata management
- **Easier Content Management**: Markdown/MDX with frontmatter is more intuitive than data fetching
- **Flexibility for Theme**: Easy to implement custom castle navigation without framework constraints

### Negative

- **Migration Time**: 2-3 days of development work required
- **Learning Curve**: Team needs to learn Astro conventions
- **Testing Gap**: Need to rebuild test infrastructure (Playwright for E2E)
- **Lost Next.js Features**: No server-side rendering or API routes (not needed currently)
- **Dependency Updates**: Some Next.js-specific libraries need alternatives

### Risks and Mitigations

**Risk**: Breaking changes during migration could cause downtime
- **Mitigation**: Deploy to preview environment first, thorough testing before production

**Risk**: Content might not migrate cleanly
- **Mitigation**: Start with fresh content collections, migrate data programmatically

**Risk**: Team unfamiliar with Astro
- **Mitigation**: Comprehensive documentation (README, CONTRIBUTING, DESIGN), gradual rollout

**Risk**: Missing features discovered during migration
- **Mitigation**: Phased approach, MVP first, iterate on features

**Risk**: SEO impact from URL changes
- **Mitigation**: Maintain same URL structure, set up redirects if needed, keep CNAME

## Links

- Related ADRs: None (first major architectural decision)
- References:
  - [Astro Documentation](https://docs.astro.build)
  - [Astro Content Collections](https://docs.astro.build/en/guides/content-collections/)
  - [Next.js to Astro Migration Guide](https://docs.astro.build/en/guides/migrate-to-astro/from-nextjs/)
  - Issue: Rebuild Securing Quest as an Astro 8-bit Castle Website
- Superseded by: N/A
