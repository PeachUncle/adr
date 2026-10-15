# ADR-011: Custom Execution Environment for Ansible Automation Platform

**Status:** Proposed

**Date:** 2025-09-09

## Context

The implementation of Ansible Automation Platform (ADR-010) requires careful consideration of the execution environment where automation playbooks will run. The default execution environments provided with AAP may not include all the necessary dependencies, tools, and configurations required for our ServiceNow-OpenShift integration use case.

Our automation requires specific dependencies including:
- **Python libraries**: `python-keycloak`, `openshift`, `kubernetes`, `requests`, `pyyaml`
- **Ansible collections**: `community.general`, `kubernetes.core`, `servicenow.itsm`, `redhat.openshift`
- **System tools**: `oc` CLI, `curl`, `git`, `jq`
- **Custom configurations**: CA certificates, proxy settings, environment-specific configurations
- **Security tools**: Credential scanning, secret management utilities

The execution environment must be containerized, versioned, and integrated with our GitOps workflow (ADR-004) while maintaining security best practices and reproducible builds.

## Decision

We will develop a **custom Execution Environment (EE)** specifically tailored for our ServiceNow-OpenShift integration automation needs. This EE will be built using the `ansible-builder` tool and deployed as a container image that AAP can consume.

### Execution Environment Architecture:

#### **Base Image Strategy:**
- **Base**: Red Hat Universal Base Image (UBI) 8 or 9 for enterprise support and security
- **Python Runtime**: Python 3.9+ with pip package management
- **Ansible Core**: Latest supported Ansible Core version compatible with AAP

#### **Dependency Management:**
```yaml
# execution-environment.yml structure
version: 3
images:
  base_image:
    name: 'registry.redhat.io/ubi8/ubi:latest'
dependencies:
  galaxy: requirements.yml
  python: requirements.txt
  system: bindep.txt
additional_build_steps:
  prepend_base:
    - RUN dnf update -y
  prepend_galaxy:
    - COPY custom-ca-certs/ /etc/pki/ca-trust/source/anchors/
    - RUN update-ca-trust
  append_final:
    - RUN dnf clean all
    - USER 1001
```

#### **Required Components:**

**1. Ansible Collections (requirements.yml):**
```yaml
collections:
  # Core OpenShift/Kubernetes automation
  - name: kubernetes.core
    version: ">=2.4.0"
  - name: redhat.openshift
    version: ">=2.0.0"
  
  # ServiceNow integration
  - name: servicenow.itsm
    version: ">=2.0.0"
  
  # General utilities and HTTP operations
  - name: community.general
    version: ">=6.0.0"
  - name: ansible.posix
    version: ">=1.4.0"
  
  # GitOps and Git operations
  - name: community.crypto
    version: ">=2.0.0"
```

**2. Python Dependencies (requirements.txt):**
```txt
# Keycloak Admin API client
python-keycloak>=2.0.0

# OpenShift/Kubernetes Python clients
openshift>=0.13.0
kubernetes>=24.0.0

# HTTP and API utilities
requests>=2.28.0
urllib3>=1.26.0

# YAML processing
PyYAML>=6.0

# ServiceNow API client
pysnow>=0.7.0

# Cryptography and security
cryptography>=3.4.0
pyOpenSSL>=22.0.0

# JSON/data processing
jq>=1.2.0
jsonschema>=4.0.0

# Logging and monitoring
python-json-logger>=2.0.0
prometheus-client>=0.14.0
```

**3. System Dependencies (bindep.txt):**
```txt
# OpenShift CLI
curl [platform:centos-8 platform:rhel-8]
tar [platform:centos-8 platform:rhel-8]

# Git for GitOps operations
git [platform:centos-8 platform:rhel-8]

# JSON processing
jq [platform:centos-8 platform:rhel-8]

# Network utilities
net-tools [platform:centos-8 platform:rhel-8]
bind-utils [platform:centos-8 platform:rhel-8]

# SSL/TLS tools
ca-certificates [platform:centos-8 platform:rhel-8]
openssl [platform:centos-8 platform:rhel-8]

# Development tools (for pip compilations)
gcc [compile platform:centos-8 platform:rhel-8]
python3-devel [compile platform:centos-8 platform:rhel-8]
```

