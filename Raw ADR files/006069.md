# ADR 003 – Framework: Helm for Deployment

* **Status**: Accepted
* **Deciders**: WebGrip Engineering Team, DevOps Team
* **Date**: 2024-01-15
* **Tags**: Deployment::Tooling, Kubernetes::PackageManagement, Infrastructure::AsCode
* **Version**: 1.0.0

---

## Context and Problem Statement

Kubernetes applications require sophisticated deployment orchestration involving multiple resources (deployments, services, configmaps, secrets, ingress) with environment-specific configurations. Raw Kubernetes YAML manifests become unwieldy for complex applications and do not provide effective mechanisms for:

- Template parameterization across environments
- Dependency management and installation ordering
- Rollback capabilities and release versioning
- Configuration value management and validation
- Chart packaging and distribution

The template must provide a deployment automation solution that enables teams to deploy consistently across environments while managing complexity and maintaining repeatability.

## Decision Drivers

| # | Driver (why this matters)                                      |
| - | -------------------------------------------------------------- |
| 1 | Enable environment-specific configuration without duplication |
| 2 | Provide reliable rollback capabilities for failed deployments |
| 3 | Support complex applications with multiple interdependent resources |
| 4 | Enable packaging and versioning of deployment artifacts       |
| 5 | Integrate with GitOps workflows and CI/CD pipelines          |
| 6 | Provide dependency management for external charts             |
| 7 | Support configuration validation and best practices enforcement |
| 8 | Enable team collaboration through shared chart repositories   |

## Considered Options

1. **Raw Kubernetes YAML** – Direct kubectl application of static manifests
2. **Kustomize** – Kubernetes-native configuration management tool
3. **Helm** – Kubernetes package manager with templating capabilities
4. **Jsonnet** – Data templating language for Kubernetes configurations
5. **Custom tooling** – Bespoke deployment scripts and configuration management

## Decision Outcome

### Chosen Option

**Helm**

### Rationale

Helm provides the most mature and comprehensive solution for Kubernetes application packaging and deployment:

- **Template engine**: Go template language enables sophisticated parameterization and logic
- **Release management**: Built-in versioning, rollback capabilities, and installation tracking
- **Dependency management**: Chart dependencies with version constraints and automatic resolution
- **Ecosystem integration**: Large library of community charts and extensive tooling support
- **Values validation**: Schema-based configuration validation and documentation generation

The implementation includes:
- Comprehensive Makefile integration for common operations
- Static analysis tools (kube-score, kube-linter, kubesec) for quality assurance
- Diff capabilities for preview of changes before deployment
- Template rendering for troubleshooting and verification

### Positive Consequences

* Environment-specific deployments through values files eliminate configuration duplication
* Rollback capabilities provide safety net for deployment failures
* Chart dependencies enable modular application architecture
* Template packaging facilitates application distribution and reuse
* Integration with CI/CD pipelines through predictable CLI interface
* Comprehensive tooling ecosystem for testing, validation, and security analysis
* Values schema validation prevents configuration errors
* Release history tracking enables audit trails and troubleshooting

### Negative Consequences / Trade‑offs

* Go template syntax learning curve for developers unfamiliar with the language
* Complex charts can become difficult to debug and maintain
* Template logic can obscure the actual Kubernetes resources being generated
* Dependency on Helm CLI and tiller/server-side components (Helm 2) or client-only (Helm 3)
* Large charts with many conditionals can become unwieldy
* Template rendering requires understanding of Helm-specific functions and pipelines

### Risks & Mitigations

* **Risk**: Chart complexity makes deployments difficult to troubleshoot
  * **Mitigation**: Comprehensive testing, template rendering validation, static analysis tools integration
* **Risk**: Helm security vulnerabilities or supply chain attacks through community charts
  * **Mitigation**: Chart provenance verification, security scanning, controlled chart repositories
* **Risk**: Values configuration errors leading to deployment failures
  * **Mitigation**: JSON schema validation, comprehensive testing, staging environment validation

## Validation

* **Immediate proof** – Helm charts successfully deploy with proper templating, dependency resolution, and validation checks
* **Ongoing guardrails** – Makefile targets for chart linting, template validation, security scanning, and diff preview before deployment

## Compliance, Security & Privacy Impact

Helm deployment patterns implement security best practices:
- Values schema validation prevents injection of malicious configurations
- Chart provenance and signing for supply chain security
- Secret management integration with external secret operators
- Security scanning of generated manifests before deployment
- RBAC integration ensuring proper permission boundaries
- Separation of chart logic from sensitive configuration values

## Notes

* **Related Decisions**: ADR-001 (Docker development environment), ADR-002 (Kubernetes deployment platform)
* **Supersedes / Amends**: N/A
* **Follow‑ups / TODOs**: Implement chart testing automation, establish private chart repository, integrate with ArgoCD for GitOps

---

### Revision Log

| Version | Date       | Author              | Change           |
| ------- | ---------- | ------------------- | ---------------- |
| 1.0.0   | 2024-01-15 | WebGrip Engineering | Initial creation |
