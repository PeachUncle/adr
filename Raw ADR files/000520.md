# ADR 002: Multi-Tenant SaaS with Hybrid Cloud/Edge Architecture

**📍 Navigation Path:** [AGOG Home](../../README.md) → [Project Spirit](../README.md) → [ADR](./README.md) → Multi-Tenant SaaS with Edge Computing

## Status
**Accepted** - 2025-11-03

## Context

### The Print Industry Reality

Print companies are stuck between two worlds:
- **Legacy expectations:** "We paid $50k for our ERP in 2005, it still works"
- **Modern demands:** Real-time dashboards, AI capabilities, cloud access
- **IT reality:** 90% infrastructure staff, minimal application expertise
- **Budget disconnect:** Want Netflix-quality infrastructure at legacy prices
- **Decision makers:** CFO/COO/CTO want OUT of the infrastructure business

### Customer Profile
```
Typical Enterprise Print Customer:
├─ Revenue: $20M-100M/year
├─ Employees: 200-500
├─ IT Staff: Infrastructure-focused (servers, network)
├─ ERP Team: Part of Operations, not IT
├─ CIO: Doesn't exist or very weak
├─ Mindset: "Just make it work, like turning on lights"
├─ Expectation: Chrome browser = entire system
├─ Budget: $50k-100k/year total (not $500k implementations)
└─ Pain Point: "Our IT costs too much"
```

### Key Requirements (Discovered Through Discussion)

1. **"Get us out of infrastructure business"**
   - Customer wants zero infrastructure management
   - Cloud-first, SaaS model
   - No servers to buy, no Kafka to manage
   - CFO calculates: 3 IT staff ($300k/year) → SaaS ($50k/year)

2. **"Chrome browser only"**
   - No desktop applications to install
   - No mobile apps to maintain
   - Works on any device with Chrome
   - Like Salesforce, but for print

3. **"BI dashboards day one"**
   - Power BI / Tableau experience expected
   - Real-time production visibility
   - Executive dashboards for CFO/COO
   - Not optional, must be included

