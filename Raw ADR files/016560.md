# 9. Hybrid GitOps and Ansible Configuration for Post-Deployment Orchestration

*   **Status:** Proposed
*   **Date:** 2025-09-05

## Context

Our architecture relies on a GitOps approach using ArgoCD for deploying applications on OpenShift, as detailed in [ADR-004](004-gitops-based-deployment-with-argocd-and-kustomize.md) and [ADR-005](005-keycloak-deployment-on-openshift-via-operator.md). This works exceptionally well for managing the desired state of Kubernetes resources, such as the Keycloak operator, the `Keycloak` custom resource, and related networking and secret objects.

However, once the Keycloak instance is running, a series of imperative, ordered configuration steps are required to make it operational for our use case. This includes:
*   Creating specific realms.
*   Configuring identity providers.
*   Creating clients for applications like OpenShift and ServiceNow.
*   Defining roles and users.
*   Applying specific integration settings required by ServiceNow.

Attempting to manage this complex, application-level setup declaratively via Kubernetes manifests or operators is brittle, complex, and blurs the line between infrastructure state and application-specific configuration.

## Decision

We will adopt a hybrid, two-phase deployment and configuration model:

1.  **Phase 1: Declarative Deployment (GitOps):** ArgoCD will remain the source of truth for all Kubernetes resources. It will deploy the Keycloak operator, the `Keycloak` instance, and all necessary supporting resources (Secrets, Services, Routes). The GitOps pipeline ensures the application is running and available on the cluster in its base state.

2.  **Phase 2: Imperative Configuration (Ansible):** For all post-deployment, application-level configuration within Keycloak, we will use Ansible. The existing `ansible/roles/rhsso_servicenow_config` role will be used by a central playbook (`ansible/playbook.yml`) to perform the specific setup tasks required for the ServiceNow integration.

This Ansible playbook will be triggered after the ArgoCD application for Keycloak is synchronized and reports a healthy status. The trigger can be manual for initial setup or integrated into a higher-level automation pipeline.

## Consequences

### Pros

*   **Separation of Concerns:** This approach creates a clean division of responsibility. GitOps manages the *running state* of the application infrastructure, while Ansible manages the *internal configuration* of the application.
*   **Right Tool for the Job:** It leverages the strengths of each tool. GitOps excels at maintaining a declarative desired state for infrastructure. Ansible is purpose-built for imperative, step-by-step configuration and orchestration logic.
*   **Improved Readability & Maintainability:** The Ansible playbook and roles are more expressive and easier to understand for complex configuration logic compared to chaining Kubernetes jobs or writing a custom operator.
*   **Idempotency and Reusability:** The Ansible playbook can be written to be idempotent, allowing it to be run multiple times safely, and the roles can be reused across different environments.

### Cons

*   **Increased Workflow Complexity:** The end-to-end process involves two distinct systems (ArgoCD and Ansible). A mechanism is required to orchestrate the handoff, i.e., triggering the Ansible run only after the GitOps sync is successfully completed.
*   **Potential for Configuration Drift:** While GitOps prevents drift at the Kubernetes resource level, the application's internal configuration could theoretically be modified outside of Ansible. This risk is mitigated by enforcing that all configuration changes are made through Ansible playbook runs.
*   **State Management:** The source of truth is split. The Git repository is the source of truth for the infrastructure state, while the Ansible playbook and its variables become the source of truth for the application's configuration. This requires discipline to keep them synchronized.
