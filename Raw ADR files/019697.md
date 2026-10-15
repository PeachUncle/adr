# ADR-006: Execution Context Handling (Root vs Subdirectory)

**Status:** Proposed
**Date:** 2025-01-24
**Decision Makers:** Development Team
**Consulted:** End Users, DevOps Team
**Informed:** Stakeholders

## Context and Problem Statement

This template repository needs to support two execution contexts:

1. **Root Directory Execution**: When used as a standalone template repository
2. **Subdirectory Execution**: When integrated as a subdirectory in a larger project

The challenge is to make all scripts, Makefiles, Ansible playbooks, and applications work correctly in both contexts without requiring significant code duplication or complex conditional logic.

## Decision Drivers

* **Flexibility**: Support both execution contexts seamlessly
* **Simplicity**: Minimize complexity in scripts and configurations
* **Maintainability**: Single codebase for both contexts
* **User Experience**: Clear and intuitive for end users
* **Path Resolution**: Correct path resolution in all scenarios

## Considered Options

### Option 1: Separate Codebases
- Maintain separate versions for root and subdirectory
- **Rejected**: Maintenance nightmare, code duplication

### Option 2: Complex Conditional Logic
- Heavy use of if/else statements throughout
- **Rejected**: Hard to maintain, error-prone

### Option 3: Environment Variable-Based Context Detection (Selected)
- Use environment variables to detect and adapt to context
- Smart path resolution utilities
- **Selected**: Clean, maintainable, flexible

## Decision Outcome

**Chosen option:** Option 3 - Environment Variable-Based Context Detection

### Implementation Strategy

#### 1. Environment Variables

```bash
# Set these environment variables to control execution context

# Execution context: 'root' or 'subdirectory'
export PATTERN_EXECUTION_CONTEXT="${PATTERN_EXECUTION_CONTEXT:-root}"

# If subdirectory, specify the subdirectory path
export PATTERN_SUBDIRECTORY="${PATTERN_SUBDIRECTORY:-}"

# Project root directory (auto-detected or explicitly set)
export PATTERN_PROJECT_ROOT="${PATTERN_PROJECT_ROOT:-$(pwd)}"

# Ansible execution environment directory
export PATTERN_EE_DIR="${PATTERN_EE_DIR:-validated-patterns-ansible-toolkit}"
```

#### 2. Path Resolution Utility

```bash
# scripts/path-resolver.sh
#!/bin/bash

# Detect execution context
detect_context() {
    if [ -n "$PATTERN_SUBDIRECTORY" ]; then
        echo "subdirectory"
    else
        echo "root"
    fi
}

# Get project root directory
get_project_root() {
    local context=$(detect_context)

    if [ "$context" = "subdirectory" ]; then
        # Navigate up from subdirectory to project root
        local current_dir=$(pwd)
        local subdir_depth=$(echo "$PATTERN_SUBDIRECTORY" | tr '/' '\n' | wc -l)

        for ((i=0; i<subdir_depth; i++)); do
            current_dir=$(dirname "$current_dir")
        done

        echo "$current_dir"
    else
        # Already at project root
        echo "$(pwd)"
    fi
}

# Resolve path relative to project root
resolve_path() {
    local relative_path="$1"
    local project_root=$(get_project_root)

    echo "${project_root}/${relative_path}"
}

# Resolve path relative to EE directory
resolve_ee_path() {
    local relative_path="$1"
    local project_root=$(get_project_root)
    local ee_dir="${PATTERN_EE_DIR}"

    if [ "$(detect_context)" = "subdirectory" ]; then
        echo "${project_root}/${PATTERN_SUBDIRECTORY}/${relative_path}"
    else
        echo "${project_root}/${relative_path}"
    fi
}

# Export functions
export -f detect_context
export -f get_project_root
export -f resolve_path
export -f resolve_ee_path
```

#### 3. Makefile with Context Awareness

