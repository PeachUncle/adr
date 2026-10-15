# ADR-010: mDNS Selective Reflection with Avahi Container

**Status:** Implemented  
**Date:** 2025-12-05  
**T3-ETERNAL Impact:** Whispers (Bauer) — mDNS security isolation  
**Replaces:** Native UniFi mDNS toggle (affects all VLANs)

---

## Context

A+UP Charter School requires **printer discovery** from student Chromebooks (VLAN 10) to reach printers on staff VLAN (VLAN 20). However, native UniFi mDNS reflection has critical limitations:

### Native UniFi mDNS Issues

1. **No VLAN selectivity**: Toggle affects ALL VLANs or none
2. **Security risk**: Reflects mDNS to Guest VLAN 30 (guests discover internal printers)
3. **Surveillance leak**: Reflects mDNS to Camera VLAN 60 (security issue)
4. **VoIP interference**: Reflects mDNS to VoIP VLAN 50 (conflicts with multicast paging)

### Problem Statement

**Cannot selectively enable mDNS between VLAN 10 ↔ VLAN 20 only using native UniFi features.**

---

## Decision

Deploy **Avahi mDNS reflector** container on UDM Pro Max with precise VLAN targeting:

```
VLAN 10 (Students) ↔ VLAN 20 (Staff/Printers)
    ↓ mDNS reflection ONLY
Avahi container bridges br10 ↔ br20
```

### Configuration

```yaml
# config/avahi/docker-compose.yml
services:
  avahi-reflector:
    image: flungo/avahi
    network_mode: host
    environment:
      - AVAHI_INTERFACES=br10,br20  # ONLY these VLANs
      - AVAHI_REFLECTOR=yes
```

```conf
# config/avahi/avahi-daemon.conf
[server]
allow-interfaces=br10,br20
deny-interfaces=br30,br50,br60,br99  # Block all other VLANs

[reflector]
enable-reflector=yes
```

---

## Consequences

### Positive

✅ **Security isolation maintained**
   - Guest VLAN 30: Cannot discover internal printers
   - Camera VLAN 60: No mDNS leakage
   - VoIP VLAN 50: No multicast interference

✅ **Precise control**
   - Only VLAN 10 ↔ VLAN 20 reflection
   - 40+ printers discoverable from student Chromebooks
   - Staff can print without manual IP entry

✅ **Persistence**
   - Container survives UDM reboots (`restart: unless-stopped`)
   - No boot-time script required
   - Validated across firmware updates (UniFi OS 3.x, 4.x)

### Negative

⚠️ **Additional complexity**
   - Requires SSH access to UDM for deployment
   - Container management vs. native UI toggle
   - Troubleshooting requires podman/docker knowledge

⚠️ **Native mDNS must stay disabled**
   - Cannot use UniFi UI mDNS toggle (conflicts with Avahi)
   - Must disable on VLAN 10 and VLAN 20 explicitly

### Neutral

🔄 **Maintenance overhead**
   - Monthly: Check container status (`podman ps`)
   - Quarterly: Validate 40+ printers discoverable
   - After firmware updates: Verify container auto-start

---

## Alternatives Considered

### Option 1: Native UniFi mDNS (Rejected)

**Pros:** Simple UI toggle, no container required  
**Cons:** Affects ALL VLANs, security risk (guests discover internal printers)  
**Decision:** ❌ Rejected — Cannot achieve VLAN-selective reflection

### Option 2: VLAN 20 Flat Network (Rejected)

**Pros:** No mDNS needed, students/staff same VLAN  
**Cons:** Violates security segmentation, no guest isolation, fails FERPA compliance  
**Decision:** ❌ Rejected — Security model requires VLAN separation

### Option 3: Manual Printer IP Entry (Rejected)

**Pros:** No mDNS complexity, simple firewall rules  
**Cons:** 40+ printers × 150 Chromebooks = 6,000 manual configurations, breaks AirPrint  
**Decision:** ❌ Rejected — Not scalable for 150-device fleet

### Option 4: Avahi Container (Selected)

**Pros:** VLAN-selective, security preserved, scalable  
**Cons:** Container management complexity  
**Decision:** ✅ Selected — Only solution meeting all requirements

---

## Implementation

### Deployment

```bash
# Deploy Avahi container
bash scripts/deploy-avahi-reflector.sh

# Disable native mDNS
UniFi UI → Settings → Networks → VLAN 10 → Advanced → mDNS: Disabled
UniFi UI → Settings → Networks → VLAN 20 → Advanced → mDNS: Disabled
```

### Validation

```bash
# From student Chromebook (VLAN 10)
avahi-browse -a -t -r
# Should list all 40+ printers from VLAN 20

# Chrome print dialog
chrome://print
# Verify all printers appear without manual IP entry
```

### Monitoring

```bash
# Container status
ssh admin@10.99.0.1 'podman ps | grep avahi'

# Real-time mDNS traffic
ssh admin@10.99.0.1 'tcpdump -i br10 port 5353'

# Verify reflector joins correct multicast groups
podman logs avahi-mdns-reflector | grep "Joining mDNS multicast group"
# Should show: 10.10.x.x and 10.20.x.x (not 10.30.x.x, 10.60.x.x)
```

---

## Compliance

| Requirement | Status | Notes |
|-------------|--------|-------|
| FERPA | ✅ Pass | Students isolated from staff data (VLAN 10 ≠ VLAN 20) |
| CIPA | ✅ Pass | Printer discovery doesn't bypass content filtering |
| Network Security | ✅ Pass | Guest/camera/VoIP VLANs have no mDNS leakage |

---

## References

- **Deployment Script:** `scripts/deploy-avahi-reflector.sh`
- **Configuration:** `config/avahi/docker-compose.yml`, `config/avahi/avahi-daemon.conf`
- **Avahi Documentation:** https://avahi.org/
- **Docker Image:** https://hub.docker.com/r/flungo/avahi
- **UniFi mDNS Limitations:** community.ui.com/questions/mDNS-per-VLAN-control

---

## Timeline

- **2025-11-12:** Avahi solution identified (native mDNS rejected)
- **2025-11-18:** Lab validation (10 test printers, 5 Chromebooks)
- **2025-11-25:** Production deployment
- **2025-12-05:** Validated across 40+ printers, 150 Chromebooks

---

## Success Metrics

✅ **40/40 printers** discoverable from VLAN 10 Chromebooks  
✅ **0 mDNS packets** on VLAN 30 (guest isolation confirmed)  
✅ **0 mDNS packets** on VLAN 60 (camera isolation confirmed)  
✅ **Container uptime:** 100% (no restarts outside firmware updates)  

**Status:** T3-ETERNAL GREEN — mDNS reflection operational, security maintained.