4. **"AI options day one (but we won't use them yet)"**
   - Checkbox feature for sales
   - "We have AI capabilities!"
   - Customer too hesitant to activate
   - 90% will leave it off (that's fine)

5. **"One-time contractor service for IoT"**
   - "Contractor runs wire, equipment monitoring works"
   - Customer doesn't know Docker agents needed
   - Customer doesn't know edge computing involved
   - Appears magical, actually sophisticated

### The Hidden Challenge: Physical Equipment

Print production requires on-premises connectivity:
- **Printers:** HP Indigo, Heidelberg, Xerox, etc. (can't move to cloud)
- **IoT sensors:** Vibration monitoring, temperature, press counters
- **Equipment protocols:** JDF/JMF, OPC-UA, Modbus, SNMP
- **Real-time data:** Production status, quality metrics, maintenance alerts

**Problem:** Can't be 100% cloud (equipment is physical!)

**Solution:** Hybrid architecture with invisible edge computing

## Decision

We will build AGOG as a **Multi-Tenant SaaS platform with Hybrid Cloud/Edge Architecture**:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              CLOUD (Our Infrastructure)                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Customer Access: Chrome Browser (PWA)                  │
│  ┌────────────────────────────────────────────────┐     │
│  │  Modern Web UI (React/Vue)                     │     │
│  │  ├─ Dashboard (Embedded BI)                    │     │
│  │  ├─ Job Management                             │     │
│  │  ├─ Inventory Control                          │     │
│  │  ├─ Production Scheduling                      │     │
│  │  ├─ Real-time Equipment Status                 │     │
│  │  └─ AI Recommendations (optional checkboxes)   │     │
│  └────────────────────────────────────────────────┘     │
│                        ↓                                │
│  ┌────────────────────────────────────────────────┐     │
│  │  GraphQL Federation Gateway                    │     │
│  │  (Single API endpoint for all services)        │     │
│  └────────────────────────────────────────────────┘     │
│                        ↓                                │
│  ┌────────────────────────────────────────────────┐     │
│  │  Multi-Tenant Core Services                    │     │
│  │  ├─ Sales API (PostgreSQL)                     │     │ 
│  │  ├─ WMS API (PostgreSQL)                       │     │
│  │  ├─ Estimating API (PostgreSQL)                │     │
│  │  ├─ Production API (PostgreSQL)                │     │
│  │  └─ Kafka Event Bus (real-time events)         │     │
│  └────────────────────────────────────────────────┘     │
│                        ↓                                │
│  ┌────────────────────────────────────────────────┐     │
│  │  Platform Services                             │     │  
│  │  ├─ Embedded BI (Metabase/Superset)            │     │
│  │  ├─ AI Engine (TensorFlow/PyTorch)             │     │
│  │  ├─ File Storage (S3/Blob)                     │     │
│  │  └─ Background Jobs (Bull/Celery)              │     │
│  └────────────────────────────────────────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
                    ↕ (Secure tunnel/VPN)
┌─────────────────────────────────────────────────────────┐
│         ON-PREMISES (Customer's Shop Floor)             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌────────────────────────────────────────────────┐     │
│  │  Edge Agent (Lightweight Docker Container)     │     │
│  │  ├─ Auto-discovery (printers, sensors)         │     │
│  │  ├─ Protocol adapters (JDF/JMF, OPC-UA, etc.)  │     │
│  │  ├─ Offline buffering (works without internet) │     │
│  │  ├─ Secure cloud tunnel (WireGuard/Tailscale)  │     │
│  │  └─ Auto-update (invisible to customer)        │     │
│  └────────────────────────────────────────────────┘     │
│            │                          │                 │
│            ↓                          ↓                 │
│  ┌──────────────────┐      ┌────────────────────┐       │
│  │  Print Equipment │      │  IoT Sensors       │       │
│  │  - HP Indigo     │      │  - Vibration       │       │
│  │  - Heidelberg    │      │  - Temperature     │       │
│  │  - Xerox iGen    │      │  - Press counters  │       │
│  └──────────────────┘      └────────────────────┘       │
│                                                         │
│  Installation: "One-time contractor visit"              │
│  Reality: Edge agent + cloud seamlessly integrated      │
└─────────────────────────────────────────────────────────┘
```

### Core Architectural Decisions

**1. Multi-Tenant SaaS (Not Self-Hosted)**
- All customers share our infrastructure
- We manage Kafka, PostgreSQL, Kubernetes
- Customer pays monthly SaaS fee
- Zero infrastructure burden on customer

**2. PostgreSQL Multi-Tenancy**
- Row-Level Security (RLS) for data isolation
- Separate schemas per tenant for sovereignty
- Shared infrastructure, isolated data
- Scales to hundreds of tenants

**3. Apache Kafka Event Bus**
- Real-time event streaming
- Our managed infrastructure
- Brand recognition (hiring + sales)
- Enables real-time dashboards, WebSocket updates

**4. GraphQL Federation**
- Single API endpoint for all services
- Real-time subscriptions via WebSocket
- Type-safe, modern, hire-able
- Better than REST for complex queries

**5. Chrome-Only PWA**
- Progressive Web App
- No installation required
- Offline-capable (service workers)
- Works on desktop, tablet, mobile
- Native app feel, zero deployment hassle

**6. Embedded BI (Day 1)**
- Metabase or Superset embedded
- Looks like Power BI / Tableau
- No separate tools to buy
- CFO/COO dashboards included

**7. AI Features (Checkboxes, Mostly Dormant)**
- Settings → AI Features → All unchecked by default
- Smart Pricing, Production Optimization, Forecasting
- Sales feature: "We have AI!"
- Reality: 90% of customers never activate

**8. Edge Computing (Hidden from Customer)**
- Docker containers on customer premises
- Auto-discovery of equipment
- Secure tunnel to cloud
- Offline buffering
- Auto-updates

### Technology Stack

**Cloud Infrastructure (Our Managed):**
- **Kubernetes:** GKE/EKS/AKS for container orchestration
- **PostgreSQL:** Multi-tenant with RLS
- **Apache Kafka:** Event streaming
- **API Layer:** 
  - **GraphQL (Apollo Federation):** PWA frontend queries
  - **REST APIs:** External integrations (shipping, payments, equipment)
  - **gRPC:** Internal microservice communication
- **BI:** Metabase/Superset embedded
- **AI/ML:** TensorFlow/PyTorch (optional models)
- **Storage:** S3/Azure Blob for files
- **CDN:** CloudFront/Azure CDN for assets

**Frontend:**
- **Framework:** React or Vue.js
- **PWA:** Service workers, offline support
- **GraphQL Client:** Apollo Client (for PWA → GraphQL API)
- **UI Library:** Material-UI or Ant Design
- **Charts:** Recharts, D3.js for BI

**Edge Computing:**
- **Platform:** Docker on Linux (Raspberry Pi / mini PC)
- **Language:** Node.js or Python for agents
- **Protocols:** JDF/JMF, OPC-UA, Modbus, SNMP
- **Tunnel:** WireGuard or Tailscale
- **Discovery:** mDNS, SSDP for equipment

## Rationale

### Why Multi-Tenant SaaS?

**Customer wants OUT of infrastructure:**
- CFO calculates: IT staff ($300k/year) → SaaS ($50k/year) = massive savings
- COO wants: "It just works, like electricity"
- CTO wants: Modern cloud, zero maintenance

**Business model sustainability:**
- Monthly recurring revenue (MRR)
- Predictable costs, predictable revenue
- Scales to hundreds of customers
- Lower customer acquisition cost

**Operational efficiency:**
- One infrastructure serves all customers
- Centralized monitoring, updates, security
- Economies of scale
- Easier hiring (you run Kafka, not customer)

### Why Kafka (Not RabbitMQ)?

**Brand recognition for hiring:**
- Developers WANT Kafka on resume
- "We use Kafka" attracts talent
- More job postings mention Kafka

**Brand recognition for sales:**
- Enterprise CTOs recognize Kafka
- "Built on Apache Kafka" = credibility
- Same tech as Netflix, LinkedIn, Uber

**Future-proofing:**
- Stream processing ready (Kafka Streams)
- Analytics pipelines (when needed)
- Event sourcing patterns

**Reality:** For most customers, even RabbitMQ would work. But perception matters.

### Why Edge Computing?

**Physical equipment can't move to cloud:**
- Printers are on shop floor
- IoT sensors are embedded
- Can't change equipment location

**Customer perception:**
- Thinks it's "all cloud"
- Doesn't know about edge agents
- "Contractor visit + it works = magic"

**Technical benefits:**
- Offline capability (buffering)
- Low latency (local processing)
- Secure (no equipment exposed to internet)
- Flexible protocols (JDF, OPC-UA, Modbus)

### Why Chrome-Only PWA?

**Zero IT burden:**
- No desktop app to install/update
- No mobile app store submissions
- Works everywhere Chrome works

**Lower development cost:**
- One codebase for all platforms
- Web technologies (React/Vue)
- Easier to hire for

**User expectation met:**
- "Like Salesforce" experience
- Modern, responsive UI
- Offline capable

### Why Hybrid API Strategy (GraphQL + REST)?

**GraphQL for PWA Frontend:**
- **Single endpoint:** Simplifies PWA development
- **Client-defined queries:** Fetch exactly what the UI needs
- **Real-time subscriptions:** Live updates for dashboards
- **Apollo Federation:** Compose services into unified graph
- **Developer experience:** Modern tooling, type safety

**REST for External Integrations:**
- **Industry standard:** Partners expect REST APIs
- **Simple authentication:** JWT tokens well-understood
- **Webhook support:** Event-driven integrations
- **Backward compatibility:** Version management easier
- **Documentation:** OpenAPI/Swagger familiar to integrators

**When to use which:**
```
GraphQL (Apollo Federation):
├─ PWA frontend ← ✅ Use GraphQL
├─ Internal dashboards ← ✅ Use GraphQL
├─ BI tool queries ← ✅ Use GraphQL
└─ Complex data aggregation ← ✅ Use GraphQL

REST APIs:
├─ Shipping carriers (FedEx, UPS) ← ✅ Use REST
├─ Payment processors (Stripe, PayPal) ← ✅ Use REST
├─ E-commerce platforms (Shopify) ← ✅ Use REST
├─ Equipment integrations (JDF/JMF) ← ✅ Use REST
├─ Partner/Reseller APIs ← ✅ Use REST
└─ Third-party developers ← ✅ Use REST

gRPC (Internal Only):
├─ Microservice-to-microservice ← ✅ Use gRPC
├─ High-performance internal calls ← ✅ Use gRPC
└─ NOT exposed externally ← ❌ Internal only
```

**Industry validation:**
- **Shopify:** GraphQL for Storefront API, REST for Admin API
- **GitHub:** GraphQL for v4 API, REST for v3 API (still maintained)
- **GitLab:** Both GraphQL and REST available
- **Pattern:** GraphQL for modern frontends, REST for integrations

### Why BI Day 1?

**CFO/COO requirement:**
- Not negotiable
- Must see value immediately
- Dashboards = perceived value

**Competitive necessity:**
- Competitors have BI
- Can't sell without it
- Must be included, not add-on

**Technical ease:**
- Metabase/Superset embeds easily
- Data already in PostgreSQL
- Low incremental cost

### Why AI Checkboxes?

**Sales advantage:**
- "We have AI capabilities!"
- Checkbox in competitor comparison
- Future-proofing story

**Customer reality:**
- Too hesitant to use it now
- Will activate in 1-2 years
- That's fine, it's there when ready

**Low cost:**
- Models dormant = no compute cost
- Build framework, activate on-demand
- 10% adoption = enough ROI

## Implementation Strategy

### Phase 1: MVP (6 months)
- Multi-tenant SaaS core (Sales, Estimating, Production)
- PostgreSQL with RLS
- GraphQL Federation
- Chrome PWA
- Basic BI dashboards (embedded Metabase)
- Manual equipment data entry (no edge yet)

### Phase 2: Edge Computing (3 months)
- Edge agent development
- Docker-based deployment
- Auto-discovery for common equipment
- Secure tunnel to cloud
- Contractor installation process

### Phase 3: AI Framework (3 months)
- AI engine infrastructure
- First model: Smart pricing recommendations
- Checkbox activation in UI
- Dormant by default

### Phase 4: Scale & Polish (Ongoing)
- Additional AI models
- Advanced BI features
- More equipment integrations
- Performance optimization

### Multi-Tenancy Implementation

**Database Isolation:**
```sql
-- Create schema per tenant
CREATE SCHEMA tenant_acme;
CREATE SCHEMA tenant_fedex;

-- Row-Level Security for paranoid customers
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

**API Tenant Context:**
```javascript
// Every request scoped by tenant
app.use((req, res, next) => {
  req.tenant = extractTenantFromToken(req.headers.authorization);
  next();
});

// All queries automatically scoped
const orders = await Order.findAll({
  where: { tenant_id: req.tenant.id }
});
```

### Edge Agent Installation

**Customer Experience:**
```
Sales: "We'll send a certified contractor for IoT setup"
Contractor visit:
1. Plug in mini PC / Raspberry Pi
2. Run installation command
3. Wire sensors to equipment
4. Test in dashboard
5. Done

Customer sees: $5k one-time + $200/month monitoring
```

**Technical Reality:**
```bash
# Contractor runs on customer's device
curl -fsSL https://install.agog.io/edge | bash \
  --token CUSTOMER_TOKEN \
  --location "Shop Floor A"

# Auto-discovers:
# - Heidelberg press (OPC-UA)
# - HP Indigo (JDF/JMF)
# - Vibration sensors (Modbus)

# Streams to cloud securely
# Customer dashboard updates in real-time
```

## Business Model

### Pricing Structure

**Monthly SaaS:**
- Small (< 50 employees): $500-1,000/month
- Medium (50-200 employees): $1,500-3,000/month
- Large (200+ employees): $3,000-5,000/month
- Enterprise (500+ employees): Custom pricing

**Includes:**
- Unlimited users
- All features (Sales, WMS, Production, Estimating)
- BI dashboards
- AI capabilities (checkbox)
- Cloud hosting
- Security & backups
- Support (email, chat)

**One-Time Setup:**
- Onboarding: $2,000-5,000
- Data migration: $3,000-10,000
- Training: $1,000-3,000
- Total: $5,000-20,000

**Optional Add-Ons:**
- Edge agent license: $100/location/month
- Equipment monitoring: $50/device/month
- Premium support: $500/month (phone, 24/7)
- Custom integrations: Project-based

### Value Proposition

**For CFO:**
> "Replace 3 IT staff ($300,000/year) with our SaaS ($50,000/year). Save $250,000/year."

**For COO:**
> "Real-time production visibility. Chrome browser. Works anywhere. No IT headaches."

**For CTO:**
> "Modern stack (Kafka, GraphQL, PostgreSQL). Cloud-native. Scales globally. BI and AI included."

## Consequences

### Positive

✅ **Customer gets what they want:**
- Out of infrastructure business
- Chrome-only simplicity
- BI day-1
- AI options (even if dormant)
- Equipment monitoring "just works"

✅ **Business sustainability:**
- Monthly recurring revenue
- Predictable costs
- Scalable infrastructure
- Lower customer acquisition cost

✅ **Competitive advantages:**
- Modern technology stack
- Brand-name technologies (Kafka)
- Easier hiring (attractive tech)
- Faster time-to-value

✅ **Technical excellence:**
- Clean architecture
- Multi-tenant from day 1
- Edge computing solves physical constraints
- Future-proof (AI, stream processing ready)

### Negative

❌ **Operational complexity:**
- We run all infrastructure (not customer)
- 24/7 monitoring required
- SLA commitments (99.9% uptime)
- Support burden higher

❌ **Initial investment:**
- Build multi-tenant from scratch
- Edge agent development
- BI integration
- AI framework

❌ **Customer lock-in concerns:**
- Some customers fear SaaS dependency
- Data sovereignty questions
- Mitigation: Data export APIs, transparent pricing

❌ **Edge agent distribution:**
- Must support Windows/Linux/macOS edge environments
- Hardware compatibility matrix
- Contractor certification program

### Mitigation Strategies

**For operational complexity:**
- Invest in monitoring (Prometheus, Grafana)
- Automated alerting and remediation
- Runbooks for common issues
- Hire SRE team when scale demands

**For customer concerns:**
- Transparent data export (daily backups available)
- Flexible contracts (monthly, annual)
- SOC2/ISO27001 compliance
- On-premises option (future, premium tier)

**For edge agent:**
- Docker standardization
- Auto-update mechanism
- Remote troubleshooting tools
- Certified contractor network

## Monitoring & Success Metrics

**Technical Metrics:**
- System uptime: 99.9% target
- API response time: p95 < 200ms
- Edge agent connectivity: 99% uptime
- Data sync latency: < 5 seconds

**Business Metrics:**
- Customer acquisition cost (CAC)
- Monthly recurring revenue (MRR)
- Customer lifetime value (LTV)
- Churn rate: < 5% annually
- Net Promoter Score (NPS): > 50

**Adoption Metrics:**
- BI dashboard usage: 80% of users weekly
- AI feature activation: Track % enabled (expect 10%)
- Edge agent installations: Track per customer
- Mobile/tablet usage: Track Chrome access patterns

## References

- [ADR 001: API-First Design](./api-first-design.md)
- [SYSTEM_OVERVIEW.md](../../Project%20Architecture/SYSTEM_OVERVIEW.md) (to be created)
- [BUSINESS_VALUE.md](../BUSINESS_VALUE.md) (to be created)
- [SESSION_CONTEXT.md](../../.github/SESSION_CONTEXT.md) - Architecture discovery session

## Related Decisions

- ADR 003: Security & Multi-Tenant Data Isolation (TBD)
- ADR 004: Edge Computing Protocol Standards (TBD)
- ADR 005: BI/Analytics Integration Strategy (TBD)
- ADR 006: AI/ML Model Framework (TBD)

---

**Decision Made:** 2025-11-03  
**Decision Makers:** Todd (Product), AI Assistant (Technical Advisor)  
**Review Date:** 2026-Q1 (re-evaluate after MVP launch)

[← Back to ADR Index](./README.md)
