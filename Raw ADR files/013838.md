# ADR-0002: Backend Technology Stack & ORM

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-04
- **Feature:** 002-fullstack-todo-app
- **Context:** The project requires a high-performance, asynchronous backend for handling API requests for user authentication and task management. The backend needs a robust ORM solution to interact with a PostgreSQL database, leveraging Python type hints for data validation and consistency. The project constitution mandates the use of FastAPI and SQLModel.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   **Framework**: FastAPI v0.123.5
-   **Language**: Python 3.11+
-   **ORM**: SQLModel
-   **Data Validation**: Pydantic (integrated with FastAPI and SQLModel)
-   **Asynchronous Support**: Achieved through FastAPI's async capabilities and `psycopg` driver.

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

-   FastAPI provides excellent performance, built-in asynchronous support, and automatic OpenAPI documentation.
-   SQLModel, built on SQLAlchemy and Pydantic, offers a type-hinted and consistent approach to defining database models and interacting with the database.
-   Seamless data validation and serialization through Pydantic models across API requests and database operations.
-   Strong Python ecosystem for development and tooling.
-   Constitution alignment ensures project consistency and compliance.

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

-   Learning curve for developers new to FastAPI's asynchronous paradigms or SQLModel's specific features.
-   While production-ready, FastAPI (being in 0.x.x version) may introduce breaking changes in major updates.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

-   **Django**: Rejected due to being a full-featured framework that might be overly opinionated and heavier than necessary for a purely API-driven backend. While powerful, it does not align with the constitution's FastAPI mandate.
-   **Flask**: Rejected due to being a microframework requiring more boilerplate and manual setup for features like routing, validation, and ORM integration, which FastAPI provides out-of-the-box. Does not align with the constitution's FastAPI mandate.
-   **SQLAlchemy (standalone)**: Rejected in favor of SQLModel, which offers a more integrated and Pydantic-driven experience, reducing boilerplate and improving type safety for database models compared to raw SQLAlchemy.

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

-   Feature Spec: `D:\Hackhathon 2\hk\project_2\Phase-II-Todo-Full-Stack-Web-Application\specs\002-fullstack-todo-app\spec.md`
-   Implementation Plan: `D:\Hackhathon 2\hk\project_2\Phase-II-Todo-Full-Stack-Web-Application\specs\002-fullstack-todo-app\plan.md`
-   Research Findings: `D:\Hackhathon 2\hk\project_2\Phase-II-Todo-Full-Stack-Web-Application\specs\002-fullstack-todo-app\research.md`
-   Related ADRs: None
-   Evaluator Evidence: None
