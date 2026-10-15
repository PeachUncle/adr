# ADR 002: Six-VLAN Network Segmentation Architecture

**Status**: Accepted  
**Date**: November 10, 2025  
**Decision Maker**: Travis Rylander + A+UP IT Leadership  
**Scope**: Network segmentation, access control, QoS prioritization  
**Source**: AUP Network Overhaul Blueprint v2.5

---

## Context

A+UP Charter School operates a K-12 facility with:
- **~120 Chromebooks** (upstairs students)
- **~40+ printers** (mixed departments)
- **8 VoIP phones** (Yealink T43U)
- **12-15 surveillance cameras** (Verkada)
- **Fiber WAN** connection (capacity: 100 Mbps symmetric)
- **UPS-backed critical infrastructure** (VoIP, firewall, switch, UPS monitoring)
- **Guest WiFi** (parent drop-ins, contractor access)

**Current State**: All devices share single VLAN (10.0.0.0/24), leading to:
- Broadcast storm risk (mDNS from 40+ printers flooding all segments)
- No QoS isolation (Chromebook bulk downloads starving VoIP jitter)
- Security exposure (guests on same network as student data)
- No bandwidth reservation (video streaming competing with DHCP)

**Problem**: Lack of segmentation prevents:
- CIPA compliance (student traffic monitoring)
- FERPA compliance (sensitive staff/student data isolation)
- VoIP call quality (no jitter guarantees)
- Printer discovery (mDNS storms across all clients)

---

## Decision

**Implement six-VLAN architecture with role-based segmentation and QoS prioritization**.

| VLAN | Name | Purpose | Subnet | Hosts | QoS | DHCP | Firewall |
|------|------|---------|--------|-------|-----|------|----------|
| 10 | Students | Chromebooks, student devices | 10.10.0.0/23 | 510 | Standard | 4 hrs | Outbound web only |
| 20 | Staff | Staff workstations, printers | 10.20.0.0/24 | 254 | High Priority | 24 hrs | Full internet + internal |
| 30 | Guest | Public WiFi (parents, contractors) | 10.30.0.0/24 | 254 | Throttled (25/10 Mbps) | 2 hrs | Web/DNS only |
| 50 | VoIP | Yealink phones, wireless headsets | 10.50.0.0/27 | 30 | DSCP EF (Expedited Forward) | Infinite | Call server only |
| 60 | Cameras | Verkada surveillance system | 10.60.0.0/26 | 62 | AF41 (Assured Forward) | Infinite | Cloud uplink only |
| 99 | Management | UDM, switch, UPS monitoring | 10.99.0.0/28 | 14 | CS6 (Control Signaling) | Static | Admin SSH/SNMP only |

---

## Rationale

### Why Six VLANs?

**VLAN 10 (Students)**: 
- **Rationale**: Isolates student Chromebook traffic to enable CIPA compliance (content filtering, monitoring)
- **Size**: 10.10.0.0/23 = 510 hosts (current 120 + 3× growth capacity)
- **QoS**: Standard (equal priority with others, no preferential treatment)
- **DHCP Lease**: 4 hours (shorter to detect rogue devices faster)
- **Firewall**: Outbound web/HTTPS/DNS only (no P2P, no student-to-student communication)
- **Benefit**: Contained compliance scope (only student VLAN requires filtering)

**VLAN 20 (Staff)**:
- **Rationale**: Staff access to internal services (file shares, gradebook, sensitive student records)
- **Size**: 10.20.0.0/24 = 254 hosts (30 staff + 40 printers + headroom)
- **QoS**: High Priority (DSCP CS4, prioritized over students)
- **DHCP Lease**: 24 hours (stable, trusted devices)
- **Firewall**: Full internet + internal access (staff need access to all services)
- **Benefit**: Printer discovery isolated to staff/admin scope; FERPA-sensitive traffic on isolated VLAN

**VLAN 30 (Guest)**:
- **Rationale**: Untrusted network for visitors (parents, contractors, community)
- **Size**: 10.30.0.0/24 = 254 hosts (capacity, but throttled)
- **QoS**: Throttled (25 Mbps download / 10 Mbps upload global limit)
- **DHCP Lease**: 2 hours (temporary access, higher security)
- **Firewall**: Web/HTTPS/DNS only (no internal access, no file shares)
- **Benefit**: Prevents guest exploitation of internal services; limits damage if guest device is compromised

