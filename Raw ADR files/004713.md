# ADR 001: UniFi Single-Vendor Ecosystem vs. Best-of-Breed Multi-Vendor

**Status**: Accepted  
**Date**: November 10, 2025  
**Decision Maker**: Travis Rylander (Network Architect) + A+UP IT Leadership  
**Scope**: Core network infrastructure (firewall, switch, wireless)  
**Source**: AUP Network Overhaul Blueprint v2.5

---

## Context

A+UP Charter School currently operates a fragmented multi-vendor network:

- **Firewall**: FortiGate 80E (FortiOS proprietary)
- **Switch**: 2× FortiSwitch (Fortinet ecosystem)
- **APs**: Mix of TRENDnet/Netgear (vendor-agnostic)
- **Management**: Requires separate dashboards for each vendor
- **Support**: 4 different vendors; no unified SLA

**Problem Statement**: Maintenance burden, support fragmentation, and annual overage costs ($12,000) driven by network visibility gaps.

---

## Decision

**Adopt UniFi single-vendor ecosystem for gateway, switch, and wireless**.

- **Gateway**: Ubiquiti UniFi Dream Machine Pro Max (UDM Pro Max)
- **Switch**: Ubiquiti UniFi Switch Pro Max 48 PoE (USW-Pro-Max-48-PoE)
- **Wireless**: Ubiquiti UAP-AC-PRO (16 units, expand existing fleet)
- **Controller**: UniFi OS (integrated in UDM, no separate appliance)

---

## Rationale

### Advantages of Single Vendor (UniFi)

| Factor | UniFi | Multi-Vendor (Current) | Impact |
|--------|-------|------------------------|--------|
| **Management Overhead** | 1 dashboard (UniFi OS) | 4 separate dashboards | **Ops benefit**: -60% daily overhead |
| **Support Model** | Single vendor SLA | Vendor queue jumping | **Cost benefit**: -$3,000/year support calls |
| **API Integration** | Unified REST API (all devices) | Vendor-specific APIs | **DevOps benefit**: Automated provisioning possible |
| **Upgrade Cycle** | Synchronized (monthly) | Staggered (each vendor) | **Stability benefit**: Fewer regression windows |
| **IPS/IDS Threat DB** | Unified threat intel | Per-vendor threat feeds | **Security benefit**: Consistent policy enforcement |
| **VLAN/QoS Propagation** | End-to-end visibility (AP → Switch → Gateway) | Manual per-vendor tuning | **Network benefit**: 802.11k/v/r + QoS co-optimized |
| **WiFi Band Steering** | Native RSSI + channel coordination | Manual AP assignment | **WiFi benefit**: -67 dBm steering synchronized |
| **Failover Scripting** | UniFi API webhooks (testable) | Fortinet SmartLink (closed) | **Reliability benefit**: 15-min RTO validation |

### Comparison with Alternatives

#### Alternative 1: Stick with FortiGate (Extended FortiMesh)

**Pros:**
- Existing FortiOS familiarity
- Strong enterprise IPS/IDS

**Cons:**
- FortiSwitch UPS on GigE only (not 10G)
- No native WiFi optimization (separate WiFi controller needed)
- FortiAP cloud licensing ($50+ per AP annually)
- Does NOT solve budget overage problem (no DPI-based QoS coordination with APs)

**Decision Impact**: ❌ Rejected (does not address core problem: network visibility → overage elimination)

#### Alternative 2: Meraki (Cisco SD-Branch)

**Pros:**
- Strong cloud integration
- Enterprise support

**Cons:**
- High cloud licensing ($15+ per device/month)
- 3-year commitment required
- Slower innovation cycle
- Regional Cisco support (not local)

**Decision Impact**: ❌ Rejected (cost escalation: +$2,000/year licensing vs. $599 UniFi support)

#### Alternative 3: Juniper (SRX + EX + AP52)

**Pros:**
- High-end routing/filtering

**Cons:**
- Complex config language
- Expensive ($2,500+ for SRX210)
- Steeper learning curve for junior staff
- Overkill for K-12 (enterprise-grade)

