# ADR-012: Validated Patterns Common Framework Integration

**Status:** Accepted
**Date:** 2025-10-25
**Deciders:** Development Team
**Technical Story:** Phase 3 Week 8 - Understanding Validated Patterns deployment architecture

## Context

During Phase 3 testing, we discovered that the repository includes a `common/` directory containing the Validated Patterns common framework. This framework provides:

1. **Makefile targets** for pattern deployment (`operator-deploy`, `operator-upgrade`)
2. **Shell scripts** for pattern management, secrets handling, and validation
3. **Integration with Helm charts** from the Validated Patterns organization
4. **Multisource architecture** support for GitOps deployments

The term "operator" in `operator-deploy` is **misleading** - it refers to the deployment **operation**, not a Kubernetes operator. There is no Validated Patterns operator to install.

### Key Discovery

The `common/Makefile` target `operator-deploy` (line 103-105) does NOT install an operator:

```makefile
.PHONY: operator-deploy
operator-deploy operator-upgrade: validate-prereq $(VALIDATE_ORIGIN) validate-cluster
	@common/scripts/deploy-pattern.sh $(PATTERN_NAME) $(PATTERN_INSTALL_CHART) $(HELM_OPTS)
```

Instead, it:
1. Validates prerequisites (Python kubernetes module, kubernetes.core collection)
2. Validates git origin and cluster connectivity
3. Deploys the pattern using `helm template` + `oc apply`

## Decision

We will integrate the Validated Patterns common framework as a git subtree and document its purpose, architecture, and relationship to our Ansible roles.

### Framework Components

**1. Common Framework (common/ directory)**
- **Source:** https://github.com/validatedpatterns/common.git
- **Branch:** main (multisource-enabled, slimmed down)
- **Integration:** Git subtree
- **Purpose:** Provides Makefile targets and scripts for pattern deployment
- **Structure:**
  - `Makefile` - Pattern deployment targets
  - `scripts/` - 14 shell scripts for automation
  - `requirements.yml` - Ansible collection dependencies
  - `README.md`, `LICENSE`, `Changes.md` - Documentation

**2. Helm Charts (OCI repositories)**
- `oci://quay.io/validatedpatterns/pattern-install` - Pattern installation chart
- `oci://quay.io/validatedpatterns/clustergroup` - Cluster group management (v0.9.33)
- `oci://quay.io/validatedpatterns/vp-rbac` - RBAC management
- Additional charts: hashicorp-vault, golang-external-secrets, acm, letsencrypt

**3. Ansible Collection**
- **Name:** rhvp.cluster_utils
- **Source:** https://github.com/validatedpatterns/rhvp.cluster_utils
- **Purpose:** Cluster utilities and pattern automation
- **Status:** Not publicly available on Ansible Galaxy (internal/restricted)
- **Playbooks Used:**
  - `rhvp.cluster_utils.process_secrets` - Secret management
  - `rhvp.cluster_utils.vault` - Vault operations
  - `rhvp.cluster_utils.iib_ci` - Index Image Bundle installation

**4. Common Scripts (common/scripts/)**

The framework provides 14 shell scripts for pattern automation:

| Script | Purpose | Key Functions |
|--------|---------|---------------|
| `deploy-pattern.sh` | Deploy pattern via Helm | Retries up to 20 times, uses `helm template` + `oc apply` |
| `validate-names-length.sh` | DNS name validation | Ensures resource names < 63 chars |
| `pattern-util.sh` | Utility container runner | Runs commands in `quay.io/validatedpatterns/utility-container` |
| `process-secrets.sh` | Secret processing | Calls `rhvp.cluster_utils.process_secrets` playbook |
| `vault-utils.sh` | Vault operations | Wrapper for `rhvp.cluster_utils.vault` playbook |
| `argocd-login.sh` | ArgoCD authentication | Logs into all ArgoCD instances in cluster |
| `manage-secret-app.sh` | Secret app management | Add/remove vault or golang-external-secrets apps |
| `manage-secret-namespace.sh` | Namespace management | Create/delete secret-related namespaces |
| `set-secret-backend.sh` | Backend configuration | Switch between vault/kubernetes/none |
| `load-k8s-secrets.sh` | Kubernetes secrets | Load secrets to Kubernetes backend |
| `display-secrets-info.sh` | Secret information | Display secret configuration details |
| `determine-main-clustergroup.sh` | Clustergroup detection | Find main clustergroup from values files |
| `determine-pattern-name.sh` | Pattern name detection | Extract pattern name from values-global.yaml |
| `determine-secretstore-backend.sh` | Backend detection | Determine current secret backend |
| `preview.sh` | Template preview | Preview rendered templates for clustergroup |
| `preview-all.sh` | Full preview | Preview all hub and managed cluster templates |
| `write-token-kubeconfig.sh` | Kubeconfig generation | Create token-based kubeconfig |
| `make-common-subtree.sh` | Subtree setup | Initialize common framework as git subtree |