#### **Build Process Integration:**

**1. GitOps Integration:**
- EE definition files stored in Git repository (`execution-environment/` directory)
- Automated builds triggered by Git commits
- Version tagging aligned with semantic versioning
- Integration with existing kustomize structure (ADR-004)

**2. Container Registry Strategy:**
- Build images in OpenShift internal registry or external registry (Quay.io)
- Multi-architecture support (x86_64, arm64) if required
- Vulnerability scanning integrated into build pipeline
- Signed images for security and integrity

**3. Build Pipeline:**
```yaml
# .github/workflows/build-ee.yml or Tekton Pipeline
name: Build Execution Environment
on:
  push:
    paths:
      - 'execution-environment/**'
    branches: [main, develop]
  pull_request:
    paths:
      - 'execution-environment/**'

jobs:
  build-execution-environment:
    steps:
      - name: Build EE
        run: |
          ansible-builder build \
            --tag servicenow-ocp-ee:${GITHUB_SHA} \
            --container-runtime podman \
            execution-environment/
      
      - name: Security Scan
        run: |
          podman run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy image servicenow-ocp-ee:${GITHUB_SHA}
      
      - name: Push to Registry
        run: |
          podman push servicenow-ocp-ee:${GITHUB_SHA} \
            ${{ secrets.CONTAINER_REGISTRY }}/servicenow-ocp-ee:${GITHUB_SHA}
```

### Custom Tools and Utilities:

#### **OpenShift CLI Installation:**
```dockerfile
# Custom build step for oc CLI
RUN curl -sLo /tmp/oc.tar.gz \
    "https://mirror.openshift.com/pub/openshift-v4/clients/ocp/stable/openshift-client-linux.tar.gz" && \
    tar -xzf /tmp/oc.tar.gz -C /usr/local/bin/ oc && \
    chmod +x /usr/local/bin/oc && \
    rm -f /tmp/oc.tar.gz
```

#### **Custom Ansible Modules/Plugins:**
```python
# Custom modules for ServiceNow-specific operations
# Located in: execution-environment/custom-modules/
- servicenow_connection_alias.py
- openshift_project_with_rbac.py
- keycloak_client_validator.py
```

#### **Environment-Specific Configurations:**
```yaml
# Environment variables for different deployment contexts
ENV ANSIBLE_HOST_KEY_CHECKING=False
ENV ANSIBLE_GATHERING=smart
ENV ANSIBLE_RETRY_FILES_ENABLED=False
ENV PYTHONUNBUFFERED=1

# Custom paths for our automation
ENV ANSIBLE_LIBRARY=/opt/ansible/custom-modules
ENV ANSIBLE_COLLECTIONS_PATH=/usr/share/ansible/collections
```

## Rationale

### Technical Justification:
- **Dependency Isolation**: Custom EE ensures all required dependencies are available and versioned
- **Reproducible Builds**: Container-based approach guarantees consistent execution environment
- **Security Hardening**: Custom build allows security patches, vulnerability management, and compliance
- **Performance Optimization**: Pre-installed dependencies reduce job startup time
- **Maintainability**: Version-controlled EE definitions enable change tracking and rollback

### Operational Benefits:
- **Standardization**: All automation jobs run in identical environments
- **Troubleshooting**: Consistent environment simplifies debugging and support
- **Compliance**: Auditable build process and dependency management
- **Scalability**: Container-based execution scales with AAP infrastructure

### Integration Advantages:
- **GitOps Alignment**: EE builds integrated with existing Git workflows (ADR-004)
- **Security Integration**: Vulnerability scanning and secret management built-in
- **Monitoring Integration**: Logging and metrics collection capabilities
- **Multi-Environment Support**: Different EE versions for dev/test/prod environments

## Consequences

### Positive Consequences:

- **Enhanced Reliability**: Consistent execution environment eliminates "works on my machine" issues
- **Improved Security**: Controlled dependency management and vulnerability scanning
- **Better Performance**: Pre-installed dependencies reduce automation job startup time
- **Operational Excellence**: Professional build pipeline with testing and validation
- **Future-Proofing**: Extensible architecture for additional tools and dependencies
- **Compliance**: Auditable dependency management and build process

### Negative Consequences:

