# ADR-0003: Containerization as Core Service Strategy

**Status**: Accepted  
**Date**: 2025-11-26  
**Deciders**: Tony Moores  
**Technical Story**: Phase 0 - Foundation

## Context

TJMPaaS aims to build a library of services that can be deployed across multiple cloud providers and potentially offered commercially. The packaging and deployment strategy for these services fundamentally impacts portability, scalability, and operational complexity.

### Problem Statement

Determine the primary packaging and deployment mechanism for TJMPaaS services that supports:
- Multi-cloud portability
- Operational consistency
- Scalability and resource efficiency
- Commercial distribution
- Development and deployment simplicity

### Goals

- Enable cloud-agnostic service deployment
- Standardize operational patterns across services
- Support both development and production environments
- Facilitate commercial distribution
- Minimize operational overhead for customers
- Enable horizontal scaling

### Constraints

- Must work on GCP initially, other clouds later
- Solo developer - operational simplicity matters
- Services may have different runtime requirements
- Need to support both stateless and stateful services
- Commercial customers expect standard deployment patterns

## Decision

**Adopt containerization (Docker/OCI containers) as the core packaging strategy for all TJMPaaS services**, orchestrated primarily via Kubernetes (GKE on GCP).

All services will:
1. Be packaged as OCI-compliant container images
2. Follow container best practices (12-factor app principles)
3. Use Kubernetes for orchestration
4. Include Kubernetes manifests or Helm charts
5. Support configuration via environment variables
6. Expose health check endpoints
7. Implement graceful shutdown

## Rationale

### Cloud Portability

Containers provide:
- **Runtime consistency** across cloud providers
- **Infrastructure abstraction** - same container runs anywhere
- **Kubernetes ubiquity** - available on all major clouds (GKE, EKS, AKS)
- **No cloud lock-in** for application layer

### Operational Benefits

Containers enable:
- **Immutable infrastructure** - reproducible deployments
- **Resource efficiency** - lightweight compared to VMs
- **Fast startup times** - quick scaling and recovery
- **Isolated dependencies** - no conflicts between services
- **Version control** - images are versioned artifacts

### Developer Experience

Containers improve:
- **Local development** - matches production environment
- **Testing** - consistent test environments
- **CI/CD** - standard build and deployment pipelines
- **Debugging** - can replicate production locally

### Commercial Distribution

Containers provide:
- **Standard packaging** - industry-standard distribution
- **Simple deployment** - customers understand containers
- **Marketplace ready** - can publish to cloud marketplaces
- **Licensing control** - image-based distribution
- **Update mechanism** - new versions via new images

### Ecosystem and Tooling

Container ecosystem offers:
- **Mature tooling** - Docker, Kubernetes, registries
- **Security scanning** - vulnerability detection in images
- **Registry support** - GCP Artifact Registry, Docker Hub, etc.
- **Monitoring integration** - Prometheus, Grafana, etc.
- **Service mesh** - Istio, Linkerd for advanced networking

## Alternatives Considered

### Alternative 1: Virtual Machines (VMs)

**Description**: Package services as VM images (GCP Compute Engine, AWS AMI, Azure VM)

**Pros**:
- Complete OS control
- Familiar to many operators
- Strong isolation
- Can run any workload

**Cons**:
- Heavy resource consumption
- Slower startup times
- More complex to maintain (OS patching)
- Less portable across clouds
- Higher infrastructure costs
- Slower deployment cycles

**Reason for rejection**: Too heavy, cloud-specific, operationally complex, and resource inefficient for PaaS services

### Alternative 2: Serverless Functions (FaaS)

**Description**: Deploy services as serverless functions (Cloud Functions, Lambda, Azure Functions)

**Pros**:
- Zero infrastructure management
- Automatic scaling
- Pay-per-use pricing
- Simple deployment

**Cons**:
- Vendor lock-in (different APIs per cloud)
- Cold start latency
- Execution time limits
- Limited runtime control
- Difficult for stateful services
- Restrictions on dependencies and languages

**Reason for rejection**: Too constraining for general PaaS services; appropriate for some components but not core strategy

### Alternative 3: Platform-Specific Services (PaaS)

**Description**: Use cloud-specific PaaS offerings (Cloud Run, App Engine, Elastic Beanstalk, Azure App Service)

**Pros**:
- Managed infrastructure
- Simplified deployment
- Built-in scaling
- Lower operational overhead

**Cons**:
- Cloud-specific lock-in
- Limited portability
- Different capabilities per cloud
- Restricts architecture choices
- Harder to offer commercially

**Reason for rejection**: Defeats multi-cloud portability goal; creates cloud lock-in

### Alternative 4: Bare Metal / Traditional Deployment

**Description**: Deploy directly on servers without containerization

**Pros**:
- Maximum performance
- Full control
- No abstraction overhead
- Traditional approach

**Cons**:
- Environment inconsistencies
- Dependency conflicts
- Complex deployment automation
- No cloud portability
- Difficult to scale
- Not commercially viable

**Reason for rejection**: Operationally impractical; incompatible with cloud-native and commercial goals

### Alternative 5: Hybrid Approach

**Description**: Mix containers with VMs, serverless, or platform services as appropriate

**Pros**:
- Flexibility to choose per service
- Optimize for specific needs
- Use best tool for each job

