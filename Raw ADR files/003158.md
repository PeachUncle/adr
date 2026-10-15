# ADR-004: Project Structure and Deployment Model for RAG Pipeline

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Proposed
- **Date:** 2025-12-18
- **Feature:** 002-rag-data-ingestion
- **Context:** Defining the organizational structure of the project's source code and the implied deployment strategy for the RAG data ingestion pipeline. This decision impacts maintainability, testability, and the ease of future expansion or integration.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

The RAG data ingestion pipeline will adopt the following project structure and deployment model:
-   **Project Structure:** All core pipeline logic will be encapsulated within a single Python script named `main.py`. This script, along with a `requirements.txt` file (listing Python dependencies) and a `.env.example` file (documenting required environment variables), will reside in a dedicated `rag_pipeline/` directory at the repository root.
-   **Deployment Model:** The pipeline is designed as a standalone, script-based application. Deployment primarily involves setting up a Python environment, installing the listed dependencies, configuring the necessary environment variables, and executing the `main.py` script. It is intended to be run as an on-demand batch job or a scheduled task.

## Consequences

### Positive

-   **Simplicity and Clarity:** A single-script approach within a dedicated directory maintains a minimal and straightforward project structure, making it easy for developers to understand the entire pipeline's flow at a glance. This is particularly beneficial for an initial prototype or a focused utility.
-   **Ease of Deployment:** The standalone nature of the script makes it highly portable and exceptionally straightforward to deploy across various environments (e.g., local developer machines, CI/CD runners, virtual machines, or as a component within a cloud function) by simply ensuring the Python runtime and dependencies are present.
-   **Maintainability (Initial Phase):** During the initial development and iteration phases, centralizing all core logic into `main.py` can simplify development, debugging, and rapid iteration, as changes are confined to a single file.

### Negative

-   **Scalability (Codebase Complexity):** As the RAG pipeline inevitably grows in complexity (e.g., incorporating more diverse data sources, introducing advanced NLP preprocessing steps, adding more sophisticated error handling, or integrating with multiple external systems), a monolithic `main.py` script can quickly become unwieldy. This can lead to decreased readability, make refactoring challenging, and reduce overall maintainability.
-   **Testability Challenges (Advanced):** While basic functional and integration testing of the entire pipeline is feasible, truly granular unit testing of individual components (e.g., the URL discovery logic, the text extraction, or the embedding generation functions) can become more challenging without a clear separation of concerns and proper internal modularization within the script.
-   **Limited Concurrency/Parallelism:** A single script execution typically processes data sequentially. For very large datasets or high-throughput requirements, this deployment model might not effectively leverage parallel processing capabilities without external orchestration, potentially leading to longer processing times.

## Alternatives Considered

-   **Alternative Project Structure (Modular Python Package):**
    -   **Description:** Organizing the code into a formal Python package with multiple submodules (e.g., `scraper.py`, `embedder.py`, `vector_store.py` each containing distinct functionalities), along with a `__init__.py` file and a `setup.py` or `pyproject.toml` for proper packaging.
    -   **Why rejected:** While this structure is superior for larger, more complex applications and promotes better separation of concerns, it introduces initial overhead (e.g., setting up package metadata, namespace management) that is not strictly necessary for the current, focused scope. The single-script approach with internal modularization (functions) is preferred for rapid development and simplicity at this stage.
-   **Alternative Deployment Model (Containerized Application using Docker/Kubernetes):**
    -   **Description:** Packaging the entire pipeline application into a Docker image and deploying it using container orchestration tools like Kubernetes or Docker Compose.
    -   **Why rejected:** Introduces an additional layer of complexity and infrastructure management (e.g., writing Dockerfiles, building images, managing container registries, configuring orchestration) that is not justified for the current scale and the relatively straightforward nature of the single-script application. While containerization is a common best practice, its adoption can be deferred until the deployment requirements or the application's complexity explicitly warrant it.

## References

- Feature Spec: `specs/002-rag-data-ingestion/spec.md`
- Implementation Plan: `specs/002-rag-data-ingestion/plan.md`
- Related ADRs: N/A
- Evaluator Evidence: `specs/002-rag-data-ingestion/research.md`
