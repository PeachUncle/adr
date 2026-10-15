# 4. choose-svelte-for-steel-thread-ui

Date: 2025-07-05

## Status

Accepted

## Context

The steel thread implementation for the personal task management app requires a simple, maintainable, and modern UI framework. The requirements include:
- Minimal boilerplate
- Easy learning curve
- Fast setup with TypeScript and Vite
- No backend required (static deployment)
- Good support for code organization and abstraction (e.g., storage module)

## Decision

We will use **Svelte (latest stable, Svelte 5)** with TypeScript and Vite for the steel thread UI implementation.

### Rationale
- **Minimal boilerplate:** Svelte's syntax and compiler approach allow us to write less code for the same functionality compared to other frameworks.
- **Easy learning curve:** Svelte is approachable for new contributors and easy to reason about.
- **Fast setup:** Official Vite template (`svelte-ts`) provides instant TypeScript support and a dev server.
- **No backend required:** Svelte apps can be built and deployed as static files.
- **Good code organization:** Svelte supports modular code and shared abstractions (e.g., a single storage module).
- **Excellent DX:** Fast hot reloads, readable code, and minimal configuration.

Several frameworks were considered:

### Alternatives Considered
- **React (with TypeScript):** Large ecosystem, but introduces more boilerplate and complexity than needed for a small, single-user app.
- **Vue (with TypeScript):** Excellent documentation and flexibility, but slightly more boilerplate and complexity than Svelte for this use case.
- **SolidJS:** Extremely fast and modern, but a smaller ecosystem and less documentation for beginners.
- **Preact:** Very lightweight React alternative, but still inherits React's component patterns and some boilerplate.

## Consequences

- The UI will be implemented in Svelte 5 with TypeScript, using Vite for development and bundling.
- All UI code should follow Svelte idioms and best practices.
- If future requirements demand more complexity or a different architecture, this ADR can be superseded.
