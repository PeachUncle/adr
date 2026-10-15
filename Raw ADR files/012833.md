# Project Infrastructure Review: ECS vs EKS Clarification

**Date:** 2025-11-21  
**Reviewer:** Developer C (Infrastructure & DevOps)  
**Issue:** Confusion between ECS and EKS deployment paths  
**Status:** 🔴 **CRITICAL - NEEDS RESOLUTION**

---

## Executive Summary

**Problem Identified:** The project has developed **TWO SEPARATE infrastructure paths** in parallel:
1. **ECS (Elastic Container Service)** via Terraform - in `infrastructure/terraform/`
2. **EKS (Kubernetes)** - in `infrastructure/aws/eks/`

This creates confusion, duplication of effort, and potential maintenance burden.

**Recommendation:** **Consolidate to ONE deployment approach** - ECS via Terraform (current/proven).

---

## Current State Analysis

### What Actually Exists

#### 1. ECS Infrastructure (Terraform) - ✅ **DEPLOYED AND OPERATIONAL**

**Location:** `infrastructure/terraform/`

**Status:** **FULLY DEPLOYED** to AWS staging environment (Nov 19, 2025)

**What's Running:**
- ✅ VPC with public/private subnets (Multi-AZ)
- ✅ RDS PostgreSQL database (db.t3.micro, single-AZ for staging)
- ✅ ElastiCache Redis (cache.t3.micro, single node)
- ✅ ECS Fargate cluster
- ✅ Application Load Balancer
- ✅ Backend API (FastAPI) - 1 task running
- ✅ Frontend (Vue.js) - 1 task running
- ✅ IAM roles and security groups
- ✅ Secrets Manager for credentials
- ✅ CloudWatch logging

**Deployment Method:**
```bash
cd infrastructure/terraform/environments/staging
terraform init
terraform plan
terraform apply
```

**Cost:** ~$135/month (staging)

**Maturity:** Production-ready, tested, documented

**Evidence:**
- 7 Terraform modules (~4,000 lines)
- 2 environments (staging deployed, production ready)
- GitHub Actions CI/CD workflow
- Comprehensive documentation

#### 2. EKS Infrastructure (Kubernetes) - ⚠️ **PARTIALLY IMPLEMENTED, NOT DEPLOYED**

**Location:** `infrastructure/aws/eks/`

**Status:** **MANIFESTS CREATED, CLUSTER EXISTS FOR CI/CD ONLY**

**What Exists:**
- ✅ EKS cluster `OMC-test` (deployed for GitHub Actions runners)
- ✅ Kubernetes manifests for monitoring (Prometheus, Grafana, Loki)
- ✅ Kubernetes manifests for applications (backend, collectors, agents)
- ✅ Deployment scripts and guides
- ❌ **NOT deployed for application workloads**
- ❌ **NOT running any OMC application services**

**Purpose of EKS Cluster:**
The `OMC-test` EKS cluster was created for **GitHub Actions self-hosted runners**, NOT for application deployment. It's for CI/CD infrastructure autoscaling.

**Evidence:**
```
infrastructure/aws/eks/
├── README.md (describes self-hosted runners)
├── STEP0_CREATE_CLUSTER.md
├── STEP1_INSTALL_ARC.md (Actions Runner Controller)
├── STEP2_UPDATE_WORKFLOWS.md
├── monitoring/ (Kubernetes manifests - NOT deployed)
├── applications/ (Kubernetes manifests - NOT deployed)
└── scripts/ (deployment scripts - NOT used)
```

**Maturity:** Draft/planning stage, not production-ready

---

## How Did This Happen?

### Timeline Analysis

**Weeks 1-2 (Developer C):**
- Created Terraform infrastructure with **ECS** for container orchestration
- Deployed to AWS staging successfully
- **Decision:** Use ECS Fargate for simplicity

**Weeks 3-6 (Developer C):**
- Created **EKS cluster** for self-hosted GitHub Actions runners
- Goal: Cost-optimized CI/CD with scale-to-zero
- **EKS cluster purpose:** CI/CD infrastructure, NOT application hosting

**Weeks 7-8 (Developer C):**
- Created Kubernetes manifests for monitoring and applications
- **Confusion:** Manifests created as if deploying to EKS for applications
- **Reality:** ECS infrastructure already handles this

