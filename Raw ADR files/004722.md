# ADR-011: CIPA Compliance via CyberSecure (Manual Configuration)

**Status:** Implemented  
**Date:** 2025-12-05  
**T3-ETERNAL Impact:** Perimeter (Suehring) — Content filtering compliance  
**Disclaimer:** CyberSecure alone is **NOT CIPA-certified**

---

## Context

A+UP Charter School requires **CIPA (Children's Internet Protection Act) compliance** for federal E-Rate funding. CIPA mandates:

1. **Content filtering** blocking access to obscene, pornographic, or harmful material
2. **Monitoring** of online activity for minors (students)
3. **Safety policy** educating students on appropriate online behavior
4. **Audit trail** demonstrating compliance (90-day retention minimum)

### Current Environment

- **UniFi CyberSecure:** Included with UDM Pro Max
- **150+ Chromebooks:** Student devices (VLAN 10)
- **Guest WiFi:** Visitor access (VLAN 30)

### Problem Statement

**CyberSecure DPI identifies content categories but does NOT auto-configure CIPA-compliant filtering.**

---

## Decision

Use **CyberSecure with manual category selection** as **baseline filtering**, supplemented by **syslog export** for audit trail.

### Configuration

```bash
# Enable CyberSecure
UniFi UI → Settings → Security → CyberSecure → Enabled

# Block CIPA-required categories (MANUAL configuration)
- Adult content
- Gambling
- Violence/weapons
- Drugs/alcohol
- Hate speech
- Malware/phishing

# Apply to networks
- VLAN 10 (Students)
- VLAN 30 (Guest WiFi)
```

### CIPA Audit Logging

```bash
# Enable syslog export (90-day retention)
UniFi UI → Settings → System → Logging → Remote Syslog
  - Host: 10.99.0.10 (syslog server)
  - Port: 514
  - Protocol: UDP

# Log all content filter blocks
UniFi UI → Settings → Security → CyberSecure → Advanced
  - Log Blocked Content: Enabled
  - Retention: 90 days minimum
```

---

## Critical Limitations

### ⚠️ CyberSecure is NOT CIPA-Certified

**What this means:**
- CyberSecure provides DPI-based category blocking
- **BUT:** Not audited or certified by CIPA authorities
- **Result:** May not meet strict E-Rate compliance audits

### ⚠️ Manual Configuration Required

**No auto-magic:**
- Must manually select each blocked category
- DPI identifies traffic but does NOT auto-block
- Weekly review required (new categories may emerge)

### ⚠️ No YouTube Restricted Mode Enforcement

**Limitation:**
- CyberSecure cannot force YouTube Restricted Mode
- Students can disable Restricted Mode in YouTube settings
- **Workaround:** Google Admin Console → YouTube Restricted Mode policy

### ⚠️ Limited Reporting

**Audit gap:**
- CyberSecure logs are minimal (category blocks only)
- No detailed user-level reporting (which student accessed what)
- **Requirement:** Third-party filter for full CIPA audit trail

---

## Recommendation: Add Third-Party Filter

For **full CIPA compliance**, deploy one of these:

### Option 1: Lightspeed Filter (Recommended)

**Cost:** ~$3/student/year  
**Features:**
- CIPA-certified content filtering
- YouTube Restricted Mode enforcement
- Detailed user-level reporting (per-student activity)
- SSL inspection (HTTPS filtering)
- Parent notifications

**Deployment:** Chrome extension pushed via Google Admin Console

### Option 2: Securly

**Cost:** ~$4/student/year  
**Features:**
- CIPA-certified filtering
- 24/7 self-harm monitoring
- Parent portal access
- Chrome extension deployment

### Option 3: GoGuardian

**Cost:** ~$10/student/year  
**Features:**
- CIPA filtering + classroom management
- Screen monitoring for teachers
- Activity timeline per student
- Chrome extension deployment

---

## Implementation

### Phase 1: CyberSecure Baseline (Current)

```bash
# Configure CyberSecure manually
bash scripts/configure-cybersecure-cipa.sh

# Enable syslog audit trail
bash scripts/configure-cipa-logging.sh
```

### Phase 2: Third-Party Filter (Recommended for Full Compliance)

```bash
# Procurement timeline
- Q1 2026: Budget approval for Lightspeed ($450/year × 150 students)
- Q2 2026: Deploy Chrome extension via Google Admin Console
- Q3 2026: Validate CIPA compliance with E-Rate auditor
```

---

## Consequences

### Current State (CyberSecure Only)

✅ **Pros:**
   - Included with UDM Pro Max (no additional cost)
   - DPI-based category blocking
   - Minimal performance impact (hardware DPI engine)

⚠️ **Cons:**
   - **NOT CIPA-certified** (audit risk)
   - Manual category selection required
   - No YouTube Restricted Mode enforcement
   - Limited user-level reporting

### Recommended State (CyberSecure + Lightspeed)

✅ **Pros:**
   - **CIPA-certified** (E-Rate safe)
   - Detailed per-student reporting
   - YouTube Restricted Mode enforced
   - SSL inspection for HTTPS filtering
   - Parent notifications

⚠️ **Cons:**
   - Additional cost: ~$450/year (150 students)
   - Chrome extension management overhead

---

## Validation

### CyberSecure Testing

```bash
# Test blocked categories from VLAN 10 Chromebook
curl http://example-adult-site.com
# Should return: "Blocked by CyberSecure"

# Verify syslog export
ssh admin@10.99.0.10 'tail -f /var/log/syslog | grep CyberSecure'
# Should log: "Content blocked: Adult, source: 10.10.x.x"
```

### CIPA Audit Checklist

- [ ] Content filtering enabled on student network (VLAN 10)
- [ ] Blocked categories match CIPA requirements
- [ ] Syslog retention ≥ 90 days
- [ ] Safety policy documented and distributed to students
- [ ] Annual review of blocked categories
- [ ] Third-party CIPA-certified filter deployed (Lightspeed/Securly)

---

## Compliance

| Requirement | CyberSecure | CyberSecure + Lightspeed |
|-------------|-------------|--------------------------|
| Block obscene content | ✅ Yes | ✅ Yes |
| Block pornography | ✅ Yes | ✅ Yes |
| Block harmful material | ⚠️ Partial | ✅ Full |
| User-level monitoring | ❌ No | ✅ Yes |
| CIPA certification | ❌ No | ✅ Yes |
| E-Rate audit trail | ⚠️ Minimal | ✅ Comprehensive |
| YouTube Restricted Mode | ❌ No | ✅ Yes |

---

## References

- **Configuration Script:** `scripts/configure-cybersecure-cipa.sh`
- **Logging Script:** `scripts/configure-cipa-logging.sh`
- **CIPA Requirements:** https://www.fcc.gov/consumers/guides/childrens-internet-protection-act
- **CyberSecure Docs:** https://help.ui.com/hc/en-us/articles/360006893234-UniFi-CyberSecure
- **Lightspeed Filter:** https://www.lightspeedsystems.com/filter/

---

## Timeline

- **2025-11-12:** CyberSecure enabled, manual categories configured
- **2025-12-05:** Syslog export validated, 90-day retention confirmed
- **2026-Q2 (Planned):** Lightspeed procurement and deployment

---

## Success Metrics

### Current (CyberSecure Baseline)

✅ **8 CIPA categories blocked** (adult, gambling, violence, drugs, hate, malware)  
✅ **Syslog export operational** (90-day retention)  
⚠️ **CIPA certification:** None (audit risk)

### Target (CyberSecure + Lightspeed)

✅ **CIPA-certified filtering**  
✅ **Per-student activity reports**  
✅ **YouTube Restricted Mode enforced**  
✅ **E-Rate audit ready**

**Status:** Phase 1 complete (baseline filtering), Phase 2 required for full CIPA compliance.
