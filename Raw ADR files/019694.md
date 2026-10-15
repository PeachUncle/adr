# ADR-003: Multi-Stage Validation Framework

**Status:** Proposed
**Date:** 2025-01-24
**Decision Makers:** Development Team, QE Team
**Consulted:** Operations Teams, SRE
**Informed:** End Users

## Context and Problem Statement

Validated Patterns deployments are complex, involving multiple operators, applications, and GitOps synchronization. We need a comprehensive validation framework that:

1. Validates deployments at multiple stages (pre-deployment, during deployment, post-deployment)
2. Provides both Ansible-based checks and Tekton pipeline validation
3. Generates clear, actionable reports
4. Supports continuous validation for deployed patterns
5. Integrates with monitoring and alerting systems

## Decision Drivers

* **Reliability**: Catch issues early and provide clear feedback
* **Automation**: Minimize manual validation steps
* **Observability**: Clear visibility into deployment health
* **Flexibility**: Support different validation scenarios
* **Integration**: Work with existing tools (ArgoCD, Prometheus, etc.)
* **Actionability**: Provide clear guidance on fixing issues

## Considered Options

### Option 1: Ansible-Only Validation
- All validation in Ansible playbooks
- **Rejected**: Limited CI/CD integration, no continuous validation

### Option 2: Tekton-Only Validation
- All validation in Tekton pipelines
- **Rejected**: Difficult for local development, requires cluster

### Option 3: Hybrid Ansible + Tekton Validation (Selected)
- Ansible for immediate, synchronous validation
- Tekton for CI/CD and continuous validation
- **Selected**: Best of both worlds

## Decision Outcome

**Chosen option:** Option 3 - Hybrid Ansible + Tekton Validation

### Validation Architecture

```
Validation Framework
├── Ansible Validation (Synchronous)
│   ├── Pre-deployment checks
│   ├── During-deployment monitoring
│   └── Post-deployment verification
│
└── Tekton Validation (Asynchronous/Continuous)
    ├── CI/CD pipeline validation
    ├── Continuous health monitoring
    └── Scheduled validation runs
```

### External Dependencies Validation

**Important Update (2025-01-24):** The validatedpatterns/common repository now uses a multisource architecture with external Helm chart repositories and the rhvp.cluster_utils Ansible collection.

**New validation checks required:**

```yaml
# tasks/validate_external_dependencies.yml
---
- name: Verify rhvp.cluster_utils collection installed
  ansible.builtin.command:
    cmd: ansible-galaxy collection list rhvp.cluster_utils
  register: collection_check
  failed_when: collection_check.rc != 0
  changed_when: false

- name: Verify Helm repositories configured
  kubernetes.core.helm_repository_info:
    name: "{{ item }}"
  loop:
    - validatedpatterns
    - jetstack
    - external-secrets
  register: helm_repos
  failed_when: helm_repos.failed

- name: Verify clustergroup-chart v0.9.* available
  kubernetes.core.helm_info:
    name: clustergroup
    release_namespace: openshift-gitops
  register: clustergroup_info
  failed_when: clustergroup_info.status.version is not match("0.9.*")

- name: Verify multisource configuration enabled
  kubernetes.core.k8s_info:
    api_version: v1
    kind: ConfigMap
    name: values-global
    namespace: openshift-gitops
  register: values_cm
  failed_when: >
    'multiSourceConfig' not in values_cm.resources[0].data.values_global or
    values_cm.resources[0].data.values_global.multiSourceConfig.enabled != true
```

### Ansible Validation Structure

```
ansible/roles/validated_patterns_validate/
├── tasks/
│   ├── main.yml
│   ├── pre_deployment_checks.yml
│   ├── validate_external_dependencies.yml
│   ├── validate_cluster_prerequisites.yml
│   ├── validate_operators.yml
│   ├── validate_gitops_sync.yml
│   ├── validate_applications.yml
│   ├── validate_secrets.yml
│   ├── validate_networking.yml
│   ├── validate_storage.yml
│   └── generate_report.yml
├── templates/
│   ├── validation_report.html.j2
│   └── validation_report.json.j2
├── defaults/
│   └── main.yml
└── README.md
```