**Week 9+ (Current):**
- Deployment guides created for BOTH paths
- Confusion between what's deployed vs. what's planned

### Root Cause

**Miscommunication** between:
1. EKS cluster for **GitHub Actions runners** (CI/CD)
2. EKS cluster for **application workloads** (containers)

The EKS cluster exists for #1, but documentation was written as if it was for #2.

---

## Architecture Comparison

### Current: ECS via Terraform

```
┌─────────────────────────────────────────────────────┐
│                   AWS Account                        │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │                VPC (10.0.0.0/16)                │ │
│  │                                                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │ │
│  │  │  Public  │  │ Private  │  │  Private    │  │ │
│  │  │  Subnets │  │  App     │  │  Database   │  │ │
│  │  │          │  │  Subnets │  │  Subnets    │  │ │
│  │  │   ALB    │  │          │  │             │  │ │
│  │  │          │  │  ECS     │  │  RDS        │  │ │
│  │  │          │  │  Tasks   │  │  Redis      │  │ │
│  │  └────┬─────┘  └────┬─────┘  └─────┬───────┘  │ │
│  │       │             │               │          │ │
│  │    Internet      NAT Gateway    Private        │ │
│  └────────┴─────────────┴───────────────┴─────────┘ │
│                                                      │
│  ECS Services:                                       │
│  • Backend (FastAPI) - RUNNING                      │
│  • Frontend (Vue.js) - RUNNING                      │
│  • Future: Collectors, Agents                       │
│                                                      │
│  Managed via: Terraform                             │
│  Deployment: terraform apply                        │
└──────────────────────────────────────────────────────┘
```

### Alternative: EKS for Applications (NOT IMPLEMENTED)

```
┌─────────────────────────────────────────────────────┐
│                   AWS Account                        │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │                VPC (New VPC)                    │ │
│  │                                                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────┐  │ │
│  │  │  Public  │  │ Private  │  │  Private    │  │ │
│  │  │  Subnets │  │  EKS     │  │  Database   │  │ │
│  │  │          │  │  Nodes   │  │  Subnets    │  │ │
│  │  │   ALB    │  │          │  │             │  │ │
│  │  │  Ingress │  │  Pods:   │  │  RDS        │  │ │
│  │  │          │  │  Backend │  │  Redis      │  │ │
│  │  │          │  │  Agents  │  │             │  │ │
│  │  │          │  │  Monitor │  │             │  │ │
│  │  └────┬─────┘  └────┬─────┘  └─────┬───────┘  │ │
│  │       │             │               │          │ │
│  │    Internet      NAT Gateway    Private        │ │
│  └────────┴─────────────┴───────────────┴─────────┘ │
│                                                      │
│  Kubernetes Resources:                              │
│  • Deployments (backend, agents)                    │
│  • CronJobs (collectors)                            │
│  • Services, Ingress                                │
│  • Monitoring stack (Prometheus, Grafana)           │
│                                                      │
│  Managed via: kubectl / Helm / Terraform            │
│  Deployment: kubectl apply / helm install           │
└──────────────────────────────────────────────────────┘
```

### Actual EKS Cluster (GitHub Actions Runners)

```
┌─────────────────────────────────────────────────────┐
│              EKS Cluster: OMC-test                   │
│              Purpose: CI/CD ONLY                     │
│                                                      │
│  System Nodes (1x t3.medium):                       │
│  • CoreDNS                                          │
│  • Actions Runner Controller                        │
│  • Cluster Autoscaler                               │
│                                                      │
│  Runner Nodes (0-10x t3.large, scale to zero):     │
│  • Ephemeral GitHub Actions runner pods            │
│  • Scale up when workflows trigger                 │
│  • Scale down to 0 when idle                       │
│                                                      │
│  NOT used for application workloads                 │
└──────────────────────────────────────────────────────┘
```

---

## Decision Matrix: ECS vs EKS

### ECS (Current Approach)

**Pros:**
- ✅ **Already deployed and working**
- ✅ **Simpler to manage** - no Kubernetes complexity
- ✅ **Fully managed by AWS** - no node management
- ✅ **Lower operational overhead** - no kubectl, no K8s upgrades
- ✅ **Terraform-managed** - Infrastructure as Code
- ✅ **Cost-effective** - Fargate only charges for task runtime
- ✅ **Proven in production** - mature AWS service
- ✅ **Team familiarity** - easier learning curve

