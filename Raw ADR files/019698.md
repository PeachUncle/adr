# ADR-007: Ansible Navigator Deployment Strategy

**Status:** Proposed
**Date:** 2025-01-24
**Decision Makers:** Development Team
**Consulted:** End Users, DevOps Team
**Informed:** Stakeholders

## Context and Problem Statement

End users need a simple, consistent way to deploy Validated Patterns without:
- Installing multiple dependencies on their local machine
- Dealing with Python virtual environments
- Managing Ansible collection versions
- Worrying about OS-specific issues

The validated-patterns-ansible-toolkit already provides a containerized environment with all dependencies. We need to make it easy for end users to leverage this with Ansible Navigator and Podman.

## Decision Drivers

* **Simplicity**: Single command to deploy patterns
* **Consistency**: Same environment for all users
* **Isolation**: No local dependency conflicts
* **Portability**: Works on any system with Podman
* **Reproducibility**: Locked dependency versions
* **User Experience**: Clear, intuitive workflow
* **Documentation**: Easy to understand and follow

## Considered Options

### Option 1: Direct Ansible Installation
- Users install Ansible and collections locally
- **Rejected**: Dependency hell, version conflicts, OS-specific issues

### Option 2: Docker/Podman with Manual Commands
- Users run containers manually with complex commands
- **Rejected**: Too complex, error-prone, poor UX

### Option 3: Ansible Navigator with Execution Environment (Selected)
- Use ansible-navigator with pre-built EE image
- Simple configuration file
- Consistent experience
- **Selected**: Best balance of simplicity and power

## Decision Outcome

**Chosen option:** Option 3 - Ansible Navigator with Execution Environment

### Why Ansible Navigator?

Ansible Navigator provides:
- **Containerized Execution**: Runs playbooks in EE containers
- **Interactive Mode**: TUI for exploring playbook execution
- **Stdout Mode**: Traditional output for CI/CD
- **Configuration Management**: Simple YAML configuration
- **Volume Mounting**: Easy access to local files
- **Podman Native**: First-class Podman support

## Implementation Strategy

### 1. Execution Environment Configuration

The existing `execution-environment.yml` already defines our EE:

```yaml
# execution-environment.yml
version: 3

images:
  base_image:
    name: quay.io/ansible/creator-ee:latest

dependencies:
  galaxy: files/requirements.yml
  python: files/requirements.txt
  system: files/bindep.txt

additional_build_steps:
  prepend_galaxy:
    - ADD files/ansible.cfg /etc/ansible/ansible.cfg
  prepend_final:
    - RUN echo "Validated Patterns Execution Environment"

options:
  package_manager_path: /usr/bin/microdnf
```

### 2. Ansible Navigator Configuration

Create a user-friendly `ansible-navigator.yml`:

```yaml
# ansible-navigator.yml
---
ansible-navigator:
  # Execution environment settings
  execution-environment:
    enabled: true
    container-engine: podman
    image: quay.io/validated-patterns/ansible-ee:latest
    pull:
      policy: missing

    # Volume mounts for local development
    volume-mounts:
      - src: "{{ lookup('env', 'PWD') }}/patterns"
        dest: "/runner/patterns"
        options: "Z"
      - src: "{{ lookup('env', 'PWD') }}/ansible"
        dest: "/runner/ansible"
        options: "Z"
      - src: "{{ lookup('env', 'HOME') }}/.kube"
        dest: "/runner/.kube"
        options: "Z"

    # Environment variables
    environment-variables:
      pass:
        - KUBECONFIG
        - K8S_AUTH_KUBECONFIG
        - ANSIBLE_HUB_TOKEN
        - VAULT_TOKEN
      set:
        ANSIBLE_FORCE_COLOR: "true"
        ANSIBLE_HOST_KEY_CHECKING: "false"

  # Playbook settings
  playbook-artifact:
    enable: true
    save-as: "artifacts/playbook-{playbook_name}-{time_stamp}.json"

  # Logging
  logging:
    level: info
    append: true
    file: "logs/ansible-navigator.log"

  # Mode settings
  mode: stdout  # Use 'interactive' for TUI mode

  # Color settings
  color:
    enable: true
    osc4: true
```

### 3. Simplified User Workflow

#### Quick Start for End Users

