# ADR-002: GitOps with ArgoCD Hub Architecture

## Status
Accepted

## Date
2024-12-01

## Context
The multi-cluster RH OVE ecosystem requires a consistent, auditable, and scalable approach to application deployment and configuration management across multiple clusters. Traditional CI/CD approaches with push-based deployments create security concerns and operational complexity in multi-cluster environments.

## Decision
We will implement GitOps using ArgoCD in a hub-spoke pattern:
- **ArgoCD Hub**: Centralized ArgoCD instance in the management cluster
- **ArgoCD Agents**: Lightweight agents in each application cluster
- **Git-based Configuration**: All infrastructure and application configurations stored in Git repositories

## Rationale

### Advantages
1. **Declarative Configuration**: Infrastructure and applications defined as code
2. **Audit Trail**: Complete Git history of all changes
3. **Security**: Pull-based model eliminates need for external access to clusters
4. **Consistency**: Identical deployment processes across all environments
5. **Rollback Capability**: Easy rollback using Git revert operations
6. **Self-Healing**: Automatic drift correction and reconciliation

### Alternatives Considered
1. **Jenkins-based CI/CD**: Rejected due to security concerns with push-based deployments
2. **Tekton Pipelines**: Rejected due to complexity in multi-cluster scenarios
3. **Fleet by Rancher**: Rejected due to vendor lock-in concerns
4. **Flux**: Rejected due to preference for ArgoCD's UI and workflow capabilities

## Implementation Details

### ArgoCD Hub Configuration
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ArgoCD
metadata:
  name: argocd-hub
  namespace: argocd
spec:
  server:
    replicas: 3
    route:
      enabled: true
      tls:
        termination: reencrypt
  ha:
    enabled: true
  dex:
    openShiftOAuth: true
  rbac:
    defaultPolicy: 'role:readonly'
```

### Repository Structure
```
gitops-repo/
├── clusters/
│   ├── management/
│   ├── production/
│   ├── staging/
│   └── development/
├── applications/
│   ├── base/
│   └── overlays/
└── infrastructure/
    ├── networking/
    ├── storage/
    └── monitoring/
```

### Application of Applications Pattern
- Root ArgoCD Application manages cluster-specific applications
- Environment-specific overlays using Kustomize
- Automated sync policies for non-production environments
- Manual sync for production deployments

## Consequences

### Positive
- **Enhanced Security**: No direct cluster access required for deployments
- **Improved Compliance**: Complete audit trail through Git history
- **Reduced Operational Overhead**: Automated deployment and drift correction
- **Better Collaboration**: Git-based workflows familiar to development teams
- **Disaster Recovery**: Easy recreation of cluster state from Git

### Negative
- **Learning Curve**: Teams need to adapt to GitOps workflows
- **Git Repository Complexity**: Large repositories can become difficult to manage
- **Network Dependencies**: Requires reliable connectivity to Git repositories
- **Secret Management**: Additional complexity for managing sensitive data

## Security Considerations
- ArgoCD service accounts use minimal required permissions
- Private Git repositories with SSH key authentication
- RBAC integration with OpenShift OAuth
- Secret management through External Secrets Operator
- Network policies restrict ArgoCD communication

## Monitoring and Alerting
- ArgoCD application health monitoring
- Git repository sync status tracking
- Deployment success/failure notifications
- Performance metrics for sync operations
- Custom dashboards for GitOps workflows

## Migration Strategy
1. **Phase 1**: Deploy ArgoCD hub in management cluster
2. **Phase 2**: Migrate existing applications to Git repositories
3. **Phase 3**: Configure ArgoCD applications for each cluster
4. **Phase 4**: Implement automated sync for non-production
5. **Phase 5**: Train teams on GitOps workflows