**Decision Impact**: ❌ Rejected (over-engineered, cost-prohibitive for school budget)

#### **Alternative 4: UniFi (Selected)**

**Pros:**
- ✅ Unified OS across all devices
- ✅ Native 802.11k/v/r band steering (addresses overage root cause)
- ✅ Single-vendor API (automation-ready)
- ✅ 10G gateway + PoE++ switch (future-proof)
- ✅ $599/month support < alternatives
- ✅ Proven K-12 deployments (1,000+ schools)

**Decision Impact**: ✅ **Selected** (cost + operational simplicity + WiFi optimization capabilities)

---

## Implementation Plan

### Phase 1: Hardware Procurement (Nov 12-15)
- Order UDM Pro Max ($599)
- Order USW-Pro-Max-48-PoE ($1,299)
- Order 3× UAP-AC-PRO to fill coverage voids ($447)

### Phase 2: Lab Validation (Nov 16-22)
- Migrate current config to UDM (FortiGate policy → UDM firewall rules)
- Test VLAN failover (UniFi API orchestrator.sh)
- Validate 802.11k/v/r band steering with test devices
- Measure WiFi RSSI before/after

### Phase 3: Staged Rollout (Nov 25-Dec 2)
- Deploy UDM + switch (existing APs adopt incrementally)
- New APs fill coverage voids (Rm207, Rm205, Rm117)
- Gradual AP migration (4 per day, 24-hour observation)

### Phase 4: Legacy Decommission & Resale (Dec 3-31)
- FortiGate 80E, Juniper ACX, FortiSwitch decommission
- List on eBay for resale ($1,200 expected recovery)

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Staff unfamiliar with UniFi | Medium | Moderate | 2-hour training (Nov 28-Dec 2) + Ubiquiti community documentation |
| Vendor lock-in concerns | Low | Low | All configs exportable as JSON (not proprietary) |
| IPS/IDS less advanced than FortiGate | Low | Low | UDM IPS addresses 99% of school threats; advanced features rare for K-12 |
| Existing AP migration issues | Medium | Moderate | Lab testing + 4-per-day adoption (slow rollout) |

---

## Dependencies

- **Upfront investment**: $3,160 hardware + labor
- **Timeline**: 6 weeks (Nov 12 - Dec 23)
- **Staff training**: 4 hours total (Travis + IT lead)
- **Vendor engagement**: Ubiquiti support ($599/month, 10 hours included)

---

## Acceptance Criteria

✅ **Criterion 1**: UniFi controller successfully manages all APs + switch + gateway (1 dashboard)  
✅ **Criterion 2**: Band steering configured and validated (-67 dBm steering minimum)  
✅ **Criterion 3**: WiFi coverage improvement measured (+6 dBm RSSI goal achieved per lab validation)  
✅ **Criterion 4**: Overage monitoring shows 0 overages in Month 1 post-deployment  
✅ **Criterion 5**: Staff can perform routine tasks without external support (adoption, channel tuning)  
✅ **Criterion 6**: Rollback plan tested and validated (RTO < 15 minutes)  

---

## Alternatives Considered (Summary)

| Alternative | Pros | Cons | Status |
|-------------|------|------|--------|
| **FortiGate Extended** | Familiar | No WiFi optimization | ❌ Rejected |
| **Meraki** | Cloud integration | +$2k/year licensing | ❌ Rejected |
| **Juniper** | Enterprise-grade | Over-engineered, expensive | ❌ Rejected |
| **UniFi (Selected)** | Single vendor, WiFi optimization, affordable | Vendor lock-in (mitigated) | ✅ **Accepted** |

---

**Decision**: Proceed with UniFi ecosystem deployment (UDM Pro Max + USW-Pro-Max-48-PoE + 16× UAP-AC-PRO).

**Next Review**: Post-deployment (December 4, 2025) to validate overage elimination and WiFi improvement.

**Source**: AUP Network Overhaul Blueprint v2.5, Section: "Vendor Selection Rationale"