**VLAN 50 (VoIP)**:
- **Rationale**: Real-time voice communication requires lowest latency/jitter
- **Size**: 10.50.0.0/27 = 30 usable hosts (8 phones + 22 headroom for wireless headsets/future expansion)
- **QoS**: DSCP EF (Expedited Forwarding, RFC 3246—absolute priority, pre-empts all others)
- **DHCP Lease**: Infinite (static assignment, phones registered by MAC)
- **Firewall**: SIP/RTP ports only (5060-5061, 16384-32768 UDP)
- **Jitter Target**: <30 ms (industry standard for MOS 4.0+)
- **Benefit**: Guaranteed call quality; no student bulk downloads starve voice traffic

**VLAN 60 (Cameras)**:
- **Rationale**: Video surveillance requires sustained bandwidth but not real-time jitter
- **Size**: 10.60.0.0/26 = 62 usable hosts (12-15 cameras + recording buffers + cloud uplink)
- **QoS**: AF41 (Assured Forwarding, RFC 2597—high priority, but can be delayed during extreme congestion)
- **DHCP Lease**: Infinite (static by MAC, cloud-registered)
- **Firewall**: Cloud uplink only (Verkada cloud portal, no local access)
- **Bandwidth Profile**: 100 Kbps idle, 3-45 Mbps per camera during motion (burst)
- **Benefit**: Cameras do not compete with VoIP; cloud-only (no local recording bottlenecks)

**VLAN 99 (Management)**:
- **Rationale**: Infrastructure devices (UDM, USW, UPS) require highest security
- **Size**: 10.99.0.0/28 = 14 usable hosts (3 devices + spares for future monitoring agents)
- **QoS**: CS6 (Control Signaling, RFC 3168—network operations priority)
- **DHCP Lease**: Static (immutable infrastructure)
- **Firewall**: SSH (22), SNMP (161), HTTPS (443) from admin workstations only
- **Benefit**: Management access isolated; UPS monitoring always reachable; UDM controller cannot be hijacked by user VLANs

---

### Why NOT Other Segmentation Models?

#### Alternative 1: Single VLAN (Current State)
- ❌ No CIPA/FERPA compliance isolation
- ❌ Printer mDNS storms affect all devices
- ❌ VoIP has no QoS guarantees (jitter bleeds from bulk transfers)
- ❌ No guest isolation (security risk)
- ❌ No rate limiting capability

#### Alternative 2: Three VLANs (Common Simplified Model)
VLANs: Students | Staff | Guest

- ❌ No VoIP/camera isolation (cameras will jam VoIP during live event recording)
- ❌ mDNS printer discovery still floods students (printers mixed with staff VLAN)
- ❌ No management isolation (UDM accessible from staff workstations)
- ❌ Single-point failure (Staff VLAN loss = printers + phones down)

#### Alternative 3: Ten+ VLANs (Over-Segmented)
One VLAN per department/device type

- ❌ Excessive complexity (OSI layer 2 management overhead)
- ❌ Printer subnet needs separate mDNS reflector config (multiple instances)
- ❌ Firewall rule explosion (O(n²) rules, hard to audit)
- ❌ Junior staff cannot manage during 3am emergency

#### **Six-VLAN Model (Selected)**: ✅ **Optimal Balance**
- Clear role-based isolation (Students, Staff, VoIP, Cameras, Management)
- Natural printer/staff consolidation (mDNS scope bound to 1 VLAN)
- QoS aligned to real-time requirements (EF for VoIP, AF41 for cameras)
- Firewall rules stay under 10-rule cap (segmentation only)
- Junior-at-3am deployable (<15 min via orchestrator.sh)

---

## Implementation Details

### DHCP Scope Configuration

| VLAN | Subnet | Pool Start | Pool End | Reserved | Lease |
|------|--------|-----------|---------|----------|-------|
| 10 | 10.10.0.0/23 | 10.10.1.0 | 10.10.3.199 | 10.10.3.200-10.10.3.255 (static IPs) | 4 hrs |
| 20 | 10.20.0.0/24 | 10.20.0.10 | 10.20.0.200 | 10.20.0.1-10.20.0.9, 10.20.0.201-10.20.0.255 | 24 hrs |
| 30 | 10.30.0.0/24 | 10.30.0.10 | 10.30.0.250 | 10.30.0.1-10.30.0.9, 10.30.0.251-10.30.0.255 | 2 hrs |
| 50 | 10.50.0.0/27 | — | — | 10.50.0.1 (router), 10.50.0.2-10.50.0.30 (static MAC binding) | Infinite |
| 60 | 10.60.0.0/26 | — | — | 10.60.0.1 (router), 10.60.0.2-10.60.0.62 (static MAC binding) | Infinite |
| 99 | 10.99.0.0/28 | — | — | All static (10.99.0.1 gateway, 10.99.0.2-10.99.0.14 infrastructure) | Static |

