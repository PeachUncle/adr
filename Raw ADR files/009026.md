# ADR-020: Azure Container Apps for Hosting

**Status:** ✅ Accepted  
**Date:** October 2025  
**Context:** Production Deployment Platform Selection

## Context

The system required cloud hosting that supports:

- Multiple Blazor Server apps (6 user personas)
- Web API with SignalR
- Auto-scaling (0-50 instances based on load)
- Cost optimization (scale to zero for admin apps)
- HTTPS with custom domains
- Health checks and rolling updates
- Easy CI/CD integration

Options:

- Azure Kubernetes Service (AKS) - full control, complex
- Azure Container Apps - serverless, managed
- Azure App Service - PaaS, expensive
- Azure VM Scale Sets - IaaS, too low-level
- Azure Functions - stateless only, not suitable

## Decision

Selected **Azure Container Apps** as the primary production hosting platform.

## Rationale

1. **Serverless**: Pay only for running containers (per-second billing)
2. **Auto-scaling**: Scales 0→N based on HTTP requests, CPU, memory
3. **Managed**: No cluster management overhead (vs AKS)
4. **Built-in Features**: HTTPS, ingress, health probes, secrets, Dapr
5. **Cost-Effective**: Scale to zero for low-traffic admin apps (~$15-30/month)
6. **Fast Deployment**: Minutes vs hours (AKS)
7. **Azure Native**: Integrates with Azure Database, Redis, KeyVault
8. **Migration Path**: Can move to AKS later if needed

## Consequences

### Positive

- **Cost savings**: Admin apps scale to zero during off-hours
- **Simple deployment**: azd deploy automates everything
- **No cluster management**: No Kubernetes learning curve
- **Fast scaling**: 0→10 instances in seconds
- **Built-in observability**: Application Insights integration
- **Easy rollback**: Revisions system for blue/green deployment

### Negative

- **Less control**: Limited customization vs AKS
- **Cold start**: 1-2s delay when scaling from zero
- **VNet complexity**: Private networking requires VNET integration
- **Limits**: Max 30 replicas per app (vs unlimited in AKS)
- **Billing complexity**: Per-second billing harder to predict

### Risks Mitigated

- Min replicas=2 for Web API (no cold starts)
- Min replicas=1 for Student App (acceptable cold start)
- Health checks ensure traffic only routes to healthy instances
- Multiple environments (dev, staging, production) for testing
- Bicep infrastructure as code for reproducibility

## Architecture

**Production Environment**:

```
Azure Container Apps Environment (kindsea-395ab1c0.eastus.azurecontainerapps.io)
├── webapi (min=2, max=20)          # High availability
├── studentapp (min=1, max=50)      # Scales with student load
├── dashboard (min=0, max=10)       # Teacher dashboards
├── schooladminapp (min=0, max=5)   # School admins
├── courseadminapp (min=0, max=3)   # Course admins
├── bizadminapp (min=0, max=3)      # Business admins
└── sysadminapp (min=0, max=2)      # System admins
```

**Scaling Rules**:

- **HTTP**: 100 concurrent requests per instance
- **CPU**: 70% threshold
- **Memory**: 80% threshold

**Resource Allocation**:

- **Web API**: 1.0 CPU, 2.0 Gi memory
- **Student App**: 0.5 CPU, 1.0 Gi memory
- **Admin Apps**: 0.25 CPU, 0.5 Gi memory

## Deployment Process

**Using Azure Developer CLI (azd)**:

```bash
azd auth login
azd up --environment production
```

**What happens:**

1. `azd provision` → Deploys Bicep infrastructure
2. Builds Docker images for each app
3. Pushes images to Azure Container Registry
4. Creates/updates container apps
5. Injects secrets from Azure KeyVault
6. Runs health checks before routing traffic

## Cost Estimates

**Monthly Costs** (production, moderate load):

- Container Apps Environment: $58/month (dedicated plan)
- Web API (2 replicas × 1.0 CPU): $72/month
- Student App (avg 5 replicas × 0.5 CPU): $90/month
- Admin Apps (scale to zero, avg usage): $15/month
- **Total Container Apps**: ~$235/month

**Plus data services:**

- Azure Database for PostgreSQL: $12-50/month
- Azure Cache for Redis: $15-100/month
- Azure SignalR Service: $50/month
- Application Insights: $0-50/month (5GB free)

**Total**: ~$320-500/month (50-500 active students)

## Internal Networking (FQDN)

Container Apps use internal FQDNs for service-to-service communication:

- `postgres.internal.kindsea-395ab1c0.eastus.azurecontainerapps.io`
- `cache.internal.kindsea-395ab1c0.eastus.azurecontainerapps.io`

**Challenge**: Template variables don't work reliably → **Solution**: Runtime FQDN detection (ADR-022)

## Health Checks

**Liveness** (is container alive?):

```yaml
probes:
  liveness:
    httpGet:
      path: /health/live
      port: 8080
    initialDelaySeconds: 10
    periodSeconds: 30
```

**Readiness** (is container ready for traffic?):

```yaml
probes:
  readiness:
    httpGet:
      path: /health/ready
      port: 8080
    initialDelaySeconds: 5
    periodSeconds: 10
```

## Alternative Considered: Azure Kubernetes Service (AKS)

**Rejected because:**

- Higher complexity (Kubernetes learning curve)
- More expensive ($150-300/month baseline for cluster)
- Longer deployment time (cluster provisioning)
- Requires dedicated DevOps expertise
- Overkill for current scale (50-5,000 students)

**When to migrate to AKS:**

- Need >30 replicas per app
- Require advanced networking (service mesh, Istio)
- Need custom resource types (CRDs)
- Hit Container Apps limitations
- Scale exceeds 50,000 concurrent users

## Related Decisions

- ADR-021: Azure Database for PostgreSQL (managed service)
- ADR-022: Runtime FQDN Detection (connection string patching)
- ADR-006: Redis for Caching Layer (SignalR backplane)
- ADR-033: Client-Secret Authentication (vs OIDC)

## References

- `infra/resources.bicep` - Container Apps infrastructure
- `src/infra/*.tmpl.yaml` - Container app configurations
- Commit: `252231e` - "Migrate to Azure Database for PostgreSQL"
- docs/deployment/AZURE_DEPLOYMENT_STRATEGY.md
