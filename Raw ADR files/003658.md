# ADR-001: Stripe to Sovereign Infrastructure Transition

**Status:** Proposed  
**Date:** December 12, 2024  
**Authors:** Nathan (SOLVY Founder), Manus AI  
**Reviewers:** TBD

---

## Context

The SOLVY platform is being built as **America's first P2P payment platform** with a mission to provide economic sovereignty to veterans, freelancers, and small businesses through a **member-owned cooperative** structure. The platform combines payment processing, self-sovereign identity (SOVEREIGNITITY™), and cooperative economics to break systemic barriers to wealth building.

### Current State (Phase 1: MVP)

The initial MVP leverages third-party services to achieve rapid time-to-market and minimize upfront capital requirements:

| Service Category | Provider | Cost Structure | Limitations |
|-----------------|----------|----------------|-------------|
| **Payment Processing** | Stripe | 2.9% + $0.30 per transaction | High fees, data not owned |
| **Banking** | Mercury | $0/month (startup tier) | Limited control, US-only |
| **KYC** | Persona | $1-2 per verification | Per-verification cost |
| **Authentication** | Clerk | Free up to 10K users | Vendor lock-in |
| **Email** | Resend | Free up to 3K emails/month | Limited customization |
| **Admin Dashboard** | Tooljet (self-hosted) | Free | Requires maintenance |
| **Hosting** | Hetzner VPS | $10/month | Single point of failure |

**Total Monthly Cost (at 100 members):** ~$50-100/month  
**Revenue (at 100 members):** ~$1,500/month (1.5% interchange on $100K volume)  
**Break-even:** First month (KYC costs recovered from interchange fees)

### Strategic Problem

While the MVP approach enables rapid launch and validation, it creates **fundamental conflicts** with SOLVY's core mission:

1. **Economic Sovereignty Paradox**: We advocate for economic independence while depending on Stripe (owned by institutional investors) and Mercury (venture-backed fintech).

2. **Data Sovereignty Conflict**: SOVEREIGNITITY™ promises self-sovereign identity, but member data flows through multiple third-party systems (Stripe, Clerk, Persona).

3. **Revenue Leakage**: Stripe captures 2.9% + $0.30 per transaction, while SOLVY only earns 1.5-2.5% interchange. At scale (10K members, $10M annual volume), this represents **$290K/year in unnecessary fees**.

4. **Cooperative Control**: Members cannot truly "own" the platform if critical infrastructure is controlled by external corporations with misaligned incentives.

5. **Regulatory Risk**: Third-party dependencies expose SOLVY to platform risk (account termination, policy changes, price increases).

---

## Decision

We will **transition from third-party infrastructure (Stripe/Mercury) to fully sovereign infrastructure** in a phased approach, triggered by specific member count and revenue milestones.

### Transition Timeline

| Phase | Trigger | Infrastructure | Timeline |
|-------|---------|----------------|----------|
| **Phase 1: MVP** | 0-1K members | Stripe + Mercury | Months 0-12 |
| **Phase 2: Hybrid** | 1K-5K members | Stripe + Own banking charter | Months 12-24 |
| **Phase 3: Sovereign** | 5K+ members | Direct card network + Own bank | Months 24-36 |

### Phase 1: MVP (Current)

**Objective:** Validate product-market fit with minimal capital.

**Infrastructure:**
- Stripe for payment processing
- Mercury for banking
- Persona for KYC
- Clerk for authentication
- Resend for email
- Tooljet (self-hosted) for admin

**Success Criteria:**
- 1,000 active members
- $1M annual transaction volume
- $180K annual revenue
- Positive unit economics ($15/member/month revenue vs. $2/member/month costs)

### Phase 2: Hybrid Infrastructure

**Objective:** Reduce dependency on Stripe while maintaining stability.

**Infrastructure Changes:**
- **Banking:** Apply for own banking charter or partner with community bank
- **Payment Processing:** Continue using Stripe (reduces risk during banking transition)
- **Data Storage:** Migrate to self-hosted infrastructure
- **Authentication:** Migrate from Clerk to self-hosted solution

**Capital Requirements:** $500K-1M (banking charter, legal, compliance)

