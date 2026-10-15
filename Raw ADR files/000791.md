---
docid: ADR-081
title: ADR 038 Customer Integration Stages
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿---
docid: ADR-038
title: Customer Integration Stages Framework
status: Accepted
date: 2026-01-05
accepted-date: 2026-01-05
decision-makers: "@SARAH, @Architect, @ProductOwner"
consulted: "@Backend, @DevOps, @TechLead"
informed: "All agents"
supersedes: null
related: "ADR-033, ADR-034, ADR-037"
---

# ADR-038: Customer Integration Stages Framework

## Status

**Accepted** - Approved by @Architect, @ProductOwner on 2026-01-05

## Context

B2X is a multi-tenant B2B/B2C e-commerce platform with ERP integration capabilities. As we onboard customers, we need a standardized framework that:

1. **Defines clear integration stages** from evaluation to mature production use
2. **Sets expectations** for timelines, deliverables, and success criteria per stage
3. **Enables tracking** of customer progress through the integration journey
4. **Automates stage transitions** via CLI tooling and health checks
5. **Differentiates service tiers** (self-service vs. assisted onboarding)

### Current Gaps

- No formal definition of customer integration stages
- No standardized onboarding checklist
- ERP connector deployment (ADR-033, ADR-034) lacks integration journey context
- Missing success metrics per stage
- No automation for stage progression tracking

### Relationship to ADR-037

ADR-037 defines **internal development lifecycle stages** (Alpha → Stable → EOL).  
This ADR defines **customer-facing integration stages** (Evaluate → Optimize).

## Decision

We will implement a **4-stage Customer Integration Framework** with defined sub-stages, success criteria, and automation support.

### Customer Integration Journey

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    B2X Customer Integration Journey                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌───────────┐    ┌───────────┐    ┌───────────────────┐   │
│  │ EVALUATE │───▶│  ONBOARD  │───▶│ INTEGRATE │───▶│     OPTIMIZE      │   │
│  │ (Trial)  │    │  (Setup)  │    │  (Deploy) │    │    (Mature)       │   │
│  └──────────┘    └───────────┘    └───────────┘    └───────────────────┘   │
│       │               │                 │                    │              │
│       ▼               ▼                 ▼                    ▼              │
│    Sandbox       Tenant Config      ERP Connector       Advanced Features   │
│    Demo Store    Domain Setup       Catalog Sync        Analytics           │
│    API Keys      User Roles         Order Flow          AI Features         │
│                  Theme/Branding     Payment Gateway     Marketplace         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Stage Definitions

| Stage | Duration | Goal | Exit Criteria |
|-------|----------|------|---------------|
| **Evaluate** | 14-30 days | Validate platform fit | Contract signed OR trial expires |
| **Onboard** | 1-4 weeks | Production tenant ready | Store accessible, branding applied |
| **Integrate** | 2-8 weeks | Full data flow established | First order synced to ERP |
| **Optimize** | Ongoing | Maximize platform value | Continuous improvement |

---

## Stage 1: EVALUATE (Trial/Discovery)

**Duration**: 14-30 days  
**Goal**: Customer validates B2X fits their business needs

### Activities

| Activity | Description | Success Criteria |
|----------|-------------|------------------|
| Sandbox provisioning | Isolated demo tenant | Tenant created < 5 min |
| Demo store access | Pre-populated catalog | Customer can browse products |
| API playground | Interactive API documentation | Customer makes successful API calls |
| Admin console access | Limited admin features | Customer configures basic settings |
| Feature assessment | Capability checklist review | Feature match > 80% |

### Sub-stages

```
1.1 DISCOVERY       → Initial contact, requirements gathering
1.2 SANDBOX         → Trial tenant provisioned
1.3 ASSESSMENT      → Customer evaluates features
1.4 DECISION        → Contract negotiation and signing
```

### Automated Tasks

```bash
# Trial tenant creation
B2X trial create --company "Customer Corp" --plan professional --duration 30

# Outputs:
# - Tenant ID: trial-customer-corp-xxx
# - Admin URL: https://trial-customer-corp.B2X.cloud/admin
# - Store URL: https://trial-customer-corp.B2X.cloud
# - API Key: sk_trial_xxx (expires in 30 days)
```

### Success Metrics

| Metric | Target |
|--------|--------|
| Trial-to-Paid conversion | > 20% |
| Time to first API call | < 1 hour |
| Demo store page views | > 50 |
| Admin console logins | > 10 |

---

## Stage 2: ONBOARD (Setup/Configuration)

**Duration**: 1-4 weeks (complexity-dependent)  
**Goal**: Production tenant fully configured and accessible