```bash
# 1. Clone the template repository
git clone https://github.com/your-org/validated-patterns-ansible-toolkit.git
cd validated-patterns-ansible-toolkit

# 2. Login to OpenShift
oc login --server=https://api.cluster.example.com:6443

# 3. Deploy a pattern with ansible-navigator
ansible-navigator run ansible/playbooks/deploy_pattern.yml \
  -e pattern_name=multicloud-gitops

# That's it! 🎉
```

### 4. Makefile Integration

Add user-friendly Make targets:

```makefile
# Makefile additions

# Deploy pattern using ansible-navigator
.PHONY: deploy-pattern
deploy-pattern:
	@if [ -z "$(PATTERN_NAME)" ]; then \
		echo "Error: PATTERN_NAME is required"; \
		echo "Usage: make deploy-pattern PATTERN_NAME=multicloud-gitops"; \
		exit 1; \
	fi
	ansible-navigator run ansible/playbooks/deploy_pattern.yml \
		-e pattern_name=$(PATTERN_NAME) \
		$(EXTRA_VARS)

# Validate pattern deployment
.PHONY: validate-pattern
validate-pattern:
	@if [ -z "$(PATTERN_NAME)" ]; then \
		echo "Error: PATTERN_NAME is required"; \
		exit 1; \
	fi
	ansible-navigator run ansible/playbooks/validate_pattern.yml \
		-e pattern_name=$(PATTERN_NAME)

# Setup Gitea development environment
.PHONY: setup-gitea
setup-gitea:
	ansible-navigator run ansible/playbooks/setup_gitea.yml

# Interactive mode for debugging
.PHONY: deploy-pattern-interactive
deploy-pattern-interactive:
	@if [ -z "$(PATTERN_NAME)" ]; then \
		echo "Error: PATTERN_NAME is required"; \
		exit 1; \
	fi
	ansible-navigator run ansible/playbooks/deploy_pattern.yml \
		-e pattern_name=$(PATTERN_NAME) \
		-m interactive

# List available patterns
.PHONY: list-patterns
list-patterns:
	@echo "Available Patterns:"
	@ls -1 patterns/ | grep -v README

# Show ansible-navigator configuration
.PHONY: show-navigator-config
show-navigator-config:
	ansible-navigator settings --effective

# Pull latest EE image
.PHONY: pull-ee
pull-ee:
	podman pull quay.io/validated-patterns/ansible-ee:latest
```

### 5. User Documentation

Create `docs/tutorials/deploying-with-ansible-navigator.md`:

```markdown
# Deploying Patterns with Ansible Navigator

## Prerequisites

- Podman installed
- ansible-navigator installed (`pip install ansible-navigator`)
- Access to an OpenShift cluster
- Logged into OpenShift (`oc login`)

## Quick Start

### 1. Deploy a Pattern

```bash
# Using Make (recommended)
make deploy-pattern PATTERN_NAME=multicloud-gitops

# Or using ansible-navigator directly
ansible-navigator run ansible/playbooks/deploy_pattern.yml \
  -e pattern_name=multicloud-gitops
```

### 2. Validate Deployment

```bash
make validate-pattern PATTERN_NAME=multicloud-gitops
```

### 3. Setup Gitea (Optional)

```bash
make setup-gitea
```

## Advanced Usage

### Interactive Mode

Use interactive mode for debugging:

```bash
make deploy-pattern-interactive PATTERN_NAME=multicloud-gitops
```

### Custom Variables

Pass additional variables:

```bash
make deploy-pattern PATTERN_NAME=multicloud-gitops \
  EXTRA_VARS="-e git_branch=develop -e debug=true"
```

### Using Local Gitea

```bash
make deploy-pattern PATTERN_NAME=multicloud-gitops \
  EXTRA_VARS="-e pattern_git_url=https://gitea-with-admin-gitea.apps.cluster.com/validated-patterns/multicloud-gitops.git"
```

## Troubleshooting

### Image Pull Issues

```bash
# Pull image manually
make pull-ee

# Or specify a different image
ansible-navigator run ansible/playbooks/deploy_pattern.yml \
  --eei quay.io/validated-patterns/ansible-ee:v1.0.0 \
  -e pattern_name=multicloud-gitops
