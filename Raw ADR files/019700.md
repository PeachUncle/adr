# ADR-009: OpenShift AI Workload Validation

**Status:** Proposed
**Date:** 2025-01-24
**Decision Makers:** Development Team, AI/ML Platform Team
**Consulted:** OpenShift AI Users, Data Scientists
**Informed:** Stakeholders

## Context and Problem Statement

When deploying Validated Patterns on top of **Red Hat OpenShift AI (RHOAI)**, users need to ensure that:

1. **OpenShift AI dependencies** are properly installed and configured
2. **Notebooks/Workbenches** are functional and accessible
3. **Data Science Pipelines** are operational
4. **Model serving** infrastructure is ready
5. **Storage and data connections** are configured correctly
6. **GPU/accelerator resources** are available (if required)

Unlike general application deployments, OpenShift AI workloads have specific validation requirements around:
- Operator installation and component configuration
- Notebook image availability and functionality
- Pipeline execution and artifact storage
- Model serving runtime readiness
- Data science project setup

**Important**: We do NOT need to create a sample application for OpenShift AI validation. The validation focuses on verifying the platform components and infrastructure are ready for data science workloads.

## Decision Drivers

* **Platform Readiness**: Ensure RHOAI is properly configured before deploying patterns
* **Notebook Validation**: Verify notebooks can start and connect to resources
* **Pipeline Validation**: Ensure data science pipelines can execute
* **Model Serving**: Validate model serving infrastructure is operational
* **No Sample App**: Focus on infrastructure validation, not application examples
* **Idempotency**: Validation checks should be repeatable and non-destructive
* **Integration**: Work with existing validated-patterns-toolkit validation framework

## Considered Options

### Option 1: Manual Validation Checklist
- Document manual steps for users to verify
- **Rejected**: Error-prone, not automated, doesn't integrate with toolkit

### Option 2: Separate OpenShift AI Validation Tool
- Build standalone tool for RHOAI validation
- **Rejected**: Doesn't integrate with validated-patterns-toolkit workflow

### Option 3: Integrated Ansible Role with Tekton Pipelines (Selected)
- Ansible role for pre-deployment validation
- Tekton pipelines for continuous validation
- **Selected**: Integrates with ADR-003 validation framework

## Decision Outcome

**Chosen option:** Option 3 - Integrated Ansible Role with Tekton Pipelines

### Validation Scope

We validate the **OpenShift AI platform and infrastructure**, NOT sample applications:

✅ **What We Validate:**
- OpenShift AI Operator installation
- DataScienceCluster (DSC) configuration
- DSCInitialization status
- Notebook images availability
- Data Science Pipeline infrastructure
- Model serving runtimes
- Storage classes and PVC provisioning
- GPU/accelerator availability (if configured)
- Service mesh integration (for KServe)

❌ **What We DON'T Validate:**
- Sample notebook applications
- Example ML models
- Demo pipelines
- Training workloads

### Validation Architecture

```
validated-patterns-toolkit/
├── ansible/
│   └── roles/
│       └── validated_patterns_openshift_ai/
│           ├── tasks/
│           │   ├── main.yml
│           │   ├── validate_operator.yml
│           │   ├── validate_dsc.yml
│           │   ├── validate_notebooks.yml
│           │   ├── validate_pipelines.yml
│           │   ├── validate_model_serving.yml
│           │   └── validate_storage.yml
│           ├── defaults/
│           │   └── main.yml
│           └── README.md
├── tekton/
│   └── openshift-ai/
│       ├── pipeline-validate-rhoai.yaml
│       ├── task-validate-operator.yaml
│       ├── task-validate-notebooks.yaml
│       ├── task-validate-pipelines.yaml
│       └── task-validate-model-serving.yaml
└── docs/
    └── how-to/
        └── validate-openshift-ai.md
```

## Validation Categories

### 1. Operator and Component Validation

