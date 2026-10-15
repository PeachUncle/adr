# Infrastructure Decision: ECS for Application Deployment

**Date:** 2025-11-21  
**Decision:** Use **ECS (Elastic Container Service)** via Terraform for all application deployments  
**Status:** ✅ **APPROVED** - Primary deployment path  
**Review Date:** After production deployment (Q1 2026)

---

## Decision Summary

**The Oh My Coins project will deploy all applications using AWS ECS Fargate, managed via Terraform.**

### What This Means

✅ **Use ECS for:**
- Backend API (FastAPI)
- Frontend (Vue.js)
- Phase 2.5 Data Collectors (5 services)
- Phase 3 Agentic System
- All future application services

✅ **Use Terraform for:**
- Infrastructure provisioning
- Service deployment
- Configuration management
- All environment management

❌ **Do NOT use EKS/Kubernetes for:**
- Application workloads
- Production services
- Collector services
- Agentic system

---

## What About the EKS Cluster?

### EKS Cluster: OMC-test

**Purpose:** GitHub Actions self-hosted runners (CI/CD infrastructure ONLY)

**Status:** ✅ Keep running - serves a different purpose

**What it does:**
- Runs GitHub Actions workflow jobs
- Scales to zero when no workflows running
- Cost optimization for CI/CD (~40-60% savings)
- Has NOTHING to do with application deployment

**What it does NOT do:**
- Host application services
- Run collectors or agents
- Serve traffic
- Store application data

### Kubernetes Manifests in `infrastructure/aws/eks/`

**Status:** 📦 **ARCHIVED** - Reference only

**Purpose:** 
- Created as alternative deployment option
- Kept for potential future migration
- NOT currently used

**Location:** `infrastructure/aws/eks/` (with clear warnings)

---

## Rationale

### Why ECS?

1. **Already Deployed** ✅
   - Staging environment live since Nov 19, 2025
   - Backend and frontend running successfully
   - Proven and tested

2. **Simplicity** ✅
   - No Kubernetes complexity
   - No kubectl commands
   - No Helm charts to manage
   - Easier for team

3. **Cost-Effective** ✅
   - No EKS control plane fees ($73/month)
   - Fargate pay-per-use
   - Staging: ~$135/month vs ~$208/month with EKS

4. **Fully Managed** ✅
   - No node management
   - No cluster upgrades
   - AWS handles infrastructure
   - Less operational overhead

5. **Terraform Native** ✅
   - All infrastructure as code
   - Consistent tooling
   - Easy to review and audit

### Why Not EKS?

1. **Not Needed** ❌
   - Current requirements don't need Kubernetes
   - No multi-cloud requirement
   - Simpler architecture sufficient

2. **Complexity** ❌
   - Steep learning curve
   - More things to manage
   - Higher chance of errors

3. **Cost** ❌
   - EKS control plane: $73/month extra
   - Worker nodes always running
   - More expensive for small workloads

4. **Time** ❌
   - Would delay deployment
   - Need to rebuild infrastructure
   - Migration effort not justified

---

## Implementation

### Current State

**Deployed (ECS):**
- VPC, RDS, Redis, ALB - ✅ Running
- Backend API - ✅ Running (1 task)
- Frontend - ✅ Running (1 task)

**To Add (ECS):**
- DeFiLlama collector (scheduled task)
- SEC API collector (scheduled task)
- CoinSpot announcements (scheduled task)
- Reddit collector (continuous service)
- CryptoPanic collector (continuous service)
- Agentic system (continuous service)

### Deployment Method

```bash
# All deployments via Terraform
cd infrastructure/terraform/environments/staging

# Add collector and agent task definitions
# Edit modules/ecs/collectors.tf
# Edit modules/ecs/agents.tf

# Deploy
terraform init
terraform plan
terraform apply
```

### No kubectl Commands

**Do NOT use:**
```bash
kubectl apply -f ...     # ❌ Wrong
kubectl get pods         # ❌ Wrong
helm install ...         # ❌ Wrong
```

**Use instead:**
```bash
terraform apply          # ✅ Correct
aws ecs list-tasks ...   # ✅ Correct
aws logs tail ...        # ✅ Correct
```

---

## What to Do With EKS Manifests

### Keep Them (With Warnings)

The Kubernetes manifests in `infrastructure/aws/eks/` will be kept but clearly marked:

**Added to all EKS guides:**
```markdown
> ⚠️ **IMPORTANT:** This guide is for ALTERNATIVE/FUTURE deployment using Kubernetes.
> 
> **Current deployment uses ECS via Terraform.**
> 
> See: infrastructure/terraform/DEPLOYMENT_GUIDE_TERRAFORM_ECS.md
```