### Ansible Validation Implementation

```yaml
# tasks/main.yml
---
- name: Run pre-deployment validation checks
  include_tasks: pre_deployment_checks.yml
  when: validation_stage == 'pre-deployment'
  tags: ['pre-deployment']

- name: Validate cluster prerequisites
  include_tasks: validate_cluster_prerequisites.yml
  tags: ['prerequisites']

- name: Validate operators
  include_tasks: validate_operators.yml
  tags: ['operators']

- name: Validate GitOps synchronization
  include_tasks: validate_gitops_sync.yml
  tags: ['gitops']

- name: Validate applications
  include_tasks: validate_applications.yml
  tags: ['applications']

- name: Validate secrets management
  include_tasks: validate_secrets.yml
  when: validated_patterns_use_vault | default(true) | bool
  tags: ['secrets']

- name: Validate networking
  include_tasks: validate_networking.yml
  tags: ['networking']

- name: Validate storage
  include_tasks: validate_storage.yml
  when: pattern_requires_storage | default(false) | bool
  tags: ['storage']

- name: Generate validation report
  include_tasks: generate_report.yml
  tags: ['report']
```

```yaml
# tasks/validate_cluster_prerequisites.yml
---
- name: Check OpenShift version
  k8s_info:
    api_version: config.openshift.io/v1
    kind: ClusterVersion
    name: version
  register: cluster_version

- name: Validate OpenShift version
  assert:
    that:
      - cluster_version.resources | length > 0
      - cluster_version.resources[0].status.desired.version is version(validated_patterns_min_ocp_version, '>=')
    fail_msg: "OpenShift version {{ cluster_version.resources[0].status.desired.version }} is below minimum required version {{ validated_patterns_min_ocp_version }}"
    success_msg: "OpenShift version {{ cluster_version.resources[0].status.desired.version }} meets requirements"

- name: Check cluster resources
  k8s_info:
    api_version: v1
    kind: Node
  register: cluster_nodes

- name: Validate cluster has sufficient nodes
  assert:
    that:
      - cluster_nodes.resources | length >= validated_patterns_min_nodes
    fail_msg: "Cluster has {{ cluster_nodes.resources | length }} nodes, minimum required is {{ validated_patterns_min_nodes }}"
    success_msg: "Cluster has {{ cluster_nodes.resources | length }} nodes"

- name: Check cluster storage classes
  k8s_info:
    api_version: storage.k8s.io/v1
    kind: StorageClass
  register: storage_classes

- name: Validate default storage class exists
  assert:
    that:
      - storage_classes.resources | selectattr('metadata.annotations.storageclass.kubernetes.io/is-default-class', 'defined') | list | length > 0
    fail_msg: "No default storage class found"
    success_msg: "Default storage class configured"
```

```yaml
# tasks/validate_gitops_sync.yml
---
- name: Get ArgoCD applications
  k8s_info:
    api_version: argoproj.io/v1alpha1
    kind: Application
    namespace: openshift-gitops
  register: argocd_apps

- name: Check ArgoCD application sync status
  set_fact:
    app_sync_status: >-
      {{
        argocd_apps.resources |
        map(attribute='status.sync.status') |
        list
      }}
    app_health_status: >-
      {{
        argocd_apps.resources |
        map(attribute='status.health.status') |
        list
      }}

- name: Validate all applications are synced
  assert:
    that:
      - "'OutOfSync' not in app_sync_status"
      - "'Unknown' not in app_sync_status"
    fail_msg: "Some ArgoCD applications are not synced: {{ argocd_apps.resources | selectattr('status.sync.status', 'in', ['OutOfSync', 'Unknown']) | map(attribute='metadata.name') | list }}"
    success_msg: "All ArgoCD applications are synced"

- name: Validate all applications are healthy
  assert:
    that:
      - "'Degraded' not in app_health_status"
      - "'Unknown' not in app_health_status"
    fail_msg: "Some ArgoCD applications are unhealthy: {{ argocd_apps.resources | selectattr('status.health.status', 'in', ['Degraded', 'Unknown']) | map(attribute='metadata.name') | list }}"
    success_msg: "All ArgoCD applications are healthy"
```