**Ansible Tasks:**
```yaml
# ansible/roles/validated_patterns_openshift_ai/tasks/validate_operator.yml
---
- name: Check OpenShift AI Operator is installed
  kubernetes.core.k8s_info:
    api_version: operators.coreos.com/v1alpha1
    kind: Subscription
    name: rhods-operator
    namespace: redhat-ods-operator
  register: rhoai_operator
  failed_when: rhoai_operator.resources | length == 0

- name: Verify Operator is in Succeeded state
  kubernetes.core.k8s_info:
    api_version: operators.coreos.com/v1alpha1
    kind: ClusterServiceVersion
    namespace: redhat-ods-operator
  register: csv_info
  failed_when: >
    csv_info.resources |
    selectattr('metadata.name', 'search', 'rhods-operator') |
    selectattr('status.phase', 'equalto', 'Succeeded') |
    list | length == 0

- name: Check DSCInitialization exists
  kubernetes.core.k8s_info:
    api_version: dscinitialization.opendatahub.io/v1
    kind: DSCInitialization
    name: default-dsci
  register: dsci
  failed_when: dsci.resources | length == 0

- name: Verify DSCInitialization is Ready
  assert:
    that:
      - dsci.resources[0].status.phase == "Ready"
    fail_msg: "DSCInitialization is not ready: {{ dsci.resources[0].status.phase }}"

- name: Check DataScienceCluster exists
  kubernetes.core.k8s_info:
    api_version: datasciencecluster.opendatahub.io/v1
    kind: DataScienceCluster
    name: default-dsc
  register: dsc
  failed_when: dsc.resources | length == 0

- name: Verify required components are Managed
  assert:
    that:
      - dsc.resources[0].spec.components.dashboard.managementState == "Managed"
      - dsc.resources[0].spec.components.workbenches.managementState == "Managed"
      - dsc.resources[0].spec.components.datasciencepipelines.managementState == "Managed"
    fail_msg: "Required RHOAI components are not in Managed state"
```

### 2. Notebook/Workbench Validation

**Ansible Tasks:**
```yaml
# ansible/roles/validated_patterns_openshift_ai/tasks/validate_notebooks.yml
---
- name: Check notebook images are available
  kubernetes.core.k8s_info:
    api_version: image.openshift.io/v1
    kind: ImageStream
    namespace: redhat-ods-applications
    label_selectors:
      - "opendatahub.io/notebook-image=true"
  register: notebook_images
  failed_when: notebook_images.resources | length == 0

- name: Verify required notebook images exist
  assert:
    that:
      - notebook_images.resources | selectattr('metadata.name', 'search', 'minimal-notebook') | list | length > 0
      - notebook_images.resources | selectattr('metadata.name', 'search', 'pytorch') | list | length > 0
    fail_msg: "Required notebook images are not available"

- name: Check notebook controller is running
  kubernetes.core.k8s_info:
    api_version: v1
    kind: Pod
    namespace: redhat-ods-applications
    label_selectors:
      - "app=notebook-controller"
  register: notebook_controller
  failed_when: >
    notebook_controller.resources |
    selectattr('status.phase', 'equalto', 'Running') |
    list | length == 0

- name: Verify OdhDashboardConfig exists
  kubernetes.core.k8s_info:
    api_version: opendatahub.io/v1alpha
    kind: OdhDashboardConfig
    name: odh-dashboard-config
    namespace: redhat-ods-applications
  register: dashboard_config
  failed_when: dashboard_config.resources | length == 0
```

### 3. Data Science Pipelines Validation

**Ansible Tasks:**
```yaml
# ansible/roles/validated_patterns_openshift_ai/tasks/validate_pipelines.yml
---
- name: Check Data Science Pipelines operator is running
  kubernetes.core.k8s_info:
    api_version: v1
    kind: Pod
    namespace: redhat-ods-applications
    label_selectors:
      - "app.kubernetes.io/name=data-science-pipelines-operator"
  register: dsp_operator
  failed_when: >
    dsp_operator.resources |
    selectattr('status.phase', 'equalto', 'Running') |
    list | length == 0

- name: Verify DSP CRD is installed
  kubernetes.core.k8s_info:
    api_version: apiextensions.k8s.io/v1
    kind: CustomResourceDefinition
    name: datasciencepipelinesapplications.datasciencepipelinesapplications.opendatahub.io
  register: dsp_crd
  failed_when: dsp_crd.resources | length == 0

- name: Check if test project has DSPA configured (if exists)
  kubernetes.core.k8s_info:
    api_version: datasciencepipelinesapplications.opendatahub.io/v1
    kind: DataSciencePipelinesApplication
    namespace: "{{ openshift_ai_test_project | default('') }}"
  register: dspa
  when: openshift_ai_test_project is defined
  failed_when:
    - openshift_ai_test_project is defined
    - dspa.resources | length == 0
```

### 4. Model Serving Validation