### Firewall Rules (10 Total)

| Rule # | Source | Dest | Port | Action | Rationale |
|--------|--------|------|------|--------|-----------|
| 1 | VLAN 10 | RFC1918 (internal) | Any | DENY | Students cannot access staff/management |
| 2 | VLAN 10 | 0.0.0.0/0 | 80, 443, 53 | ALLOW | Students web/DNS only |
| 3 | VLAN 20 | 0.0.0.0/0 | Any | ALLOW | Staff full internet |
| 4 | VLAN 20 | VLAN 50 | 5060-5061 | ALLOW | Staff can dial phones (optional) |
| 5 | VLAN 30 | 0.0.0.0/0 | 80, 443, 53 | ALLOW | Guests web/DNS (throttled) |
| 6 | VLAN 30 | RFC1918 | Any | DENY | Guests cannot access internal |
| 7 | VLAN 50 | 0.0.0.0/0 | 5060-5061, RTP | ALLOW | VoIP outbound calls |
| 8 | VLAN 50 | VLAN 50 | 5060-5061, RTP | ALLOW | Inter-phone calls (local) |
| 9 | VLAN 60 | Verkada DNS | 53, 443 | ALLOW | Cameras cloud uplink |
| 10 | VLAN 99 | 0.0.0.0/0 | SSH (22), SNMP (161) | DENY | Management locked down (no outbound) |

---

## Band Steering (802.11k/v/r)

**RSSI Thresholds** (per WiFi Assessment V2.1 lab tuning):

| VLAN | Threshold | Steering Target | Rationale |
|------|-----------|-----------------|-----------|
| VLAN 10 (Students) | -70 dBm hard | Nearest 5GHz AP | Maximize throughput for Chromebook classroom apps |
| VLAN 20 (Staff) | -70 dBm hard | Nearest 5GHz AP | Stable wireless for productivity (file uploads, VPN) |
| VLAN 30 (Guest) | -67 dBm minimum | Furthest 5GHz AP (load balance) | Reduce single-AP burden; guest devices have weak antennas |
| VLAN 50 (VoIP) | -65 dBm (softest) | Nearest 5GHz AP + 802.11k neighbor reports | VoIP phones must maintain highest signal to minimize jitter |
| VLAN 60 (Cameras) | -70 dBm hard | Nearest 5GHz AP (fixed mount) | Fixed locations; band steering less critical |

---

## Compliance Alignment

| Regulation | VLAN | Requirement | Implementation |
|-----------|------|-------------|-----------------|
| **CIPA** (Children's Internet Protection Act) | 10 (Students) | Content filtering + monitoring required | Student VLAN has ingress filtering rules; all student web traffic loggable via DPI |
| **FERPA** (Family Educational Rights & Privacy Act) | 20 (Staff) | Sensitive student records isolated | Staff VLAN segregated with CS4 QoS (implied importance) |
| **COPPA** (Children's Online Privacy Protection Act) | 10 (Students) | Parental consent for data collection | Student VLAN firewall rules prevent unauthorized cloud uploads |
| **MSA** (Managed Security Agreement) | 99 (Management) | Infrastructure security auditing | Management VLAN logs all UDM/USW changes via syslog to Loki |

---

## Acceptance Criteria

✅ **Criterion 1**: All six VLANs created in UDM and tagged on USW  
✅ **Criterion 2**: DHCP scopes configured with correct lease times per VLAN  
✅ **Criterion 3**: 802.11k/v/r band steering validated (test client roaming <5 sec)  
✅ **Criterion 4**: Printer mDNS discovery limited to VLAN 20 (staff only)  
✅ **Criterion 5**: VoIP QoS (DSCP EF) measured <30 ms jitter under load  
✅ **Criterion 6**: Firewall rules enforce segmentation (0 cross-VLAN unauthorized traffic)  
✅ **Criterion 7**: Guest VLAN throttling confirmed (25 Mbps download limit enforced)  

---

**Decision**: Proceed with six-VLAN architecture (VLANs 10, 20, 30, 50, 60, 99).

**Next Review**: Post-deployment VLAN validation (December 4, 2025).

**Source**: AUP Network Overhaul Blueprint v2.5, Section: "VLAN Architecture & Segmentation"
