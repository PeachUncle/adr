# Architecture Decision Record: AWS Kubernetes Learning Environment Strategy

## Status

Proposed

## Context

As a Platform Engineering team member working with approximately 50 C# microservices across AWS infrastructure, there is a need to establish personal learning environments for practicing Kubernetes, Terraform, and platform engineering patterns. This ADR addresses two distinct use cases:

1. **Production-like AWS Learning Environment**: Practice and learning environment that mirrors real-world platform engineering scenarios
2. **Homelab Integration**: Existing on-premises Kubernetes homelab running Talos Linux on spare hardware that could benefit from AWS integration

The learning environment must support:

- Terraform infrastructure-as-code practices
- Realistic platform engineering patterns (observability, GitOps, IAM, networking)
- Cost-effective operation for personal learning
- Skills transferable to production platform work
- Integration with existing homelab infrastructure where applicable

Current homelab setup:

- Kubernetes cluster running on local network
- Talos Linux as the OS and Kubernetes distribution
- Spare PC hardware

## Decision

### Use Case 1: Production-like Learning - Amazon EKS (Standard)

**Selected Option**: Amazon EKS with self-managed node groups

**Key Characteristics**:

- Managed Kubernetes control plane (API server, etcd, scheduler, controller manager)
- Self-managed worker nodes on EC2 instances
- Full control over node configuration, scaling, and lifecycle
- Complete access to Kubernetes primitives and features
- Integration with AWS services via IAM roles for service accounts (IRSA)

**Rationale**:

- **Production alignment**: EKS with EC2 nodes is the most common production pattern, directly applicable to platform engineering work
- **Learning depth**: Provides hands-on experience with:
  - Node lifecycle management
  - Auto-scaling groups and cluster autoscaler
  - CNI networking and VPC integration
  - Storage classes and CSI drivers
  - Security groups and network policies
  - IAM authentication and RBAC
- **Terraform practice**: Rich ecosystem of Terraform modules and patterns for EKS
- **Platform patterns**: Supports full implementation of platform engineering concepts including add-ons, observability, GitOps, and service mesh
- **Cost control**: Node selection and scaling fully controllable for budget management
- **Troubleshooting skills**: Exposes real-world operational challenges and debugging scenarios

**EKS vs EKS Fargate Comparison**:

| Aspect | EKS (EC2 Nodes) | EKS Fargate |
|--------|----------------|-------------|
| **Node Management** | Self-managed EC2 instances via ASG | Serverless - no node management |
| **Control & Flexibility** | Full control over node configuration, instance types, AMIs | Limited - pod-level scheduling only |
| **Cost Model** | Pay for EC2 instances (even if idle) | Pay per pod vCPU/memory per second |
| **Learning Value** | High - mirrors production operations | Lower - abstracts away infrastructure |
| **Kubernetes Features** | All features supported (DaemonSets, HostPath, etc.) | Limited - no DaemonSets, HostPath, or privileged containers |
| **Platform Add-ons** | Can run any Kubernetes workload | Limited - some add-ons incompatible |
| **Observability** | Full node and pod metrics | Pod-level metrics only |
| **Networking** | VPC CNI with full control | VPC CNI with pod-per-ENI model |
| **Startup Time** | Nodes stay running | ~30-60 second pod cold start |
| **Use Case Fit** | Production-like platform learning | Specific workload patterns, less learning depth |

**Decision**: Use EKS with EC2 nodes for production-like learning because:

1. Fargate abstracts away critical platform engineering concerns (node management, system add-ons, resource optimization)
2. Many platform patterns require node-level access (monitoring agents, CNI plugins, security tooling)
3. Fargate limitations would restrict learning scope (no DaemonSets, privileged containers, or hostPath volumes)
4. Real platform work involves node lifecycle management, autoscaling decisions, and infrastructure optimization
5. Cost can be managed through small instance types and proper shutdown practices

### Use Case 2: Homelab Integration - Amazon EKS Anywhere

**Selected Option**: Amazon EKS Anywhere on existing Talos Linux homelab

**Key Characteristics**:

- Kubernetes distribution that runs on-premises with AWS integration
- Optional connection to AWS for cluster lifecycle management, billing, and support
- GitOps-based cluster management using Flux
- Support for multiple infrastructure providers including bare metal
- Curated software packages and Kubernetes distribution similar to EKS