### Activities

| Activity | Description | Success Criteria |
|----------|-------------|------------------|
| **Tenant Provisioning** | Production tenant creation | Tenant ID assigned |
| **Domain Configuration** | Custom domain, SSL certificate | DNS verified, HTTPS active |
| **Identity Setup** | SSO, admin users, roles | Admin can authenticate |
| **Branding** | Theme, logo, colors, fonts | Store matches brand guidelines |
| **Localization** | Languages, currencies, formats | All locales configured |
| **Legal Compliance** | Privacy policy, terms, GDPR | Compliance checklist passed |
| **Content Setup** | Initial CMS pages, email templates | Core pages published |

### Sub-stages

```
2.1 PROVISIONING    → Production tenant + infrastructure
2.2 CONFIGURATION   → Settings, preferences, localization
2.3 IDENTITY        → Users, roles, permissions, SSO
2.4 BRANDING        → Theme, visual identity
2.5 CONTENT         → CMS pages, email templates
2.6 LEGAL           → Compliance, privacy, terms
2.7 VERIFICATION    → QA checklist, smoke tests
```

### CLI Support

```bash
# Production tenant creation
B2X tenant create \
  --name "Customer Corp" \
  --plan enterprise \
  --region eu-central

# Domain configuration
B2X tenant configure-domain \
  --tenant customer-corp \
  --domain store.customer.com \
  --ssl auto

# Branding setup
B2X tenant setup-branding \
  --tenant customer-corp \
  --theme professional \
  --primary-color "#1a365d" \
  --logo ./assets/logo.svg

# Readiness verification
B2X tenant verify-readiness --tenant customer-corp
# Outputs checklist with pass/fail status
```

### Onboarding Checklist

```yaml
onboarding:
  provisioning:
    - [ ] Production tenant created
    - [ ] Database provisioned
    - [ ] Storage allocated
    
  configuration:
    - [ ] Timezone configured
    - [ ] Default language set
    - [ ] Currencies configured
    - [ ] Tax settings defined
    
  identity:
    - [ ] Admin users created
    - [ ] Roles assigned
    - [ ] SSO configured (if applicable)
    - [ ] MFA enabled for admins
    
  domain:
    - [ ] Custom domain configured
    - [ ] DNS records verified
    - [ ] SSL certificate active
    - [ ] Redirects configured
    
  branding:
    - [ ] Logo uploaded
    - [ ] Color scheme applied
    - [ ] Fonts configured
    - [ ] Favicon set
    
  content:
    - [ ] Homepage created
    - [ ] About page created
    - [ ] Contact page created
    - [ ] Email templates customized
    
  legal:
    - [ ] Privacy policy published
    - [ ] Terms of service published
    - [ ] Cookie consent configured
    - [ ] GDPR compliance verified
```

### Success Metrics

| Metric | Target |
|--------|--------|
| Time to store live | < 2 weeks |
| Onboarding completion rate | > 95% |
| First admin login | < 24 hours |
| Branding approval | First iteration |

---

## Stage 3: INTEGRATE (Connect/Deploy)

**Duration**: 2-8 weeks (ERP complexity-dependent)  
**Goal**: Full bidirectional data flow between B2X and customer systems

### Activities

| Integration | Description | Success Criteria |
|-------------|-------------|------------------|
| **ERP Connector** | On-premise or cloud connector deployment | Connection test passes |
| **Catalog Sync** | ERP articles → B2X products | Initial sync complete, delta working |
| **Customer Sync** | ERP customers → B2X users | Customer data flows correctly |
| **Order Flow** | B2X orders → ERP | Test order appears in ERP |
| **Pricing Integration** | ERP price lists → B2X | Prices display correctly |
| **Inventory Sync** | ERP stock levels → B2X | Availability shows real-time |
| **Payment Gateway** | Stripe, PayPal, invoice, etc. | Test payment succeeds |

### Integration Tiers

| Tier | Features | Complexity | Timeline | Service Level |
|------|----------|------------|----------|---------------|
| **Basic** | Catalog sync only | Low | 1-2 weeks | Self-service |
| **Standard** | Catalog + Customers + Orders | Medium | 3-4 weeks | Guided |
| **Enterprise** | Full bidirectional + Real-time + Custom | High | 6-8 weeks | Dedicated |

### Sub-stages

