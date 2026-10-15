# ADR-011: Hosting Infrastructure Decision

**Status:** Accepted
**Date:** 2025-12-02
**Decision Makers:** Development Team, Business Owner
**Technical Story:** Evaluate hosting infrastructure options for the Twines and Straps e-commerce platform

## Context and Problem Statement

Twines and Straps SA has selected Azure as the hosting infrastructure to balance cost, performance, reliability, and operational complexity. The application is now deployed on Azure App Service with Azure PostgreSQL and Azure Blob Storage, providing a unified Azure stack.

> **Note:** If you're seeing a 503 error on `/api/admin/upload`, this is a configuration issue, not a hosting issue. Azure Blob Storage environment variables need to be configured in Azure App Service. See [docs/SETUP.md](../SETUP.md#azure-blob-storage-required-for-production) for setup instructions.

### Current Architecture

| Component | Current Provider | Monthly Cost (Est.) |
|-----------|-----------------|---------------------|
| Frontend Hosting | Azure App Service | ~$13 (dev) / ~$70 (prod) |
| Database | Azure PostgreSQL Flexible Server | ~$15 (dev) / ~$60 (prod) |
| Image Storage | Azure Blob Storage | ~$0.20 (10GB) |
| Key Vault | Azure Key Vault | Included |
| Monitoring | Azure Application Insights | ~$2-5 |
| Domain/DNS | External | ~$10/year |

## Decision Drivers

- **Cost Efficiency:** Total cost of ownership for a small e-commerce site
- **Operational Complexity:** Number of providers/dashboards to manage
- **Performance:** Global CDN, edge computing, database latency
- **Scalability:** Ability to grow with business needs
- **Developer Experience:** Deployment workflow, monitoring, debugging
- **South African Market:** CDN presence, latency for SA users
- **Reliability:** Uptime SLAs, disaster recovery options

## Considered Options

### Option 1: Full Azure Stack (Current Implementation)

**Description:** Unified Azure infrastructure for all services.

```
┌─────────────────────────────────────────────────────────────────┐
│                         Architecture                             │
├─────────────────────────────────────────────────────────────────┤
│  User → Azure Front Door → Azure App Service (Next.js)          │
│                           │                                      │
│                    ┌──────┴──────┐                               │
│                    ↓             ↓                               │
│         Azure PostgreSQL    Azure Blob Storage                  │
│         Flexible Server     (Images)                            │
└─────────────────────────────────────────────────────────────────┘
```

| Aspect | Details |
|--------|---------|
| **Monthly Cost** | ~$30 (dev), ~$135 (production) |
| **Providers** | Single unified provider (Azure) |
| **Deployment** | GitHub Actions → Azure App Service |
| **Database** | Azure PostgreSQL Flexible Server |
| **CDN** | Azure Front Door (global) |
| **SA Latency** | Excellent (Azure South Africa regions) |

**Pros:**
- Single provider for all services
- Unified billing and management
- Azure South Africa region for low latency
- Integrated monitoring (Azure Monitor)
- Enterprise-grade SLAs
- Infrastructure as Code (Bicep templates)
- Automated CI/CD via GitHub Actions

**Cons:**
- Higher base cost than free tiers
- More complex initial setup
- Requires Azure expertise
- Three separate billing relationships
- Potential latency between services
- Cross-provider debugging is harder
- No unified logging/monitoring

### Option 2: Full Azure Stack