```makefile
# Makefile

# Detect execution context
EXECUTION_CONTEXT ?= $(shell [ -n "$(PATTERN_SUBDIRECTORY)" ] && echo "subdirectory" || echo "root")

# Determine project root
ifeq ($(EXECUTION_CONTEXT),subdirectory)
    PROJECT_ROOT := $(shell pwd | sed 's|/$(PATTERN_SUBDIRECTORY)||')
    EE_DIR := $(PROJECT_ROOT)/$(PATTERN_SUBDIRECTORY)
else
    PROJECT_ROOT := $(shell pwd)
    EE_DIR := $(PROJECT_ROOT)
endif

# Common directories
ANSIBLE_DIR := $(EE_DIR)/ansible
QUARKUS_DIR := $(EE_DIR)/quarkus-app
TEKTON_DIR := $(EE_DIR)/tekton
GITEA_DIR := $(EE_DIR)/gitea
PATTERNS_DIR := $(EE_DIR)/patterns
DOCS_DIR := $(EE_DIR)/docs

# Display context information
.PHONY: show-context
show-context:
	@echo "Execution Context: $(EXECUTION_CONTEXT)"
	@echo "Project Root: $(PROJECT_ROOT)"
	@echo "EE Directory: $(EE_DIR)"
	@echo "Ansible Directory: $(ANSIBLE_DIR)"
	@echo "Subdirectory: $(PATTERN_SUBDIRECTORY)"

# Deploy pattern with context awareness
.PHONY: deploy-pattern
deploy-pattern:
	@echo "Deploying pattern from $(EXECUTION_CONTEXT) context..."
	cd $(ANSIBLE_DIR) && \
	ansible-playbook playbooks/deploy_pattern.yml \
		-e "execution_context=$(EXECUTION_CONTEXT)" \
		-e "project_root=$(PROJECT_ROOT)" \
		-e "ee_directory=$(EE_DIR)"

# Setup Gitea
.PHONY: setup-gitea
setup-gitea:
	@echo "Setting up Gitea from $(EXECUTION_CONTEXT) context..."
	cd $(ANSIBLE_DIR) && \
	ansible-playbook playbooks/setup_gitea.yml \
		-e "execution_context=$(EXECUTION_CONTEXT)" \
		-e "project_root=$(PROJECT_ROOT)"

# Build Quarkus application
.PHONY: build-quarkus
build-quarkus:
	@echo "Building Quarkus application from $(EXECUTION_CONTEXT) context..."
	cd $(QUARKUS_DIR) && \
	./mvnw clean package \
		-Dquarkus.container-image.build=true \
		-Dproject.root=$(PROJECT_ROOT)

# Deploy Tekton pipelines
.PHONY: deploy-tekton
deploy-tekton:
	@echo "Deploying Tekton pipelines from $(EXECUTION_CONTEXT) context..."
	oc apply -f $(TEKTON_DIR)/pipelines/ -R
	oc apply -f $(TEKTON_DIR)/tasks/ -R
	oc apply -f $(TEKTON_DIR)/triggers/ -R
```

#### 4. Ansible Configuration

```yaml
# ansible/group_vars/all.yml
---
# Execution context detection
execution_context: "{{ lookup('env', 'PATTERN_EXECUTION_CONTEXT') | default('root', true) }}"
pattern_subdirectory: "{{ lookup('env', 'PATTERN_SUBDIRECTORY') | default('', true) }}"
project_root: "{{ lookup('env', 'PATTERN_PROJECT_ROOT') | default(playbook_dir + '/../..', true) }}"

# Path resolution
ee_directory: >-
  {% if execution_context == 'subdirectory' %}
  {{ project_root }}/{{ pattern_subdirectory }}
  {% else %}
  {{ project_root }}
  {% endif %}

ansible_directory: "{{ ee_directory }}/ansible"
quarkus_directory: "{{ ee_directory }}/quarkus-app"
tekton_directory: "{{ ee_directory }}/tekton"
gitea_directory: "{{ ee_directory }}/gitea"
patterns_directory: "{{ ee_directory }}/patterns"
common_directory: "{{ ee_directory }}/common"

# Display context information
- name: Display execution context
  debug:
    msg:
      - "Execution Context: {{ execution_context }}"
      - "Project Root: {{ project_root }}"
      - "EE Directory: {{ ee_directory }}"
      - "Subdirectory: {{ pattern_subdirectory }}"
```

#### 5. Quarkus Application Configuration

```properties
# quarkus-app/src/main/resources/application.properties

# Execution context
pattern.execution.context=${PATTERN_EXECUTION_CONTEXT:root}
pattern.subdirectory=${PATTERN_SUBDIRECTORY:}
pattern.project.root=${PATTERN_PROJECT_ROOT:}

# Path resolution
%dev.pattern.ansible.path=${PATTERN_PROJECT_ROOT}/ansible
%prod.pattern.ansible.path=/opt/ansible

%dev.pattern.tekton.path=${PATTERN_PROJECT_ROOT}/tekton
%prod.pattern.tekton.path=/opt/tekton

%dev.pattern.patterns.path=${PATTERN_PROJECT_ROOT}/patterns
%prod.pattern.patterns.path=/opt/patterns
```