```
3.1 CONNECTOR DEPLOY     → Download, install, configure ERP connector
3.2 CONNECTION TEST      → Validate ERP connectivity and authentication
3.3 INITIAL SYNC         → First full catalog import
3.4 DELTA SYNC           → Incremental updates configured and working
3.5 CUSTOMER SYNC        → Customer/contact data flowing
3.6 ORDER FLOW           → Orders transmit to ERP successfully
3.7 PAYMENT SETUP        → Payment gateway integration complete
3.8 GO-LIVE READINESS    → Full E2E test, UAT sign-off
```

### ERP Connector Deployment (per ADR-033, ADR-034)

```bash
# Discover available connectors
B2X erp list-connectors

# Download connector for specific ERP
B2X erp download-connector \
  --erp-type enventa \
  --version latest

# Configure connector
B2X erp configure-connector \
  --erp-type enventa \
  --connection-string "Server=ERP-SERVER;Database=ENVENTA;..." \
  --license-server "LICENSE:1234" \
  --base-path "C:\enventa\base"

# Test connectivity
B2X erp test-connection --erp-type enventa

# Start connector service
B2X erp start-connector --erp-type enventa --background

# Verify sync status
B2X erp sync-status --erp-type enventa
```

### Integration Checklist

```yaml
integration:
  connector:
    - [ ] Connector downloaded
    - [ ] Connector configured
    - [ ] Service installed
    - [ ] Connection test passed
    - [ ] Firewall rules configured
    
  catalog:
    - [ ] Article mapping defined
    - [ ] Initial sync completed
    - [ ] Delta sync scheduled
    - [ ] Categories imported
    - [ ] Images synced
    
  customers:
    - [ ] Customer mapping defined
    - [ ] Initial customer import
    - [ ] Customer groups configured
    - [ ] Pricing tiers mapped
    
  orders:
    - [ ] Order flow configured
    - [ ] Test order created
    - [ ] Order confirmed in ERP
    - [ ] Status updates flowing
    
  payments:
    - [ ] Payment gateway configured
    - [ ] Test payment processed
    - [ ] Refund flow tested
    - [ ] Invoice generation working
    
  go_live:
    - [ ] UAT completed
    - [ ] Performance tested
    - [ ] Monitoring configured
    - [ ] Support handover done
```

### Success Metrics

| Metric | Target |
|--------|--------|
| Time to first order synced | < 4 weeks |
| Catalog sync success rate | > 99% |
| Order sync success rate | > 99.9% |
| Integration completion rate | > 90% |

---

## Stage 4: OPTIMIZE (Mature/Expand)

**Duration**: Ongoing  
**Goal**: Maximize business value from the platform

### Activities

| Activity | Description | Unlock Criteria |
|----------|-------------|-----------------|
| **Analytics** | Sales, traffic, conversion dashboards | 30 days live data |
| **AI Features** | Visual search, recommendations | Catalog > 1000 products |
| **Marketplace** | Multi-channel (Amazon, eBay, Google) | Order flow stable 30+ days |
| **Customer Stores** | B2B customer-specific portals | Customer data synced |
| **Advanced Pricing** | Dynamic rules, promotions, campaigns | Pricing integration complete |
| **Performance Tuning** | CDN, caching, search optimization | Traffic baseline established |
| **Custom Integrations** | Additional ERPs, PIM, CRM | Enterprise tier |

### Sub-stages

```
4.1 STABILIZE      → First 30 days production monitoring
4.2 ENHANCE        → Enable advanced platform features
4.3 SCALE          → Multi-channel, high traffic optimization
4.4 INNOVATE       → AI features, custom integrations
```

### Feature Unlocks

```yaml
feature_unlocks:
  analytics:
    requirement: "30 days live data"
    features:
      - Sales dashboard
      - Traffic analytics
      - Conversion funnel
      - Customer insights
      
  ai_features:
    requirement: "1000+ products, 90 days data"
    features:
      - Visual product search
      - Product recommendations
      - Search relevance tuning
      - Price optimization
      
  marketplace:
    requirement: "Order flow stable 30+ days"
    features:
      - Google Merchant feed
      - Amazon integration
      - eBay connector
      - Facebook Shop
      
  customer_stores:
    requirement: "Customer sync active"
    features:
      - B2B customer portals
      - Custom catalogs per customer
      - Customer-specific pricing
      - Approval workflows
```

### Success Metrics

| Metric | Target |
|--------|--------|
| 90-day retention | > 95% |
| Feature adoption rate | > 60% |
| NPS score | > 50 |
| Support ticket volume | Decreasing trend |

---

## Service Tiers

### Self-Service (SMB)

| Aspect | Description |
|--------|-------------|
| Target | Small-medium businesses |
| Onboarding | Self-guided with documentation |
| Integration | Basic tier (catalog sync) |
| Support | Email, knowledge base |
| SLA | Business hours |

