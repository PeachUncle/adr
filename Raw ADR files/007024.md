# ADR 009: Choosing Python & FastAPI for the Backend

- **Date created**: 05/02/2025
- **Driver**: Alex Foxleigh (Foxy)

## Status

![accepted]

## Context

For the backend of `box-tracker`, we needed to choose a technology stack that would allow for rapid development, strong API support, and maintainability.

One of the major motivators for this decision was to learn Python while also evaluating whether it could be a viable alternative for backend development, especially given its strong ecosystem for APIs, data processing, and machine learning.

FastAPI was chosen because:

- It is modern and async-first, making it comparable to Node.js backends in terms of performance.
- It has built-in OpenAPI documentation, making API development smoother.
- It offers strong type safety and works well with tools like Pydantic.
- It integrates well with PostgreSQL, SQLAlchemy, and Alembic.

Given these factors, we evaluated other options before making a final decision.

## Alternatives Considered

### Node.js with Express.js

- Familiarity with Node.js and JavaScript.
- Large ecosystem and community support.
- Requires additional middleware for async validation and documentation.
- Not as type-safe without additional tools (e.g., TypeScript, Zod).

### Node.js with NestJS

- Strong TypeScript support and a well-structured framework.
- Built-in OpenAPI generation like FastAPI.
- Heavier learning curve due to its opinionated architecture.
- More boilerplate compared to FastAPI.

## Decision

After evaluating these options, we decided to go with Python and FastAPI for the backend of `box-tracker`.

This decision was influenced by:

- The opportunity to learn and get comfortable with Python.
- The modern async capabilities of FastAPI.
- The built-in API documentation and validation via Pydantic.
- The strong support for PostgreSQL and SQLAlchemy.
- The need for a backend with long-term maintainability.

## Consequences

- We gain experience with Python and FastAPI, which can be beneficial for future projects.
- API documentation is automatically generated, making development and testing easier.
- We have a strong, type-safe foundation for backend development.
- There is a learning curve associated with Python tooling (Poetry, Alembic, etc.).
- Some existing JavaScript tooling won’t be directly usable, requiring new workflows.

[proposed]: https://img.shields.io/badge/Proposed-yellow?style=for-the-badge
[accepted]: https://img.shields.io/badge/Accepted-green?style=for-the-badge
[superceded]: https://img.shields.io/badge/Superceded-orange?style=for-the-badge
[rejected]: https://img.shields.io/badge/Rejected-red?style=for-the-badge
[deprecated]: https://img.shields.io/badge/Deprecated-grey?style=for-the-badge