**Description:** Migrate everything to Azure for unified management.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Azure Architecture                            │
├─────────────────────────────────────────────────────────────────┤
│  User → Azure Front Door (CDN)                                  │
│              │                                                   │
│              ↓                                                   │
│    Azure App Service / Container Apps                            │
│    (Next.js Application)                                         │
│              │                                                   │
│       ┌──────┴──────┐                                           │
│       ↓             ↓                                           │
│  Azure PostgreSQL   Azure Blob                                   │
│  Flexible Server    Storage                                      │
└─────────────────────────────────────────────────────────────────┘
```

| Aspect | Details |
|--------|---------|
| **Monthly Cost** | $50-150 (starter), $150-400 (production) |
| **Providers** | 1 unified provider |
| **Deployment** | Azure DevOps / GitHub Actions |
| **Database** | Azure Database for PostgreSQL |
| **CDN** | Azure Front Door / CDN |
| **SA Latency** | Excellent (Azure South Africa regions) |

**Pros:**
- Single provider for all services
- Azure South Africa region for low latency
- Unified billing and management
- Integrated monitoring (Azure Monitor)
- Enterprise-grade SLAs
- Access to Azure AI services

**Cons:**
- Higher base cost for small sites
- More complex initial setup
- Requires Azure expertise
- Less streamlined than Netlify for Next.js
- Overengineered for current scale

### Option 3: Vercel + Neon + Azure Blob

**Description:** Use Vercel (Next.js creators) for optimal frontend hosting.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Vercel Architecture                           │
├─────────────────────────────────────────────────────────────────┤
│  User → Vercel Edge Network                                      │
│              │                                                   │
│              ↓                                                   │
│    Vercel Serverless (Next.js)                                  │
│              │                                                   │
│       ┌──────┴──────┐                                           │
│       ↓             ↓                                           │
│  Neon PostgreSQL    Azure Blob                                   │
│  (or Vercel Postgres)                                           │
└─────────────────────────────────────────────────────────────────┘
```

| Aspect | Details |
|--------|---------|
| **Monthly Cost** | $20-50 (starter), $80-200 (production) |
| **Providers** | 2-3 providers |
| **Deployment** | Git push (best-in-class) |
| **Database** | Neon or Vercel Postgres |
| **CDN** | Vercel Edge Network |
| **SA Latency** | Good (Vercel has African edge nodes) |

**Pros:**
- Best Next.js performance and features
- First-party Next.js support
- Excellent preview deployments
- Built-in analytics
- Vercel Postgres integration option

**Cons:**
- Higher cost than Netlify
- Still multiple providers
- Hobby tier limitations
- Team plans can get expensive

### Option 4: Cloudflare Pages + D1/Turso + R2

**Description:** Full Cloudflare stack for edge-first architecture.

```
┌─────────────────────────────────────────────────────────────────┐
│                  Cloudflare Architecture                         │
├─────────────────────────────────────────────────────────────────┤
│  User → Cloudflare CDN (global edge)                            │
│              │                                                   │
│              ↓                                                   │
│    Cloudflare Pages + Workers                                    │
│    (Next.js on Edge Runtime)                                     │
│              │                                                   │
│       ┌──────┴──────┐                                           │
│       ↓             ↓                                           │
│   D1 / Turso        R2 Storage                                   │
│   (SQLite Edge)     (S3-compatible)                              │
└─────────────────────────────────────────────────────────────────┘
```

| Aspect | Details |
|--------|---------|
| **Monthly Cost** | Free-$25 (starter), $50-100 (production) |
| **Providers** | 1-2 providers |
| **Deployment** | Git push |
| **Database** | D1 (SQLite) or Turso (edge SQLite) |
| **CDN** | Cloudflare (excellent global coverage) |
| **SA Latency** | Excellent (Cloudflare has SA PoPs) |

**Pros:**
- Lowest latency globally
- Excellent free tier
- S3-compatible storage (R2)
- Unified Cloudflare dashboard
- Great DDoS protection included

**Cons:**
- Requires PostgreSQL to SQLite migration
- Some Next.js features limited on edge
- D1 is still in beta
- Less mature than other options

### Option 5: AWS Amplify + RDS + S3

**Description:** Full AWS stack using Amplify for simplified deployment.

| Aspect | Details |
|--------|---------|
| **Monthly Cost** | $30-80 (starter), $100-300 (production) |
| **Providers** | 1 unified provider |
| **Deployment** | Git push via Amplify |
| **Database** | RDS PostgreSQL / Aurora Serverless |
| **CDN** | CloudFront |
| **SA Latency** | Good (AWS Cape Town region) |

**Pros:**
- Single provider
- AWS Cape Town region
- Enterprise-grade infrastructure
- Excellent scaling options

**Cons:**
- Complex pricing model
- AWS expertise required
- Higher cost for small sites
- Steeper learning curve

