# ADR 003: Defer Loki Installation for Initial Development

**Status**: Accepted

**Date**: 2025-08-05

## Context

Task 1.4 of the project plan requires the deployment of a complete observability stack, including Prometheus, Grafana, Tempo, and Loki for centralized logging. Multiple attempts were made to install a functioning Loki instance into the local Kind cluster using the `grafana/loki` Helm chart.

These attempts included:
* Configuring Loki in `SingleBinary` mode with a `filesystem` backend, which failed due to persistent Helm templating errors (`nil pointer` exceptions).
* Configuring Loki in its default scalable mode, integrated with a MinIO object storage backend. This also failed due to different, but equally persistent, Helm templating errors (`tpl function execution` errors).

The `grafana/loki` Helm chart, in its recent versions, has proven to be unstable and overly complex to configure for a local development environment. Continuing to debug this single component is blocking progress on other critical project deliverables.

## Decision

We will **defer the installation of a centralized logging solution (Loki)** for the initial phases of the project.

For local development and debugging, engineers will use the standard `kubectl logs <pod-name>` command to inspect the logs of individual microservices. The project will proceed with installing the other pillars of observability (Prometheus for metrics and Tempo for traces) to provide a strong-but-incomplete observability platform. The task of implementing a robust, centralized logging solution will be deferred to a later project phase.

## Consequences

* **Positive**:
    * **Unblocks Development**: This decision immediately removes a significant blocker, allowing development to proceed on core business logic and microservices (Deliverable 2).
    * **Maintains Project Momentum**: It prevents further time being spent on a frustrating infrastructure issue, ensuring the project timeline does not stall.
    * **Focus on Core Value**: The team can focus on delivering the transaction simulator and fraud detection services, which are the primary goals of the project.
    * **Sufficient Observability for Now**: The combination of Prometheus metrics and Tempo traces still provides a powerful observability foundation for the initial development phase.

* **Negative**:
    * **No Centralized Logging**: Without Loki, there is no single place to view or query logs from all services combined. This makes cross-service debugging more difficult.
    * **Ephemeral Logs**: Logs accessed via `kubectl logs` are ephemeral and will be permanently lost if a pod is deleted or recreated.
    * **Introduces Technical Debt**: This decision consciously creates a known task for the future (implementing centralized logging), which must be tracked and addressed before the platform could be considered truly production-ready.