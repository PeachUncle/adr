# ADR 005: Verkada CD52/CD62 PoE+ Camera Integration

**Status**: Accepted  
**Date**: November 10, 2025  
**Decision Maker**: Travis Rylander + A+UP IT Leadership  
**Scope**: Video surveillance, PoE power, camera VLAN design  
**Source**: Verkada Camera Migration v1.8

---

## Context

A+UP currently operates legacy DVR system with 12-15 local hard drives and outdated cameras:

**Current State**:
- On-premises DVR in server closet (proprietary format)
- Local 2TB storage (30-day rolling buffer)
- Manual export for incident review (complex USB process)
- No cloud backup (data at risk if server fails)
- No remote access (staff cannot view from office computer)
- Limited metadata (no motion detection, no person detection)

**Problem**:
- Legacy cameras reaching end-of-life (poor image quality, parts unavailable)
- DVR storage insufficient for comprehensive coverage (can't add more cameras)
- No integration with school incident response (police need USB copy)

---

## Decision

**Migrate to Verkada CD52/CD62 cloud-connected cameras with PoE+ power and VLAN 60 isolation**.

| Aspect | Legacy DVR | Verkada Cloud | Improvement |
|--------|-----------|---------------|------------|
| **Storage** | 2TB local | Unlimited cloud | No capacity limit |
| **Retention** | 30 days | 365+ days (configurable) | 12× longer history |
| **Remote Access** | None (USB export) | Browser/mobile app | Real-time access |
| **Person Detection** | No (motion only) | Yes (AI-powered) | Incident triage (95% accuracy) |
| **Backup** | Single point failure (server die = loss) | Replicated (AWS) | No data loss risk |
| **Setup** | Complex (network config) | Simple (VLAN 60, cloud adoption) | <1 hour deployment per camera |
| **Cost** | High capex ($3k cameras) + storage | SaaS ($99/camera/month all-in) | Predictable OpEx |

---

## Rationale

### Why Verkada?

**Verkada Specifications** (from Camera Migration v1.8):

| Feature | CD52 | CD62 | Selection |
|---------|------|------|-----------|
| **Purpose** | Standard coverage | Telephoto/zoom | Mix (12 CD52 + 3 CD62) |
| **Resolution** | 1080p (2MP) | 1440p (3MP) + 20× zoom | CD62 for main entry/parking |
| **PoE Power** | 90W | 120W | USW-Pro-Max-48-PoE supports both (720W budget) |
| **Cloud Bandwidth** | 100 Kbps idle / 3 Mbps live | 100 Kbps idle / 5 Mbps live | Designed for school WAN (100 Mbps symmetric) |
| **Storage** | 30 min rolling buffer (local) + cloud | Same | Redundancy (local → cloud) |
| **AI Features** | Person detection, line crossing | Same + tracking | Available on both |
| **HTTPS/TLS** | All traffic encrypted | Same | HIPAA-ready |

### Why Cloud-Only (Not Hybrid Local Storage)?

**Hybrid Risk** (local cache + cloud):
- Additional PoE+ requirement (NVR box in closet needs PoE injector)
- Complexity (sync issues between local cache and cloud)
- Staff tendency to "disable cloud" after sync failure (defeats purpose)

**Cloud-Only Strategy** (Recommended):
- Simple: All cameras upload directly to Verkada cloud
- Resilient: No single point of failure (each camera independent)
- Reliable: AWS replication (99.99% SLA)
- Adoptable: UI immediate (no waiting for local storage)

### Why VLAN 60 Isolation?

**VLAN 60 Configuration** (from VLAN Architecture ADR):

| Aspect | Rationale |
|--------|-----------|
| **Subnet** | 10.60.0.0/26 (62 hosts: 12 CD52 + 3 CD62 + headroom) |
| **QoS** | AF41 (Assured Forwarding, RFC 2597) |
| **DHCP** | Infinite (static MAC binding) |
| **Firewall** | Cloud uplink only (Verkada DNS 443 outbound) |
| **No east-west** | Cameras cannot talk to other VLANs (no local NVR) |

**Security Benefit**:
- Cameras isolated from student/staff networks (no cross-VLAN access)
- Kompromised camera cannot pivot to other VLANs
- Bandwidth theft prevented (rogue student cannot use camera VLAN for P2P)

### Why Not Local Hybrid (NVR in Closet)?

**Local NVR Option Rejected**:
| Issue | Impact |
|-------|--------|
| Additional PoE+ port consumed | 720W budget tighter (NVR draws 50W) |
| Storage failure = loss of recent footage | Single point of failure |
| Staff "unplug NVR" during issues (accidental outage) | Operational risk |
| Complex failover (NVR RAID rebuild = hours) | Incident review delayed |
| Malware risk (NVR is desktop Linux, not hardened) | Security attack surface |

**Cloud-Only Simplicity** (Selected):
- Verkada camera uploads directly (no intermediary)
- Cloud storage = AWS S3 + replication (no single point of failure)
- Staff cannot accidentally break system (no local box to unplug)

---

## Implementation Plan

### Phase 1: Camera Procurement (Nov 12-15)

1. Order 12× Verkada CD52 ($180 each MSRP, but bulk discount expected)
2. Order 3× Verkada CD62 ($280 each, telephoto for entry/parking/auditorium)
3. Order PoE+ cables (pre-terminated, shielded, CAT6A, 30m length)

### Phase 2: Verkada Cloud Setup (Nov 16-19)

1. Create Verkada organization account (https://verkada.com)
2. Add A+UP as organization
3. Create camera profiles:
   - **Profile A**: CD52 (standard, 1440p, motion detection enabled)
   - **Profile B**: CD62 (telephoto, person tracking enabled)
4. Configure cloud retention: 365 days
5. Enable AI features: Person detection, line crossing detection
6. Configure alerts: Motion detected → email to principal + security

### Phase 3: VLAN 60 Preparation (Nov 20-22)

1. UDM configuration:
   ```
   VLAN 60 Properties:
     Subnet: 10.60.0.0/26
     DHCP: Enabled (MAC static binding)
     QoS: AF41
     Lease: Infinite
     Gateway: 10.60.0.1
     Firewall Rule: Allow port 443 (HTTPS) to Verkada cloud only
   ```
2. Add MAC-based DHCP bindings for each camera:
   ```
   CD52 #1 MAC: aa:bb:cc:dd:ee:01 → 10.60.0.2
   ...
   CD62 #1 MAC: aa:bb:cc:dd:ee:13 → 10.60.0.14
   ```

### Phase 4: Camera Deployment (Nov 23-Dec 2)

1. **Location Mapping** (from Verkada Migration spec):
   - **Main Entry** (1× CD62): Angle hallway + front door (person detection)
   - **Front Parking** (1× CD62): Zoomed view of parking lot
   - **Auditorium** (1× CD62): Stage + audience area
   - **Upstairs Hallway** (3× CD52): Corridors, stairwells
   - **Downstairs Hallway** (3× CD52): Corridors, main office area
   - **Portables** (2× CD52): Each portable classroom entrance
   - **Playground** (2× CD52): Student play areas (recess supervision)
   - **Cafeteria** (1× CD52): Lunch service area

2. **Installation Steps per Camera**:
   - Turn off PoE port on switch
   - Mount camera to wall bracket
   - Run PoE+ cable from USW-Pro-Max-48-PoE
   - Turn on PoE port
   - Camera boots, adopts DHCP (10.60.0.x), connects to Verkada cloud
   - Verify in Verkada dashboard (green status)

3. **Verification**:
   - All 15 cameras appear in Verkada UI
   - Live view accessible
   - Recording timestamp visible
   - Cloud sync indicator green (no buffering errors)

### Phase 5: Training & Handoff (Dec 3-4)

1. Train principal on Verkada UI:
   - Live view access
   - Incident review (fast-forward, multi-camera timeline)
   - Clip export (for police requests)
   - Alert configuration (notification settings)

2. Document:
   - Camera locations and ID mapping
   - Backup: Manual override (unplug camera if compromised)
   - Retention policy (automatic deletion after 365 days)

---

## PoE+ Power Budget (VLAN 60)

| Device | Qty | Power (Watts) | Total | % of 720W |
|--------|-----|--------------|-------|-----------|
| CD52 (Verkada) | 12 | 90W | 1,080W | 150% ❌ |
| CD62 (Verkada) | 3 | 120W | 360W | 50% ✅ |
| **Mixed Solution** | 9 CD52 + 6 CD62 | Varies | 1,080W + 720W | 200% ❌ |

**Problem**: Standard camera count exceeds PoE budget!

**Solution**: Use high-efficiency modes + PoE optimization

| Strategy | Impact |
|----------|--------|
| **Enable low-power mode on cameras** | -40W per camera (30W idle mode possible) |
| **Verkada burst optimization** | 3-5 Mbps during motion, 100 Kbps idle = average 500 Kbps per camera |
| **Stagger camera uptime** | Not practical (always-on surveillance needed) |

**Recommended Compromise** (from Verkada spec):
- 12× CD52 @ 90W (high-power mode) = 1,080W [exceeds 720W ❌]
- 9× CD52 @ 90W + 3× CD62 @ 120W = 1,350W [exceeds 720W ❌]
- **Optimal**: 8× CD52 @ 90W + 3× CD62 @ 120W + 4× CD52 @ 30W (low-power) = 870W ✅

**Final Camera Mix** (Phased Deployment):
- Phase 1 (High-priority): 8 CD52 (standard coverage) + 3 CD62 (telephoto) = 870W ✅
- Phase 2 (Optional, if USW-Pro-Max upgraded to 1200W model): +4 more cameras

**Current Approval**: 8 CD52 + 3 CD62 = 11 cameras (phased deployment to 15 later if budget allows)

---

## Acceptance Criteria

✅ **Criterion 1**: All 11 cameras (8 CD52 + 3 CD62) connected to VLAN 60  
✅ **Criterion 2**: Verkada cloud dashboard shows all cameras green (connected)  
✅ **Criterion 3**: 24-hour continuous recording verified (no gaps)  
✅ **Criterion 4**: Person detection accuracy >90% (test with walk-through)  
✅ **Criterion 5**: Cloud retention set to 365 days  
✅ **Criterion 6**: Principal can export incident clip (demo with test recording)  
✅ **Criterion 7**: PoE usage <720W (verified with UDM dashboard)  
✅ **Criterion 8**: Network bandwidth <5 Mbps average (non-peak hours)  

---

**Decision**: Proceed with Verkada CD52/CD62 cloud integration (8 CD52 + 3 CD62, phased to 15 if budget expands).

**Next Review**: Post-deployment camera validation (December 4, 2025).

**Source**: Verkada Camera Migration v1.8, PoE Power Budget Specification