**Cons:**
- ❌ Less portable (AWS-specific)
- ❌ Limited orchestration features vs. Kubernetes
- ❌ Scheduled tasks via EventBridge (not native CronJobs)

**Best For:**
- Projects that don't need Kubernetes features
- Teams without Kubernetes expertise
- AWS-native deployments
- Simpler operational requirements

### EKS (Alternative Approach)

**Pros:**
- ✅ **Kubernetes standard** - portable across clouds
- ✅ **Rich ecosystem** - Helm charts, operators
- ✅ **Advanced orchestration** - StatefulSets, DaemonSets, CronJobs
- ✅ **Better for complex microservices** - service mesh, advanced networking
- ✅ **Monitoring tools** - Prometheus, Grafana native

**Cons:**
- ❌ **Not deployed** - would require complete infrastructure rebuild
- ❌ **Higher complexity** - Kubernetes learning curve
- ❌ **More operational overhead** - node management, upgrades, patching
- ❌ **Higher cost** - always-on control plane ($0.10/hour = $73/month)
- ❌ **Longer deployment time** - cluster setup, node provisioning
- ❌ **More to manage** - kubectl, Helm, RBAC, network policies

**Best For:**
- Multi-cloud deployments
- Teams with Kubernetes expertise
- Complex microservices architectures
- Need for Kubernetes-specific features

---

## Recommendation

### **PRIMARY RECOMMENDATION: Continue with ECS via Terraform**

**Rationale:**

1. **Already Working:** ECS infrastructure is deployed and operational
2. **Simplicity:** Team doesn't need Kubernetes complexity for current requirements
3. **Cost:** Lower operational costs (no EKS control plane fees)
4. **Maintenance:** Less to manage, update, and troubleshoot
5. **Terraform:** Everything is Infrastructure as Code
6. **Proven:** Current staging environment validates the approach

### **Implementation Plan:**

#### Immediate Actions (Week 9):

1. **Document the Decision**
   - Create `INFRASTRUCTURE_DECISION.md` explaining ECS choice
   - Update all documentation to clarify ECS is the deployment path
   - Mark EKS application manifests as "Future/Alternative"

2. **Update Developer C Summary**
   - Clarify EKS cluster is for CI/CD runners only
   - Remove confusion about deploying applications to EKS
   - Focus on ECS for application deployment

3. **Add Collectors and Agents to ECS**
   - Create Terraform resources for collector tasks
   - Create Terraform resources for agentic system
   - Use ECS Scheduled Tasks for cron-like collectors
   - Use ECS Services for continuous collectors
   - Add EFS volume for agent artifacts

4. **Update Deployment Guides**
   - Remove kubectl-based deployment guides from main docs
   - Keep EKS manifests in `infrastructure/aws/eks/` as "future option"
   - Focus documentation on Terraform/ECS deployment

#### What to Do with EKS Manifests:

**Option 1 (Recommended): Archive for Future Use**
```bash
mkdir -p infrastructure/archive/
mv infrastructure/aws/eks/applications/ infrastructure/archive/eks-kubernetes-manifests/
mv infrastructure/aws/eks/monitoring/ infrastructure/archive/eks-kubernetes-manifests/
```

Add README:
```markdown
# EKS Kubernetes Manifests (Archived)

These manifests were created as an alternative deployment option using Kubernetes.

**Status:** Not currently used. OMC uses ECS via Terraform.

**Purpose:** Reference for future EKS migration if needed.

**To use:** Would require setting up EKS cluster for application workloads
(separate from the existing OMC-test cluster used for CI/CD runners).
```

**Option 2 (Alternative): Keep as Migration Path**

Keep manifests but clearly mark them:
- Add warning in README: "ALTERNATIVE DEPLOYMENT - NOT CURRENTLY USED"
- Document when to consider EKS (scaling to 50+ services, multi-cloud, etc.)
- Maintain as a future option if project grows significantly

### What About the Existing EKS Cluster?

**Keep it!** The `OMC-test` EKS cluster serves a different purpose:
- **Purpose:** Self-hosted GitHub Actions runners
- **Benefit:** Cost optimization for CI/CD (scale to zero)
- **Status:** Keep as-is, it's working well

