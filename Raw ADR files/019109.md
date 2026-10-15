# ADR 002: Use Next.js as the React framework

- **Date created**: 28/06/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

The project specification explicitly mentioned Next.js as a preferential framework for building React applications. Next.js provides several advantages over vanilla React:

- Server-side rendering (SSR) and static site generation (SSG) capabilities
- Built-in routing system
- Automatic code splitting and performance optimisations
- Image optimisation out of the box
- API routes for backend functionality
- Strong TypeScript support
- Excellent developer experience with hot reloading and error reporting

Given that this application may need to scale and considering the benefits of a production-ready framework, Next.js is an appropriate choice.

## Discussions

- Alex Foxleigh - Next.js was specified as preferential in the project requirements, which aligns well with modern web
development best practices. The framework provides excellent performance optimisations and developer experience that would
benefit both the initial development and future scaling.

## Decision

Use Next.js as the React framework for this project.

## Consequences

**Positive:**

- Built-in performance optimisations and SEO benefits through SSR/SSG
- Strong ecosystem and community support
- Excellent developer experience with hot reloading and error reporting
- Future-proofed for scaling with features like API routes and middleware
- Automatic code splitting reduces bundle sizes

**Negative:**

- Slightly higher learning curve for developers unfamiliar with Next.js concepts
- Some additional complexity compared to vanilla React for very simple applications
- Framework lock-in, though migration paths exist

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge 