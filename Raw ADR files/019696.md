# ADR-005: Gitea Development Environment on OpenShift

**Status:** Accepted
**Date:** 2025-01-24
**Updated:** 2025-01-24 (Added Gitea Operator approach)
**Decision Makers:** Development Team
**Consulted:** DevOps Team, End Users
**Informed:** Stakeholders

## Context and Problem Statement

Developers need a local, self-hosted Git environment for:

1. Testing pattern deployments without affecting production repositories
2. Developing and testing GitOps workflows
3. Experimenting with pattern configurations
4. Training and demonstration purposes
5. Air-gapped or disconnected environments

We need to deploy and configure Gitea on OpenShift as an integrated development environment.

## Decision Drivers

* **Self-Hosted**: Run entirely on OpenShift cluster
* **Lightweight**: Minimal resource consumption
* **GitOps Compatible**: Work with ArgoCD and OpenShift GitOps
* **Easy Setup**: Automated deployment and configuration via Operator
* **Integration**: Connect with pattern deployment workflows
* **Persistence**: Data survives pod restarts
* **User Management**: Support multiple users for training scenarios

## Considered Options

### Option 1: Manual Gitea Deployment
- Deploy Gitea + PostgreSQL manually with YAML manifests
- **Rejected**: More complex, manual configuration required

### Option 2: Gitea Helm Chart
- Use community Helm chart
- **Rejected**: Less integrated with OpenShift, more configuration needed

### Option 3: Gitea Operator (Selected)
- Use Red Hat GPTE Gitea Operator
- Declarative CRD-based deployment
- Automatic user creation and configuration
- **Selected**: Best integration with OpenShift, simplest deployment

## Decision Outcome

**Chosen option:** Option 3 - Gitea Operator from Red Hat GPTE

### Why the Gitea Operator?

The [Red Hat GPTE Gitea Operator](https://github.com/rhpds/gitea-operator) provides:
- **Declarative Management**: CRD-based Gitea instances
- **Automatic Setup**: PostgreSQL, SSL, user creation
- **User Management**: Bulk user creation for training
- **OpenShift Native**: Designed for OpenShift environments
- **Maintained**: Actively maintained by Red Hat GPTE team

### Deployment Architecture

```
Gitea Operator Deployment
├── Gitea Operator (Namespace: gitea-operator)
│   ├── Operator Deployment
│   ├── CRDs (Gitea Custom Resource)
│   └── RBAC (ServiceAccount, Roles, RoleBindings)
│
└── Gitea Instance (Namespace: gitea)
    ├── Gitea Custom Resource (CR)
    ├── Gitea Application (Deployment)
    ├── PostgreSQL Database (Deployment)
    ├── Persistent Storage (PVC)
    ├── Service & Route (HTTPS)
    └── Secrets (Admin & User Credentials)
```

### Directory Structure

```
gitea/
├── operator/
│   └── kustomization.yaml           # Points to operator deployment
├── instance/
│   ├── gitea-instance.yaml          # Gitea CR definition
│   └── namespace.yaml               # Gitea namespace
├── ansible/
│   ├── deploy-gitea-operator.yml    # Ansible playbook
│   └── configure-gitea.yml          # Post-deployment configuration
├── scripts/
│   ├── deploy-gitea.sh              # Quick deployment script
│   ├── create-organizations.sh      # Create orgs via API
│   ├── mirror-repositories.sh       # Mirror pattern repos
│   └── get-credentials.sh           # Retrieve credentials
└── README.md
```

### Implementation Details

#### 1. Deploy Gitea Operator

The Gitea Operator is deployed using Kustomize from the upstream repository:

```bash
# scripts/deploy-gitea.sh
#!/bin/bash
set -euo pipefail

# Function to wait for pod to be ready
wait-for-pod() {
    local pod_name=$1
    local namespace=$2

    echo "Waiting for pod ${pod_name} in namespace ${namespace}..."
    while [[ $(oc get pods ${pod_name} -n ${namespace} \
        -o 'jsonpath={..status.conditions[?(@.type=="Ready")].status}') != "True" ]]; do
        sleep 2
    done
    echo "Pod ${pod_name} is ready!"
}

# Deploy the Gitea Operator
echo "Deploying Gitea Operator..."
oc apply -k https://github.com/rhpds/gitea-operator/OLMDeploy

# Wait for operator to be deployed
echo "Waiting for operator deployment (60 seconds)..."
sleep 60

# Get operator pod name and wait for it
OPERATOR_POD=$(oc get pods -n gitea-operator \
    | grep gitea-operator-controller-manager- \
    | awk '{print $1}')

wait-for-pod "${OPERATOR_POD}" "gitea-operator"

echo "Gitea Operator deployed successfully!"
```

#### 2. Create Gitea Instance

Once the operator is running, create a Gitea instance using the Custom Resource:

```yaml
# gitea/instance/gitea-instance.yaml
apiVersion: pfe.rhpds.com/v1
kind: Gitea
metadata:
  name: gitea-with-admin
  namespace: gitea
spec:
  # SSL/TLS Configuration
  giteaSsl: true

  # Admin User Configuration
  giteaAdminUser: opentlc-mgr
  giteaAdminPassword: ""                    # Empty = auto-generate
  giteaAdminPasswordLength: 32
  giteaAdminEmail: opentlc-mgr@redhat.com

  # Additional Users (for training/multi-user scenarios)
  giteaCreateUsers: true
  giteaGenerateUserFormat: "lab-user"       # Creates: lab-user-0, lab-user-1, etc.
  giteaUserNumber: 1                        # Number of users to create
  giteaUserPasswordLength: 16

  # Optional: Volume sizes (defaults to 4Gi each)
  # giteaVolumeSize: 10Gi
  # postgresqlVolumeSize: 10Gi
```

Deploy the instance:

```bash
# Create gitea namespace
oc new-project gitea

# Deploy Gitea instance
oc apply -f gitea/instance/gitea-instance.yaml -n gitea

# Wait for deployment
oc wait --for=condition=Successful gitea/gitea-with-admin \
    -n gitea --timeout=300s
```

#### 3. Retrieve Credentials

The operator automatically generates and stores credentials:

```bash
# scripts/get-credentials.sh
#!/bin/bash
set -euo pipefail

NAMESPACE="${1:-gitea}"
GITEA_NAME="${2:-gitea-with-admin}"

echo "=== Gitea Credentials ==="
echo

# Get Gitea CR status
GITEA_STATUS=$(oc get gitea ${GITEA_NAME} -n ${NAMESPACE} -o yaml)

# Extract information
GITEA_ROUTE=$(echo "${GITEA_STATUS}" | yq eval '.status.giteaRoute' -)
ADMIN_USER=$(echo "${GITEA_STATUS}" | yq eval '.spec.giteaAdminUser' -)
ADMIN_PASSWORD=$(echo "${GITEA_STATUS}" | yq eval '.status.adminPassword' -)
USER_PASSWORD=$(echo "${GITEA_STATUS}" | yq eval '.status.userPassword' -)

echo "Gitea URL: ${GITEA_ROUTE}"
echo "Admin User: ${ADMIN_USER}"
echo "Admin Password: ${ADMIN_PASSWORD}"
echo
echo "Lab User Password: ${USER_PASSWORD}"
echo

# Test connection
echo "Testing connection..."
curl -k -s "${GITEA_ROUTE}/api/v1/version" | jq .
```

#### 4. What the Operator Creates

The Gitea Operator automatically creates and manages:

- **Namespace**: `gitea` (if using `oc new-project`)
- **PostgreSQL Deployment**: Database backend with PVC
- **Gitea Deployment**: Gitea application with PVC
- **Services**: Internal services for PostgreSQL and Gitea
- **Route**: HTTPS route with edge termination
- **Secrets**: Admin and user credentials in CR status
- **Configuration**: Gitea app.ini configuration
### Ansible Role Implementation

#### Role: `validated_patterns_gitea`

```yaml
# ansible/roles/validated_patterns_gitea/defaults/main.yml
---
# Gitea Operator Configuration
gitea_operator_repo: "https://github.com/rhpds/gitea-operator"
gitea_operator_path: "OLMDeploy"
gitea_operator_namespace: "gitea-operator"
gitea_operator_wait_timeout: 300

# Gitea Instance Configuration
gitea_namespace: "gitea"
gitea_instance_name: "gitea-with-admin"
gitea_ssl_enabled: true

# Admin User
gitea_admin_user: "opentlc-mgr"
gitea_admin_password: ""  # Empty = auto-generate
gitea_admin_password_length: 32
gitea_admin_email: "opentlc-mgr@redhat.com"

# Additional Users (for training scenarios)
gitea_create_users: true
gitea_user_format: "lab-user"
gitea_user_number: 1
gitea_user_password_length: 16

# Volume Sizes
gitea_volume_size: "4Gi"
gitea_postgresql_volume_size: "4Gi"

# Pattern Repository Configuration
gitea_mirror_patterns: true
gitea_pattern_repos:
  - name: "multicloud-gitops"
    url: "https://github.com/validatedpatterns/multicloud-gitops.git"
  - name: "industrial-edge"
    url: "https://github.com/validatedpatterns/industrial-edge.git"
  - name: "medical-diagnosis"
    url: "https://github.com/validatedpatterns/medical-diagnosis.git"
  - name: "common"
    url: "https://github.com/validatedpatterns/common.git"
```

```yaml
# ansible/roles/validated_patterns_gitea/tasks/main.yml
---
- name: Deploy Gitea for Validated Patterns
  block:
    - name: Check if Gitea Operator is already deployed
      k8s_info:
        api_version: v1
        kind: Namespace
        name: "{{ gitea_operator_namespace }}"
      register: operator_namespace

    - name: Deploy Gitea Operator
      when: operator_namespace.resources | length == 0
      block:
        - name: Apply Gitea Operator from upstream
          k8s:
            state: present
            src: "{{ gitea_operator_repo }}/{{ gitea_operator_path }}"
          register: operator_deployment

        - name: Wait for Gitea Operator to be ready
          k8s_info:
            api_version: v1
            kind: Pod
            namespace: "{{ gitea_operator_namespace }}"
            label_selectors:
              - control-plane=controller-manager
          register: operator_pods
          until:
            - operator_pods.resources | length > 0
            - operator_pods.resources[0].status.phase == "Running"
          retries: 30
          delay: 10

    - name: Create Gitea namespace
      k8s:
        state: present
        definition:
          apiVersion: v1
          kind: Namespace
          metadata:
            name: "{{ gitea_namespace }}"
            labels:
              app: gitea
              validated-patterns: "true"

    - name: Deploy Gitea instance
      k8s:
        state: present
        definition:
          apiVersion: pfe.rhpds.com/v1
          kind: Gitea
          metadata:
            name: "{{ gitea_instance_name }}"
            namespace: "{{ gitea_namespace }}"
          spec:
            giteaSsl: "{{ gitea_ssl_enabled }}"
            giteaAdminUser: "{{ gitea_admin_user }}"
            giteaAdminPassword: "{{ gitea_admin_password }}"
            giteaAdminPasswordLength: "{{ gitea_admin_password_length }}"
            giteaAdminEmail: "{{ gitea_admin_email }}"
            giteaCreateUsers: "{{ gitea_create_users }}"
            giteaGenerateUserFormat: "{{ gitea_user_format }}"
            giteaUserNumber: "{{ gitea_user_number }}"
            giteaUserPasswordLength: "{{ gitea_user_password_length }}"
            giteaVolumeSize: "{{ gitea_volume_size }}"
            postgresqlVolumeSize: "{{ gitea_postgresql_volume_size }}"
      register: gitea_instance

    - name: Wait for Gitea instance to be ready
      k8s_info:
        api_version: pfe.rhpds.com/v1
        kind: Gitea
        name: "{{ gitea_instance_name }}"
        namespace: "{{ gitea_namespace }}"
      register: gitea_status
      until:
        - gitea_status.resources | length > 0
        - gitea_status.resources[0].status.conditions is defined
        - gitea_status.resources[0].status.conditions | selectattr('type', 'equalto', 'Successful') | list | length > 0
        - (gitea_status.resources[0].status.conditions | selectattr('type', 'equalto', 'Successful') | first).status == "True"
      retries: 30
      delay: 10

    - name: Get Gitea credentials and URL
      set_fact:
        gitea_url: "{{ gitea_status.resources[0].status.giteaRoute }}"
        gitea_admin_password_generated: "{{ gitea_status.resources[0].status.adminPassword }}"
        gitea_user_password_generated: "{{ gitea_status.resources[0].status.userPassword }}"

    - name: Display Gitea information
      debug:
        msg:
          - "Gitea URL: {{ gitea_url }}"
          - "Admin User: {{ gitea_admin_user }}"
          - "Admin Password: {{ gitea_admin_password_generated }}"
          - "Lab User Password: {{ gitea_user_password_generated }}"

    - name: Mirror pattern repositories
      when: gitea_mirror_patterns
      include_tasks: mirror_repositories.yml

  rescue:
    - name: Log Gitea deployment failure
      debug:
        msg: "Gitea deployment failed: {{ ansible_failed_result }}"

    - name: Get Gitea Operator logs
      shell: |
        oc logs -n {{ gitea_operator_namespace }} \
          -l control-plane=controller-manager \
          --tail=50
      register: operator_logs
      ignore_errors: true

    - name: Display operator logs
      debug:
        var: operator_logs.stdout_lines

    - fail:
        msg: "Gitea deployment failed. Check logs above."
```

```yaml
# ansible/roles/validated_patterns_gitea/tasks/mirror_repositories.yml
---
- name: Mirror Validated Pattern repositories to Gitea
  block:
    - name: Create validated-patterns organization
      uri:
        url: "{{ gitea_url }}/api/v1/orgs"
        method: POST
        user: "{{ gitea_admin_user }}"
        password: "{{ gitea_admin_password_generated }}"
        force_basic_auth: yes
        body_format: json
        body:
          username: "validated-patterns"
          full_name: "Validated Patterns"
          description: "Red Hat Validated Patterns"
          visibility: "public"
        status_code: [201, 422]  # 422 = already exists
        validate_certs: no
      register: org_creation

    - name: Mirror pattern repositories
      uri:
        url: "{{ gitea_url }}/api/v1/repos/migrate"
        method: POST
        user: "{{ gitea_admin_user }}"
        password: "{{ gitea_admin_password_generated }}"
        force_basic_auth: yes
        body_format: json
        body:
          clone_addr: "{{ item.url }}"
          repo_name: "{{ item.name }}"
          repo_owner: "validated-patterns"
          mirror: true
          private: false
          description: "Mirror of {{ item.name }} pattern"
        status_code: [201, 409]  # 409 = already exists
        validate_certs: no
      loop: "{{ gitea_pattern_repos }}"
      register: repo_mirrors

    - name: Display mirrored repositories
      debug:
        msg: "Mirrored {{ gitea_pattern_repos | length }} pattern repositories to Gitea"
```
### Usage Examples

#### Example 1: Deploy Gitea with Ansible

```yaml
# ansible/playbooks/setup_gitea.yml
---
- name: Setup Gitea Development Environment
  hosts: localhost
  connection: local
  gather_facts: false

  roles:
    - role: validated_patterns_gitea
      vars:
        gitea_namespace: "gitea"
        gitea_instance_name: "gitea-with-admin"
        gitea_admin_user: "admin"
        gitea_admin_email: "admin@example.com"
        gitea_user_number: 5  # Create 5 lab users
        gitea_mirror_patterns: true
```

Run the playbook:

```bash
ansible-playbook ansible/playbooks/setup_gitea.yml
```

#### Example 2: Deploy Gitea with Make

```makefile
# Makefile
.PHONY: setup-gitea
setup-gitea:
	@echo "Setting up Gitea development environment..."
	cd ansible && ansible-playbook playbooks/setup_gitea.yml

.PHONY: get-gitea-credentials
get-gitea-credentials:
	@echo "Retrieving Gitea credentials..."
	@./gitea/scripts/get-credentials.sh

.PHONY: open-gitea
open-gitea:
	@GITEA_URL=$$(oc get gitea gitea-with-admin -n gitea \
		-o jsonpath='{.status.giteaRoute}') && \
	echo "Opening Gitea at $$GITEA_URL" && \
	xdg-open "$$GITEA_URL" || open "$$GITEA_URL"
```

#### Example 3: Use Gitea in Pattern Deployment

```yaml
# patterns/multicloud-gitops/values-gitea.yaml
main:
  git:
    # Use local Gitea instead of GitHub
    repoURL: https://gitea-with-admin-gitea.apps.cluster-domain.com/validated-patterns/multicloud-gitops.git
    targetRevision: main

  # Disable cert verification for self-signed certs
  options:
    - name: insecure
      value: "true"
```

Deploy pattern with Gitea:

```bash
ansible-playbook ansible/playbooks/deploy_pattern.yml \
  -e pattern_name=multicloud-gitops \
  -e pattern_git_url=https://gitea-with-admin-gitea.apps.cluster-domain.com/validated-patterns/multicloud-gitops.git \
  -e git_insecure=true
```
## Consequences

### Positive
* **Operator-Managed**: Declarative, automated deployment and lifecycle management
* **Self-Contained**: Complete Git environment on OpenShift cluster
* **Lightweight**: Efficient resource usage (< 1GB RAM total)
* **Quick Setup**: Deploy in < 5 minutes with operator
* **User Management**: Automatic user creation for training scenarios
* **GitOps Ready**: Works seamlessly with ArgoCD and OpenShift GitOps
* **SSL/TLS**: Automatic HTTPS with edge termination
* **Training-Friendly**: Multi-user support out of the box
* **Maintained**: Actively maintained by Red Hat GPTE team

### Negative
* **Operator Dependency**: Requires Gitea Operator to be available
* **Resource Overhead**: Requires storage and compute resources
* **Not Production**: Not suitable for production Git hosting
* **Limited Customization**: Some advanced Gitea features may not be exposed via CRD

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Operator unavailable | High | Cache operator manifests, document manual deployment |
| Storage exhaustion | Medium | Monitor storage usage, set appropriate volume sizes |
| Certificate issues | Low | Use OpenShift's built-in certificate management |
| Performance degradation | Low | Set appropriate resource limits, monitor usage |

## Usage Scenarios

### 1. Development and Testing
- Test pattern changes locally before pushing to GitHub
- Experiment with GitOps workflows
- Validate pattern configurations

### 2. Training and Workshops
- Provide each student with their own Git account
- Self-contained environment for hands-on labs
- No external dependencies

### 3. Demonstrations
- Self-contained demos that work offline
- Show complete GitOps workflow
- No reliance on external services

### 4. Air-Gapped Environments
- Deploy patterns in disconnected environments
- Mirror pattern repositories locally
- Complete GitOps workflow without internet

### 5. CI/CD Testing
- Test GitOps pipelines
- Validate pattern deployment automation
- Integration testing

## Integration Points

### With Validated Patterns
- Mirror pattern repositories to Gitea
- Use Gitea as ArgoCD source
- Test pattern modifications locally

### With OpenShift GitOps
- Configure ArgoCD to use Gitea repositories
- Set up webhooks for automatic sync
- Manage multiple patterns from Gitea

### With Ansible Automation
- Automated Gitea deployment
- Repository mirroring
- User and organization management

## Monitoring and Maintenance

### Health Checks
```bash
# Check Gitea instance status
oc get gitea gitea-with-admin -n gitea

# Check pods
oc get pods -n gitea

# Check operator logs
oc logs -n gitea-operator -l control-plane=controller-manager --tail=50
```

### Backup and Restore
```bash
# Backup Gitea data
oc exec -n gitea deployment/gitea-with-admin -- \
  tar czf /tmp/gitea-backup.tar.gz /data

# Copy backup locally
oc cp gitea/gitea-with-admin-xxx:/tmp/gitea-backup.tar.gz ./gitea-backup.tar.gz
```

### Troubleshooting
```bash
# Get Gitea CR details
oc describe gitea gitea-with-admin -n gitea

# Check operator events
oc get events -n gitea-operator --sort-by='.lastTimestamp'

# Access Gitea logs
oc logs -n gitea deployment/gitea-with-admin
```

## References

* [Red Hat GPTE Gitea Operator](https://github.com/rhpds/gitea-operator)
* [Gitea Documentation](https://docs.gitea.io/)
* [OpenShift Operators](https://docs.openshift.com/container-platform/latest/operators/understanding/olm-what-operators-are.html)
* [Validated Patterns](https://validatedpatterns.io/)
* [OpenShift GitOps](https://docs.openshift.com/gitops/)
