# ADR-001: Use Next.js App Router

## Status

Accepted

## Context

We need to choose a web application framework that provides:

- Server-side rendering capabilities for SEO and performance
- Type safety with TypeScript support
- Excellent developer experience
- Built-in API route handling for serverless deployment
- Strong community support and ecosystem
- Production-ready with optimization features

The main options considered were:

1. Next.js with App Router (React-based)
2. Remix (React-based)
3. SvelteKit (Svelte-based)
4. Nuxt 3 (Vue-based)

## Decision

We will use Next.js 15.4.5 with the App Router paradigm as our primary web framework.

Key factors in this decision:

- **App Router Benefits**: The new App Router provides improved performance through React Server Components, nested layouts, and enhanced data fetching patterns
- **Vercel Integration**: Seamless deployment to Vercel's edge network with automatic optimizations
- **TypeScript First**: Excellent TypeScript support with automatic type inference for routes and API endpoints
- **Ecosystem**: Largest ecosystem in the React space with extensive third-party library support
- **Serverless Ready**: API routes deploy as serverless functions by default, aligning with our architecture goals
- **Streaming SSR**: Support for streaming server-side rendering improves perceived performance

## Consequences

### Positive

- **Performance**: React Server Components reduce JavaScript bundle size by running components on the server
- **Developer Experience**: File-based routing, automatic code splitting, and built-in optimizations
- **SEO Friendly**: Server-side rendering ensures content is crawlable by search engines
- **Type Safety**: Full TypeScript support throughout the stack
- **Future Proof**: Active development by Vercel with regular updates and improvements
- **Community**: Large community means better documentation, tutorials, and third-party solutions

### Negative

- **Learning Curve**: App Router introduces new concepts that differ from Pages Router
- **Vendor Lock-in**: Some features are optimized specifically for Vercel deployment
- **Complexity**: Server Components add complexity to the mental model
- **Breaking Changes**: App Router is relatively new and may have breaking changes

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js App Router Introduction](https://nextjs.org/docs/app)
- Architecture Document: [2-tech-stack.md](../architecture/2-tech-stack.md)
- Related ADR: ADR-002 (Supabase for Backend)