## Cost Comparison

### Estimated Monthly Costs by Traffic Level

| Scenario | Netlify+Neon+Azure | Full Azure | Vercel+Neon+Azure | Cloudflare+R2 | AWS |
|----------|-------------------|------------|-------------------|---------------|-----|
| **Development** | Free | $30-50 | $20 | Free | $30 |
| **Small (1K visits/mo)** | $0-30 | $50-80 | $20-40 | $0-10 | $40-60 |
| **Medium (10K visits/mo)** | $40-60 | $80-120 | $50-80 | $25-40 | $70-100 |
| **Growth (50K visits/mo)** | $60-100 | $150-250 | $100-150 | $50-80 | $120-180 |

### Feature Comparison

| Feature | Netlify+Neon | Full Azure | Vercel+Neon | Cloudflare |
|---------|--------------|------------|-------------|------------|
| Deploy Preview | ✅ Excellent | ⚠️ Manual setup | ✅ Excellent | ✅ Good |
| CDN | ✅ Good | ✅ Front Door | ✅ Excellent | ✅ Excellent |
| Edge Functions | ✅ Good | ⚠️ Limited | ✅ Excellent | ✅ Excellent |
| Database Branching | ✅ Neon | ❌ No | ✅ Neon | ❌ No |
| SA Presence | ✅ Yes | ✅ Native | ✅ Yes | ✅ Yes |
| Unified Billing | ❌ 3 providers | ✅ 1 provider | ❌ 2-3 providers | ✅ 1 provider |
| Monitoring | ⚠️ Separate | ✅ Azure Monitor | ⚠️ Separate | ⚠️ Separate |

## Decision Outcome

**Chosen Option: Option 2 - Full Azure Stack**

### Rationale

1. **Already Working:** The current architecture is functional and proven
2. **Cost-Effective:** Free tiers cover development; production costs are reasonable
3. **Right-Sized:** Matches current traffic and complexity needs
4. **Best-of-Breed:** Each provider excels at their specific function
5. **Migration Risk:** Moving to a new platform introduces unnecessary risk
6. **Azure Integration:** Already using Azure Blob Storage; easy to expand Azure usage later

### When to Reconsider

Consider migrating to Full Azure (Option 2) when:
- Monthly traffic exceeds 50K visits
- Need unified enterprise logging/monitoring
- Want to leverage Azure AI services more heavily
- Team has Azure expertise
- Require Azure Active Directory integration

Consider Vercel (Option 3) when:
- Need cutting-edge Next.js features immediately
- Preview deployments become critical to workflow
- Team size grows significantly

### Implementation Notes

#### Current Stack Optimization

1. **Add Azure CDN in front of Blob Storage** for faster image delivery:
   ```
   Azure CDN → Azure Blob Storage
   ```

2. **Configure Neon for South Africa** by selecting appropriate region

3. **Monitor costs** using Azure Cost Management:
   - Azure Portal → Cost Management + Billing
   - Set up budgets and alerts
   - Track spending by resource group

4. **Set up unified logging** using external service (e.g., Axiom, LogRocket) if needed

### Future Migration Path

If consolidation becomes necessary:

```
Phase 1: Current Stack (Now)
    ↓
Phase 2: Add Azure CDN for images
    ↓
Phase 3: Evaluate Azure Container Apps for app hosting
    ↓
Phase 4: Consider Azure PostgreSQL migration
    ↓
Phase 5: Full Azure Stack (if justified by scale)
```

### Positive Consequences

- No immediate migration effort required
- Continue using familiar tools
- Costs remain predictable
- Each provider can be replaced independently
- Can gradually adopt more Azure services

### Negative Consequences

- Multiple dashboards to monitor
- Cross-provider debugging challenges
- No unified support contract
- Potential latency between services

## Links

- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [Azure App Service Pricing](https://azure.microsoft.com/pricing/details/app-service/windows/)
- [Neon Pricing](https://neon.tech/pricing)
- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [Vercel Pricing](https://vercel.com/pricing)
- [Cloudflare Pages](https://pages.cloudflare.com/)

---

*Last Updated: December 2025*
