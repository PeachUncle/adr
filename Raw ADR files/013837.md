# ADR-0001: Frontend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-04
- **Feature:** 002-fullstack-todo-app
- **Context:** The project requires a modern, scalable, and efficient frontend framework for building a multi-user Todo Web Application. The chosen stack must support a component-based architecture, provide a good developer experience, and align with industry best practices. The project constitution mandates the use of Next.js.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   **Framework**: Next.js v16.0.6 (App Router)
-   **Language**: TypeScript
-   **Styling**: Tailwind CSS
-   **Authentication**: Better Auth (for login/signup)
-   **API Client**: Custom client in `/frontend/lib/api.ts`

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

-   Leverages React's component model for reusable UI.
-   Next.js App Router provides advanced routing, data fetching, and server-side capabilities (SSR, RSCs).
-   TypeScript enhances code quality, maintainability, and developer experience with static type checking.
-   Tailwind CSS enables rapid UI development with utility-first styling and ensures consistency.
-   Better Auth simplifies authentication flows (login, signup) with JWT management.
-   Constitution alignment ensures project consistency and compliance.

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

-   Next.js (especially App Router) has a learning curve for developers new to the framework or its newer paradigms.
-   Tailwind CSS requires a build step and can lead to verbose class names if not managed with tools like `clsx` or component abstractions.
-   Potential for vendor lock-in with Better Auth if tightly coupled, though JWT is a standard.
-   Initial setup overhead for a full-stack Next.js project.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

-   **React (standalone)**: Rejected due to requiring manual setup for routing, server-side rendering, and other features that Next.js provides out-of-the-box. Increased development effort for foundational elements.
-   **Vue.js/Angular**: Rejected as they are not mandated by the constitution and would introduce new ecosystems and learning curves, violating the project's established technology stack principles.

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
