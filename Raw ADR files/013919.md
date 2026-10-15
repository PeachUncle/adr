# ADR-0001: Better Auth Integration Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-25
- **Feature:** 1-rag-chatbot-integration
- **Context:** The project requires user authentication for both end-users and administrators. The specification (`admin_api.yaml`) explicitly defines "AdminAuth" as a security requirement. For the initial MVP, a decision has been made to integrate with a hypothetical "Better Auth" system. This decision needs to establish a clear strategy for how authentication will be handled, considering the balance between security, development effort, and future scalability.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

The authentication approach will integrate with a hypothetical "Better Auth" system using a token-based strategy (e.g., JWT). A dedicated `AuthService` will handle user authentication and token management. For the initial implementation, a mock authentication mechanism will be used within `AuthService` and `get_current_admin_user` dependency.

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

-   Simplifies initial development by abstracting away complex authentication details.
-   Provides a clear interface (`AuthService`) for future integration with a real authentication provider.
-   Enforces a consistent authentication mechanism across API endpoints.
-   Allows for early development of protected API routes.

### Negative

-   "Better Auth" is currently hypothetical, requiring a mock implementation that will need to be replaced.
-   Potential for security vulnerabilities if the mock is not robustly replaced or if the eventual "Better Auth" integration is flawed.
-   Requires careful planning for user management and roles within the "Better Auth" system.

## Alternatives Considered

-   **Custom Authentication System**: Implement a full authentication system from scratch (e.g., user registration, login, session management, password hashing). Rejected because: High development effort and security risks for an MVP.
-   **OAuth2/OIDC with known providers (Google, GitHub)**: Integrate with established OAuth2 providers. Rejected because: Might introduce external dependencies and complexities not immediately needed for the "Better Auth" concept, and "Better Auth" might imply a different internal system.

## References

- Feature Spec: `specs/1-rag-chatbot-integration/spec.md`
- Implementation Plan: `specs/1-rag-chatbot-integration/plan.md`
- Related ADRs: N/A
- Evaluator Evidence: N/A