```

### Volume Mount Issues

Ensure SELinux labels are correct:

```bash
# Fix SELinux labels
chcon -Rt svirt_sandbox_file_t ansible/
chcon -Rt svirt_sandbox_file_t patterns/
```

### Kubeconfig Issues

```bash
# Ensure KUBECONFIG is set
export KUBECONFIG=~/.kube/config

# Or specify explicitly
ansible-navigator run ansible/playbooks/deploy_pattern.yml \
  -e pattern_name=multicloud-gitops \
  -e kubeconfig_path=~/.kube/config
```
```

### 6. CI/CD Integration

```yaml
# .github/workflows/deploy-pattern.yml
name: Deploy Pattern

on:
  workflow_dispatch:
    inputs:
      pattern_name:
        description: 'Pattern to deploy'
        required: true
        type: choice
        options:
          - multicloud-gitops
          - industrial-edge
          - medical-diagnosis

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Podman
        run: |
          sudo apt-get update
          sudo apt-get install -y podman

      - name: Install ansible-navigator
        run: pip install ansible-navigator

      - name: Login to OpenShift
        run: |
          oc login --token=${{ secrets.OCP_TOKEN }} \
            --server=${{ secrets.OCP_SERVER }}

      - name: Deploy pattern
        run: |
          ansible-navigator run ansible/playbooks/deploy_pattern.yml \
            -e pattern_name=${{ inputs.pattern_name }} \
            -m stdout

      - name: Validate deployment
        run: |
          ansible-navigator run ansible/playbooks/validate_pattern.yml \
            -e pattern_name=${{ inputs.pattern_name }} \
            -m stdout

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playbook-artifacts
          path: artifacts/
```

## Consequences

### Positive

* **Simplified UX**: Single command to deploy patterns
* **Consistency**: Same environment for all users
* **No Local Dependencies**: Everything runs in container
* **Reproducible**: Locked versions in EE image
* **Portable**: Works on any system with Podman
* **CI/CD Ready**: Easy integration with pipelines
* **Interactive Debugging**: TUI mode for troubleshooting
* **Volume Mounting**: Easy access to local files
* **Environment Isolation**: No conflicts with local tools

### Negative

* **Learning Curve**: Users need to learn ansible-navigator
* **Container Overhead**: Slight performance impact
* **Image Size**: EE images can be large (500MB-1GB)
* **Network Dependency**: Need to pull images initially

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Users unfamiliar with ansible-navigator | Medium | Comprehensive documentation, Make targets |
| Image pull failures | High | Cache images, provide alternative registries |
| Volume mount issues | Medium | Clear documentation, SELinux guidance |
| Podman not installed | High | Installation guide, alternative with Docker |
| Large image size | Low | Optimize EE, provide slim variants |

## Usage Examples

### Example 1: First-Time User

```bash
# Install prerequisites
sudo dnf install podman
pip install ansible-navigator

# Clone and deploy
git clone https://github.com/your-org/validated-patterns-ansible-toolkit.git
cd validated-patterns-ansible-toolkit
oc login
make deploy-pattern PATTERN_NAME=multicloud-gitops
```

### Example 2: Developer Testing Changes

```bash
# Make changes to playbooks
vim ansible/playbooks/deploy_pattern.yml

# Test with interactive mode
make deploy-pattern-interactive PATTERN_NAME=multicloud-gitops

# Validate
make validate-pattern PATTERN_NAME=multicloud-gitops
```

### Example 3: CI/CD Pipeline

```bash
# In CI/CD pipeline
ansible-navigator run ansible/playbooks/deploy_pattern.yml \
  -e pattern_name=multicloud-gitops \
  -e git_branch=${CI_COMMIT_BRANCH} \
  -m stdout \
  --pae false  # Disable playbook artifact encryption
```

## Integration with Other ADRs

- **ADR-002**: Ansible roles run inside EE via navigator
- **ADR-003**: Validation playbooks executed via navigator
- **ADR-005**: Gitea setup playbook runs via navigator
- **ADR-006**: Execution context handled via volume mounts

## References

* [Ansible Navigator Documentation](https://ansible.readthedocs.io/projects/navigator/)
* [Ansible Builder Documentation](https://ansible.readthedocs.io/projects/builder/)
* [Execution Environments](https://docs.ansible.com/automation-controller/latest/html/userguide/execution_environments.html)
* [Podman Documentation](https://docs.podman.io/)
* [Validated Patterns](https://validatedpatterns.io/)
