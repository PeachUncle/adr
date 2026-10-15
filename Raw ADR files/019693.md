# ADR-001: Project Vision and Scope - Validated Patterns Deployment Template

**Status:** Proposed
**Date:** 2025-01-24
**Decision Makers:** Development Team, Platform Engineering
**Consulted:** Validated Patterns Community
**Informed:** End Users, Operations Teams

## Context and Problem Statement

Organizations need a reliable, idempotent way to deploy [Validated Patterns](https://validatedpatterns.io/) on OpenShift clusters. Currently, there is no standardized template repository that:

1. Provides a complete, production-ready deployment framework for Validated Patterns
2. Supports both root directory and subdirectory execution contexts
3. Includes comprehensive validation mechanisms (Ansible-based and Tekton pipelines)
4. Offers a development environment (Gitea on OpenShift)
5. Integrates with the [validatedpatterns/common](https://github.com/validatedpatterns/common) repository
6. Provides a simple management interface (Quarkus application)

This ADR establishes the vision, scope, and high-level architecture for creating such a template repository.

## Decision Drivers

* **Idempotency**: Deployments must be repeatable and produce consistent results
* **Flexibility**: Must work as both a standalone project and as a subdirectory component
* **Validation**: Comprehensive validation at multiple stages (pre-deployment, post-deployment, continuous)
* **Developer Experience**: Easy-to-use development environment with Gitea
* **GitOps Principles**: Leverage GitOps for declarative infrastructure management
* **Community Alignment**: Integrate with existing Validated Patterns ecosystem
* **Observability**: Clear visibility into deployment status and health

## Considered Options

### Option 1: Minimal Template (Rejected)
- Simple Makefile-based deployment
- No validation framework
- No management UI
- **Rejected**: Insufficient for production use cases

### Option 2: Comprehensive Template with Ansible + Quarkus + Validation (Selected)
- Full Ansible role structure for idempotent deployments
- Quarkus management application
- Multi-stage validation (Ansible + Tekton)
- Gitea development environment
- **Selected**: Provides complete solution for enterprise deployments

### Option 3: Operator-Based Approach (Deferred)
- Custom Kubernetes Operator for pattern management
- **Deferred**: Too complex for initial implementation; consider for v2.0

## Decision Outcome

**Chosen option:** Option 2 - Comprehensive Template with Ansible + Quarkus + Validation

### Architecture Overview

```
validated-patterns-ansible-toolkit/
├── ansible/                          # Ansible roles and playbooks
│   ├── roles/
│   │   ├── validated_patterns_deploy/
│   │   ├── validated_patterns_validate/
│   │   └── validated_patterns_configure/
│   ├── playbooks/
│   │   ├── deploy_pattern.yml
│   │   ├── validate_pattern.yml
│   │   └── configure_gitea.yml
│   └── inventory/
├── quarkus-app/                      # Management application
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/
│   │   │   ├── resources/
│   │   │   └── docker/
│   │   └── test/
│   └── pom.xml
├── tekton/                           # Validation pipelines
│   ├── pipelines/
│   │   ├── pattern-validation-pipeline.yaml
│   │   └── continuous-validation-pipeline.yaml
│   ├── tasks/
│   │   ├── validate-gitops-sync.yaml
│   │   ├── validate-operators.yaml
│   │   └── validate-applications.yaml
│   └── triggers/
├── gitea/                            # Development environment
│   ├── deployment/
│   │   ├── gitea-deployment.yaml
│   │   ├── gitea-service.yaml
│   │   └── gitea-route.yaml
│   └── config/
├── patterns/                         # Pattern configurations
│   ├── multicloud-gitops/
│   ├── industrial-edge/
│   └── medical-diagnosis/
├── common/                           # Git subtree from validatedpatterns/common
├── docs/
│   ├── adr/                          # Architecture Decision Records
│   ├── tutorials/
│   ├── how-to/
│   ├── reference/
│   └── explanation/
├── files/                            # Existing EE files
├── execution-environment.yml
├── Makefile
└── README.md
```

## Goals and Success Criteria

### Primary Goals

1. **Template Repository**: Create a reusable template for deploying Validated Patterns
2. **Idempotent Deployment**: Ensure all deployments are repeatable and consistent
3. **Comprehensive Validation**: Multi-stage validation framework
4. **Developer Experience**: Integrated Gitea development environment
5. **Management Interface**: Simple Quarkus application for pattern management

### Success Criteria

- [ ] Deploy any Validated Pattern with a single command
- [ ] Support execution from root directory or subdirectory
- [ ] Validate deployment health automatically
- [ ] Provide Gitea development environment on OpenShift
- [ ] Integrate with validatedpatterns/common repository
- [ ] Pass all validation checks (Ansible + Tekton)
- [ ] Documentation following Diátaxis framework
- [ ] CI/CD pipeline for template testing

## Consequences

### Positive

* **Standardization**: Consistent deployment approach across all Validated Patterns
* **Reduced Errors**: Idempotent Ansible roles minimize configuration drift
* **Faster Onboarding**: New users can deploy patterns quickly
* **Better Validation**: Multi-stage validation catches issues early
* **Developer Productivity**: Gitea environment accelerates development
* **Maintainability**: Clear structure and documentation

### Negative

* **Complexity**: More components to maintain
* **Learning Curve**: Users need to understand Ansible, Tekton, and Quarkus
* **Resource Requirements**: Additional resources for Quarkus app and Gitea

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Complexity overwhelms users | High | Comprehensive documentation, tutorials, and examples |
| Ansible role maintenance burden | Medium | Modular design, community contributions |
| Gitea resource consumption | Low | Optional component, resource limits |
| Pattern compatibility issues | High | Extensive testing, version pinning |

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- ADR documentation
- Repository structure
- Basic Ansible roles
- Makefile targets

### Phase 2: Core Deployment (Weeks 3-4)
- Validated Patterns deployment roles
- Integration with common repository
- Basic validation checks

### Phase 3: Validation Framework (Weeks 5-6)
- Tekton pipelines
- Ansible validation playbooks
- Health check automation

### Phase 4: Management & Dev Environment (Weeks 7-8)
- Quarkus application
- Gitea deployment
- Integration testing

### Phase 5: Documentation & Polish (Weeks 9-10)
- Complete documentation
- Tutorials and guides
- CI/CD pipeline

## References

* [Validated Patterns Documentation](https://validatedpatterns.io/)
* [validatedpatterns/common Repository](https://github.com/validatedpatterns/common)
* [OpenShift GitOps](https://docs.openshift.com/gitops/)
* [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
* [Tekton Pipelines](https://tekton.dev/)
* [Quarkus Framework](https://quarkus.io/)

## Notes

This ADR establishes the foundation for subsequent ADRs that will detail specific architectural decisions for:
- Ansible role structure (ADR-002)
- Validation framework (ADR-003)
- Quarkus application design (ADR-004)
- Gitea integration (ADR-005)
- Pattern configuration management (ADR-006)
