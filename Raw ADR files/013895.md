# ADR-0005: Decouple Backend Deployment

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Amended
- **Date:** 2025-12-07
- **Feature:** RAG Backend - Phase 1 (Server Foundation)
- **Context:**
    *   The initial plan for the RAG Backend (Phase 1) was to deploy a FastAPI application as part of a Vercel monorepo alongside the Docusaurus frontend, using a single `vercel.json` at the project root.
    *   During initial deployment attempts, encountered `vercel.json` parsing issues (`mix-routing-props` error) and persistent difficulties in successfully routing API requests via the root `vercel.json` configuration.
    *   The user's existing setup involves separate Vercel projects being deployed from the `frontend/` and `backend/` subdirectories of this single GitHub repository.

## Decision

*   The FastAPI backend will be developed and maintained within the `backend/` subdirectory of this GitHub repository.
*   The `backend/` subdirectory will be deployed as an independent Vercel project, targeting this subdirectory as its Root Directory on Vercel. This project will contain its own `vercel.json` within the `backend/` subdirectory to configure its Python build and routing.
*   The `frontend/` subdirectory will continue to be deployed as an independent Vercel project, targeting the `frontend/` subdirectory as its Root Directory. It will manage its own `vercel.json` (if needed) for its static build.
*   The Docusaurus frontend will call the separately deployed backend API using its public URL, which will be configured via an environment variable.
*   The `vercel.json` at the *root* of the repository will be removed or simplified to avoid conflicts and ambiguity, as routing will be managed by `vercel.json` files within the respective subdirectories.

## Consequences

### Positive

*   Simplified `vercel.json` configurations for each Vercel project (frontend and backend), reducing deployment complexity.
*   Clearer separation of concerns, enabling independent development and deployment cycles for frontend and backend, while keeping code in a single Git repository.
*   Easier to debug deployment issues for each component.
*   Frontend deployment is unaffected by backend build issues, and vice-versa.

### Negative

*   Requires managing two separate Vercel projects from a single GitHub repository.
*   Frontend needs to explicitly manage the backend API's public URL (requires environment variable configuration).

## Alternatives Considered

*   **Continue troubleshooting Vercel root-level monorepo configuration:** Rejected due to persistent deployment errors (`mix-routing-props`), consuming excessive time without guaranteed resolution, and the user's current successful subdirectory deployment pattern.
*   **Completely separate GitHub repositories (as per prior ADR update):** Rejected as the user's current deployment approach already involves Vercel projects targeting subdirectories, making a full repository separation unnecessary and adding overhead.

## References

- Feature Spec: [specs/012-backend-server-foundation/spec.md](specs/012-backend-server-foundation/spec.md)
- Implementation Plan: [specs/012-backend-server-foundation/plan.md](specs/012-backend-server-foundation/plan.md)
- Related ADRs: [history/adr/0004-deployment-strategy-migration-to-vercel.md](history/adr/0004-deployment-strategy-migration-to-vercel.md)
- Evaluator Evidence: N/A
