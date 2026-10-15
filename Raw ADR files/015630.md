# ADR-004: Admission Controller Strategy

## Status
Accepted

## Date
2024-12-01

## Context
The RH OVE ecosystem requires a flexible, secure, and policy-driven approach for managing resource admission and validation within clusters. Implementing appropriate admission control policies ensures compliance, security, and operational consistency.

## Decision
We will implement a layered admission control strategy utilizing OpenShift's built-in admission controllers, KubeVirt webhooks, Kyverno policies, and OIDC-integrated RBAC enforcement via Keycloak.

## Rationale

### Advantages
1. **Centralized Policy Management**: Simplify governance with cluster-wide policies
2. **Dynamic Policy Application**: Adjust policies without redeploying cluster components
3. **Security Enforcement**: Validate resource configurations before persistence
4. **Prevention of Misconfiguration**: Guard against policy violations
5. **Identity-based Access Management**: Integration with OIDC providers for enhanced user identity verification
6. **Extensibility**: Easy to introduce new policies as needs evolve

### Alternatives Considered
1. **Legacy Admission Controllers**: Rejected due to limited flexibility and poor integration
2. **Custom Webhooks**: Rejected due to complexity in management and maintenance
3. **Third-Party Solutions**: Rejected due to integration difficulties and vendor lock-in

## Implementation Details

### OpenShift Built-in Admission
- **Security Context Constraints**: Default and custom SCCs for VM and container workloads
- **RBAC Enforcements**: Actionable role- and label-based access controls
- **Quotas and Limit Ranges**: Ensuring fair resource allocation per team

### KubeVirt Webhooks
- **Validation Webhooks**: Enforce configuration standards for VM specs
- **Mutation Webhooks**: Apply defaults and constraints to VM definitions

### Kyverno Policies
- **Configuration Validation**: Ensure compliance with organization best practices
- **Resource Constraints**: Limit what configurations may be used / deployed
- **Dynamic Policies**: Automate policy reapplication based on changes

## Compliance Considerations
- **Auditability**: Policy applications and violation logging
- **Policy-as-Code**: Centralized version control and history of policy changes
- **Enforcement vs Warning**: Progressive policy application based on audit

## Consequences

### Positive
- **Improved Security Posture**: Clusters protected from non-compliant configurations
- **Enhanced Compliance Auditability**: Documentation and reporting of policy compliance
- **Reduced Operational Risk**: Guard against human error and unsafe configurations

### Negative
- **Complex Rule Management**: Need mature processes to handle policy lifecycle
- **Performance Overhead**: May introduce latency to resource creation/update
- **Learning Curve**: Required training for policy authors

## Implementation Plan

### Phase 1: Planning
1. Identify key compliance and security requirements
2. Design initial policy set and test environment
3. Engage stakeholders to define policy boundaries

### Phase 2: Rollout
1. Deploy core admission controllers with policy-as-code principles, leveraging IAM for authentication and authorization
2. Begin enforcement in non-production environments
3. Gradually extend to production with monitoring and logging

### Phase 3: Monitoring and Adjustment
1. Enable continuous policy evaluation and audit logging
2. Conduct regular policy reviews and updates
3. Train teams on policy creation and maintenance

## Compliance and Observability

### Monitoring
- Policy applicability and compliance dashboards
- Alerts for policy violations and enforcement actions

### Logging and Reporting
- Centralized logging of admission requests and results
- Automated compliance reports tied to policy adherence
