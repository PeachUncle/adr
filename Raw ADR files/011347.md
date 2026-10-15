# ADR 001: Tier 0 Deployment Strategy - Local Docker Environment

*   **Status:** Proposed
*   **Date:** 2025-04-27
*   **Deciders:** Architect Mode
*   **Consulted:** `docs/project-specifications.md` v2.3 (Section 3)
*   **Affected:** Tier 0 Implementation, Infrastructure Setup, Developer Workflow

## Context and Problem Statement

PhiloGraph requires a functional Minimum Viable Product (MVP) - Tier 0 - that provides core features (ingestion, high-quality semantic search, basic graph, CLI/MCP interfaces) with minimal direct software/API cost. The target deployment environment is typical developer hardware (e.g., laptop) without requiring specialized hardware like GPUs for core functionality, while still achieving good semantic search performance. We need a consistent, reproducible, and manageable way to deploy the necessary components (database, backend, middleware, processing tools) locally.

## Decision Drivers

*   **Cost Minimization:** Tier 0 aims for ~$0 direct software/API cost (excluding hardware/time).
*   **Developer Accessibility:** Must run on standard developer laptops.
*   **Consistency:** Ensure the environment is reproducible across different developer machines.
*   **Component Management:** Need to manage multiple services (DB, backend, proxy, etc.).
*   **Migration Path:** Should facilitate future migration to cloud environments (Tier 1+).
*   **Specification v2.3:** Explicitly defines Tier 0 target environment as local Docker.

## Considered Options

1.  **Local Docker Environment:** Use Docker and Docker Compose to containerize and orchestrate all necessary services (Postgres, LiteLLM Proxy, Python Backend, Text Processing Tools).
2.  **Direct Local Installation:** Install all dependencies (PostgreSQL, Python libraries, GROBID, etc.) directly onto the host machine.
3.  **Virtual Machine (VM):** Set up a dedicated VM (e.g., using VirtualBox, VMware) to host the services.

## Decision Outcome

**Chosen Option:** 1. Local Docker Environment.

**Rationale:**

*   **Consistency & Reproducibility:** Docker ensures that all developers run the same service versions and configurations, minimizing "works on my machine" issues. Docker Compose simplifies starting/stopping the entire stack.
*   **Dependency Management:** Isolates dependencies within containers, preventing conflicts with host system libraries.
*   **Component Management:** Docker Compose provides a declarative way to define and manage the multi-service application.
*   **Alignment with Spec:** Directly implements the requirement from `docs/project-specifications.md` v2.3.
*   **Migration Path:** Containerization is a standard practice that simplifies deployment to cloud container orchestration platforms (e.g., Kubernetes, Cloud Run, Fargate, ACA) in later tiers.
*   **Cost:** Docker itself is free.

**Rejection Rationale:**

*   *Direct Local Installation:* Prone to dependency conflicts, difficult to ensure consistency across environments, harder to manage multiple services, less clean migration path.
*   *Virtual Machine:* Heavier resource usage than Docker containers, slower startup times, less flexible for managing individual service updates.

## Consequences

*   **Positive:**
    *   Consistent development and deployment environment locally.
    *   Simplified dependency management.
    *   Easier onboarding for new developers.
    *   Clear path for migrating containerized services to the cloud.
*   **Negative:**
    *   Requires Docker Desktop (or equivalent) installation on developer machines.
    *   Adds a layer of abstraction that might require some Docker knowledge for debugging.
    *   Resource consumption (RAM, CPU) of running multiple containers locally needs monitoring on developer hardware.
    *   Initial setup of Dockerfiles and Docker Compose configuration required.

## Validation

*   Successful execution of `docker-compose up -d` should start all required Tier 0 services.
*   CLI and MCP interfaces should be able to interact with the backend API running within Docker.
*   Ingestion and search workflows should complete successfully using the containerized services.

## Links

*   `docs/project-specifications.md` v2.3 (Section 3)
*   `docs/architecture/tier0_mvp_architecture.md`