- **Build Complexity**: Additional CI/CD pipeline for EE builds and testing
- **Storage Requirements**: Container images require registry storage and bandwidth
- **Maintenance Overhead**: EE updates require coordination with AAP deployments
- **Skill Requirements**: Team needs container build and registry management knowledge
- **Dependency Management**: Complex dependency resolution and conflict management

### Risk Mitigation:

- **Automated Testing**: EE validation through automated test suites
- **Version Management**: Semantic versioning and backward compatibility testing
- **Fallback Strategy**: Multiple EE versions available for rollback scenarios
- **Documentation**: Comprehensive build and troubleshooting documentation
- **Monitoring**: Build pipeline monitoring and alerting

## Implementation Plan

### Phase 1: Foundation (Week 1-2)
1. **Repository Structure**: Create `execution-environment/` directory structure
2. **Base EE Definition**: Create initial execution-environment.yml with core dependencies
3. **Build Pipeline**: Implement basic build pipeline with ansible-builder
4. **Registry Setup**: Configure container registry for EE storage

### Phase 2: Core Dependencies (Week 2-3)
1. **Ansible Collections**: Add and test required Ansible collections
2. **Python Dependencies**: Install and validate Python libraries
3. **System Tools**: Add OpenShift CLI and system utilities
4. **Custom Modules**: Develop ServiceNow-specific Ansible modules

### Phase 3: Integration (Week 3-4)
1. **AAP Integration**: Deploy custom EE to AAP and configure job templates
2. **Testing**: Comprehensive testing of all automation workflows
3. **Documentation**: Create operational runbooks and troubleshooting guides
4. **Security Validation**: Security scanning and vulnerability assessment

### Phase 4: Production (Week 4-5)
1. **Production Deployment**: Deploy to production AAP environment
2. **Monitoring**: Implement EE build and usage monitoring
3. **Maintenance Procedures**: Establish update and maintenance workflows
4. **Knowledge Transfer**: Team training on EE management

## Technical Specifications

### Container Image Structure:
```
/opt/ansible/
├── collections/          # Ansible collections
├── custom-modules/       # Custom Ansible modules
├── plugins/             # Custom Ansible plugins
├── configs/             # Environment-specific configs
└── scripts/             # Utility scripts

/usr/local/bin/
├── oc                   # OpenShift CLI
├── ansible-playbook     # Ansible runtime
└── custom-tools/        # Custom automation tools
```

### Version Management:
- **Semantic Versioning**: MAJOR.MINOR.PATCH format
- **Git Tagging**: Automated tagging based on changes
- **Registry Tags**: Multiple tags (latest, stable, version-specific)
- **Compatibility Matrix**: AAP version compatibility documentation

### Security Considerations:
- **Base Image Security**: Regular UBI updates and security patches
- **Dependency Scanning**: Automated vulnerability scanning for all dependencies
- **Secret Management**: No secrets baked into EE images
- **Access Control**: Registry access controls and image signing
- **Compliance**: FIPS 140-2 compliance if required

## Quality Assurance

### Testing Strategy:
1. **Unit Tests**: Test individual Ansible modules and plugins
2. **Integration Tests**: Test complete automation workflows
3. **Security Tests**: Vulnerability and penetration testing
4. **Performance Tests**: Job execution time and resource usage
5. **Compatibility Tests**: Cross-version compatibility validation

### Validation Criteria:
- All required dependencies successfully installed
- Ansible collections and modules functional
- OpenShift CLI operational
- Custom modules pass validation tests
- Security scan results within acceptable thresholds
- Performance meets baseline requirements

## References

- **ADR-010:** Ansible Automation Platform Integration (parent decision)
- **ADR-004:** GitOps-based Deployment with ArgoCD and Kustomize (build integration)
- **ADR-007:** Secret Management with External Secrets Operator (security integration)
- **ADR-008:** Observability Strategy (monitoring integration)

## Future Considerations

- **Multi-Cloud Support**: Add cloud-specific tools and modules
- **GPU Workloads**: Support for GPU-accelerated automation if needed
- **Advanced Security**: Integration with advanced security scanning tools
- **AI/ML Integration**: Support for AI-driven automation capabilities
- **Edge Computing**: Lightweight EE variants for edge deployments
