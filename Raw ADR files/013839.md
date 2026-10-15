# ADR-0003: Database System

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-04
- **Feature:** 002-fullstack-todo-app
- **Context:** The project requires a robust, scalable, and managed relational database solution to store user and task data. The database must integrate well with the chosen backend ORM (SQLModel) and support the projected medium scale of 1,000 users and 200 tasks per user. The project constitution mandates the use of Neon Serverless PostgreSQL.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
 If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Neon Serverless PostgreSQL

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

-   Managed service reduces operational overhead for database administration.
-   Serverless capabilities allow for automatic scaling and cost-efficiency (pay-per-use).
-   PostgreSQL is a highly extensible and reliable relational database, well-suited for structured user and task data.
-   Strong support for advanced features like JSON columns, indexing, and transactional integrity.
-   Excellent compatibility with SQLModel and the Python ecosystem.
-   Constitution alignment ensures project consistency and compliance.

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

-   Potential vendor lock-in to Neon for database infrastructure.
-   Serverless nature might introduce latency variations if not properly configured for cold starts, though this is less critical for a medium-scale application.
-   Cost management requires careful monitoring, especially with unpredictable usage patterns in a serverless model.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

-   **MySQL**: Rejected. While popular, PostgreSQL offers more advanced features and is generally preferred for its extensibility and compliance with SQL standards. Also, the constitution specifically mandates PostgreSQL.
-   **SQLite**: Rejected. Not suitable for multi-user, concurrent access, or production deployments requiring scalability and high availability. Primarily designed for embedded use cases.
-   **MongoDB**: Rejected. A NoSQL database, less suitable for the inherently relational structure of users and their tasks. Would require different ORM/ODM choices and does not align with the constitution's mandate for PostgreSQL.

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
