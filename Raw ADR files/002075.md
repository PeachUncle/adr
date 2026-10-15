# ADR-0001: Better Auth with MCP Server Integration

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-13
- **Feature:** Better Auth Implementation

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

- Authentication Framework: Better Auth for Python backend
- Database Integration: Neon DB with MCP server connection
- Configuration: Environment variables from .env file
- Architecture: Dedicated better_auth.py module for auth logic

<!-- For technology stacks, list all components:
     - Framework: Next.js 14 (App Router)
     - Styling: Tailwind CSS v3
     - Deployment: Vercel
     - State Management: React Context (start simple)
-->

## Consequences

### Positive

- Secure authentication with industry-standard practices
- Centralized database management through MCP servers
- Clean separation of authentication concerns in dedicated module
- Proper environment configuration management

### Negative

- Dependency on Better Auth framework and its ecosystem
- Additional complexity with MCP server integration
- Potential vendor lock-in to Neon DB and MCP infrastructure

## Alternatives Considered

- Custom authentication implementation: More development time and security risks
- Other auth libraries: May not have MCP server integration or Python compatibility
- Direct database connections: Would violate MCP server requirement
- Hardcoded configuration: Would create security vulnerabilities

<!-- Group alternatives by cluster:
     Alternative Stack A: Remix + styled-components + Cloudflare
     Alternative Stack B: Vite + vanilla CSS + AWS Amplify
     Why rejected: Less integrated, more setup complexity
-->

## References

- Feature Spec: specs/001-better-auth-impl/spec.md
- Implementation Plan: specs/001-better-auth-impl/plan.md
- Related ADRs: None
- Evaluator Evidence: specs/001-better-auth-impl/research.md <!-- link to eval notes/PHR showing graders and outcomes -->