**Cons**:
- Operational complexity multiplies
- Inconsistent patterns
- More skills required
- Harder to document and support
- Confusing for customers

**Reason for rejection**: Excessive complexity for solo operator; prefer consistent approach

## Consequences

### Positive

- **Cloud Portability**: Services run consistently across cloud providers
- **Scalability**: Kubernetes handles horizontal scaling automatically
- **Development Parity**: Local dev environment matches production
- **CI/CD Simplicity**: Standard container build and deployment pipeline
- **Resource Efficiency**: Better resource utilization than VMs
- **Commercial Viability**: Standard packaging customers expect
- **Ecosystem Access**: Leverage vast container and Kubernetes ecosystem
- **Isolation**: Service dependencies isolated in containers

### Negative

- **Learning Curve**: Kubernetes has significant complexity
- **Operational Overhead**: Need to manage Kubernetes clusters
- **Statefulness**: Stateful services more complex in containers
- **Debugging**: Container debugging different from traditional
- **Storage**: Persistent storage requires additional configuration
- **Networking**: Container networking adds complexity layer

### Neutral

- **Maturity**: Containers are mature but still evolving
- **Security**: Container security requires attention (image scanning, runtime security)
- **Performance**: Slight overhead vs. bare metal (negligible for most workloads)
- **Costs**: Kubernetes control plane costs, but efficient resource usage

## Implementation

### Requirements

1. **Container Standards**:
   - Use OCI-compliant images (Docker, Podman compatible)
   - Multi-stage builds for smaller images
   - Minimal base images (Alpine, Distroless)
   - Non-root user execution
   - Health check endpoints

2. **Kubernetes Patterns**:
   - Deployments for stateless services
   - StatefulSets for stateful services
   - Services for networking
   - ConfigMaps for configuration
   - Secrets for sensitive data
   - Ingress for external access

3. **Image Management**:
   - GCP Artifact Registry for storage
   - Semantic versioning for images
   - Automated security scanning
   - Image signing (future)

4. **Service Requirements**:
   - `/health` endpoint (liveness probe)
   - `/ready` endpoint (readiness probe)
   - Graceful shutdown on SIGTERM
   - 12-factor app principles
   - Configuration via environment variables
   - Structured logging to stdout

5. **Development Workflow**:
   - Docker Compose for local development
   - Skaffold or similar for local Kubernetes dev
   - CI pipeline builds and pushes images
   - Automated deployment to GKE

### Migration Path

Phase-by-phase adoption:
1. ✅ **Phase 0**: Establish containerization as standard
2. **Phase 1**: Deploy first services to GKE
3. **Phase 2**: Expand service catalog
4. **Phase 3**: Implement service mesh (Istio)
5. **Phase 4**: Validate on additional clouds (EKS, AKS)

### Timeline

- **Q4 2025**: Container standards established, GKE setup
- **Q1 2026**: First production services on GKE
- **Q2-Q3 2026**: Service catalog expansion
- **Q4 2026**: Multi-cloud validation

## Validation

Success criteria:

- All services packaged as containers
- Services deploy consistently to GKE
- Container images pass security scans
- Local development uses containers
- CI/CD pipeline builds and deploys containers
- Services demonstrate portability (can run on different Kubernetes clusters)
- Resource utilization efficient
- Scaling works as expected

Metrics:
- Container build time < 5 minutes
- Deployment time < 2 minutes
- Container startup time < 30 seconds
- Resource overhead < 10% vs. native
- Zero environment-specific bugs

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Kubernetes complexity | High | Use managed Kubernetes (GKE); focus on core features; leverage Helm charts |
| Security vulnerabilities | High | Automated image scanning; regular base image updates; security policies |
| Stateful service challenges | Medium | Use StatefulSets; leverage cloud storage; document patterns |
| Performance overhead | Low | Use efficient base images; profile workloads; optimize as needed |
| Storage persistence | Medium | Use Persistent Volumes; cloud storage integration; backup strategies |
| Networking complexity | Medium | Use service mesh for advanced features; document networking patterns |
| Image size bloat | Medium | Multi-stage builds; minimal base images; regular image audits |

## Related Decisions

- ADR-0001: GCP as pilot platform (GKE is the Kubernetes platform)
- Future ADR: Kubernetes distribution and configuration approach
- Future ADR: Service mesh selection (Istio vs. alternatives)
- Future ADR: Container registry and image management strategy

## References

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [12-Factor App](https://12factor.net/)
- [OCI Specification](https://opencontainers.org/)
- [GKE Documentation](https://cloud.google.com/kubernetes-engine/docs)
- [Container Security Best Practices](https://cloud.google.com/architecture/best-practices-for-building-containers)

## Notes

This decision aligns with industry best practices for cloud-native applications and positions TJMPaaS for:
- Multi-cloud deployment (Kubernetes everywhere)
- Commercial distribution (standard packaging)
- Operational efficiency (resource optimization)
- Developer productivity (consistent environments)

The commitment to containerization is not just a technical decision—it's a strategic choice that enables the entire business model of TJMPaaS. Without containers and Kubernetes, multi-cloud portability and commercial distribution would be significantly more complex.

While Kubernetes has a learning curve, managed Kubernetes (GKE) mitigates much of the operational burden, and the benefits far outweigh the complexity costs.

## Revision History

| Date | Change | Author |
|------|--------|--------|
| 2025-11-26 | Initial draft and acceptance | Tony Moores |