### ArgoCD Custom Health Checks

The clustergroup-chart v0.9.* includes custom health checks for:

**1. PersistentVolumeClaim (PVC)**
- Monitors PVC binding status
- Validates PVC is in "Bound" state
- Checks for "Pending" state transitions

**2. InferenceService (KServe)**
- Comprehensive model serving health check
- Monitors model status and transition status
- Validates all conditions are healthy
- Checks for "Stopped" condition (should be False)
- Provides detailed status messages

**Validation in Ansible:**

```yaml
# tasks/validate_argocd_health_checks.yml
---
- name: Verify ArgoCD custom health checks deployed
  kubernetes.core.k8s_info:
    api_version: v1
    kind: ConfigMap
    name: argocd-cm
    namespace: openshift-gitops
  register: argocd_cm
  failed_when: argocd_cm.resources | length == 0

- name: Validate PVC health check configured
  assert:
    that:
      - "'PersistentVolumeClaim' in argocd_cm.resources[0].data['resource.customizations.health.persistentvolumeclaim']"
    fail_msg: "PVC health check not configured in ArgoCD"

- name: Validate InferenceService health check configured
  assert:
    that:
      - "'InferenceService' in argocd_cm.resources[0].data['resource.customizations.health.serving.kserve.io_inferenceservice']"
    fail_msg: "InferenceService health check not configured in ArgoCD"
```

### Tekton Pipeline Structure

```
tekton/
├── pipelines/
│   ├── pattern-validation-pipeline.yaml
│   ├── continuous-validation-pipeline.yaml
│   └── deployment-validation-pipeline.yaml
├── tasks/
│   ├── validate-prerequisites.yaml
│   ├── validate-operators.yaml
│   ├── validate-gitops-sync.yaml
│   ├── validate-applications.yaml
│   ├── validate-secrets.yaml
│   ├── validate-networking.yaml
│   ├── validate-storage.yaml
│   ├── run-smoke-tests.yaml
│   └── generate-report.yaml
├── triggers/
│   ├── validation-trigger-binding.yaml
│   ├── validation-trigger-template.yaml
│   └── validation-event-listener.yaml
└── README.md
```

### Tekton Pipeline Implementation

```yaml
# pipelines/pattern-validation-pipeline.yaml
apiVersion: tekton.dev/v1beta1
kind: Pipeline
metadata:
  name: pattern-validation-pipeline
  namespace: validated-patterns-ci
spec:
  params:
    - name: pattern-name
      type: string
      description: Name of the pattern to validate
    - name: pattern-repo
      type: string
      description: Git repository URL
    - name: pattern-revision
      type: string
      default: main
      description: Git revision to validate
    - name: cluster-domain
      type: string
      description: OpenShift cluster domain

  workspaces:
    - name: shared-workspace
    - name: kubeconfig

  tasks:
    - name: validate-prerequisites
      taskRef:
        name: validate-prerequisites
      params:
        - name: pattern-name
          value: $(params.pattern-name)
      workspaces:
        - name: kubeconfig
          workspace: kubeconfig

    - name: validate-operators
      taskRef:
        name: validate-operators
      params:
        - name: pattern-name
          value: $(params.pattern-name)
      workspaces:
        - name: kubeconfig
          workspace: kubeconfig
      runAfter:
        - validate-prerequisites

    - name: validate-gitops-sync
      taskRef:
        name: validate-gitops-sync
      params:
        - name: pattern-name
          value: $(params.pattern-name)
      workspaces:
        - name: kubeconfig
          workspace: kubeconfig
      runAfter:
        - validate-operators

    - name: validate-applications
      taskRef:
        name: validate-applications
      params:
        - name: pattern-name
          value: $(params.pattern-name)
      workspaces:
        - name: kubeconfig
          workspace: kubeconfig
      runAfter:
        - validate-gitops-sync

    - name: validate-secrets
      taskRef:
        name: validate-secrets
      params:
        - name: pattern-name
          value: $(params.pattern-name)
      workspaces:
        - name: kubeconfig
          workspace: kubeconfig
      runAfter:
        - validate-applications

    - name: run-smoke-tests
      taskRef:
        name: run-smoke-tests
      params:
        - name: pattern-name
          value: $(params.pattern-name)
        - name: cluster-domain
          value: $(params.cluster-domain)
      workspaces:
        - name: shared-workspace
          workspace: shared-workspace
        - name: kubeconfig
          workspace: kubeconfig
      runAfter:
        - validate-secrets

    - name: generate-report
      taskRef:
        name: generate-report
      params:
        - name: pattern-name
          value: $(params.pattern-name)
      workspaces:
        - name: shared-workspace
          workspace: shared-workspace
      runAfter:
        - run-smoke-tests
```

