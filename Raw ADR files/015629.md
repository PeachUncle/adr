# ADR-003: Namespace-Based Cluster Topology

## Status
Accepted

## Date
2024-12-01

## Context
The RH OVE ecosystem requires an efficient organizational strategy for managing mixed VM and container workloads within clusters. We need to balance isolation, security, resource management, and operational simplicity while supporting multi-tenant use cases.

## Decision
We will implement an **application namespace-based topology** where resources are organized by business application or domain rather than by resource type or technology stack.

### Topology Structure
```
Cluster
├── app-web-prod (namespace)
│   ├── VMs (web servers)
│   ├── Containers (microservices)
│   ├── Storage (PVCs, DataVolumes)
│   └── Network (NetworkPolicies, NADs)
├── app-database-prod (namespace)
│   ├── VMs (database servers)
│   ├── Containers (database operators)
│   ├── Storage (high-performance storage)
│   └── Network (isolated database networks)
└── app-monitoring-prod (namespace)
    ├── VMs (legacy monitoring tools)
    ├── Containers (modern observability stack)
    ├── Storage (metrics and logs storage)
    └── Network (monitoring networks)
```

## Rationale

### Advantages
1. **Strong Isolation**: Each application has its own security boundary
2. **Simplified RBAC**: Teams get namespace-level access aligned with their applications
3. **Clear Resource Attribution**: Easy to track costs and resource usage per application
4. **Network Microsegmentation**: Network policies can be application-specific
5. **Operational Clarity**: Troubleshooting and maintenance scoped to business context
6. **Compliance Alignment**: Audit boundaries match business applications

### Alternatives Considered

#### 1. Technology-Based Topology
- **Structure**: Separate namespaces for VMs vs containers
- **Rejected**: Creates artificial barriers between related workloads
- **Issues**: Complex cross-namespace communication, unclear ownership

#### 2. Environment-Based Topology Only
- **Structure**: Single namespace per environment (prod, staging, dev)
- **Rejected**: Poor isolation between different applications
- **Issues**: Resource contention, security boundary concerns

#### 3. Team-Based Topology
- **Structure**: Namespaces per team/department
- **Rejected**: Teams often work on multiple applications
- **Issues**: Unclear application boundaries, resource conflicts

## Implementation Details

### Namespace Naming Convention
```yaml
# Pattern: {app-name}-{environment}
# Examples:
- app-web-prod
- app-web-staging  
- app-web-dev
- app-database-prod
- app-analytics-prod
- shared-monitoring-prod
- shared-storage-prod
```

### Standard Namespace Template
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: app-web-prod
  labels:
    application: web
    environment: production
    tier: frontend
    cost-center: "12345"
    owner: web-team
  annotations:
    backup-policy: "daily"
    monitoring-enabled: "true"
    network-policy: "strict"
    compliance-level: "high"
spec:
  finalizers:
  - kubernetes
---
# Resource Quota per namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: app-web-prod
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    persistentvolumeclaims: "20"
    services: "10"
    secrets: "20"
    configmaps: "20"
---
# Limit Range per namespace
apiVersion: v1
kind: LimitRange
metadata:
  name: resource-limits
  namespace: app-web-prod
spec:
  limits:
  - default:
      cpu: "2"
      memory: 4Gi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    type: Container
  - default:
      cpu: "8"
      memory: 16Gi
    defaultRequest:
      cpu: "2"
      memory: 4Gi
    type: PersistentVolumeClaim
```

### Cross-Namespace Communication Policy
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-communication
  namespace: app-web-prod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow ingress from gateway namespace
  - from:
    - namespaceSelector:
        matchLabels:
          name: shared-gateway-prod
  egress:
  # Allow egress to database namespace
  - to:
    - namespaceSelector:
        matchLabels:
          application: database
          environment: production
    ports:
    - protocol: TCP
      port: 5432
  # Allow egress to shared services
  - to:
    - namespaceSelector:
        matchLabels:
          tier: shared-services
```

## Governance and Management

### Namespace Lifecycle Management
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: namespace-manager
  namespace: argocd
spec:
  project: infrastructure
  source:
    repoURL: https://git.company.com/infrastructure/namespaces
    targetRevision: HEAD
    path: namespaces
  destination:
    server: https://kubernetes.default.svc
  syncPolicy:
    automated:
      prune: false
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

### RBAC Template per Namespace
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: app-web-prod
  name: app-admin
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["*"]
- apiGroups: ["apps", "extensions"]
  resources: ["*"]
  verbs: ["*"]
- apiGroups: ["kubevirt.io"]
  resources: ["*"]
  verbs: ["*"]
- apiGroups: ["cdi.kubevirt.io"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-admin-binding
  namespace: app-web-prod
subjects:
- kind: Group
  name: web-team
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: app-admin
  apiGroup: rbac.authorization.k8s.io
```

## Consequences

### Positive
- **Clear Ownership**: Each namespace has a clear business owner
- **Improved Security**: Strong isolation boundaries between applications
- **Simplified Operations**: Easier to manage, monitor, and troubleshoot
- **Better Resource Management**: Clear resource attribution and quota management
- **Compliance Ready**: Audit boundaries align with business applications

### Negative
- **Initial Complexity**: Requires careful planning of namespace boundaries
- **Cross-App Dependencies**: Need clear policies for inter-namespace communication
- **Shared Services Challenge**: Need strategy for common services (monitoring, logging)
- **Learning Curve**: Teams need to understand namespace-based organization

## Migration Strategy

### Phase 1: Planning and Design
1. Inventory existing applications and their dependencies
2. Define namespace naming conventions and standards
3. Create RBAC and network policy templates

### Phase 2: Shared Services Migration
1. Create shared services namespaces (monitoring, logging, gateway)
2. Migrate common infrastructure components
3. Establish cross-namespace communication patterns

### Phase 3: Application Migration
1. Start with least critical applications
2. Create application-specific namespaces with proper quotas and policies
3. Migrate workloads and validate functionality

### Phase 4: Governance Implementation
1. Implement automated namespace provisioning
2. Enable monitoring and alerting per namespace
3. Create operational runbooks for namespace management

## Monitoring and Compliance

### Namespace-Level Metrics
- Resource utilization per namespace
- Cost attribution per application
- Security policy violations
- Cross-namespace communication patterns

### Compliance Reporting
- Resource usage reports per business unit
- Security posture per application
- Audit logs scoped to business context
- Data residency compliance per namespace

This topology provides a solid foundation for managing complex multi-tenant RH OVE environments while maintaining security, operational clarity, and business alignment.