**Rationale**:

- **Homelab value-add**: Enhances existing investment in on-premises Kubernetes infrastructure
- **Hybrid cloud patterns**: Practice hybrid and multi-cluster scenarios relevant to enterprise platform engineering
- **AWS integration**: Connect on-premises workloads with AWS services (IAM, CloudWatch, Systems Manager)
- **Talos compatibility**: EKS Anywhere supports bare metal installations, compatible with Talos-based infrastructure
- **Cost efficiency**: Leverages existing hardware; only AWS service costs for integration features
- **Advanced patterns**: Enables learning about:
  - Multi-cluster management
  - Hybrid cloud networking
  - Edge computing patterns
  - Disaster recovery across environments
  - Workload portability

**EKS Anywhere vs Local Talos Kubernetes**:

| Aspect | EKS Anywhere | Standard Talos Kubernetes |
|--------|--------------|---------------------------|
| **AWS Integration** | Native AWS service integration available | Requires custom integration work |
| **Cluster Management** | GitOps with Flux, optional AWS console integration | Self-managed with Talos CLI |
| **Support Model** | AWS support available (paid) | Community support only |
| **Kubernetes Distribution** | EKS-curated with tested packages | Standard Kubernetes |
| **Multi-cluster** | Built-in management cluster pattern | Manual setup required |
| **Upgrades** | Coordinated with EKS release cycle | Independent upgrade path |
| **Skills Transfer** | Directly applicable to EKS hybrid scenarios | Generic Kubernetes skills |

**Implementation Approach for EKS Anywhere**:

1. Maintain existing Talos cluster for immediate use
2. Evaluate EKS Anywhere as an evolution/replacement path
3. Use as opportunity to learn cluster migration and management patterns
4. Consider running both to practice multi-cluster management

## Implementation Plan

### Phase 1: EKS Production-like Learning Environment

**Infrastructure Setup**:

```text
Terraform Layer 1: Networking
- VPC with public and private subnets across 2-3 AZs
- NAT Gateway for private subnet egress
- VPC endpoints for cost optimization (optional)

Terraform Layer 2: EKS Cluster
- EKS cluster with OIDC provider for IRSA
- IAM roles for cluster and nodes
- Security groups and network policies
- CloudWatch logging for control plane

Terraform Layer 3: Node Groups
- Self-managed node group using t3.medium (2-3 nodes)
- Launch template with user data
- Auto Scaling Group configuration
- Cluster Autoscaler setup

Terraform Layer 4: Kubernetes Add-ons
- AWS Load Balancer Controller
- EBS CSI Driver
- VPC CNI updates
- CoreDNS configuration
- Metrics Server
```

**Cost Optimization**:

- Use t3.medium or t3.small instances (approx $30-60/month for 2-3 nodes)
- Implement automatic cluster shutdown during non-use hours via Lambda
- Use Spot instances for cost savings (acceptable for learning environment)
- Single AZ deployment acceptable for learning (reduces NAT Gateway costs)

**GitOps Integration**:

- Deploy ArgoCD or Flux for GitOps workflows
- Practice environment variable management patterns currently being implemented for production
- Integrate with existing platform documentation RAG system for capturing learnings

### Phase 2: EKS Anywhere Homelab Integration

**Evaluation and Planning**:

1. Assess EKS Anywhere compatibility with current Talos setup
2. Determine AWS integration requirements and costs
3. Plan migration or parallel operation strategy
4. Document hybrid cloud networking requirements

**Implementation Options**:

- **Option A**: Replace Talos with EKS Anywhere for unified management
- **Option B**: Run parallel clusters for multi-cluster pattern practice
- **Option C**: Migrate workloads progressively from Talos to EKS Anywhere

## Consequences

### Positive

- **Skill Development**: Direct experience with production-grade Kubernetes patterns in AWS
- **Platform Engineering Practice**: Hands-on implementation of golden paths, guardrails, and self-service patterns
- **Terraform Mastery**: Real-world IaC practice with complex, multi-layered infrastructure
- **Resume Building**: Demonstrable experience with industry-standard tools and practices
- **Homelab Enhancement**: Adds enterprise integration capabilities to existing infrastructure
- **Hybrid Cloud Skills**: Practice patterns relevant to multi-cloud and edge scenarios
- **Cost Effective**: Controlled costs while maintaining production-like complexity