**Revenue at Trigger Point (1K members):** $180K/year (sufficient to support transition costs)

**Success Criteria:**
- Banking charter approved
- 5,000 active members
- $10M annual transaction volume
- $1.8M annual revenue

### Phase 3: Full Sovereignty

**Objective:** Achieve complete independence from third-party payment processors.

**Infrastructure Changes:**
- **Payment Processing:** Direct integration with Visa/Mastercard networks
- **Banking:** Own banking charter or deep partnership with community bank
- **Card Issuance:** Direct card issuance (not through Stripe)
- **Data:** 100% self-hosted, member-owned infrastructure
- **Governance:** Full cooperative control with member voting

**Capital Requirements:** $2-5M (card network integration, compliance, infrastructure)

**Revenue at Trigger Point (5K members):** $900K/year (sufficient to fund transition)

**Cost Savings:** $290K/year (eliminating Stripe fees at $10M volume)

---

## Rationale

### Why Start with Stripe?

Despite philosophical conflicts, starting with Stripe is pragmatic:

1. **Time to Market**: Stripe integration takes weeks, not years. Direct card network integration requires 12-24 months.

2. **Capital Efficiency**: Stripe requires no upfront capital. Banking charter requires $500K-1M.

3. **Regulatory Complexity**: Stripe handles PCI compliance, AML/KYC, and regulatory reporting. Building this in-house requires significant legal/compliance expertise.

4. **Risk Management**: Validating product-market fit before committing millions to infrastructure reduces existential risk.

5. **Member Trust**: Stripe's brand provides credibility during early adoption phase.

### Why Transition to Sovereignty?

The transition becomes both **economically viable** and **mission-critical** at scale:

1. **Economic Case**: At 5K members ($10M volume), eliminating Stripe saves $290K/year—enough to fund sovereign infrastructure development.

2. **Cooperative Alignment**: True member ownership requires infrastructure ownership. Renting from Stripe contradicts cooperative principles.

3. **Data Sovereignty**: SOVEREIGNITITY™ requires complete control over member data. Third-party processors create data sovereignty violations.

4. **Competitive Moat**: Direct card network integration creates barriers to entry that protect the cooperative from venture-backed competitors.

5. **Mission Integrity**: Economic sovereignty cannot be achieved while dependent on venture-backed intermediaries.

---

## Implementation Strategy

### Phase 1 → Phase 2 Transition (1K members)

**Preparation (Months 9-12):**
1. Engage banking charter consultants
2. Begin regulatory compliance documentation
3. Hire banking/compliance expertise
4. Establish legal entity structure for banking operations

**Execution (Months 12-18):**
1. Submit banking charter application (or negotiate community bank partnership)
2. Build banking infrastructure (accounts, ledger, compliance)
3. Migrate member accounts from Mercury to own bank
4. Maintain Stripe for payment processing (reduces risk)

**Rollback Plan:**
- If banking charter denied, continue with Mercury + Stripe
- Evaluate alternative paths (partnership with existing community bank)

### Phase 2 → Phase 3 Transition (5K members)

**Preparation (Months 18-24):**
1. Engage card network integration consultants
2. Build direct card processing infrastructure
3. Obtain PCI DSS Level 1 certification
4. Negotiate direct relationships with Visa/Mastercard

**Execution (Months 24-36):**
1. Launch parallel card processing system (Stripe + Sovereign)
2. Migrate 10% of members to sovereign system (beta test)
3. Monitor transaction success rates, member satisfaction
4. Gradually migrate remaining members
5. Sunset Stripe integration

**Rollback Plan:**
- Maintain Stripe integration for 6 months post-cutover
- If sovereign system fails, revert members to Stripe
- Establish clear success metrics before full cutover

---

## Technical Architecture

### Phase 1: MVP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SOLVY Frontend                       │
│                  (React + TypeScript)                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Abstracted API Layer                     │
│  (/src/api/stripe, /src/api/mercury, /src/api/persona)    │
└─┬───────────────┬───────────────┬───────────────┬───────────┘
  │               │               │               │
  ▼               ▼               ▼               ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│ Stripe  │  │ Mercury │  │ Persona │  │  Clerk  │
