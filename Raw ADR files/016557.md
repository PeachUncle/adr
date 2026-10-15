# 004: GitOps-based Deployment with ArgoCD and Kustomize

*   **Status:** Proposed
*   **Date:** 2025-09-05

## Context and Problem Statement

The ServiceNow-OpenShift integration, including its workflows and any potential in-cluster components (like service accounts or config maps), requires a standardized, automated, and reliable deployment method onto the OpenShift cluster. We need to manage its Kubernetes resources and configuration declaratively to ensure consistency, auditability, and maintainability across different environments (e.g., development, staging, production).

## Decision Drivers

*   The need for a declarative, version-controlled source of truth for all deployments.
*   The requirement to automate deployment and reduce manual, error-prone processes.
*   The need for a consistent and repeatable process for promoting changes across environments.
*   The desire to empower developers with a clear, Git-based workflow for managing application configuration.

## Considered Options

*   **GitOps with ArgoCD and Kustomize:** A pull-based, declarative approach where an in-cluster agent (ArgoCD) ensures the live state matches a Git repository. Kustomize allows for template-free customization of manifests.
*   **Manual Deployment:** Using `oc apply -f <file>` or the OpenShift web console. This is simple for one-off tasks but is not scalable, repeatable, or auditable.
*   **Traditional CI/CD (Push-based):** Using a tool like Jenkins or OpenShift Pipelines to actively push manifest changes to the cluster. This is a valid approach but requires granting CI/CD tools cluster-admin-level credentials, which can be a security concern.
*   **Helm Charts:** A package manager for Kubernetes. While powerful, it can introduce complexity with templating for the relatively simple configuration needs of this project.

## Decision Outcome

Chosen option: **"GitOps with ArgoCD and Kustomize"**, because it provides a secure, declarative, and highly automated framework that aligns with modern cloud-native best practices.

### Positive Consequences

*   **Auditability:** Every change to the deployment is a Git commit, providing a clear and auditable history.
*   **Consistency:** ArgoCD ensures the cluster state always matches the Git repository, eliminating configuration drift.
*   **Security:** The pull-based model is more secure; cluster credentials are not stored in an external CI server.
*   **Developer Experience:** Changes are proposed and reviewed through standard pull requests.
*   **Environment Management:** Kustomize provides a clean, template-free way to manage configuration differences between environments.

### Negative Consequences

*   **Initial Setup:** Requires installing and configuring ArgoCD on the OpenShift cluster.
*   **Learning Curve:** The team may need training on GitOps principles, ArgoCD, and Kustomize if they are not already familiar with them.
*   **Repository Management:** Requires a well-defined strategy for managing the configuration Git repository.
