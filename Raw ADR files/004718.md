# ADR 006: Printer mDNS Reflector & AirPrint Discovery

**Status**: Accepted  
**Date**: November 10, 2025  
**Decision Maker**: Travis Rylander (Network Architect)  
**Scope**: Printer discovery, VLAN 20 isolation, AirPrint support  
**Source**: Additional Considerations Addendum AUP.docx, Comprehensive WiFi Assessment V2.1

---

## Context

A+UP operates 40+ printers distributed across campus:

**Current State**:
- All printers on same VLAN as students (VLAN 10)
- mDNS (Bonjour) enabled on all printers → broadcast storms
- Staff cannot reliably find printers from Chromebooks (mDNS scope not configured)
- Some printers unreachable from certain WiFi APs (band steering issues)

**Problem**:
- Printer mDNS floods all 510 student devices (VLAN 10 broadcasts)
- Students accidentally print to wrong printer (security risk: grades printing to office printer)
- Staff cannot print from student Chromebooks (different subnets, no mDNS bridge)
- Band steering inadvertently steers Chromebooks away from printers (2.4GHz disabled)

---

## Decision

**Implement mDNS reflector on UDM (VLAN 20 isolation for printers) + AirPrint fallback for cross-VLAN printing**.

| Aspect | Before | After | Improvement |
|--------|--------|-------|------------|
| **Printer Location** | VLAN 10 (student scope) | VLAN 20 (staff scope) | Printer discovery isolated to staff |
| **mDNS Broadcast** | 40+ printers flood all 510 Chromebooks | mDNS reflector bridges VLAN 20 ↔ VLAN 10 on-demand | Broadcast storms eliminated |
| **Chromebook Printing** | Manual IP entry required | AirPrint discovery + automatic queue | User-friendly |
| **Cross-VLAN Printing** | Staff cannot print from student accounts | mDNS reflector + DNS-SD proxy | Discovery works across VLANs |
| **2.4GHz Support** | All printers on 2.4GHz (weak signal) | Printers on WAP2/4 low-power AP | Stable printer connection |

---

## Rationale

### Why VLAN 20 (Staff) for Printers?

**Printer Assignment Logic**:

| Criterion | Candidate | Selection | Rationale |
|-----------|-----------|-----------|-----------|
| **Scope** | Student (V10) vs. Staff (V20) | V20 (Staff) | Printers are administrative devices (IT controls, purchasing) |
| **Security** | Who should manage? | Staff (IT + admin) | Students should not reconfigure printers |
| **mDNS Broadcast** | V10 = 510 hosts, V20 = 254 hosts | V20 | Smaller scope = fewer mDNS storms |
| **DHCP Lease** | V10 (4 hrs) vs. V20 (24 hrs) | V20 | Printers stable (never disconnects) |
| **IP Stability** | Dynamic leases risky | Static MAC binding | Printers never change IPs |

**Consequence**: Students (VLAN 10) cannot directly discover printers via mDNS.

**Solution**: mDNS reflector (see below) bridges gap.

### Why mDNS Reflector (Not Avahi on Separate Device)?

**mDNS Reflector Options**:

#### Option A: Avahi Daemon (Linux box in closet)
- ❌ Additional hardware to manage
- ❌ Power/cooling requirements
- ❌ Single point of failure
- ✅ Fine-grained control (custom reflector rules)

#### Option B: UDM Built-in Reflector
- ✅ UDM already powers on (no extra device)
- ✅ High availability (redundant with UDM failover)
- ✅ Integrated into firewall (reflector rules aligned with VLAN firewall)
- ❌ Less granular (built-in reflector may have limitations)

**Selected**: **Option B - UDM Built-in Reflector** (simplicity + existing infrastructure)

### mDNS Reflector Configuration

**What It Does**:
1. Listen for mDNS queries on VLAN 10 (students asking "where are printers?")
2. Query VLAN 20 for printer mDNS records
3. Return printer records to student (appears as if printer is on VLAN 10)
4. Student sends print job via IP address (VLAN 20 firewall allows VLAN 10 → VLAN 20 for port 9100 = IPP, 515 = LPR, 631 = CUPS)

**UDM Configuration**:
```
UDM Dashboard > Network > DNS:
  mDNS Reflector: Enabled
  Reflector Rules:
    - VLAN 10 ← VLAN 20 (_ipp._tcp.local)  [Apple AirPrint service]
    - VLAN 10 ← VLAN 20 (_printer._tcp.local) [Generic printer service]
    - VLAN 10 ← VLAN 20 (_http._tcp.local)  [CUPS web interface]
```

---

## Implementation Plan

### Phase 1: VLAN 20 Printer Assignment (Nov 20-22)

1. Audit all 40+ printers → document current IP addresses
2. For each printer:
   - Get MAC address (print network config page)
   - Assign static IP via VLAN 20 DHCP MAC binding
   - Test: Can device boot and obtain IP in VLAN 20?