│   API   │  │   API   │  │   API   │  │   API   │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
```

**Key Design Decision:** The abstracted API layer (`/src/api/`) isolates third-party dependencies. When transitioning to sovereign infrastructure, we only need to swap the implementation behind these abstractions—**frontend components remain unchanged**.

### Phase 3: Sovereign Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SOLVY Frontend                       │
│                  (React + TypeScript)                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Abstracted API Layer                     │
│    (/src/api/sovereign-payment, /src/api/sovereign-bank)   │
└─┬───────────────┬───────────────┬───────────────┬───────────┘
  │               │               │               │
  ▼               ▼               ▼               ▼
┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐
│  Visa/  │  │  SOLVY  │  │  SOLVY  │  │  SOLVY  │
│  MC     │  │  Bank   │  │   KYC   │  │  Auth   │
│ Direct  │  │ (owned) │  │ (owned) │  │ (owned) │
└─────────┘  └─────────┘  └─────────┘  └─────────┘
```

**Infrastructure Ownership:**
- Payment processing: Direct card network integration (no intermediaries)
- Banking: Own charter or deep community bank partnership
- KYC: Self-hosted identity verification
- Authentication: Self-hosted auth system
- Data: 100% member-owned, cooperative-controlled

---

## Risks and Mitigations

### Risk 1: Banking Charter Denial

**Probability:** Medium (30-40%)  
**Impact:** High (blocks Phase 2 transition)

**Mitigation:**
- Pursue community bank partnership as parallel path
- Engage experienced banking charter consultants early
- Build strong regulatory compliance from Day 1
- Demonstrate cooperative structure aligns with community banking mission

### Risk 2: Card Network Integration Complexity

**Probability:** Medium (40-50%)  
**Impact:** High (delays Phase 3 transition)

**Mitigation:**
- Engage card network integration consultants 12 months before cutover
- Budget $2-3M for integration (legal, technical, compliance)
- Establish direct relationships with Visa/Mastercard early
- Hire experienced payments engineers with card network experience

### Risk 3: Member Disruption During Cutover

**Probability:** High (60-70%)  
**Impact:** Medium (temporary member dissatisfaction)

**Mitigation:**
- Phased rollout (10% → 50% → 100%)
- Maintain Stripe as fallback for 6 months post-cutover
- Clear member communication (48 hours notice minimum)
- 24/7 support during cutover period
- Financial incentives for early adopters (beta testers)

### Risk 4: Regulatory Compliance Burden

**Probability:** High (70-80%)  
**Impact:** High (ongoing operational cost)

**Mitigation:**
- Hire compliance expertise early (Phase 1)
- Budget 10-15% of revenue for compliance costs
- Automate compliance reporting where possible
- Establish relationships with regulators early
- Join industry associations (community banking, fintech)

### Risk 5: Capital Requirements Exceed Projections

**Probability:** Medium (40-50%)  
**Impact:** High (delays transition)

**Mitigation:**
- Conservative financial projections (assume 50% higher costs)
- Establish credit facility or line of credit at Phase 2
- Consider member capital raise (cooperative investment)
- Explore grants for community banking / economic justice initiatives

---

## Success Metrics

### Phase 1 Success Metrics (0-12 months)

- **Member Growth:** 1,000 active members
- **Transaction Volume:** $1M annual volume
- **Revenue:** $180K annual revenue
- **Unit Economics:** $15/member/month revenue, $2/member/month costs
- **Member Satisfaction:** 80%+ NPS score
- **Technical Stability:** 99.9% uptime

### Phase 2 Success Metrics (12-24 months)

- **Banking Charter:** Approved (or community bank partnership signed)
- **Member Growth:** 5,000 active members
- **Transaction Volume:** $10M annual volume
- **Revenue:** $1.8M annual revenue
- **Cost Reduction:** 50% reduction in third-party fees
- **Data Sovereignty:** 80% of member data self-hosted

### Phase 3 Success Metrics (24-36 months)

- **Card Network Integration:** Direct Visa/Mastercard integration live
- **Member Growth:** 10,000 active members
- **Transaction Volume:** $50M annual volume
- **Revenue:** $9M annual revenue
- **Cost Savings:** $290K/year saved (Stripe fees eliminated)
- **Infrastructure Ownership:** 100% self-hosted, member-owned
- **Cooperative Governance:** Member voting system operational

