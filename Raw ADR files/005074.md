# ADR-002: Control Framework Selection

**Status:** Accepted  
**Date:** 2026-01-03  
**Deciders:** Security Architecture Team  
**Technical Story:** Establish authoritative control framework mapping for enterprise AI governance

---

## Context

Enterprise organizations deploying agentic AI systems face a **compliance translation problem**: regulatory frameworks for AI (NIST AI RMF, EU AI Act, ISO 42001) don't map directly to existing security control frameworks (NIST 800-53, ISO 27001, SOC 2) that auditors understand. Security teams need a defensible crosswalk to demonstrate AI governance within established compliance programs.

### Market Reality

| Framework | Target Audience | AI-Specific Coverage | Enterprise Adoption |
|-----------|-----------------|---------------------|---------------------|
| **NIST AI RMF** | All sectors | Comprehensive AI lifecycle | Emerging, high government interest |
| **EU AI Act** | EU market access | Risk-based AI classification | Required for EU deployment |
| **ISO 42001** | International | AI management systems | Early adoption phase |
| **NIST 800-53** | FedRAMP/Government | Traditional security, no AI | Universal in regulated industries |
| **ISO 27001** | International | Information security, no AI | Mature, widespread |
| **SOC 2** | SaaS/Enterprise | Trust principles, no AI | Standard for B2B software |

### The Gap

**No vendor provides comprehensive AI-to-legacy control mappings:**

1. **NIST AI RMF** is the most complete AI governance framework but doesn't map to auditor-familiar 800-53
2. **FedRAMP** organizations have 800-53 as their control baseline—they need to demonstrate AI governance in those terms
3. **Auditors** don't yet understand AI RMF—translating to 800-53 provides familiar context
4. **Multi-framework** organizations (FedRAMP + SOC 2 + ISO) need unified view

---

## Decision Drivers

| Driver | Weight | Description |
|--------|--------|-------------|
| **Regulatory trajectory** | High | NIST AI RMF has federal backing, likely to become standard |
| **Enterprise adoption** | High | 800-53 is the lingua franca of enterprise security |
| **FedRAMP alignment** | High | Primary target market requires 800-53 compliance |
| **International applicability** | Medium | ISO mappings extend market reach |
| **Audit defensibility** | High | Mappings must withstand regulatory scrutiny |
| **Implementation complexity** | Medium | Crosswalks require ongoing maintenance |

---

## Considered Options

### Option 1: NIST AI RMF → NIST 800-53 (Primary) + ISO 42001 (Secondary)

**Build comprehensive crosswalk from AI RMF to 800-53, with supplemental ISO 42001 mapping.**

**Pros:**
- NIST AI RMF is the most comprehensive AI governance framework
- 800-53 is required for FedRAMP, universal in regulated industries
- Both are NIST frameworks—natural alignment in terminology and structure
- Federal government momentum behind AI RMF adoption
- ISO 42001 provides international extension

**Cons:**
- Crosswalk requires significant expertise to build defensibly
- Ongoing maintenance as frameworks evolve
- Some AI RMF controls have no direct 800-53 equivalent

### Option 2: EU AI Act → ISO 27001 + SOC 2

**Build crosswalk from EU AI Act to ISO 27001 and SOC 2 trust principles.**

**Pros:**
- EU AI Act is legally binding (not voluntary like NIST)
- ISO 27001 has global recognition
- SOC 2 is standard for SaaS companies

**Cons:**
- EU AI Act is narrow (risk classification focused)
- Less comprehensive than NIST AI RMF
- ISO 27001 already has established AI extensions (ISO 42001)
- Limited applicability to US federal market

### Option 3: Unified Framework Abstraction Layer

**Create abstract "AI Security Controls" that map to ALL frameworks simultaneously.**

**Pros:**
- Single source of truth for all mappings
- Framework-agnostic control definitions
- Simplified maintenance

**Cons:**
- Abstraction loses framework-specific nuance
- Auditors want specific control citations, not abstractions
- Significant design complexity
- No precedent or industry acceptance

### Option 4: Custom Control Framework (Build Our Own)