### Architecture Clarification

**What IS deployed:**
- ✅ OpenShift GitOps (ArgoCD) operator
- ✅ Helm charts (clustergroup, pattern-install, etc.)
- ✅ ArgoCD applications and AppProjects
- ✅ Namespaces, ServiceAccounts, RBAC resources

**What is NOT deployed:**
- ❌ No "Validated Patterns operator" (doesn't exist)
- ❌ No custom CRDs beyond ArgoCD's
- ❌ No operator-sdk based operator

## Consequences

### Positive

1. **Standard Framework:**
   - Uses proven Validated Patterns architecture
   - Consistent with Red Hat's validated patterns
   - Well-documented and community-supported

2. **Makefile Integration:**
   - Provides standard targets: `operator-deploy`, `validate-cluster`, `load-secrets`
   - Simplifies pattern deployment workflow
   - Includes validation and health checks

3. **Multisource Architecture:**
   - Helm charts pulled from OCI registries
   - Git repositories for application manifests
   - Separation of concerns (charts vs. config)

4. **Secrets Management:**
   - Supports multiple backends: Vault, Kubernetes, none
   - External Secrets Operator integration
   - Flexible secret loading mechanisms

### Negative

1. **Confusing Terminology:**
   - `operator-deploy` target name implies operator installation
   - May confuse developers looking for an operator
   - Requires documentation to clarify

2. **Git Subtree Complexity:**
   - Subtree updates require specific git commands
   - Potential merge conflicts with upstream
   - Need to track common framework version

3. **Collection Availability:**
   - rhvp.cluster_utils not on Ansible Galaxy
   - May require special access or mirroring
   - Installation failures need graceful handling

4. **Dependency Chain:**
   - Requires Helm, oc/kubectl, yq, git
   - Python kubernetes module required
   - kubernetes.core Ansible collection required

### Neutral

1. **Framework Updates:**
   - Need to periodically sync with upstream common
   - May require testing after updates
   - Version compatibility considerations

2. **Pattern Structure:**
   - Requires values-global.yaml configuration
   - Specific directory structure expected
   - Makefile targets assume certain paths

## Implementation

### 1. Common Framework Integration

The common framework is integrated as a git subtree:

```bash
# Initial import (already done)
git remote add -f common-upstream https://github.com/validatedpatterns/common.git
git subtree add --prefix common common-upstream/main --squash

# Future updates
git fetch common-upstream
git merge -s subtree -Xtheirs -Xsubtree=common common-upstream/main
```

### 2. Required Configuration

**values-global.yaml** (pattern root):
```yaml
global:
  pattern: common  # Pattern name
  targetRevision: main  # Git branch

main:
  multiSourceConfig:
    enabled: true
    clusterGroupChartVersion: 0.9.*
  git:
    repoURL: https://github.com/tosin2013/validated-patterns-ansible-toolkit.git
    revision: main
```

### 3. Makefile Targets

**Pattern Deployment:**
```bash
# Deploy pattern (NOT installing an operator!)
make -f common/Makefile operator-deploy

# Validate cluster before deployment
make -f common/Makefile validate-cluster

# Check ArgoCD application health
make -f common/Makefile argo-healthcheck
```

**Secrets Management:**
```bash
# Load secrets to backend
make -f common/Makefile load-secrets

# Switch to Vault backend
make -f common/Makefile secrets-backend-vault

# Switch to Kubernetes backend
make -f common/Makefile secrets-backend-kubernetes
```

### 4. Integration with Our Ansible Roles

Our 6 Ansible roles provide the same functionality as common framework scripts, but in idempotent, testable Ansible format:

| Our Role | Common Framework Equivalent | Scripts/Targets Used |
|----------|----------------------------|---------------------|
| **validated_patterns_prerequisites** | `validate-prereq`, `validate-cluster` | Makefile validation targets |
| **validated_patterns_common** | `operator-deploy` | `deploy-pattern.sh`, `validate-names-length.sh` |
| **validated_patterns_deploy** | ArgoCD app deployment | `argocd-login.sh`, pattern-install chart |
| **validated_patterns_gitea** | Git repository setup | Custom (not in common framework) |
| **validated_patterns_secrets** | `load-secrets`, backend switching | `process-secrets.sh`, `vault-utils.sh`, `set-secret-backend.sh`, `manage-secret-app.sh` |
| **validated_patterns_validate** | `argo-healthcheck`, validation | `argocd-login.sh`, Makefile health checks |

**Key Differences:**

1. **Idempotency:** Our roles use Ansible's idempotent modules; scripts may not be idempotent
2. **Testing:** Our roles have molecule tests; scripts have no automated tests
3. **Error Handling:** Ansible provides structured error handling; scripts use exit codes
4. **Modularity:** Roles can be used independently; scripts assume full framework
5. **Documentation:** Roles have structured docs; scripts have inline comments
6. **Reusability:** Roles can be imported in any playbook; scripts require common/ structure

### 5. Script Functionality Details

**Pattern Deployment (deploy-pattern.sh):**
```bash
# Retries deployment up to 20 times with 15-second delays
# Handles CRD installation timing issues
helm template --include-crds --name-template $PATTERN_NAME $PATTERN_INSTALL_CHART $HELM_OPTS | oc apply -f-
```

**Name Validation (validate-names-length.sh):**
```bash
# Validates DNS-compatible names (max 63 chars)
# Formula: (2 * clusterGroup.name length) + pattern length + 16 < 63
# Example: hub-gitops-server-common-hub (30 chars) ✅
```

**Utility Container (pattern-util.sh):**
```bash
# Runs commands in containerized environment
# Mounts: $HOME, current directory, SSL certificates
# Supports: podman 4.3.0+, disconnected environments
podman run -it --rm quay.io/validatedpatterns/utility-container $COMMAND
```

**Secret Management (process-secrets.sh):**
```bash
# Processes secrets based on backend (vault/kubernetes/none)
ansible-playbook -e pattern_name=$PATTERN_NAME \
                 -e secrets_backing_store=$BACKEND \
                 rhvp.cluster_utils.process_secrets
```

**ArgoCD Login (argocd-login.sh):**
```bash
# Automatically logs into all ArgoCD instances
# Extracts admin password from cluster secrets
# Supports multiple ArgoCD instances per cluster
for NAMESPACE in $ARGOCD_NAMESPACES; do
    PASSWORD=$(oc get secret $ARGOCD_INSTANCE-cluster -n $NAMESPACE -o jsonpath='{.data.admin\.password}' | base64 -d)
    argocd login --insecure $SERVER_URL --username admin --password $PASSWORD
done
```

**Secret Backend Management:**
```bash
# Switch to Vault backend
make -f common/Makefile secrets-backend-vault
# Calls: set-secret-backend.sh vault
#        manage-secret-app.sh vault present
#        manage-secret-app.sh golang-external-secrets present

# Switch to Kubernetes backend
make -f common/Makefile secrets-backend-kubernetes
# Calls: set-secret-backend.sh kubernetes
#        manage-secret-namespace.sh validated-patterns-secrets present
#        manage-secret-app.sh vault absent
```

### 6. Helm Chart Deployment Flow

```mermaid
graph TD
    A[make operator-deploy] --> B[validate-prereq]
    B --> C[validate-cluster]
    C --> D[deploy-pattern.sh]
    D --> E[helm template pattern-install]
    E --> F[oc apply manifests]
    F --> G[Pattern deployed]
    G --> H[ArgoCD syncs applications]
```

### 7. Secret Management Flow

```mermaid
graph TD
    A[make load-secrets] --> B[process-secrets.sh]
    B --> C[determine-secretstore-backend.sh]
    C --> D{Backend Type?}
    D -->|Vault| E[rhvp.cluster_utils.vault]
    D -->|Kubernetes| F[load-k8s-secrets.sh]
    D -->|None| G[Skip secret loading]
    E --> H[Secrets loaded to Vault]
    F --> I[Secrets loaded to K8s]
```

## Alternatives Considered

### 1. Fork Common Framework

**Pros:**
- Full control over framework code
- Can customize for our needs
- No upstream sync issues

**Cons:**
- Lose upstream updates
- Maintenance burden
- Diverge from standard patterns

**Decision:** Rejected - Use subtree to stay aligned with upstream

### 2. Ignore Common Framework

**Pros:**
- Simpler repository structure
- No git subtree complexity
- Full custom implementation

**Cons:**
- Reinvent the wheel
- Miss standard tooling
- Not compatible with VP patterns

**Decision:** Rejected - Leverage existing framework

### 3. Use Common as Submodule

**Pros:**
- Cleaner git history
- Explicit version tracking
- Easier updates

**Cons:**
- Requires submodule initialization
- More complex for contributors
- Submodule pointer management

**Decision:** Rejected - Subtree is VP standard

## Compliance

### ADR-002: Ansible Role Architecture
- Our roles implement the same functionality as common framework
- Roles can be used independently or with common Makefile
- Maintain compatibility with VP architecture

### ADR-007: Ansible Navigator Deployment
- Common framework uses ansible-navigator for playbooks
- Execution environment must include required collections
- Makefile targets integrate with ansible-navigator

### ADR-011: Helm Installation
- Common framework requires Helm for pattern deployment
- `deploy-pattern.sh` uses `helm template`
- Helm charts pulled from OCI registries

## Documentation Updates Required

1. **README.md:**
   - Clarify "operator-deploy" terminology
   - Document common framework purpose
   - Add Makefile target reference

2. **docs/tutorials/:**
   - Add "Using Common Framework" tutorial
   - Document Makefile targets
   - Explain multisource architecture

3. **docs/reference/:**
   - Document common/ directory structure
   - List available Makefile targets
   - Reference upstream documentation

4. **docs/explanation/:**
   - Explain why there's no VP operator
   - Clarify deployment architecture
   - Describe Helm chart relationships

## Monitoring and Validation

### Health Checks

```bash
# Validate pattern deployment
make -f common/Makefile argo-healthcheck

# Check cluster prerequisites
make -f common/Makefile validate-cluster

# Verify git origin
make -f common/Makefile validate-origin
```

### Troubleshooting

**Issue:** "operator-deploy" fails with missing prerequisites
```bash
# Solution: Install prerequisites
pip install kubernetes
ansible-galaxy collection install kubernetes.core
```

**Issue:** Helm chart not found
```bash
# Solution: Update Helm repositories
helm repo update
helm search repo validatedpatterns
```

**Issue:** rhvp.cluster_utils collection not found
```bash
# Solution: Make collection installation optional (already done in our role)
# See: ansible/roles/validated_patterns_common/tasks/install_collection.yml
```

## References

### Official Documentation
- [Validated Patterns Common Framework](https://github.com/validatedpatterns/common)
- [Validated Patterns Documentation](https://validatedpatterns.io)
- [Clustergroup Chart](https://github.com/validatedpatterns/clustergroup-chart)
- [Pattern Install Chart](https://github.com/validatedpatterns/pattern-install-chart)
- [rhvp.cluster_utils Collection](https://github.com/validatedpatterns/rhvp.cluster_utils)

### Helm Charts
- [Validated Patterns Helm Repository](https://charts.validatedpatterns.io)
- [HashiCorp Vault Chart](https://github.com/validatedpatterns/hashicorp-vault-chart)
- [Golang External Secrets Chart](https://github.com/validatedpatterns/golang-external-secrets-chart)
- [ACM Chart](https://github.com/validatedpatterns/acm-chart)
- [LetsEncrypt Chart](https://github.com/validatedpatterns/letsencrypt-chart)

### Container Images
- [Utility Container](https://quay.io/repository/validatedpatterns/utility-container)
- [Ansible EE](https://quay.io/repository/validatedpatterns/ansible-ee)

## Quick Reference

### Common Makefile Targets

```bash
# Pattern Deployment
make -f common/Makefile operator-deploy          # Deploy pattern
make -f common/Makefile operator-upgrade         # Upgrade pattern
make -f common/Makefile uninstall                # Remove pattern

# Validation
make -f common/Makefile validate-prereq          # Check prerequisites
make -f common/Makefile validate-cluster         # Check cluster
make -f common/Makefile validate-origin          # Check git origin
make -f common/Makefile validate-schema          # Validate values files
make -f common/Makefile argo-healthcheck         # Check ArgoCD apps

# Secrets Management
make -f common/Makefile load-secrets             # Load secrets
make -f common/Makefile secrets-backend-vault    # Switch to Vault
make -f common/Makefile secrets-backend-kubernetes  # Switch to K8s
make -f common/Makefile secrets-backend-none     # Disable secrets

# Preview and Testing
make -f common/Makefile show                     # Preview templates
make -f common/Makefile preview-all              # Preview all clusters
make -f common/Makefile qe-tests                 # Run QE tests
make -f common/Makefile super-linter             # Run linter

# Utilities
make -f common/Makefile token-kubeconfig         # Create token kubeconfig
make -f common/Makefile help                     # Show help
```

### Environment Variables

```bash
# Pattern Configuration
export PATTERN_NAME="common"                     # Pattern name
export TARGET_BRANCH="main"                      # Git branch
export TARGET_ORIGIN="origin"                    # Git remote
export TARGET_SITE="hub"                         # Cluster group name

# Secrets
export TOKEN_SECRET="git-secret"                 # Git token secret name
export TOKEN_NAMESPACE="openshift-operators"     # Secret namespace
export VALUES_SECRET="values-secret"             # Values secret name

# Helm Options
export EXTRA_HELM_OPTS="--set foo=bar"          # Additional Helm args
export PATTERN_INSTALL_CHART="oci://..."        # Custom chart location

# Ansible Options
export EXTRA_PLAYBOOK_OPTS="-vvv"               # Ansible verbosity

# Disconnected Environments
export PATTERN_DISCONNECTED_HOME="registry.local:5000"  # Local registry
export INDEX_IMAGES="registry.local:5000/iib:123"       # Index images

# Kubernetes Authentication
export KUBECONFIG="~/.kube/config"              # Kubeconfig path
export K8S_AUTH_HOST="https://api.cluster"      # API server
export K8S_AUTH_TOKEN="sha256~..."              # Auth token
```

### Script Usage Examples

```bash
# Deploy pattern with custom options
EXTRA_HELM_OPTS="--set global.targetRevision=develop" \
  common/scripts/deploy-pattern.sh common oci://quay.io/validatedpatterns/pattern-install

# Validate resource names
common/scripts/validate-names-length.sh

# Process secrets for pattern
common/scripts/process-secrets.sh my-pattern

# Login to ArgoCD instances
common/scripts/argocd-login.sh

# Run command in utility container
common/scripts/pattern-util.sh make operator-deploy

# Switch secret backend to Vault
common/scripts/set-secret-backend.sh vault
common/scripts/manage-secret-app.sh vault present
common/scripts/manage-secret-app.sh golang-external-secrets present

# Load secrets to Kubernetes
common/scripts/load-k8s-secrets.sh my-pattern

# Preview clustergroup templates
common/scripts/preview.sh hub my-app https://github.com/org/repo main
```

### values-global.yaml Template

```yaml
global:
  pattern: common                    # Pattern name (required)
  targetRevision: main               # Git branch (required)
  extraValueFiles: []                # Additional values files

  options:
    syncPolicy: Automatic            # ArgoCD sync policy
    applicationRetryLimit: 20        # Retry limit
    installPlanApproval: Automatic   # Operator install approval
    useCSV: true                     # Use ClusterServiceVersion

  secretStore:
    backend: vault                   # vault, kubernetes, or none

  secretLoader:
    disabled: false                  # Disable secret loading

main:
  multiSourceConfig:
    enabled: true                    # Required for slimmed-down common
    clusterGroupChartVersion: 0.9.*  # Clustergroup chart version

  git:
    repoURL: https://github.com/org/repo  # Git repository
    revision: main                   # Git branch
    repoUpstreamURL: ""              # Upstream repo (for forks)

  tokenSecret: ""                    # Git token secret (for private repos)
  tokenSecretNamespace: openshift-operators

  analyticsUUID: ""                  # Analytics UUID (optional)

clusterGroup:
  name: hub                          # Cluster group name (required)
  isHubCluster: true                 # Is this the hub cluster?
  targetCluster: in-cluster          # Target cluster name

  applications: {}                   # ArgoCD applications
  namespaces: []                     # Namespaces to create
  subscriptions: {}                  # Operator subscriptions

  sharedValueFiles: []               # Shared values files
  managedClusterGroups: {}           # Managed cluster groups
```

## Notes

- The common framework is a **git subtree**, not a submodule
- `operator-deploy` is a **Makefile target**, not an operator installation
- The framework uses **Helm charts** from OCI registries, not local charts
- **Multisource architecture** is required (enabled in values-global.yaml)
- Our Ansible roles provide the same functionality as common framework scripts
- Scripts assume `yq`, `helm`, `oc`, `podman`, and `ansible-playbook` are available
- The utility container provides a consistent environment for pattern operations
- Secret backends can be switched dynamically without redeploying the pattern
- ArgoCD applications are created by the clustergroup chart, not manually
- Pattern names and clustergroup names must be DNS-compatible (< 63 chars total)

---

**Approved by:** Development Team
**Implementation Date:** 2025-10-25
**Review Date:** 2026-01-25 (Quarterly review)
