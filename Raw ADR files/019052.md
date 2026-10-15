# ADR-0008: Docker Multi-Stage Containerization

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-24
- **Feature:** 001-k8s-local-deploy
- **Context:** Phase 4 requires containerizing the Todo application for Kubernetes deployment. The application consists of 3 services (Next.js frontend, FastAPI backend, FastMCP server). Images must be production-ready, secure, and optimized for size. Constitution Principle II mandates multi-stage builds to separate build dependencies from runtime.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Defines containerization pattern for all services
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - Single-stage, distroless evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - Affects frontend, backend, and MCP server
-->

## Decision

We will adopt multi-stage Docker builds for all three services:

**Frontend (Next.js):**
- Base Image: node:20-alpine for both builder and runner stages
- Builder Stage: Install dependencies, build Next.js with `output: 'standalone'`
- Runner Stage: Copy only `.next/standalone`, `.next/static`, and `public` directories
- Non-root user: `USER node`
- Target size: <200MB

**Backend (FastAPI):**
- Base Image: python:3.13-slim
- Builder Stage: Install UV, compile dependencies with `uv pip install --system --no-cache-dir`
- Runtime Stage: Copy only runtime dependencies and application code
- Non-root user: Create dedicated `appuser`
- Target size: <500MB

**MCP Server (FastMCP):**
- Base Image: python:3.13-slim
- Single Stage (minimal): Install only FastMCP dependencies
- Non-root user: Create dedicated `appuser`
- Target size: <100MB

### Rationale

Multi-stage builds separate build-time dependencies (compilers, build tools, dev dependencies) from runtime requirements. This reduces image size by 60-80%, improves security by removing build tools, and aligns with Docker best practices. The standalone Next.js output is a specific optimization for Next.js that eliminates node_modules from the final image.

## Consequences

### Positive

- **Reduced Image Size:** Multi-stage builds reduce final image size by 60-80% compared to single-stage, saving storage and transfer costs
- **Improved Security:** Build tools and compilers are not present in runtime, reducing attack surface
- **Faster Deployment:** Smaller images pull faster during Kubernetes deployment
- **Constitution Alignment:** Satisfies Constitution Principle II (Multi-Stage Builds)
- **Optimized Layers:** Build artifacts in one layer, copy in next layer for better layer caching
- **Production Ready:** Images follow Dockerfile best practices and are cloud-registry compatible

### Negative

- **Build Complexity:** Multi-stage Dockerfiles are more complex to understand and debug than single-stage
  - *Mitigation:* Document each stage with comments; use Docker AI Gordon for assistance
- **Longer Initial Build:** First build is slower due to multiple stages (no benefit of layer reuse)
  - *Mitigation:* Docker layer caching makes subsequent builds fast
- **Alpine Limitations:** Alpine Linux (for frontend) uses musl libc which may have compatibility issues
  - *Mitigation:* Use node:20-alpine which is well-tested; switch to debian-slim if issues arise

## Alternatives Considered

### Alternative A: Single-Stage Builds
- **Pros:** Simpler Dockerfiles, faster initial builds, easier to understand
- **Cons:** Larger images (2-3x size), includes build tools, violates Constitution Principle II
- **Why Rejected:** Image size targets (<200MB frontend, <500MB backend) impossible with single-stage. Build tools in runtime increase security risk and deployment time.

### Alternative B: Distroless Images
- **Pros:** Minimal attack surface, smallest possible size, Google-maintained
- **Cons:** Difficult debugging (no shell), requires separate debug image for troubleshooting, more complex builds
- **Why Rejected:** Distroless is excellent for production but adds complexity during Phase 4 development. Consider for Phase 5 when application is stable and debugging needs are known.

### Alternative C: Buildpacks (e.g., paketo)
- **Pros:** Automatic Dockerfile generation, opinionated best practices
- **Cons:** Less control over build process, harder to customize, additional tool dependency
- **Why Rejected:** Buildpacks abstract away build details, but our requirements (specific size targets, non-root users) are better handled with explicit Dockerfiles.

## References

- Feature Spec: [specs/001-k8s-local-deploy/spec.md](../../specs/001-k8s-local-deploy/spec.md)
- Implementation Plan: [specs/001-k8s-local-deploy/plan.md](../../specs/001-k8s-local-deploy/plan.md) §Phase 1
- Research Notes: [specs/001-k8s-local-deploy/research.md](../../specs/001-k8s-local-deploy/research.md) §1
- Related ADRs: ADR-0001 (Frontend Stack), ADR-0002 (Backend Stack), ADR-0006 (MCP Server Architecture)
- Docker Multi-Stage Builds: https://docs.docker.com/build/building/multi-stage/
- Next.js Standalone Output: https://nextjs.org/docs/deployment#standalone-output