3. Migrate printers gradually (5 per day):
   - Power cycle printer in new VLAN
   - Verify connection to VLAN 20
   - Test print from admin workstation

### Phase 2: mDNS Reflector Configuration (Nov 23-24)

1. Log into UDM dashboard (10.99.0.1)
2. Network > DNS > Enable mDNS Reflector
3. Add reflector rules (VLAN 10 ← VLAN 20 for printer services):
   ```
   Rule 1: Reflect _ipp._tcp.local (Apple AirPrint)
   Rule 2: Reflect _printer._tcp.local (Generic printers)
   Rule 3: Reflect _http._tcp.local (Web admin)
   ```
4. Save and restart UDM networking (2 min downtime)

### Phase 3: Firewall Rules (VLAN 10 → VLAN 20 Printer Access)

1. Add firewall rule (allow printing):
   ```
   Source: VLAN 10 (Students)
   Destination: VLAN 20 (Staff/Printers)
   Ports: 9100 (IPP), 515 (LPR), 631 (CUPS)
   Action: ALLOW
   ```
2. Verify in UDM firewall dashboard (rule appears)

### Phase 4: Chromebook Testing (Nov 25-26)

1. Deploy test Chromebook in VLAN 10
2. Open Google Cloud Print (or native printer discovery)
3. **Test 1 - mDNS Discovery**: "Available printers" should list all VLAN 20 printers
4. **Test 2 - Print Job**: Submit test print → document emerges from physical printer
5. **Test 3 - Multiple Printers**: Verify multiple printers appear in list (not just one)
6. **Repeat Test 1-3 from different APs** (ensure band steering doesn't break discovery)

### Phase 5: Staff Deployment (Nov 27-Dec 1)

1. Send staff email: "Printer discovery now available on Chromebooks"
2. Training (15 min):
   - Open print dialog from Google Classroom
   - Select from available printers (no manual IP entry needed)
   - Submit print job
   - Collect output

### Phase 6: WAP2/4 Fallback (Printer 2.4GHz AP) (Dec 2)

1. Dedicate one UAP-AC-PRO to 2.4GHz-only (WAP2/4 carve)
2. SSID: "Printer-Setup-2.4"
3. Place in central location (copy room or break room)
4. Tx Power: -10 dBm (low, ~25 feet range)
5. VLAN: 20 (printer VLAN)
6. **Purpose**: Legacy printer setup devices (some printers cannot adopt 5GHz)

---

## Cross-VLAN Printing Architecture

**Diagram** (VLAN 10 Chromebook → VLAN 20 Printer):
```
Chromebook (VLAN 10)
    ↓
[mDNS Query: "_ipp._tcp.local?"]
    ↓
UDM mDNS Reflector
    ↓ (reflects query to VLAN 20)
Printer (VLAN 20)
    ↓ [mDNS Response: "Brother-MFC-7360 at 10.20.0.50"]
    ↓
Chromebook receives response
    ↓
[Firewall Rule: VLAN 10 → VLAN 20:631 ALLOW]
    ↓
Print job sent to 10.20.0.50:631 (CUPS port)
    ↓
Printer outputs document
```

---

## AirPrint Fallback (If mDNS Reflector Fails)

**Risk Mitigation**:
- If mDNS reflector fails to bridge VLAN 10 ↔ VLAN 20
- Alternative: **Google Cloud Print** (cloud-based, no mDNS required)
  - Printers register with Google Cloud Print service
  - Chromebook queries Google service (not local mDNS)
  - Print job routed through cloud (higher latency, but works)
  - Limitation: Requires Google Workspace account (A+UP has this)

**Activation Steps** (if needed):
1. Go to https://google.com/cloudprint (deprecated 2021, but schools still supported)
2. Add each printer to Google account
3. Chromebooks see "Cloud Printers" list
4. Fall back to cloud printing

---

## Acceptance Criteria

✅ **Criterion 1**: All 40+ printers assigned VLAN 20 (static MAC binding)  
✅ **Criterion 2**: mDNS reflector enabled and running in UDM  
✅ **Criterion 3**: Firewall rule VLAN 10 → VLAN 20 (ports 9100/515/631) active  
✅ **Criterion 4**: Chromebook discovers 40+ printers in print dialog (mDNS discovery)  
✅ **Criterion 5**: Test print from Chromebook → document prints successfully  
✅ **Criterion 6**: Multiple printers listed (not just first printer visible)  
✅ **Criterion 7**: Band steering does not break discovery (test on all 16 APs)  
✅ **Criterion 8**: WAP2/4 printer AP up and operational (2.4GHz fallback)  

---

**Decision**: Proceed with UDM mDNS reflector + VLAN 20 printer isolation + AirPrint fallback.

**Next Review**: Post-deployment printer discovery validation (December 4, 2025).

**Source**: Additional Considerations Addendum AUP.docx, Comprehensive WiFi Assessment V2.1
