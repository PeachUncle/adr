# 2. Meta-Framework

Date: 2025-06-07

## Status

Accepted

## Context

Having chosen React as our frontend framework, we need a full-stack framework that can handle both frontend and backend concerns with minimal boilerplate. The goal is to find a solution that simplifies development while teaching modern web standards and learning new skills that are in demand.

## Decision

We will use **React Router v7 in framework mode** with **Vite** as the build tool.

### Alternatives Considered

- **Remix** - Initially preferred but the Remix team now recommends starting new projects with React Router v7
- **Next.js** - Rejected as it's more complex and opinionated than needed for this project
- **Redwood.js** - Rejected as it's less established and has a steeper learning curve
- **Blitz.js** - Rejected as it's less mainstream and has uncertain long-term support
- **Astro** - Rejected as it's more suited for static/content sites rather than full-stack applications

### Notes

Originally considered Remix, but followed the Remix team's official recommendation: "We now recommend starting all new projects with React Router v7." This represents the natural evolution of Remix's approach.

Vite is used as the build tool to access React Router v7's full framework features including SSR, automatic code-splitting, route modules with loaders and actions, and optimized development experience.

## Consequences

**What becomes easier:**
- Learning web fundamentals and standards-based approaches
- Flexible deployment options across different hosting providers
- Minimal configuration and boilerplate
- Transferable skills to other React-based projects
- Access to modern features like data loading, mutations, and nested routing

**What becomes more difficult:**
- Less opinionated than frameworks like Next.js, requiring more decisions
- Smaller ecosystem compared to Next.js
- Fewer built-in optimizations and conventions

**Risks:**
- React Router v7 is relatively new, though it builds on mature React Router foundations
- Smaller community compared to Next.js for troubleshooting