### Guided (Professional)

| Aspect | Description |
|--------|-------------|
| Target | Mid-market businesses |
| Onboarding | Kickoff call + guided setup |
| Integration | Standard tier |
| Support | Email + chat, dedicated CSM |
| SLA | 8-hour response |

### Dedicated (Enterprise)

| Aspect | Description |
|--------|-------------|
| Target | Enterprise customers |
| Onboarding | Dedicated implementation team |
| Integration | Enterprise tier + custom |
| Support | Phone + dedicated engineer |
| SLA | 1-hour response, 99.9% uptime |

---

## Automation & Tooling

### Stage Tracking

```yaml
# .ai/templates/customer-integration-tracker.yml
customer:
  name: "Customer Corp"
  tenant_id: "customer-corp"
  tier: enterprise
  start_date: "2026-01-15"
  target_go_live: "2026-03-01"

stages:
  evaluate:
    status: complete
    started: "2025-12-01"
    completed: "2025-12-20"
    
  onboard:
    status: complete
    started: "2026-01-02"
    completed: "2026-01-14"
    
  integrate:
    status: in_progress
    started: "2026-01-15"
    current_substage: "3.5 CUSTOMER SYNC"
    blockers: []
    
  optimize:
    status: pending
```

### Health Check Commands

```bash
# Check overall integration status
B2X integration status --tenant customer-corp

# Detailed stage report
B2X integration report --tenant customer-corp --format detailed

# Automated readiness checks
B2X integration check-readiness \
  --tenant customer-corp \
  --stage integrate
```

### Notifications & Alerts

- Stage completion notifications (email, webhook)
- Blocker alerts to customer success team
- Automated follow-up reminders
- SLA breach warnings

---

## Implementation Plan

### Phase 1: Documentation (Week 1)
- [x] Create ADR-038 (this document)
- [ ] Update DOCUMENT_REGISTRY.md
- [ ] Create customer-facing integration guide

### Phase 2: Checklists & Templates (Week 2)
- [ ] Create `.ai/templates/customer-integration-tracker.yml`
- [ ] Create onboarding checklist template
- [ ] Create integration checklist template
- [ ] Define stage transition criteria

### Phase 3: CLI Commands (Week 3-4)
- [ ] Implement `B2X trial create`
- [ ] Implement `B2X tenant verify-readiness`
- [ ] Implement `B2X integration status`
- [ ] Implement `B2X integration report`

### Phase 4: Dashboard & Tracking (Week 5-6)
- [ ] Customer integration progress dashboard (Admin)
- [ ] Stage progression automation
- [ ] Notification system for stage transitions
- [ ] Success metrics tracking

---

## Consequences

### Positive

1. **Clear Expectations**: Customers understand the journey and timelines
2. **Predictable Delivery**: Standardized stages enable accurate planning
3. **Quality Assurance**: Checklists ensure nothing is missed
4. **Scalable Onboarding**: Self-service tier reduces support burden
5. **Measurable Success**: Metrics per stage enable continuous improvement

### Negative

1. **Rigidity**: Some customers may not fit standard stages
2. **Overhead**: Tracking and checklists require maintenance
3. **Complexity**: Multiple tiers require different processes

### Risks

| Risk | Mitigation |
|------|------------|
| Stage skipping | Enforce prerequisites via tooling |
| Stalled integrations | Automated alerts, CSM follow-up |
| Tier mismatch | Pre-sales assessment, tier upgrades |
| Timeline overruns | Buffer time, escalation paths |

---

## Alternatives Considered

### A. No Formal Stages
- **Pros**: Flexibility, less overhead
- **Cons**: Inconsistent experience, unpredictable timelines
- **Decision**: Rejected — standardization needed for scale

### B. More Granular Stages (6+)
- **Pros**: Fine-grained tracking
- **Cons**: Complexity, overhead
- **Decision**: Rejected — 4 stages with sub-stages provides balance

### C. Single Process for All Tiers
- **Pros**: Simpler to manage
- **Cons**: Over-serves SMB, under-serves enterprise
- **Decision**: Rejected — tiered approach matches customer needs

---

## References

- [ADR-033] Tenant-Admin Download for ERP-Connector
- [ADR-034] Multi-ERP Connector Architecture
- [ADR-037] Lifecycle Stages Framework (internal)
- [PRODUCT_VISION.md] Product Vision and Roadmap

---

**Proposed by**: @SARAH  
**Awaiting approval from**: @Architect, @ProductOwner  
**Date**: 2026-01-05
