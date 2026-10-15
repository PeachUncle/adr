# ADR-010: Ansible Automation Platform Integration for ServiceNow-Driven Infrastructure Orchestration

**Status:** Proposed

**Date:** 2025-09-09

## Context

The current architecture (ADR-001, ADR-009) relies on ServiceNow calling APIs directly and using local Ansible playbooks for post-deployment configuration. While this works for basic scenarios, it presents several limitations as the system scales:

1. **Limited Execution Environment:** ServiceNow Flow Designer has constraints on long-running operations and complex automation logic
2. **Credential Management Complexity:** Managing multiple API credentials and tokens directly within ServiceNow increases security risk
3. **Scalability Concerns:** Direct API calls from ServiceNow don't provide robust error handling, retry logic, or parallel execution capabilities
4. **Audit and Compliance Gaps:** Limited visibility into automation execution details and logs for compliance requirements
5. **Maintenance Overhead:** Ansible playbooks running locally require manual coordination and lack centralized lifecycle management

The introduction of Red Hat Ansible Automation Platform (AAP) as an intermediary automation layer would address these limitations while maintaining the three-tier architecture principles established in ADR-001.

## Decision

We will enhance the architecture by introducing **Ansible Automation Platform (AAP)** as a dedicated automation execution layer between ServiceNow and the target infrastructure:

### Enhanced Four-Tier Architecture:

1. **ServiceNow (Orchestration Tier):** Maintains its role as the central orchestrator and single point of initiation, but delegates complex automation tasks to AAP via REST API calls
2. **Ansible Automation Platform (Automation Execution Tier):** Serves as the automation engine, executing job templates that contain the complex infrastructure and application configuration logic
3. **Keycloak (Identity Tier):** Unchanged - continues to serve as the identity source of truth
4. **OpenShift (Resource Tier):** Unchanged - remains the target platform for resource provisioning

### Integration Architecture:

- **ServiceNow → AAP Integration:** ServiceNow workflows will call AAP Job Templates via the AAP REST API
- **AAP → Infrastructure Integration:** AAP executes Ansible playbooks that interact with Keycloak Admin API, OpenShift API, and other infrastructure components
- **Credential Management:** AAP manages all infrastructure credentials using AAP's native credential store, reducing ServiceNow's credential footprint
- **Execution Environment:** AAP provides robust execution environments with proper dependency management, logging, and error handling

### Job Template Strategy:

1. **Keycloak User Provisioning Template:** Handles user creation, realm management, and client configuration
2. **OpenShift Project Provisioning Template:** Manages project creation, RBAC configuration, and resource quotas
3. **Integration Validation Template:** Performs end-to-end validation of provisioned resources
4. **Cleanup and Deprovisioning Template:** Handles resource cleanup and user deactivation

## Rationale

### Technical Benefits:
- **Enhanced Scalability:** AAP provides robust execution environments with parallel job execution and resource management
- **Improved Error Handling:** Built-in retry logic, failure handling, and detailed logging capabilities
- **Centralized Automation:** All infrastructure automation logic consolidated in AAP with version control and change management
- **Execution Isolation:** Ansible playbooks run in isolated execution environments with proper dependency management

### Security Benefits:
- **Reduced Attack Surface:** ServiceNow no longer needs direct access to infrastructure API credentials
- **Credential Consolidation:** AAP's credential store provides centralized, encrypted credential management
- **Audit Trail:** Comprehensive logging and audit trails for all automation executions
- **Role-Based Access:** AAP's RBAC system provides granular control over automation execution

### Operational Benefits:
- **Monitoring and Alerting:** AAP provides comprehensive monitoring, dashboards, and alerting for automation jobs
- **Change Management:** Job template versioning and approval workflows aligned with ITIL processes
- **Standardization:** Consistent execution environments and automation patterns across all operations
- **Skills Alignment:** Leverages existing Ansible expertise while providing enterprise-grade automation platform

## Consequences

### Positive Consequences:

- **Enhanced Reliability:** AAP provides enterprise-grade automation execution with built-in resilience
- **Improved Security Posture:** Centralized credential management and reduced ServiceNow privilege requirements
- **Better Compliance:** Comprehensive audit trails and approval workflows for all automation activities
- **Scalable Architecture:** Can handle increased automation complexity and volume as the platform grows
- **Operational Excellence:** Professional monitoring, logging, and troubleshooting capabilities
- **Team Productivity:** Ansible developers can work in their native environment while ServiceNow focuses on business logic

### Negative Consequences:

- **Increased Infrastructure Complexity:** Additional platform to deploy, manage, and maintain
- **Licensing Costs:** AAP requires additional licensing (though may be offset by included RHEL subscriptions)
- **Integration Complexity:** Additional integration layer requires careful design and testing
- **Skill Requirements:** Team needs AAP administration and operational knowledge
- **Dependency Risk:** ServiceNow automation becomes dependent on AAP availability

### Risk Mitigation:

- **High Availability:** Deploy AAP in HA configuration across multiple nodes
- **Monitoring Integration:** Integrate AAP health monitoring with existing observability stack (ADR-008)
- **Fallback Procedures:** Maintain capability for manual execution of critical automation tasks
- **Documentation:** Comprehensive runbooks for AAP operations and troubleshooting

## Implementation Considerations

### Deployment Strategy:
1. **Phase 1:** Deploy AAP on OpenShift using kustomize and AAP Operator (ADR-012)
2. **Phase 2:** Migrate existing Ansible playbooks to AAP Job Templates
3. **Phase 3:** Update ServiceNow workflows to call AAP instead of direct APIs
4. **Phase 4:** Implement monitoring, alerting, and operational procedures

### Deployment Implementation:
The AAP deployment is now implemented via GitOps using kustomize overlays at `kustomize/ansible-automation-platform/`:
- **Operator Deployment:** Automated subscription management with configurable channels
- **Instance Configuration:** AnsibleAutomationPlatform custom resource with controller and hub components
- **Environment Management:** Layered overlays support multiple deployment environments
- **ArgoCD Integration:** Fully integrated with existing GitOps workflow (ADR-004)

### Integration Points:
- **ServiceNow Integration:** Use AAP REST API for job template execution
- **Credential Management:** Migrate credentials from ServiceNow to AAP credential store
- **GitOps Integration:** AAP deployment and playbooks stored in Git, aligned with ADR-004 principles
- **Monitoring Integration:** AAP metrics and logs integrated with OpenShift monitoring (ADR-008)

## References

- **ADR-001:** Three-Tier Orchestration Architecture (enhanced to four-tier)
- **ADR-002:** Decoupled, API-Driven Integration (AAP becomes additional API layer)
- **ADR-003:** Centralized Configuration (enhanced with AAP credential management)
- **ADR-009:** Hybrid GitOps and Ansible Configuration (enhanced with AAP execution)

## Future Considerations

This architecture positions the platform for future enhancements:
- **Multi-Cloud Support:** AAP can orchestrate across multiple cloud platforms
- **Advanced Workflows:** Complex automation workflows with conditional logic and approvals
- **Self-Service Capabilities:** AAP can provide self-service automation portals
- **Integration Expansion:** Easy integration with additional tools and platforms