```yaml
# tasks/validate-gitops-sync.yaml
apiVersion: tekton.dev/v1beta1
kind: Task
metadata:
  name: validate-gitops-sync
  namespace: validated-patterns-ci
spec:
  params:
    - name: pattern-name
      type: string
  workspaces:
    - name: kubeconfig
  steps:
    - name: check-argocd-apps
      image: quay.io/openshift/origin-cli:latest
      script: |
        #!/bin/bash
        set -e

        export KUBECONFIG=$(workspaces.kubeconfig.path)/kubeconfig

        echo "Checking ArgoCD applications for pattern: $(params.pattern-name)"

        # Get all ArgoCD applications
        apps=$(oc get applications -n openshift-gitops -o json)

        # Check sync status
        out_of_sync=$(echo "$apps" | jq -r '.items[] | select(.status.sync.status != "Synced") | .metadata.name')

        if [ -n "$out_of_sync" ]; then
          echo "ERROR: The following applications are out of sync:"
          echo "$out_of_sync"
          exit 1
        fi

        # Check health status
        unhealthy=$(echo "$apps" | jq -r '.items[] | select(.status.health.status != "Healthy") | .metadata.name')

        if [ -n "$unhealthy" ]; then
          echo "ERROR: The following applications are unhealthy:"
          echo "$unhealthy"
          exit 1
        fi

        echo "All ArgoCD applications are synced and healthy"
```

## Validation Stages

### 1. Pre-Deployment Validation
- Cluster prerequisites (version, resources, storage)
- Network connectivity
- Required operators availability
- Credentials and secrets

### 2. During-Deployment Validation
- Operator installation progress
- GitOps sync status
- Resource creation monitoring

### 3. Post-Deployment Validation
- All operators healthy
- All applications deployed and healthy
- GitOps fully synced
- Secrets properly configured
- Networking functional
- Storage provisioned

### 4. Continuous Validation
- Scheduled Tekton pipeline runs
- Prometheus-based monitoring
- Alerting on degradation

## Validation Report Format

```json
{
  "pattern_name": "multicloud-gitops",
  "validation_timestamp": "2025-01-24T10:30:00Z",
  "validation_stage": "post-deployment",
  "overall_status": "PASSED",
  "checks": [
    {
      "category": "prerequisites",
      "name": "OpenShift Version",
      "status": "PASSED",
      "message": "OpenShift 4.14.8 meets minimum requirement 4.12.0"
    },
    {
      "category": "operators",
      "name": "OpenShift GitOps",
      "status": "PASSED",
      "message": "Operator installed and healthy"
    },
    {
      "category": "gitops",
      "name": "ArgoCD Sync Status",
      "status": "PASSED",
      "message": "All 12 applications synced and healthy"
    }
  ],
  "recommendations": [],
  "next_validation": "2025-01-24T11:30:00Z"
}
```

## Consequences

### Positive
* **Early Detection**: Issues caught before they impact users
* **Comprehensive Coverage**: Multiple validation stages
* **Automation**: Reduces manual validation effort
* **Clear Reporting**: Actionable insights

### Negative
* **Complexity**: More components to maintain
* **Resource Usage**: Tekton pipelines consume cluster resources

## References

* [Tekton Pipelines](https://tekton.dev/)
* [ArgoCD Health Assessment](https://argo-cd.readthedocs.io/en/stable/operator-manual/health/)
* [OpenShift Monitoring](https://docs.openshift.com/container-platform/latest/monitoring/monitoring-overview.html)
