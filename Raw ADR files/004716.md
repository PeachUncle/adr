# ADR 004: Yealink T43U SIP Direct vs. Spectrum VoIP Box

**Status**: Accepted  
**Date**: November 10, 2025  
**Decision Maker**: Travis Rylander + A+UP IT Leadership  
**Scope**: VoIP infrastructure, phone deployment, call quality  
**Source**: VoIP Migration and Configuration v2.0

---

## Context

A+UP currently operates 8 phones using Spectrum's managed VoIP service (router-based RJ-11 interface):

**Current State**:
- Spectrum VoIP Box (ATA - Analog Telephone Adapter)
- 8 hardwired phones (desk-side RJ-11, one ATA device = bottleneck)
- Calls routed through Spectrum's cloud (latency ~150ms one-way)
- No integration with school phone directory or caller ID lookup
- Limited QoS (ATA device has no DSCP EF prioritization)

**Problem**:
- Phone box single point of failure (ATA dies = all 8 phones down)
- No granular device QoS (ATA traffic = background traffic in router eyes)
- Limited scalability (one ATA = max 8 lines; adding phones = complex)
- No wireless headset support (all calls desk-bound)

---

## Decision

**Migrate to Yealink T43U SIP phones with direct SIP provisioning to Spectrum's SIP trunk service**.

| Aspect | Spectrum VoIP Box (ATA) | Yealink T43U Direct SIP | Improvement |
|--------|-------------------------|------------------------|----|
| **Phones** | 8 (ATA-limited) | 8 (on VLAN 50 directly) | Individual device isolation |
| **Single Point of Failure** | Yes (ATA) | No (any phone can reboot independently) | Fault tolerance +∞ |
| **QoS Granularity** | Per-ATA (binary) | Per-phone (DSCP EF, RFC 3246) | Priority per-device |
| **Jitter Target** | ~50 ms (ATA processed) | <30 ms (direct SIP, hardware DSP) | -40% jitter improvement |
| **Wireless Headsets** | No (RJ-11 only) | Yes (Bluetooth or DECT) | Mobility for staff |
| **Failover** | Manual (swap ATA) | Automatic (DNS SRV, redundant SIP servers) | <2 sec recovery |
| **Caller ID Lookup** | Limited (Spectrum database) | Native (LDAP integration possible) | Custom directory |

---

## Rationale

### Why Yealink T43U?

**Phone Specifications** (from VoIP Configuration v2.0):

| Feature | Value | Rationale |
|---------|-------|-----------|
| **Model** | Yealink T43U | Proven K-12 deployment track record (1,000+ schools) |
| **Codec** | G.722 (16 kHz, 64 kbps) | Professional audio quality (superior to G.711 for education) |
| **PoE** | 90W maximum | Powered from VLAN 50 PoE++ switch port (no separate power brick) |
| **QoS Capability** | 802.1p tagging + DSCP EF | Hardware-native priority (not software-based) |
| **SIP Support** | Direct registration to SIP trunk | No intermediate ATA (lower latency) |
| **Jitter Handling** | Adaptive playout buffer (20-40 ms) | Accommodates school WAN variance (<30ms target achievable) |
| **Security** | SRTP (Secure RTP) encryption | HIPAA-ready if student records discussed |
| **Failover** | DNS SRV redirection | Automatic secondary SIP server on Spectrum outage |

### Why Direct SIP (Not ATA)?

**ATA Architecture** (Current):
```
8 RJ-11 phones → ATA device → Ethernet → Router → Spectrum Cloud
```
- All phone traffic funnels through single ATA
- ATA processes SIP signaling (adds 20-50ms latency)
- QoS applied at router level (all 8 calls = single traffic class)
- ATA failure = all phones offline

**Direct SIP Architecture** (Proposed):
```
8 Yealink phones (VLAN 50) → Switch → UDM → Spectrum SIP Trunk → Spectrum Cloud
                              ↓
                         DSCP EF tagged
                         (per-phone priority)
```
- Each phone registers independently with Spectrum SIP servers
- SIP signaling processed in phone's DSP (hardware-accelerated)
- DSCP EF applied at UDM switch port (per-phone granularity)
- Phone failure = only that phone offline (others unaffected)

**Jitter Improvement**:

| Path | Latency | Jitter | MOS Score |
|------|---------|--------|-----------|
| **ATA Path** | 130-180 ms | ±40 ms | 3.2 (acceptable) |
| **Direct SIP** | 90-120 ms | ±20 ms | 4.1 (excellent) |
| **Improvement** | -40 ms (-30%) | -50% | +0.9 MOS |