**Ansible Tasks:**
```yaml
# ansible/roles/validated_patterns_openshift_ai/tasks/validate_model_serving.yml
---
- name: Check KServe component status
  kubernetes.core.k8s_info:
    api_version: datasciencecluster.opendatahub.io/v1
    kind: DataScienceCluster
    name: default-dsc
  register: dsc
  failed_when: >
    dsc.resources[0].spec.components.kserve.managementState != "Managed" and
    dsc.resources[0].spec.components.modelmeshserving.managementState != "Managed"

- name: Verify ServingRuntime CRD exists
  kubernetes.core.k8s_info:
    api_version: apiextensions.k8s.io/v1
    kind: CustomResourceDefinition
    name: servingruntimes.serving.kserve.io
  register: serving_runtime_crd
  failed_when: serving_runtime_crd.resources | length == 0

- name: Check serving runtime templates are available
  kubernetes.core.k8s_info:
    api_version: template.openshift.io/v1
    kind: Template
    namespace: redhat-ods-applications
    label_selectors:
      - "opendatahub.io/dashboard=true"
  register: serving_templates
  failed_when: serving_templates.resources | length == 0

- name: Verify KServe dependencies (if KServe is enabled)
  block:
    - name: Check ServiceMesh is installed
      kubernetes.core.k8s_info:
        api_version: operators.coreos.com/v1alpha1
        kind: Subscription
        name: servicemeshoperator
        namespace: openshift-operators
      register: servicemesh
      failed_when: servicemesh.resources | length == 0

    - name: Check Authorino is installed
      kubernetes.core.k8s_info:
        api_version: operators.coreos.com/v1alpha1
        kind: Subscription
        name: authorino-operator
        namespace: openshift-operators
      register: authorino
      failed_when: authorino.resources | length == 0
  when: dsc.resources[0].spec.components.kserve.managementState == "Managed"
```

### 5. Storage and GPU Validation

**Ansible Tasks:**
```yaml
# ansible/roles/validated_patterns_openshift_ai/tasks/validate_storage.yml
---
- name: Check default storage class exists
  kubernetes.core.k8s_info:
    api_version: storage.k8s.io/v1
    kind: StorageClass
  register: storage_classes
  failed_when: >
    storage_classes.resources |
    selectattr('metadata.annotations.storageclass.kubernetes.io/is-default-class', 'defined') |
    list | length == 0

- name: Verify PVC can be created (dry-run)
  kubernetes.core.k8s:
    state: present
    definition:
      apiVersion: v1
      kind: PersistentVolumeClaim
      metadata:
        name: test-pvc-validation
        namespace: redhat-ods-applications
      spec:
        accessModes:
          - ReadWriteOnce
        resources:
          requests:
            storage: 1Gi
    apply: no
    dry_run: yes

- name: Check GPU nodes (if GPU validation enabled)
  kubernetes.core.k8s_info:
    api_version: v1
    kind: Node
    label_selectors:
      - "nvidia.com/gpu.present=true"
  register: gpu_nodes
  when: openshift_ai_validate_gpu | default(false)
  failed_when:
    - openshift_ai_validate_gpu | default(false)
    - gpu_nodes.resources | length == 0

- name: Verify NFD Operator (for GPU detection)
  kubernetes.core.k8s_info:
    api_version: operators.coreos.com/v1alpha1
    kind: Subscription
    name: nfd
    namespace: openshift-nfd
  register: nfd_operator
  when: openshift_ai_validate_gpu | default(false)
```

## Tekton Pipeline Integration

**Continuous Validation Pipeline:**
```yaml
# tekton/openshift-ai/pipeline-validate-rhoai.yaml
apiVersion: tekton.dev/v1
kind: Pipeline
metadata:
  name: validate-openshift-ai
  namespace: validated-patterns-ci
spec:
  params:
    - name: validate-gpu
      type: string
      default: "false"
    - name: test-project
      type: string
      default: ""
  tasks:
    - name: validate-operator
      taskRef:
        name: validate-rhoai-operator

    - name: validate-notebooks
      taskRef:
        name: validate-rhoai-notebooks
      runAfter:
        - validate-operator

    - name: validate-pipelines
      taskRef:
        name: validate-rhoai-pipelines
      runAfter:
        - validate-operator

    - name: validate-model-serving
      taskRef:
        name: validate-rhoai-model-serving
      runAfter:
        - validate-operator

    - name: validate-storage
      taskRef:
        name: validate-rhoai-storage
      params:
        - name: validate-gpu
          value: $(params.validate-gpu)
      runAfter:
        - validate-operator
```

## Configuration Options

