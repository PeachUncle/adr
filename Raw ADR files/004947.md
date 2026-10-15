# ADR-001: Multi-tenant Kubernetes Namespace Isolation Strategy

**Status**: Accepted
**Date**: 2024-12-11
**Deciders**: Platform Architecture Team

## Context

Aegis is a multi-tenant SaaS platform serving government agencies and contractors with varying security clearance levels (IL2, IL4, IL5). We need to ensure complete data isolation between tenants while maximizing resource efficiency on shared Kubernetes infrastructure.

**Requirements**:

- FedRAMP Moderate compliance (NIST 800-53 AC-3, SC-7)
- Complete data isolation between tenants
- Support for cross-tenant auditor role (read-only access for compliance)
- Efficient resource utilization
- Support for namespace-scoped Gatekeeper policies
- Integration with Platform One Big Bang deployment model

**Constraints**:

- Must work with both AKS-Gov and EKS-Gov
- Must support Istio service mesh with mTLS
- Cannot use cluster-per-tenant (cost prohibitive at scale)

## Decision

We will implement **namespace-based multi-tenancy** with the following architecture:

### 1. Namespace Structure

Each tenant receives a dedicated Kubernetes namespace:

```
aegis-tenant-<tenant-slug>
```

Example:

- `aegis-tenant-acme-corp`
- `aegis-tenant-dod-agency-x`

### 2. Isolation Mechanisms

#### Network Isolation (NIST 800-53 SC-7)

- Calico Network Policies (default deny-all)
- Explicit allow rules only for:
  - Tenant namespace → Shared services (PostgreSQL, Redis)
  - Istio sidecar traffic (mTLS enforced)
  - Egress to S3-Gov for evidence storage

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: aegis-tenant-acme-corp
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

#### Resource Quotas (NIST 800-53 SC-6)

- CPU limits per namespace (based on tenant tier)
- Memory limits per namespace
- Storage limits (PVC count and capacity)
- Pod count limits

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: aegis-tenant-acme-corp
spec:
  hard:
    requests.cpu: '10'
    requests.memory: 20Gi
    limits.cpu: '20'
    limits.memory: 40Gi
    persistentvolumeclaims: '10'
```

#### RBAC Isolation (NIST 800-53 AC-3)

- Service accounts scoped to namespace
- RoleBindings (not ClusterRoleBindings) for tenant users
- ClusterRole with namespace-scoped permissions

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: tenant-admin
  namespace: aegis-tenant-acme-corp
subjects:
  - kind: Group
    name: acme-corp-admins
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: aegis-tenant-admin
  apiGroup: rbac.authorization.k8s.io
```

#### Pod Security Standards

- Enforce `restricted` Pod Security Standard per namespace
- No privileged containers allowed
- No hostPath volumes
- Drop all capabilities

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: aegis-tenant-acme-corp
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 3. Shared Services Architecture

Shared services run in dedicated namespaces:

- `aegis-system` - Aegis API, Workers, Web UI
- `aegis-data` - PostgreSQL, Redis (with row-level security)
- `istio-system` - Istio control plane
- `gatekeeper-system` - OPA Gatekeeper

#### Database Multi-tenancy (PostgreSQL Row-Level Security)

All tables include `tenantId` column with RLS policies:

```sql
CREATE POLICY tenant_isolation ON evidence
  USING (tenantId = current_setting('app.current_tenant')::uuid);

ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
```

Application sets session variable before queries:

```sql
SET app.current_tenant = '<tenant-uuid>';
```

### 4. Cross-Tenant Auditor Access

For compliance auditors requiring cross-tenant read access:

- ClusterRole with read-only permissions across all `aegis-tenant-*` namespaces
- Audit logs for all cross-tenant access (NIST 800-53 AU-2)
- Time-limited RBAC tokens (maximum 8 hours)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: aegis-auditor
rules:
  - apiGroups: ['']
    resources: ['pods', 'services', 'configmaps']
    verbs: ['get', 'list']
    resourceNames: []
  - apiGroups: ['apps']
    resources: ['deployments', 'statefulsets']
    verbs: ['get', 'list']
```

### 5. Gatekeeper Policy Enforcement

Namespace-scoped Constraint instances:

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: tenant-required-labels
spec:
  match:
    namespaces: ['aegis-tenant-acme-corp']
  parameters:
    labels:
      - key: 'tenant'
        value: 'acme-corp'
```

## Consequences

### Positive

✅ **Cost-efficient**: Shared cluster reduces infrastructure costs vs. cluster-per-tenant
✅ **Compliance**: Meets NIST 800-53 AC-3 (Access Enforcement) and SC-7 (Boundary Protection)
✅ **Scalability**: Can support 1000+ tenants on single cluster
✅ **Flexibility**: Easy to migrate tenant to dedicated cluster if needed (same namespace structure)
✅ **Auditor-friendly**: Cross-tenant read access without breaking isolation
✅ **Big Bang compatible**: Works with Platform One deployment model

### Negative

❌ **Noisy neighbor risk**: Resource quotas must be carefully tuned
❌ **Blast radius**: Cluster-level security issue affects all tenants (mitigated by private cluster)
❌ **Operational complexity**: More namespaces to manage vs. single namespace
❌ **Istio overhead**: Service mesh adds latency (~5ms) and resource usage

### Neutral

⚖️ **Migration path**: If IL5+ requires dedicated clusters, namespace structure remains the same
⚖️ **Database performance**: Row-level security adds ~2% query overhead (acceptable for compliance)

## Alternatives Considered

### Alternative 1: Cluster-per-tenant

**Rejected**: Cost prohibitive (each cluster ~$500/month), operational overhead unmanageable at scale.

### Alternative 2: Single namespace with label-based isolation

**Rejected**: Does not meet NIST 800-53 requirement for boundary protection (SC-7). Gatekeeper policies cannot enforce tenant isolation without namespaces.

### Alternative 3: Virtual clusters (vCluster)

**Rejected**: Adds significant complexity, not supported by Platform One Big Bang, unproven in government cloud environments.

## Implementation Notes

- Namespace provisioning automated via Aegis API (Kubernetes client)
- Terraform creates namespace resources during tenant onboarding
- NetworkPolicies generated dynamically based on tenant settings
- FluxCD manages per-namespace GitOps deployments

## References

- NIST 800-53 Rev 5: AC-3 (Access Enforcement), SC-7 (Boundary Protection), SC-6 (Resource Availability)
- [Kubernetes Multi-tenancy SIG](https://github.com/kubernetes-sigs/multi-tenancy)
- [Platform One Big Bang Docs](https://repo1.dso.mil/platform-one/big-bang/bigbang)
- FedRAMP Rev 5 Baseline Controls
