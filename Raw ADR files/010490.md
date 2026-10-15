# ADR 001: SEO Strategy & Architecture

## Status
Accepted

## Context
LionsMax Restart aims to attract organic traffic from adults 40+ searching for health supplements. The current application is a Single Page Application (SPA) built with React, which presents challenges for SEO indexing by search engines. We need a robust strategy to ensure content is discoverable, indexable, and ranks well.

## Decision
We will implement a client-side SEO strategy enhanced with pre-rendering or static generation capabilities where possible, focusing on:

1.  **Meta Tag Management**: Use `react-helmet-async` to manage document head tags (Title, Description, Canonical, Open Graph, Twitter Cards) dynamically for each route.
2.  **Structured Data**: Implement JSON-LD schemas for `Article` (blog posts) and `Product` (supplements) to enable rich snippets in search results.
3.  **Sitemap Generation**: Use a post-build script to generate `sitemap.xml` based on the static routes and content files (blog posts).
4.  **URL Structure**:
    -   Blog: `/blog/:slug` (e.g., `/blog/best-supplements-for-joint-pain-over-50`)
    -   Product: `/product/:category/:slug`
5.  **Performance**: Core Web Vitals are a ranking factor. We will prioritize LCP (Largest Contentful Paint) and CLS (Cumulative Layout Shift).

## Detailed Implementation

### Meta Tags (React Helmet)
```typescript
<Helmet>
  <title>{title} | LionsMax</title>
  <meta name="description" content={description} />
  <link rel="canonical" href={url} />
  <meta property="og:title" content={title} />
  <meta property="og:type" content={type} />
  {/* ... other tags */}
</Helmet>
```

### Structured Data (JSON-LD)
For Blog Posts:
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "...",
  "image": "...",
  "author": "LionsMax Team",
  "publisher": { ... }
}
```

### Keyword Strategy
Focus on long-tail keywords: "supplements for energy over 50", "joint pain relief for seniors", "best vitamins for 60 year old woman".

## Consequences
-   **Positive**: Improved visibility in search engines, better CTR from rich snippets.
-   **Negative**: SPAs require careful handling for SEO. If client-side rendering proves insufficient for indexing, we may need to migrate to Next.js or use a pre-rendering service, but for now, we stick to Vite + robust meta tags.