**Ansible Role Defaults:**
```yaml
# ansible/roles/validated_patterns_openshift_ai/defaults/main.yml
---
# OpenShift AI validation configuration
openshift_ai_operator_namespace: redhat-ods-operator
openshift_ai_applications_namespace: redhat-ods-applications

# Validation toggles
openshift_ai_validate_operator: true
openshift_ai_validate_notebooks: true
openshift_ai_validate_pipelines: true
openshift_ai_validate_model_serving: true
openshift_ai_validate_storage: true
openshift_ai_validate_gpu: false

# Optional: Test project for DSPA validation
# openshift_ai_test_project: my-data-science-project

# Required components
openshift_ai_required_components:
  - dashboard
  - workbenches
  - datasciencepipelines

# Optional components (validate if managed)
openshift_ai_optional_components:
  - kserve
  - modelmeshserving
  - codeflare
  - ray
  - trustyai

# Timeout settings (seconds)
openshift_ai_validation_timeout: 300
openshift_ai_pod_ready_timeout: 120
```

## Usage Examples

### Pre-Deployment Validation

```bash
# Validate OpenShift AI before deploying pattern
ansible-navigator run ansible/playbooks/validate_openshift_ai.yml \
  -e openshift_ai_validate_gpu=true
```

### Pattern Deployment with RHOAI Validation

```yaml
# ansible/playbooks/deploy_pattern_with_rhoai.yml
---
- name: Deploy Validated Pattern on OpenShift AI
  hosts: localhost
  tasks:
    - name: Validate OpenShift AI platform
      include_role:
        name: validated_patterns_openshift_ai
      tags: validate

    - name: Deploy pattern
      include_role:
        name: validated_patterns_deploy
      vars:
        pattern_name: "{{ pattern_name }}"
      tags: deploy
```

### Continuous Validation

```bash
# Create Tekton PipelineRun
oc create -f - <<EOF
apiVersion: tekton.dev/v1
kind: PipelineRun
metadata:
  name: validate-rhoai-$(date +%s)
  namespace: validated-patterns-ci
spec:
  pipelineRef:
    name: validate-openshift-ai
  params:
    - name: validate-gpu
      value: "true"
EOF
```

## Consequences

### Positive

* **Platform Readiness**: Ensures RHOAI is properly configured
* **Early Detection**: Catches configuration issues before deployment
* **No Sample App**: Focuses on infrastructure, not application examples
* **Idempotent**: Validation checks are repeatable and safe
* **Integrated**: Works with existing validation framework (ADR-003)
* **Flexible**: Can enable/disable specific validation categories
* **GPU Support**: Optional GPU/accelerator validation

### Negative

* **Maintenance**: Need to update as RHOAI evolves
* **Complexity**: Multiple validation categories to maintain
* **Dependencies**: Requires understanding of RHOAI architecture

### Neutral

* **Optional**: Users can skip RHOAI validation if not using AI workloads
* **Extensible**: Easy to add new validation checks

## Implementation Plan

### Phase 1: Core Validation (Week 1)
- [ ] Create Ansible role structure
- [ ] Implement operator validation
- [ ] Implement DSC/DSCI validation
- [ ] Add basic tests

### Phase 2: Component Validation (Week 2)
- [ ] Implement notebook validation
- [ ] Implement pipeline validation
- [ ] Implement model serving validation
- [ ] Add storage validation

### Phase 3: Advanced Validation (Week 3)
- [ ] Add GPU validation
- [ ] Implement Tekton pipelines
- [ ] Add continuous validation
- [ ] Create documentation

### Phase 4: Integration (Week 4)
- [ ] Integrate with validated-patterns-toolkit
- [ ] Add to deployment playbooks
- [ ] Create usage examples
- [ ] Write troubleshooting guide

## Success Criteria

* ✅ All RHOAI components validated before pattern deployment
* ✅ Clear error messages when validation fails
* ✅ Validation completes in < 5 minutes
* ✅ Works with RHOAI 2.16+
* ✅ Supports both KServe and ModelMesh
* ✅ Optional GPU validation
* ✅ Integrated with Tekton for continuous validation
* ✅ Comprehensive documentation

## References

* [Red Hat OpenShift AI Documentation](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/)
* [OpenShift AI GitOps Guide](https://ai-on-openshift.io/odh-rhoai/gitops/)
* [ADR-003: Validation Framework](ADR-003-validation-framework.md)
* [ADR-002: Ansible Role Architecture](ADR-002-ansible-role-architecture.md)
* [Validated Patterns](https://validatedpatterns.io/)

## Related ADRs

* [ADR-002: Ansible Role Architecture](ADR-002-ansible-role-architecture.md)
* [ADR-003: Validation Framework](ADR-003-validation-framework.md)
* [ADR-007: Ansible Navigator Deployment](ADR-007-ansible-navigator-deployment.md)
