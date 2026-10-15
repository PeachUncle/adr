# ADR 010: Replace FastAPI/Python with NestJS

- **Date created**: 27/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

Supercedes [ADR 009](./adr-009-fast-api.md)

## Context

Initially, we chose FastAPI and Python for the backend of box-tracker as a learning opportunity, as well as to evaluate whether Python could be a viable alternative for backend development. FastAPI offered strong async capabilities, automatic OpenAPI generation, and seamless integration with PostgreSQL, SQLAlchemy, and Alembic.

However, as development progressed, it became clear that maintaining a mixed TypeScript/Python stack introduced unnecessary friction. Keeping everything within the TypeScript ecosystem provided the following advantages:

- Consistency – The frontend and backend could share types and tooling, reducing complexity.
- Better Developer Experience – No need to context-switch between Python and TypeScript.
- Simplified DevOps – Managing one language across the entire stack reduces dependencies and setup complexity.
- Easier Team Onboarding should it be needed – TypeScript is already the primary language for the project, so keeping the backend in TS made collaboration simpler.

Given these factors, we decided to replace FastAPI with NestJS.

## Alternatives Considered

### Using Next.js API Routes

- Minimal setup, as Next.js includes API routes out of the box.
- Simplifies deployment by keeping frontend and backend together.
- Not ideal for a structured, large-scale API.
- Lacks the modularity and scalability of a standalone backend service.

### Node.js with Express.js

- Familiarity with Node.js and JavaScript.
- Large ecosystem and community support.
- Lightweight and flexible.
- Requires additional middleware for features like validation and OpenAPI documentation.
- Not as opinionated, leading to inconsistent architecture if not well-structured.
- Lacks built-in dependency injection, making scalable service organization harder.

### Node.js with NestJS (Chosen)

- Built-in TypeScript support with a structured and opinionated framework.
- Strong module system for scalability.
- Integrated OpenAPI support similar to FastAPI.
- Dependency injection makes managing services cleaner.
- More boilerplate compared to Express.js.
- Steeper learning curve due to its opinionated structure.

## Decision

After considering the alternatives, we decided to migrate the backend from FastAPI/Python to NestJS for the following reasons:

- Maintaining a single TypeScript stack improves consistency across the project.
- NestJS offers a structured, scalable framework with built-in features similar to FastAPI.
- It aligns better with our DevOps approach, simplifying deployment, dependency management, and developer onboarding.
- Retains strong API documentation support via OpenAPI, reducing the loss of a key FastAPI benefit.
- The need for a backend with long-term maintainability.

## Consequences

- Faster development and better maintainability due to a unified TypeScript stack.
- Some refactoring effort required to migrate from FastAPI to NestJS.
- Improved long-term scalability with NestJS’s modular architecture.
- Easier collaboration as the entire project is in TypeScript, reducing the learning curve for contributors.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
