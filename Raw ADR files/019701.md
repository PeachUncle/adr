# ADR-010: OpenShift GitOps Operator Requirement

**Status:** Accepted
**Date:** 2025-10-25
**Decision Makers:** Development Team
**Consulted:** Validated Patterns Community
**Informed:** All Contributors

## Context and Problem Statement

The Validated Patterns framework relies heavily on GitOps principles for deployment and management. OpenShift GitOps (based on ArgoCD) is a fundamental requirement for pattern deployment. We need to establish:

1. How to ensure OpenShift GitOps is installed
2. When to install it (prerequisites vs. automatic installation)
3. How to validate the installation
4. Configuration requirements for Validated Patterns

## Decision Drivers

- **GitOps-First Approach**: Validated Patterns are designed around GitOps workflows
- **Cluster Prerequisites**: OpenShift GitOps must be available before pattern deployment
- **Automation**: Installation should be automated where possible
- **Validation**: Must verify operator is installed and functional
- **Multi-Cluster Support**: Consider hub and spoke cluster scenarios

## Considered Options

### Option 1: Manual Installation (User Responsibility)
- Users must install OpenShift GitOps before using the toolkit
- Documentation provides installation instructions
- Prerequisites role only validates installation

**Pros:**
- Simple implementation
- Users have full control
- No assumptions about cluster state

**Cons:**
- Additional manual step for users
- Potential for errors
- Inconsistent configurations

### Option 2: Automatic Installation (Toolkit Responsibility)
- Toolkit automatically installs OpenShift GitOps if missing
- Prerequisites role handles installation
- Idempotent installation logic

**Pros:**
- Better user experience
- Consistent configuration
- Fewer manual steps

**Cons:**
- Requires cluster-admin permissions
- More complex implementation
- May conflict with existing installations

### Option 3: Hybrid Approach (Validate + Optional Install)
- Prerequisites role validates installation
- Separate role/playbook for installation
- User chooses when to install

**Pros:**
- Flexible approach
- Clear separation of concerns
- Supports both scenarios

**Cons:**
- More components to maintain
- Requires clear documentation

## Decision Outcome

**Chosen Option: Option 3 - Hybrid Approach**

We will implement a hybrid approach:

1. **Prerequisites Role**: Validates OpenShift GitOps is installed
2. **Separate Installation Role**: `validated_patterns_gitops_install` role for automated installation
3. **User Choice**: Users can install manually or use our automation

### Implementation Details

#### 1. Prerequisites Validation
```yaml
# ansible/roles/validated_patterns_prerequisites/tasks/check_operators.yml
- name: Check for OpenShift GitOps operator
  assert:
    that:
      - installed_operator_names | select('search', 'openshift-gitops') | list | length > 0
    fail_msg: "OpenShift GitOps operator not found. Please install it first."
    success_msg: "✅ OpenShift GitOps operator is installed"
```

#### 2. Installation Role
Create `ansible/roles/validated_patterns_gitops_install/` with:
- Operator subscription creation
- Namespace setup
- RBAC configuration
- Validation checks

#### 3. Installation Playbook
```yaml
# ansible/playbooks/install_gitops.yml
- name: Install OpenShift GitOps Operator
  hosts: localhost
  roles:
    - validated_patterns_gitops_install
```

### Configuration Requirements

**Operator Subscription:**
```yaml
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-gitops-operator
  namespace: openshift-operators
spec:
  channel: stable
  name: openshift-gitops-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
```

**Required Namespaces:**
- `openshift-gitops`: Main GitOps namespace
- `openshift-operators`: Operator installation namespace

**RBAC Requirements:**
- Cluster-admin permissions for installation
- ArgoCD service account with appropriate permissions

## Consequences

### Positive

- ✅ Clear prerequisite validation
- ✅ Automated installation option available
- ✅ Flexible approach supports different use cases
- ✅ Consistent GitOps configuration
- ✅ Better error messages for missing operator

### Negative

- ❌ Additional role to maintain
- ❌ Requires documentation for both paths
- ❌ Installation requires cluster-admin permissions

### Neutral

- 📝 Users must choose installation method
- 📝 Prerequisites role will fail if operator missing
- 📝 Installation role is optional but recommended

## Implementation Plan

### Phase 1: Prerequisites Validation (Current)
- ✅ Prerequisites role validates OpenShift GitOps
- ✅ Clear error messages when missing
- ✅ Documentation of requirement

### Phase 2: Installation Role (Week 8)
- [ ] Create `validated_patterns_gitops_install` role
- [ ] Implement operator subscription
- [ ] Add namespace and RBAC setup
- [ ] Create installation playbook
- [ ] Add validation checks

### Phase 3: Documentation (Week 11)
- [ ] Document manual installation steps
- [ ] Document automated installation
- [ ] Add troubleshooting guide
- [ ] Update quick start guide

## Validation Criteria

The OpenShift GitOps installation is considered successful when:

1. ✅ Operator CSV is in "Succeeded" phase
2. ✅ `openshift-gitops` namespace exists
3. ✅ ArgoCD instance is running
4. ✅ ArgoCD server is accessible
5. ✅ ArgoCD CLI can authenticate

## References

- [OpenShift GitOps Documentation](https://docs.openshift.com/container-platform/latest/cicd/gitops/understanding-openshift-gitops.html)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Validated Patterns GitOps Architecture](https://validatedpatterns.io/learn/gitops/)
- [ADR-002: Ansible Role Architecture](ADR-002-ansible-role-architecture.md)
- [ADR-003: Validation Framework](ADR-003-validation-framework.md)

## Related ADRs

- **ADR-002**: Defines role architecture for installation role
- **ADR-003**: Defines validation framework for prerequisites
- **ADR-007**: Ansible Navigator deployment approach

## Notes

- OpenShift GitOps is based on ArgoCD upstream project
- Operator is available in OperatorHub by default
- Installation typically takes 2-3 minutes
- Requires OpenShift 4.12 or higher
- Multi-cluster scenarios may require additional configuration

---

**Last Updated:** 2025-10-25
**Status:** Accepted - Implementation in progress