### Negative

- **Monthly Costs**: Ongoing AWS charges for EKS cluster and EC2 instances (estimated $50-100/month)
- **Operational Overhead**: Requires active management and maintenance of learning environment
- **Complexity**: More complex than simpler alternatives like minikube or kind
- **Time Investment**: Significant learning curve for full EKS implementation
- **EKS Anywhere Complexity**: Additional complexity for homelab integration, may be overkill

### Risks and Mitigations

- **Risk**: Unexpected AWS costs
  - **Mitigation**: Set up billing alerts, use AWS Budgets, implement auto-shutdown schedules
- **Risk**: Over-engineering the learning environment
  - **Mitigation**: Start with minimal viable setup, add complexity incrementally
- **Risk**: EKS Anywhere incompatibility with Talos
  - **Mitigation**: Thorough evaluation phase before commitment, maintain Talos as fallback
- **Risk**: Time investment competing with work priorities
  - **Mitigation**: Align learning goals with work projects, practice patterns directly applicable to platform team

## Alternatives Considered

### For Use Case 1: Production-like Learning

#### Alternative 1: EKS Fargate

- **Rejected**: Abstracts away too many platform engineering concerns critical for learning
- **Limitations**: No DaemonSets, limited add-on support, no node-level operations
- **Use Case**: Better suited for specific workload patterns, not comprehensive learning

#### Alternative 2: Self-managed Kubernetes (kops/kubeadm)

- **Rejected**: Excessive operational overhead for learning value
- **Reasoning**: Control plane management adds complexity without proportional learning benefit
- **Note**: Still valuable as advanced learning topic after mastering EKS

#### Alternative 3: Lightweight local Kubernetes (k3s, minikube, kind)

- **Rejected**: Insufficient for learning production patterns
- **Gap**: Doesn't expose AWS integration, networking complexity, or scale considerations
- **Note**: Useful for quick local testing but not primary learning environment

#### Alternative 4: Managed Kubernetes on other clouds (GKE, AKS)

- **Rejected**: Less relevant to current AWS-centric work environment
- **Note**: Valuable for multi-cloud learning but lower priority

### For Use Case 2: Homelab Integration

#### Alternative 1: Continue with standard Talos Kubernetes

- **Consideration**: Simpler, no additional AWS integration complexity
- **Tradeoff**: Misses opportunity for hybrid cloud pattern learning
- **Decision**: Valid fallback if EKS Anywhere proves too complex

#### Alternative 2: Rancher for multi-cluster management

- **Consideration**: Alternative to EKS Anywhere for managing multiple clusters
- **Tradeoff**: Different skill set, less AWS-specific
- **Decision**: Consider if EKS Anywhere doesn't meet needs

#### Alternative 3: K3s for lightweight homelab

- **Consideration**: Lighter weight than full Kubernetes
- **Tradeoff**: Different distribution from production EKS
- **Decision**: Doesn't align with production pattern learning goals

## References

- [Amazon EKS Documentation](https://docs.aws.amazon.com/eks/)
- [Amazon EKS Fargate Documentation](https://docs.aws.amazon.com/eks/latest/userguide/fargate.html)
- [Amazon EKS Anywhere Documentation](https://anywhere.eks.amazonaws.com/)
- [Talos Linux Kubernetes Documentation](https://www.talos.dev/)
- [Terraform AWS EKS Module](https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest)
- Team Topologies principles for platform engineering
- Internal ADRs on infrastructure layering strategy and Terraform Cloud workflows

## Notes

- This ADR focuses on personal learning environments and is separate from production platform decisions
- Cost estimates are approximate and should be monitored via AWS Cost Explorer
- EKS Anywhere evaluation should include hands-on testing before full commitment
- Consider documenting learnings in platform engineering knowledge base using RAG system
- Align Terraform patterns with team's established ADRs for consistency

## Review Date

Review this decision after 3 months of implementation to assess:

- Actual costs vs estimates
- Learning value vs time investment
- EKS Anywhere feasibility and value for homelab
- Need for additional learning environments or pattern variations
