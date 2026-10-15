# ADR-0004: Cloud Deployment Platform (Oracle Kubernetes Engine)

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-29
- **Feature:** 007-phase5-cloud-deployment
- **Context:** Phase V requires deploying 5 microservices (Backend, Recurring Task Service, Notification Service, Frontend, Audit Service) plus monitoring stack (Prometheus, Grafana, Zipkin) to a production Kubernetes cluster. The deployment must be free or low-cost, support multi-cloud portability, and provide Infrastructure-as-Code (IaC) for reproducible provisioning. Cloud credits (Azure $200, GKE $300) expire after 30-90 days, making them unsuitable for long-term free deployment.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: ✅ Long-term consequence - affects deployment strategy, operational costs, resource allocation, CI/CD pipeline
     2) Alternatives: ✅ Multiple viable options - Azure AKS, Google GKE, AWS EKS, self-hosted Kubernetes
     3) Scope: ✅ Cross-cutting concern - impacts all microservices, infrastructure provisioning, monitoring stack
     All three tests passed - ADR justified. -->

## Decision

Use Oracle Kubernetes Engine (OKE) Always-Free Tier as primary deployment platform with Terraform for Infrastructure-as-Code:

- **Primary Platform**: OKE Always-Free Tier (truly free, no credit expiry)
- **Compute Configuration**: 4 Arm Ampere A1 cores, 24GB RAM total (2 nodes × 2 cores/12GB each) - **RECOMMENDED over AMD option (2 cores, 2GB total)**
- **Storage**: 200GB block storage total (50GB per node, 2 nodes)
- **Networking**: 1 Load Balancer (10Mbps bandwidth)
- **IaC Tool**: Terraform 1.6+ with oracle-terraform-modules/oke module (official Oracle module)
- **Kubernetes Version**: 1.28+ (latest stable supported by OKE)
- **Secondary Platforms**: Azure AKS free tier, Google GKE free tier (for multi-cloud testing, not production)

Resource allocation across 2 nodes (4 Arm cores, 24GB RAM):
- Node 1: Backend (1 core, 4GB), Recurring Task Service (0.5 core, 2GB), Notification Service (0.5 core, 2GB), System overhead (1GB)
- Node 2: Frontend (0.5 core, 2GB), Prometheus (1 core, 4GB), Grafana (0.5 core, 1GB), Zipkin (0.5 core, 1GB), System overhead (1GB)

## Consequences

### Positive

- **Truly Free**: No credit expiry, no credit card required, runs indefinitely (unlike Azure $200/GKE $300 credits that expire after 30-90 days)
- **Sufficient Resources**: 4 Arm cores + 24GB RAM accommodates all 5 microservices + monitoring stack with headroom
- **Multi-Cloud Portability**: Terraform + Dapr abstraction allows deploying same application to AKS/GKE by changing Terraform modules (no code changes)
- **Kubernetes-Native**: Standard Kubernetes API (not proprietary orchestration) - skills transfer to other platforms
- **Load Balancer Included**: 1 free load balancer (no need for NodePort workarounds)
- **OCI Ecosystem**: Native integration with OCI Vault (secrets), OCI Logging (centralized logs), OCI Monitoring (infrastructure metrics)
- **Infrastructure-as-Code**: Terraform ensures reproducible provisioning (can recreate cluster in minutes, no manual clicking)
- **ARM Architecture**: Arm Ampere A1 processors energy-efficient (lower power consumption, better performance per watt)

### Negative

- **Lower Specs than Paid Tiers**: 4 cores vs 16-32 cores in paid AKS/GKE (cannot handle high traffic loads)
- **No High Availability**: Free tier limited to 2 nodes (cannot survive node failure without service interruption)
- **Oracle Account Required**: Must create Oracle Cloud account (additional account management)
- **Limited Community**: Smaller OKE community compared to AKS/GKE (fewer Stack Overflow answers, tutorials)
- **Region Availability**: Always-Free Tier only available in specific regions (us-ashburn-1, us-phoenix-1, etc.) - may have higher latency for non-US users
- **No Auto-Scaling**: Free tier nodes are fixed size (cannot auto-scale nodes based on load)
- **Arm Architecture Compatibility**: Some Docker images not built for ARM (must use arm64 images or multi-arch builds)

## Alternatives Considered

### Alternative A: Azure Kubernetes Service (AKS) Free Tier

**Components**:
- $200 free credit for new accounts (expires after 30 days)
- AKS free control plane (no charge for Kubernetes API server)
- Pay-as-you-go for worker nodes after credit expires

**Why rejected**:
- Credit expiry: $200 credit expires after 30 days - not suitable for long-term free deployment
- Requires credit card: Credit card verification required (higher barrier to entry)
- Cost after credit: Worker nodes cost ~$30/month for equivalent resources (2 cores, 8GB RAM)
- Not truly free: Only free for first 30 days, becomes paid service afterward

### Alternative B: Google Kubernetes Engine (GKE) Free Tier

**Components**:
- $300 free credit for new accounts (expires after 90 days)
- GKE Autopilot (serverless Kubernetes, pay only for pods)
- Best-in-class Kubernetes features (GKE invented by Google, created Kubernetes)

**Why rejected**:
- Credit expiry: $300 credit expires after 90 days (longer than Azure, but still not permanent)
- Requires credit card: Credit card verification required
- Cost after credit: GKE Autopilot costs ~$50/month for equivalent resources
- Not truly free: Free credit generous but temporary

### Alternative C: AWS Elastic Kubernetes Service (EKS)

**Components**:
- EKS managed control plane ($0.10/hour = $73/month)
- EC2 worker nodes (t3.medium = $0.042/hour = $30/month per node)
- Total cost: $133/month minimum (control plane + 2 nodes)

**Why rejected**:
- No free tier: EKS control plane costs $73/month (most expensive Kubernetes option)
- High minimum cost: Even minimal setup costs >$100/month
- No free credits: AWS free tier doesn't include EKS

### Alternative D: Self-Hosted Kubernetes (Minikube/K3s on VPS)

**Components**:
- VPS (Virtual Private Server) from DigitalOcean, Linode, Hetzner ($5-10/month)
- K3s lightweight Kubernetes distribution
- Manual management (updates, backups, monitoring)

**Why rejected**:
- Not free: VPS costs $5-10/month ($60-120/year)
- Operational burden: Must manually update K3s, patch security vulnerabilities, manage backups
- No managed services: No integrated load balancer, logging, monitoring (must set up manually)
- Single point of failure: VPS failure = complete outage (no redundancy)
- Learning curve: K3s differs from standard Kubernetes (reduced feature set)

## References

- Feature Spec: [specs/007-phase5-cloud-deployment/spec.md](../../specs/007-phase5-cloud-deployment/spec.md) (Part C: Cloud Deployment)
- Implementation Plan: [specs/007-phase5-cloud-deployment/plan.md](../../specs/007-phase5-cloud-deployment/plan.md)
- Technical Research: [specs/007-phase5-cloud-deployment/research.md](../../specs/007-phase5-cloud-deployment/research.md) (Section 3: Cloud Platform Selection)
- Terraform Configuration: specs/007-phase5-cloud-deployment/terraform/oke/ (to be created in implementation phase)
- Related ADRs: ADR-0001 (Infrastructure Abstraction with Dapr - OCI Vault secrets integration)
- Clarifications: PHR-0002 Clarification #1 (OKE selected as primary platform)
- OKE Always-Free Tier Documentation: https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier.htm
- oracle-terraform-modules/oke: https://github.com/oracle-terraform-modules/terraform-oci-oke
