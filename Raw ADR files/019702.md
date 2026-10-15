# ADR-011: Helm Installation for Validated Patterns

**Status:** Accepted
**Date:** 2025-10-25
**Deciders:** Development Team
**Technical Story:** Phase 3 Week 8 - Testing validated_patterns_common role

## Context

During Phase 3 testing of the `validated_patterns_common` role, we discovered that Helm is required for:
1. Managing Helm repositories (validatedpatterns, jetstack, external-secrets)
2. Deploying the clustergroup-chart v0.9.*
3. Configuring multisource architecture for Validated Patterns
4. Testing Helm-based deployments in the validation framework

The test environment did not have Helm installed, causing the `validated_patterns_common` role tests to fail. Helm is a critical dependency for Validated Patterns deployment and must be available in the execution environment.

## Decision

We will install Helm v3 using the official Helm installation script and document it as a required dependency for the Validated Patterns Toolkit.

### Installation Method

```bash
# Download Helm installation script
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3

# Make script executable
chmod 700 get_helm.sh

# Install Helm (requires sudo)
sudo ./get_helm.sh
```

### Version Installed
- **Helm Version:** v3.19.0
- **Installation Date:** 2025-10-25
- **Installation Path:** `/usr/local/bin/helm`

### Integration Points

1. **Ansible Roles:**
   - `validated_patterns_common`: Uses Helm for repository management and chart deployment
   - Future roles may use Helm for application deployment

2. **Test Framework:**
   - Week 8 tests require Helm for validating common role functionality
   - Integration tests will use Helm for end-to-end deployment validation

3. **Execution Environment:**
   - Helm must be available in the validated-patterns-ansible-toolkit
   - PATH must include `/usr/local/bin` for Helm access

## Consequences

### Positive

1. **Enables Validated Patterns Deployment:**
   - Helm is required for clustergroup-chart deployment
   - Supports multisource architecture configuration
   - Enables Helm repository management

2. **Standard Tool:**
   - Helm is the de facto standard for Kubernetes package management
   - Well-documented and widely supported
   - Active community and regular updates

3. **Testing Capability:**
   - Allows comprehensive testing of Helm-based deployments
   - Enables validation of chart configurations
   - Supports integration testing with ArgoCD

4. **Flexibility:**
   - Can deploy any Helm chart
   - Supports custom values and overrides
   - Enables templating and configuration management

### Negative

1. **Additional Dependency:**
   - Adds another tool to the execution environment
   - Requires sudo access for installation
   - Must be maintained and updated

2. **Version Management:**
   - Need to track Helm version compatibility
   - May require updates for new features
   - Potential breaking changes between versions

3. **Security Considerations:**
   - Installation script runs with elevated privileges
   - Must verify script integrity before execution
   - Need to manage Helm repository security

### Neutral

1. **PATH Configuration:**
   - `/usr/local/bin` must be in PATH
   - May require environment configuration
   - Consistent with standard Linux practices

2. **Documentation:**
   - Must document Helm installation in setup guides
   - Need to include troubleshooting steps
   - Should provide version compatibility matrix

## Implementation

### 1. Installation Steps (Completed)

```bash
# Download and install Helm
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
sudo ./get_helm.sh

# Verify installation
helm version
# Output: version.BuildInfo{Version:"v3.19.0", ...}
```

### 2. PATH Configuration

Ensure `/usr/local/bin` is in PATH:

```bash
# Add to ~/.bashrc or ~/.bash_profile
export PATH=$PATH:/usr/local/bin

# Or create symlink in existing PATH location
sudo ln -s /usr/local/bin/helm /usr/bin/helm
```

### 3. Ansible Integration

The `validated_patterns_common` role uses Helm via:

```yaml
# Configure Helm repositories
- name: Add Validated Patterns Helm repository
  kubernetes.core.helm_repository:
    name: validatedpatterns
    repo_url: https://charts.validatedpatterns.io
    state: present

# Deploy Helm chart
- name: Deploy clustergroup-chart
  kubernetes.core.helm:
    name: clustergroup
    chart_ref: validatedpatterns/clustergroup-chart
    chart_version: "0.9.*"
    release_namespace: openshift-gitops
```