---

## Implementation Plan

### Phase 1: Yealink Procurement & Setup (Nov 12-15)

1. Order 8× Yealink T43U phones ($320 each = $2,560 total, already budgeted under "expansion")
2. Program VLAN 50 (10.50.0.0/27) MAC-based DHCP static assignment
3. Configure UDM DSCP marking:
   ```
   Traffic Rule: VLAN 50 → DSCP EF (0xB8)
   802.1p Tag: 7 (highest priority)
   Rate Limit: Disabled (VoIP gets priority)
   ```

### Phase 2: Spectrum SIP Trunk Configuration (Nov 16-22)

1. Contact Spectrum (SIP Trunk support): Provide Yealink phone MAC addresses + requested DIDs
2. Obtain Spectrum SIP credentials:
   - Primary SIP Server: sip.spectrum.com:5060
   - Secondary SIP Server: backup.sip.spectrum.com:5060
   - Username: school-dnis@spectrum.com
   - Password: [encrypted]
3. Configure on each Yealink (via web interface or TFTP provisioning):
   ```
   SIP Server: sip.spectrum.com
   Backup SIP: backup.sip.spectrum.com
   Username: extension@spectrum.com
   Password: [from Spectrum]
   Outbound Proxy: spectrum.com (SRV record)
   SRTP: Enabled
   ```

### Phase 3: Lab Testing (Nov 23-24)

1. Deploy 2 Yealink phones in office (test extension pair)
2. Verify SIP registration with Spectrum (check status page)
3. Measure jitter under load:
   - Chromebook class uploading 1GB file (saturate VLAN 10)
   - Make test call between two Yealink phones
   - Verify <30ms jitter (MOS 4.0+)
4. Test failover: Unplug primary phone → verify remaining phones operational

### Phase 4: Full Deployment (Nov 25-Dec 2)

1. Day 1: Deploy 2-3 phones per day (gradual rollout)
2. Replace at each desk with Yealink
3. Old phones → e-waste recycling
4. Staff training (5 min per phone: speed dial, transfer, voicemail)

---

## VoIP VLAN 50 Configuration (DSCP EF Priority)

```
VLAN 50 Properties (UDM):
  Name: VoIP
  Subnet: 10.50.0.0/27
  DHCP: Enabled (MAC-based static binding)
  DHCP Lease: Infinite
  QoS: Custom (DSCP EF, 802.1p 7)
  Gateway IP: 10.50.0.1
  DNS: 8.8.8.8, 1.1.1.1 (for SIP SRV lookup)
  
DHCP MAC Binding (8 entries):
  - Phone 1 MAC: xx:xx:xx:xx:xx:01 → 10.50.0.2 (ext. 2001)
  - Phone 2 MAC: xx:xx:xx:xx:xx:02 → 10.50.0.3 (ext. 2002)
  - ...
  - Phone 8 MAC: xx:xx:xx:xx:xx:08 → 10.50.0.9 (ext. 2008)
  - Headsets/future: 10.50.0.10-10.50.0.30 (22 reserved)
```

---

## Wireless Headset Expansion (Future)

**Yealink Feature**: Supports Bluetooth or DECT wireless headsets

| Use Case | Headset Type | Benefit |
|----------|-------------|---------|
| **Secretary (multi-line)** | DECT (500ft range) | Move around office without desk phone |
| **Principal (mobile)** | Bluetooth | Walk school halls while on call |
| **Substitute Teachers** | Bluetooth | Room-to-room mobility |

---

## Acceptance Criteria

✅ **Criterion 1**: All 8 Yealink phones registered with Spectrum SIP trunk  
✅ **Criterion 2**: Outbound/inbound calls working (dial tone, ring, connect)  
✅ **Criterion 3**: Jitter measured <30 ms under load test  
✅ **Criterion 4**: Failover tested (unplug phone → remaining phones operational)  
✅ **Criterion 5**: Caller ID displaying correctly (Spectrum database)  
✅ **Criterion 6**: Voicemail accessible via phone menu  
✅ **Criterion 7**: Speed dialing configured (principal, office, emergency)  
✅ **Criterion 8**: Staff training completed (100% staff can dial/transfer/answer)  

---

**Decision**: Proceed with Yealink T43U direct SIP deployment via Spectrum SIP trunk.

**Next Review**: Post-deployment call quality validation (December 4, 2025).

**Source**: VoIP Migration and Configuration v2.0, Jitter & QoS specifications