**Define AgentGuard-specific controls independent of any standard.**

**Pros:**
- Complete control over control definitions
- Tailored specifically for agentic AI

**Cons:**
- Zero regulatory credibility
- Auditors won't accept non-standard controls
- Requires organizations to maintain yet another framework
- No path to compliance certification

---

## Decision

**Selected: Option 1 — NIST AI RMF → NIST 800-53 (Primary) + ISO 42001 (Secondary)**

### Rationale

1. **Federal momentum**: NIST AI RMF has strong government backing and will become the de facto US standard
2. **Audit familiarity**: 800-53 is universally understood by compliance teams and auditors
3. **FedRAMP path**: Our target market (regulated enterprises, government contractors) requires 800-53
4. **First-mover advantage**: No comprehensive crosswalk exists—AgentGuard becomes the authoritative source
5. **Extensibility**: ISO 42001 secondary mapping enables international market expansion

### Mapping Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     AGENTGUARD CONTROL MAPPING ENGINE                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐                      ┌─────────────────┐          │
│  │   NIST AI RMF   │                      │  NIST 800-53    │          │
│  │                 │                      │                 │          │
│  │ GOVERN-1.1      │──────── exact ──────▶│ PL-1            │          │
│  │ GOVERN-1.2      │──────── partial ────▶│ PL-2 + SA-8     │          │
│  │ MAP-1.1         │──────── partial ────▶│ PL-2 + SA-15    │          │
│  │ MAP-1.5         │──────── partial ────▶│ RA-3            │          │
│  │ MEASURE-1.1     │──────── partial ────▶│ CA-7 + SI-4     │          │
│  │ MANAGE-1.1      │──────── partial ────▶│ RA-7            │          │
│  │                 │                      │                 │          │
│  │   + 68 more     │                      │   + mappings    │          │
│  └─────────────────┘                      └─────────────────┘          │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     CROSSWALK METADATA                          │   │
│  │                                                                 │   │
│  │  For each mapping:                                              │   │
│  │  • mapping_type: exact | partial | superset | subset | related  │   │
│  │  • confidence: 0.0 - 1.0                                        │   │
│  │  • rationale: Why this mapping exists                           │   │
│  │  • gaps: What the target doesn't cover                          │   │
│  │  • supplements: Additional controls to close gaps               │   │
│  │  • evidence_mapping: How to satisfy both simultaneously         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────┐                      ┌─────────────────┐          │
│  │  ISO 42001      │                      │  SOC 2 TSP      │          │
│  │  (Secondary)    │                      │  (Future)       │          │
│  └─────────────────┘                      └─────────────────┘          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Mapping Types Defined

| Type | Definition | Example |
|------|------------|---------|
| **exact** | Source and target cover identical scope | GOVERN-1.1 ↔ PL-1 (both address policy requirements) |
| **partial** | Significant overlap, but gaps exist | MAP-1.1 ↔ PL-2 (PL-2 lacks AI capability documentation) |
| **superset** | Source covers more than target | AI RMF fairness controls ↔ 800-53 (no fairness in 800-53) |
| **subset** | Target covers more than source | Simple AI control ↔ comprehensive 800-53 family |
| **related** | Conceptually connected but different scope | AI transparency ↔ AU-3 (audit content) |

---

## Implementation

### Phase 1: Core Crosswalk (Weeks 1-4)

1. **Map all 72 NIST AI RMF subcategories** to 800-53 controls
2. **Assign confidence scores** based on control language analysis
3. **Document gaps** where 800-53 lacks AI coverage
4. **Define supplement recommendations** to close gaps

### Phase 2: Gap Analysis Engine (Weeks 5-8)

1. **Build gap detection** based on organization's 800-53 implementation
2. **Generate remediation roadmap** with prioritized controls
3. **Create evidence crosswalk** showing how to satisfy both frameworks

### Phase 3: ISO 42001 Extension (Weeks 9-12)

1. **Map AI RMF to ISO 42001** for international customers
2. **Build 800-53 ↔ ISO 42001 bridge** for multi-framework organizations
3. **Export capabilities** for auditor deliverables

---

## Consequences

### Positive