### 4. Testing Integration

Test playbooks verify Helm functionality:

```yaml
# Verify Helm is available
- name: Check Helm version
  ansible.builtin.command:
    cmd: helm version
  register: helm_version

# Verify Helm repositories
- name: List Helm repositories
  ansible.builtin.command:
    cmd: helm repo list
  register: helm_repos
```

## Alternatives Considered

### 1. Package Manager Installation (dnf/yum)

**Pros:**
- Standard package management
- Automatic updates via system updates
- No manual script execution

**Cons:**
- May not have latest version
- Repository availability varies by OS
- Less control over version

**Decision:** Rejected - Official script provides latest version and consistent installation

### 2. Binary Download

**Pros:**
- Direct control over version
- No script execution required
- Minimal dependencies

**Cons:**
- Manual installation steps
- No automatic PATH configuration
- More complex to automate

**Decision:** Rejected - Official script is simpler and more reliable

### 3. Container-Based Helm

**Pros:**
- Isolated from host system
- Version pinning via container tag
- No host installation required

**Cons:**
- Requires container runtime
- More complex Ansible integration
- Additional overhead

**Decision:** Rejected - Direct installation is simpler for our use case

## Compliance

### ADR-002: Ansible Role Architecture
- Helm integration follows role architecture patterns
- Uses kubernetes.core collection for Helm operations
- Maintains idempotency in Helm operations

### ADR-007: Ansible Navigator Deployment
- Helm must be available in execution environment
- Consider adding Helm to execution-environment.yml
- Ensure PATH configuration in ansible-navigator.yml

### ADR-DEVELOPMENT-RULES
- Document Helm as required dependency
- Include installation steps in setup documentation
- Add Helm version to dependency matrix

## Documentation Updates Required

1. **README.md:**
   - Add Helm to prerequisites section
   - Include installation instructions
   - Document version requirements

2. **docs/tutorials/:**
   - Update setup guides with Helm installation
   - Add Helm troubleshooting section
   - Include Helm usage examples

3. **execution-environment.yml:**
   - Consider adding Helm to container image
   - Document Helm availability in EE

4. **tests/week8/:**
   - Document Helm requirement for tests
   - Add Helm verification to test setup
   - Include Helm in test prerequisites

## Monitoring and Maintenance

### Version Tracking
- Current version: v3.19.0
- Update frequency: As needed for security/features
- Compatibility: Test with Validated Patterns charts

### Health Checks
```bash
# Verify Helm is working
helm version

# Check repository access
helm repo list

# Test chart search
helm search repo validatedpatterns
```

### Troubleshooting

**Issue:** Helm not found in PATH
```bash
# Solution: Add to PATH or create symlink
export PATH=$PATH:/usr/local/bin
# or
sudo ln -s /usr/local/bin/helm /usr/bin/helm
```

**Issue:** Permission denied
```bash
# Solution: Ensure proper permissions
sudo chmod +x /usr/local/bin/helm
```

**Issue:** Repository not accessible
```bash
# Solution: Update repositories
helm repo update
```

## References

- [Helm Official Documentation](https://helm.sh/docs/)
- [Helm Installation Guide](https://helm.sh/docs/intro/install/)
- [Validated Patterns Helm Charts](https://charts.validatedpatterns.io)
- [kubernetes.core.helm module](https://docs.ansible.com/ansible/latest/collections/kubernetes/core/helm_module.html)

## Notes

- Helm v3 does not require Tiller (removed in v3)
- Helm uses kubeconfig for cluster authentication
- Helm charts are stored in repositories, not in cluster
- Helm releases are tracked in cluster secrets/configmaps

---

**Approved by:** Development Team
**Implementation Date:** 2025-10-25
**Review Date:** 2026-01-25 (Quarterly review)