```java
// quarkus-app/src/main/java/io/validatedpatterns/manager/config/PathResolver.java
package io.validatedpatterns.manager.config;

import javax.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import java.nio.file.Path;
import java.nio.file.Paths;

@ApplicationScoped
public class PathResolver {

    @ConfigProperty(name = "pattern.execution.context", defaultValue = "root")
    String executionContext;

    @ConfigProperty(name = "pattern.subdirectory", defaultValue = "")
    String subdirectory;

    @ConfigProperty(name = "pattern.project.root")
    String projectRoot;

    public Path resolveProjectPath(String relativePath) {
        return Paths.get(projectRoot, relativePath);
    }

    public Path resolveEEPath(String relativePath) {
        if ("subdirectory".equals(executionContext) && !subdirectory.isEmpty()) {
            return Paths.get(projectRoot, subdirectory, relativePath);
        }
        return Paths.get(projectRoot, relativePath);
    }

    public boolean isSubdirectoryContext() {
        return "subdirectory".equals(executionContext);
    }

    public String getExecutionContext() {
        return executionContext;
    }
}
```

### Usage Examples

#### Example 1: Root Directory Execution

```bash
# Clone the template repository
git clone https://github.com/your-org/validated-patterns-ansible-toolkit.git
cd validated-patterns-ansible-toolkit

# No environment variables needed - defaults to root context
make deploy-pattern PATTERN_NAME=multicloud-gitops
```

#### Example 2: Subdirectory Execution

```bash
# In a larger project
cd my-large-project

# Add as subdirectory
mkdir -p automation
cd automation
git clone https://github.com/your-org/validated-patterns-ansible-toolkit.git

# Set environment variables
export PATTERN_EXECUTION_CONTEXT=subdirectory
export PATTERN_SUBDIRECTORY=automation/validated-patterns-ansible-toolkit
export PATTERN_PROJECT_ROOT=$(pwd | sed 's|/automation/validated-patterns-ansible-toolkit||')

# Deploy pattern
cd validated-patterns-ansible-toolkit
make deploy-pattern PATTERN_NAME=multicloud-gitops
```

#### Example 3: Automated Detection

```bash
# scripts/auto-detect-context.sh
#!/bin/bash

# Auto-detect if we're in a subdirectory
if git rev-parse --show-toplevel >/dev/null 2>&1; then
    GIT_ROOT=$(git rev-parse --show-toplevel)
    CURRENT_DIR=$(pwd)

    if [ "$GIT_ROOT" != "$CURRENT_DIR" ]; then
        # We're in a subdirectory
        export PATTERN_EXECUTION_CONTEXT=subdirectory
        export PATTERN_SUBDIRECTORY=$(realpath --relative-to="$GIT_ROOT" "$CURRENT_DIR")
        export PATTERN_PROJECT_ROOT="$GIT_ROOT"
        echo "Detected subdirectory context: $PATTERN_SUBDIRECTORY"
    else
        # We're at the root
        export PATTERN_EXECUTION_CONTEXT=root
        export PATTERN_PROJECT_ROOT="$CURRENT_DIR"
        echo "Detected root context"
    fi
fi
```

## Consequences

### Positive
* **Flexibility**: Works in both contexts without code changes
* **Simplicity**: Clean, maintainable code
* **User-Friendly**: Automatic detection possible
* **Testable**: Easy to test both contexts

### Negative
* **Environment Variables**: Users need to set them correctly in subdirectory context
* **Documentation**: Need clear documentation on usage

### Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Users forget to set environment variables | Auto-detection script, clear error messages |
| Path resolution errors | Comprehensive testing, validation checks |
| Confusion about context | Clear documentation, `show-context` command |

## Testing Strategy

1. **Unit Tests**: Test path resolution functions
2. **Integration Tests**: Test in both contexts
3. **CI/CD**: Automated testing in both contexts
4. **Documentation**: Clear examples for both scenarios

## References

* [Bash Environment Variables](https://www.gnu.org/software/bash/manual/html_node/Environment.html)
* [Make Variables](https://www.gnu.org/software/make/manual/html_node/Using-Variables.html)
* [Ansible Variables](https://docs.ansible.com/ansible/latest/user_guide/playbooks_variables.html)
