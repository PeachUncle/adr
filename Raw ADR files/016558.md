# 006: ServiceNow Implementation with Flow Designer and IntegrationHub

*   **Status:** Proposed
*   **Date:** 2025-09-05

## Context and Problem Statement

The orchestration logic for calling the Keycloak and OpenShift APIs needs to be implemented within our ServiceNow Zurich instance. We require a modern, low-code, and maintainable approach that leverages platform-native features for building workflows and managing external API integrations.

## Decision Drivers

*   The need for a robust workflow engine to handle the multi-step provisioning process, including approvals and notifications.
*   The requirement to integrate with external REST APIs securely, as defined in ADR-002 and ADR-003.
*   The desire to use a low-code solution to accelerate development and simplify maintenance.
*   The need for a solution that is fully supported and integrated within the ServiceNow platform.

## Considered Options

*   **Flow Designer with IntegrationHub:** Use the modern, primary workflow tool in ServiceNow. IntegrationHub provides the specific spokes (like the REST spoke) for building reusable actions to call external APIs. This is ServiceNow's strategic direction for automation.
*   **Legacy Workflows:** Use the older, legacy workflow engine. This is not recommended for new development as it is less flexible and powerful than Flow Designer.
*   **Custom Scripted REST Messages:** Develop a purely scripted solution using Business Rules and Script Includes to call outbound REST messages. This offers maximum flexibility but is high-code, harder to maintain, and bypasses the benefits of the Flow Designer and IntegrationHub frameworks.

## Decision Outcome

Chosen option: **"Flow Designer with IntegrationHub"**. The entire end-to-end process will be built as a Flow in Flow Designer. The interactions with the Keycloak and OpenShift REST APIs will be implemented as reusable Actions within a custom IntegrationHub Spoke. This approach directly leverages the Connection & Credential Aliases defined in ADR-003 and provides a clear, visual representation of the entire process.

### Positive Consequences

*   **Maintainability:** The visual, low-code nature of Flow Designer makes the logic easy to understand and modify.
*   **Reusability:** API interactions are built as reusable Actions, which can be leveraged in other flows.
*   **Platform-Native:** Tightly integrated with ServiceNow features like Connection & Credential Aliases, approvals, and notifications.
*   **Future-Proof:** Aligns with ServiceNow's strategic direction for automation.

### Negative Consequences

*   **Licensing:** Use of IntegrationHub may have licensing cost implications depending on the ServiceNow subscription.
*   **"Low-Code" Limitations:** For extremely complex logic, developers may find the low-code interface restrictive compared to pure scripting, though this can be mitigated with inline scripts.
