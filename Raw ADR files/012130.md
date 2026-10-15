# 3. CMS and Hosting Choice

Date: 2024-03-22

## Status

Proposed

## Context

The current website runs on WordPress, which presents limitations in design control and content management. We need a modern solution that:
- Provides better design flexibility
- Offers a good content editing experience
- Can be hosted on existing Dreamhost infrastructure
- Supports blog posts and testimonials
- Is maintainable long-term by a single developer

## Decision

We propose to:

1. Use Directus as our headless CMS because:
   - User-friendly admin interface
   - Strong visual editing capabilities
   - PostgreSQL support (compatible with Dreamhost)
   - Active development and community
   - Good documentation
   - Open source with no licensing fees

2. Use Next.js as our frontend framework because:
   - Excellent developer experience
   - Built-in static and server-side rendering
   - Strong TypeScript support
   - Large ecosystem and community
   - Great performance optimization features
   - Easy deployment options
   - Built-in API routes for backend functionality
   - Strong SEO capabilities

3. Host on Dreamhost using:
   - Node.js (managed via NVM)
   - PM2 for process management
   - Apache as a reverse proxy
   - PostgreSQL for the database
   - Dreamhost's SSL certificates

4. Implement a static site generation approach:
   - Pre-render pages for performance
   - Use incremental static regeneration for dynamic content
   - Implement preview capabilities for content editing

## Consequences

### Positive:
- Better content management experience
- More design flexibility
- Improved performance through static generation
- Version controlled content
- No licensing costs
- Leverages existing hosting infrastructure
- Modern development experience with Next.js
- Strong TypeScript support for better code quality
- Excellent SEO capabilities out of the box

### Challenges:
- More complex initial setup compared to WordPress
- Requires Node.js configuration on Dreamhost
- Need to implement and maintain the frontend separately
- Need to set up proper backup procedures
- Learning curve for Next.js if team is not familiar
- Need to manage two separate applications (CMS and frontend)

### Migration Considerations:
- Will need to migrate content from WordPress
- Need to set up development and staging environments
- Must document deployment procedures
- Need to establish content modeling in Directus
- Must implement frontend components and layouts

## Next Steps

1. Set up local development environment
2. Create proof of concept with basic content types
3. Document Dreamhost deployment process
4. Plan content migration strategy
5. Set up Next.js project with TypeScript
6. Implement basic frontend components
7. Create content fetching utilities for Directus 