---

## Alternatives Considered

### Alternative 1: Stay with Stripe Permanently

**Pros:**
- No capital investment required
- Lower operational complexity
- Proven reliability

**Cons:**
- Contradicts mission (economic sovereignty)
- High ongoing costs ($290K/year at scale)
- No competitive moat
- Data sovereignty violations
- Vulnerable to platform risk

**Decision:** Rejected. Mission alignment requires sovereignty.

### Alternative 2: Build Sovereign Infrastructure from Day 1

**Pros:**
- Mission-aligned from start
- No technical debt from third-party integrations
- Complete control

**Cons:**
- $5-10M upfront capital required
- 24-36 months to launch
- High risk (unvalidated product)
- Regulatory complexity before product-market fit

**Decision:** Rejected. Too risky without validation.

### Alternative 3: Partner with Existing Community Bank

**Pros:**
- Faster than banking charter (6-12 months vs. 18-24 months)
- Lower capital requirements ($500K vs. $1-2M)
- Leverage existing compliance infrastructure

**Cons:**
- Less control than own charter
- Partner bank may have misaligned incentives
- Revenue sharing reduces margins

**Decision:** Considered as parallel path to banking charter (Phase 2 fallback).

---

## References

This ADR is based on:
- SOLVY platform mission and cooperative structure
- Financial projections (100 members → 10K members)
- Stripe pricing: 2.9% + $0.30 per transaction
- Banking charter requirements (FDIC, OCC)
- Card network integration timelines (Visa, Mastercard)
- Community banking best practices
- Cooperative economics principles

---

## Appendix: Financial Projections

### Phase 1: MVP (0-1K members)

| Metric | Value |
|--------|-------|
| Members | 1,000 |
| Avg. Transaction Volume/Member | $1,000/month |
| Total Monthly Volume | $1M |
| Annual Volume | $12M |
| Interchange Revenue (1.5%) | $180K/year |
| Stripe Fees (2.9% + $0.30) | $360K/year |
| Net Payment Margin | -$180K/year |
| Membership Fees ($10/month) | $120K/year |
| **Total Revenue** | **$300K/year** |
| **Total Costs** | **$400K/year** (Stripe + ops) |
| **Net Margin** | **-$100K/year** |

**Note:** Phase 1 is intentionally unprofitable. Goal is validation, not profit.

### Phase 2: Hybrid (1K-5K members)

| Metric | Value |
|--------|-------|
| Members | 5,000 |
| Avg. Transaction Volume/Member | $1,000/month |
| Total Monthly Volume | $5M |
| Annual Volume | $60M |
| Interchange Revenue (1.5%) | $900K/year |
| Stripe Fees (2.9% + $0.30) | $1.8M/year |
| Net Payment Margin | -$900K/year |
| Membership Fees ($10/month) | $600K/year |
| **Total Revenue** | **$1.5M/year** |
| **Total Costs** | **$2M/year** (Stripe + ops + banking) |
| **Net Margin** | **-$500K/year** |

**Note:** Phase 2 invests in banking infrastructure. Still unprofitable but path to profitability clear.

### Phase 3: Sovereign (5K-10K members)

| Metric | Value |
|--------|-------|
| Members | 10,000 |
| Avg. Transaction Volume/Member | $1,000/month |
| Total Monthly Volume | $10M |
| Annual Volume | $120M |
| Interchange Revenue (1.8%) | $2.16M/year |
| Direct Card Network Fees (0.5%) | $600K/year |
| Net Payment Margin | $1.56M/year |
| Membership Fees ($10/month) | $1.2M/year |
| **Total Revenue** | **$2.76M/year** |
| **Total Costs** | **$1.5M/year** (ops + compliance) |
| **Net Margin** | **+$1.26M/year** |

**Note:** Phase 3 achieves profitability through sovereign infrastructure and scale.

---

**Document Version:** 1.0  
**Last Updated:** December 12, 2024  
**Next Review:** March 2025 (or upon reaching 500 members)