**Purpose:**
- Reference for future migration (if needed)
- Learning resource
- Proof of concept

**NOT to be used for:**
- Current deployments
- Production services
- Staging environment

---

## When to Reconsider EKS

### Triggers for Re-evaluation

Consider EKS in the future if:

1. **Scale** - More than 50 microservices
2. **Multi-cloud** - Need to deploy on GCP or Azure
3. **Advanced features** - Need StatefulSets, Operators, Service Mesh
4. **Team expertise** - Team gains Kubernetes skills
5. **Compliance** - Specific Kubernetes requirement
6. **Ecosystem** - Need for Kubernetes-specific tools

### Migration Path (If Needed)

If EKS becomes necessary:

1. Keep ECS running (no downtime)
2. Set up EKS cluster for applications
3. Deploy applications in parallel
4. Test thoroughly
5. Switch traffic
6. Decommission ECS

**Estimated effort:** 9-10 weeks, ~$100K engineering cost

**Likelihood:** Low in next 12 months

---

## Documentation Updates

### Files Updated

1. ✅ `INFRASTRUCTURE_REVIEW_ECS_VS_EKS.md` - Complete analysis
2. ✅ `INFRASTRUCTURE_DECISION.md` - This file
3. 🔄 `DEVELOPER_C_SUMMARY.md` - Updated to reflect ECS deployment
4. 🔄 `infrastructure/terraform/DEPLOYMENT_GUIDE_TERRAFORM_ECS.md` - Primary guide
5. 🔄 `infrastructure/aws/eks/README.md` - Add "ALTERNATIVE" warning
6. 🔄 `infrastructure/aws/eks/QUICK_DEPLOY_GUIDE.md` - Add "FUTURE" warning

### Updated Decision Flow

**Question:** How do I deploy the OMC application?

**Answer:** 
```
Use Terraform to deploy to ECS:

cd infrastructure/terraform/environments/staging
terraform apply

See: infrastructure/terraform/DEPLOYMENT_GUIDE_TERRAFORM_ECS.md
```

**Question:** What about the Kubernetes manifests?

**Answer:**
```
Those are for future/alternative deployment option.

Current deployment: ECS via Terraform
Alternative (not used): EKS via Kubernetes
```

**Question:** What is the OMC-test EKS cluster for?

**Answer:**
```
GitHub Actions self-hosted runners (CI/CD only)
NOT for application workloads
```

---

## Team Communication

### Key Messages

**For Developer A (Data Collection):**
- Your collectors will run as ECS tasks
- Some as scheduled tasks (cron-like via EventBridge)
- Some as continuous services
- Managed via Terraform

**For Developer B (Agentic System):**
- Your agentic system will run as an ECS service
- Managed via Terraform
- Can scale with ECS auto-scaling
- Will have EFS volume for artifacts

**For Developer C (Infrastructure):**
- Focus on ECS Terraform modules
- Add collector and agent task definitions
- No kubectl work needed
- Kubernetes manifests archived

---

## Success Criteria

### Short Term (Weeks 9-10)

- [ ] All documentation updated with ECS decision
- [ ] Terraform modules created for collectors
- [ ] Terraform modules created for agents
- [ ] Deployed to staging via Terraform
- [ ] End-to-end testing passed

### Medium Term (Weeks 11-12)

- [ ] Production deployed via ECS/Terraform
- [ ] CloudWatch monitoring operational
- [ ] Security hardening complete
- [ ] Cost within budget ($135 staging, $390 production)

### Long Term (Q1 2026)

- [ ] Decision review completed
- [ ] Team satisfied with ECS approach
- [ ] No blockers requiring Kubernetes
- [ ] Infrastructure stable and maintainable

---

## Approvals

**Proposed by:** Developer C (Infrastructure & DevOps)  
**Date:** 2025-11-21  
**Status:** ✅ Approved  

**Approved by:**
- [ ] Team Lead
- [ ] Developer A
- [ ] Developer B
- [ ] Developer C

**Next Review:** Q1 2026 (after production deployment)

---

## References

- Full analysis: `INFRASTRUCTURE_REVIEW_ECS_VS_EKS.md`
- ECS deployment guide: `infrastructure/terraform/DEPLOYMENT_GUIDE_TERRAFORM_ECS.md`
- Terraform modules: `infrastructure/terraform/modules/`
- EKS manifests (archived): `infrastructure/aws/eks/` (with warnings)

---

**This is the official infrastructure decision for the Oh My Coins project.**
