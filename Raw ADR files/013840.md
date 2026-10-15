# ADR-0004: Authentication and Authorization Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-04
- **Feature:** 002-fullstack-todo-app
- **Context:** The application requires a secure, scalable, and stateless mechanism for user authentication and authorization to protect user data and restrict access to personal tasks. The chosen strategy must integrate with both the Next.js frontend (using Better Auth) and the FastAPI backend. The project constitution mandates JWT-based authentication.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
 If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

-   **Mechanism**: JWT (JSON Web Tokens)
-   **Issuance**: Frontend via Better Auth (on login/registration)
-   **Verification (Backend)**: FastAPI middleware using `python-jose`
-   **Password Hashing**: `bcrypt` via `passlib`
-   **Authorization**: User ID extracted from JWT used to scope all task operations to the authenticated user. Backend API paths will *not* explicitly include `user_id` for task resources.

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple) -->

## Consequences

### Positive

-   **Statelessness**: JWTs eliminate the need for server-side sessions, simplifying scaling and load balancing for the backend.
-   **Scalability**: The stateless nature makes the system highly scalable horizontally.
-   **Security**: JWTs are cryptographically signed, preventing tampering. `bcrypt` provides strong password hashing.
-   **Standard-based**: JWT is a widely adopted open standard.
-   **Clean API**: Inferring `user_id` from JWT results in cleaner, user-agnostic API paths (e.g., `/api/tasks` instead of `/api/users/{user_id}/tasks`).
-   Constitution alignment ensures project consistency and compliance.

<!-- Example: Integrated tooling, excellent DX, fast deploys, strong TypeScript support -->

### Negative

-   **Token Storage**: Secure client-side storage of JWTs (e.g., `localStorage` vs `httpOnly` cookies) requires careful consideration to mitigate XSS/CSRF risks.
-   **Token Revocation**: Stateless nature makes immediate token revocation (e.g., on logout or compromise) more complex, often requiring mechanisms like blocklists or short-lived tokens with refresh tokens.
-   **Payload Size**: Large JWT payloads can increase request sizes, though for this project with only `user_id`, this is not a concern.

<!-- Example: Vendor lock-in to Vercel, framework coupling, learning curve -->

## Alternatives Considered

-   **Session-based Authentication**: Rejected. Requires server-side state, making horizontal scaling more complex and introducing potential single points of failure.
-   **OAuth**: Rejected. Overkill for simple user authentication within a single application. More suited for third-party service authorization.
-   **API Keys**: Rejected. Less secure for user authentication than JWTs, especially for managing individual user access.
-   **Explicit `user_id` in API Path (`/api/users/{user_id}/tasks`)**: Rejected for task-related endpoints. While explicit, it duplicates information available in the JWT, can be less secure if not carefully validated against the authenticated user, and leads to less RESTful, less intuitive API design. The chosen approach leverages the JWT payload for authorization context.

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