- ✅ **First-mover advantage**: AgentGuard becomes the authoritative AI→800-53 crosswalk
- ✅ **Audit defensibility**: Mappings use established framework terminology
- ✅ **Federal market access**: Direct path to FedRAMP-aligned organizations
- ✅ **Consulting opportunity**: Crosswalk expertise as professional services offering
- ✅ **Community credibility**: Contribution to industry knowledge

### Negative

- ⚠️ **Maintenance burden**: Frameworks evolve independently, crosswalks need updates
- ⚠️ **Subjective mappings**: Some mappings require judgment calls that may be challenged
- ⚠️ **Scope limitation**: 800-53 simply doesn't cover some AI risks (fairness, explainability)

### Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| NIST updates AI RMF significantly | Medium | High | Subscribe to NIST updates, version crosswalks |
| Auditors reject mapping methodology | Low | High | Document rationale extensively, seek expert review |
| ISO 42001 becomes primary standard | Medium | Medium | Already planned as secondary mapping |
| EU AI Act requires different approach | Medium | Low | Separate EU-specific crosswalk module |

---

## Validation

### Expert Review

- [ ] Submit crosswalk to NIST AI RMF working group for feedback
- [ ] Engage FedRAMP 3PAO for methodology review
- [ ] Present at ISACA/ISC2 conferences for industry validation

### Customer Validation

- [ ] Pilot with 2-3 FedRAMP organizations
- [ ] Gather auditor feedback on crosswalk utility
- [ ] Iterate based on real compliance assessments

---

## References

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [NIST SP 800-53 Rev 5](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
- [ISO/IEC 42001:2023](https://www.iso.org/standard/81230.html)
- [FedRAMP Control Baselines](https://www.fedramp.gov/documents/)

---

## Appendix: Sample Crosswalk Entries

### GOVERN-1.1 → PL-1

```yaml
source:
  framework: NIST AI RMF
  control_id: GOVERN-1.1
  title: Legal and regulatory requirements are identified

target:
  framework: NIST 800-53
  control_id: PL-1
  title: Policy and Procedures

mapping_type: partial
confidence: 0.8

rationale: |
  PL-1 requires organizations to develop and maintain security policies 
  that address applicable laws and regulations. GOVERN-1.1 specifically 
  requires identification of AI-related legal requirements. PL-1's scope 
  is broader (all security) while GOVERN-1.1 is narrower (AI-specific).

gaps:
  - PL-1 does not specifically address AI legislation (EU AI Act, state AI laws)
  - PL-1 does not address AI-specific liability considerations
  - No requirement for AI-specific regulatory monitoring

supplements:
  - SA-9: External system services (for AI vendor assessments)
  - PM-1: Information security program plan (for AI governance integration)

evidence_mapping:
  - Maintain AI regulatory tracking register (satisfies GOVERN-1.1)
  - Include AI section in security policy (satisfies both)
  - Document AI vendor compliance requirements (satisfies GOVERN-1.1 + SA-9)
```

### MEASURE-1.1 → CA-7 + SI-4

```yaml
source:
  framework: NIST AI RMF
  control_id: MEASURE-1.1
  title: Approaches for measurement are documented

target:
  framework: NIST 800-53
  control_id: CA-7
  title: Continuous Monitoring
  
secondary_target:
  framework: NIST 800-53
  control_id: SI-4
  title: System Monitoring

mapping_type: partial
confidence: 0.75

rationale: |
  MEASURE-1.1 requires documented measurement approaches for AI system 
  trustworthiness. CA-7 addresses continuous monitoring of security 
  controls, while SI-4 covers system monitoring for security events.
  Combined, they partially address AI measurement needs but lack 
  AI-specific metrics (model drift, fairness, explainability).

gaps:
  - No AI-specific metrics in 800-53 (accuracy, fairness, robustness)
  - No model performance monitoring requirements
  - No drift detection or retraining triggers
  - No AI explanation or interpretability monitoring

supplements:
  - Build AgentGuard observability for AI-specific metrics
  - Document AI measurement methodology in SSP Appendix
  - Integrate AI metrics with CA-7 continuous monitoring program
```