**Clarification in docs:**
```markdown
## EKS Cluster: OMC-test

**Purpose:** GitHub Actions self-hosted runners (CI/CD infrastructure)
**NOT used for:** Application workloads (use ECS instead)
```

---

## Comparison Table

| Aspect | ECS (Current) | EKS (Alternative) |
|--------|---------------|-------------------|
| **Status** | ✅ Deployed & Running | ❌ Not Deployed |
| **Complexity** | Low | High |
| **Learning Curve** | Easy | Steep |
| **Operational Overhead** | Low | High |
| **Monthly Cost** | ~$135 (staging) | ~$208 (staging + $73 control plane) |
| **Deployment Time** | 15-20 minutes | 30-45 minutes |
| **Management Tool** | Terraform only | Terraform + kubectl/Helm |
| **Team Expertise** | Basic AWS | Kubernetes required |
| **Portability** | AWS-only | Multi-cloud |
| **Monitoring** | CloudWatch | Prometheus/Grafana |
| **Scheduled Tasks** | EventBridge | Native CronJobs |
| **Auto-scaling** | ECS Auto Scaling | HPA, Cluster Autoscaler |
| **Service Discovery** | AWS Service Discovery | Kubernetes Services |
| **Secrets Management** | AWS Secrets Manager | Kubernetes Secrets |

---

## Migration Path (If EKS Needed in Future)

If the project grows and Kubernetes becomes necessary:

### Triggers for Considering EKS:
- Need for advanced Kubernetes features (StatefulSets, Operators)
- Multi-cloud requirement
- Team gains Kubernetes expertise
- Microservices count > 50
- Need for service mesh (Istio, Linkerd)

### Migration Approach:
1. Keep ECS running (zero downtime)
2. Set up new EKS cluster for applications
3. Deploy applications to EKS in parallel
4. Test thoroughly
5. Switch traffic to EKS
6. Decommission ECS

### Estimated Migration Effort:
- **Planning:** 1 week
- **EKS Setup:** 2 weeks
- **Application Migration:** 3-4 weeks
- **Testing:** 2 weeks
- **Cutover:** 1 week
- **Total:** 9-10 weeks

**Cost:** ~$100K+ in engineering time

---

## Action Items

### Immediate (This Week):

- [ ] **Document the decision** - Create `INFRASTRUCTURE_DECISION.md`
- [ ] **Update DEVELOPER_C_SUMMARY.md** - Clarify ECS is the deployment path
- [ ] **Add warnings to EKS guides** - Mark as "ALTERNATIVE/FUTURE"
- [ ] **Update ROADMAP.md** - Clarify Phase 9 uses ECS
- [ ] **Create issue in GitHub** - Track this decision

### Short Term (Weeks 9-10):

- [ ] **Add collectors to ECS Terraform** - Create task definitions
- [ ] **Add agents to ECS Terraform** - Create service definition
- [ ] **Deploy to staging via Terraform** - Test end-to-end
- [ ] **Update deployment documentation** - Focus on ECS/Terraform

### Medium Term (Weeks 11-12):

- [ ] **Production deployment via ECS** - Use existing Terraform
- [ ] **CloudWatch monitoring setup** - Replace Prometheus/Grafana plans
- [ ] **Security hardening** - AWS Config, GuardDuty, CloudTrail
- [ ] **Cost optimization review** - Validate $135/month estimate

---

## Conclusion

**Decision:** **Use ECS via Terraform** for application deployment.

**Rationale:** 
- ✅ Already working
- ✅ Simpler
- ✅ More cost-effective
- ✅ Sufficient for current needs

**EKS Cluster:**
- Keep for GitHub Actions runners (CI/CD)
- NOT used for application workloads

**EKS Manifests:**
- Archive or mark as "Future/Alternative"
- Keep as reference for potential future migration

**Next Steps:**
- Document this decision clearly
- Focus development effort on ECS deployment
- Add collectors and agents to ECS Terraform
- Deploy via existing proven infrastructure

**Impact:**
- Eliminates confusion
- Focuses team effort
- Reduces operational complexity
- Maintains cost efficiency
- Preserves future options

---

**Prepared by:** Developer C (Infrastructure & DevOps)  
**Date:** 2025-11-21  
**Status:** Awaiting approval to proceed with ECS consolidation  
**Next Review:** After Weeks 9-10 deployment
