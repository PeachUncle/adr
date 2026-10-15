# ADR 007: TP-Link Camera Island with STP Trunk Alignment

**Status**: Accepted  
**Date**: November 10, 2025  
**Decision Maker**: Travis Rylander (Network Architect)  
**Scope**: Isolated camera switch topology, spanning tree protocol  
**Source**: Additional Considerations Addendum AUP.docx

---

## Context

A+UP facility has additional camera systems (legacy, non-Verkada):

**Current State**:
- TP-Link camera switch in parking lot area (receives fiber uplink from closet)
- 4× additional cameras connected to TP-Link switch
- Isolated island (not connected to main USW-Pro-Max)
- TP-Link runs proprietary firmware (not UniFi-managed)

**Problem**:
- TP-Link switch operates independently → no unified management
- Spanning Tree Protocol (STP) not aligned with main network (potential bridge loops)
- Future expansion difficult (new cameras require TP-Link port expansion)

---

## Decision

**Integrate TP-Link camera island as trunk port on USW-Pro-Max (fiber uplink), align STP priority to prevent loops**.

| Aspect | Before | After | Improvement |
|--------|--------|-------|------------|
| **Management** | Isolated (manual TP-Link) | Trunk port on USW (centralized) | Unified monitoring |
| **VLAN Tagging** | No (flat network) | Tagged trunk (VLAN 60 cameras isolated) | Network segmentation preserved |
| **Spanning Tree** | TP-Link STP separate | Aligned with USW STP priority | No bridge loop risk |
| **Expansion** | Add new TP-Link switch | Add cameras to existing TP-Link | Growth-path clear |

---

## Rationale

### Why Trunk Port Integration?

**Architecture Options**:

#### Option A: Separate Isolated Island (Current)
```
Fiber from closet
    ↓
TP-Link Camera Switch
    ↓
4 cameras
(standalone, no uplink to main network)
```
- ❌ No management from UDM
- ❌ STP not coordinated (bridge loop risk if accidentally connected twice)
- ❌ Hard to expand

#### Option B: Trunk Port on USW-Pro-Max (Recommended)
```
UDM → USW-Pro-Max-48-PoE
         ↓ (Fiber SFP+, VLAN 60 tagged)
    TP-Link Camera Switch
         ↓ (4 cameras, VLAN 60 untagged)
    [4 cameras on Verkada VLAN 60]
```
- ✅ Centralized management (UDM sees trunk port stats)
- ✅ VLAN 60 tagged on trunk (cameras inherit VLAN isolation)
- ✅ STP aligned with main USW (no bridge loop risk)
- ✅ Expansion simple (add more cameras to TP-Link, all VLAN 60)

**Selected**: **Option B - Trunk Port** (unified management + STP safety)

### STP Alignment (Bridge Loop Prevention)

**Spanning Tree Basics**:
- STP prevents bridge loops (redundant paths create forwarding loops)
- Each switch has priority (lower = more likely root bridge)
- If two switches claim bridgeship, frames loop forever

**USW-Pro-Max STP Settings**:
```
Bridge Priority: 4096 (low number = more likely root)
  → Ensures USW is always STP root
  
TP-Link Switch Config (via web UI):
  Spanning Tree: Enabled
  Priority: 28672 (higher than USW)
  → Ensures TP-Link is never root
  → Prevents fighting for STP control
```

**Result**: Fiber trunk link between USW ↔ TP-Link is transparent (no loop interference).

---

## Implementation Plan

### Phase 1: TP-Link Configuration (Nov 20-21)

1. Access TP-Link camera switch web interface (default 192.168.1.1)
2. Enable Spanning Tree Protocol:
   ```
   Configuration > Advanced > STP
     Enable: Yes
     Mode: RSTP (Rapid Spanning Tree)
     Bridge Priority: 28672 (higher than USW 4096)
     Port Cost: Default
   ```
3. Verify STP enabled and stable (no topology changes)

### Phase 2: Fiber Uplink Connection (Nov 22)

1. From UDM/USW central closet:
   - Identify unused fiber port on USW (SFP+ slot)
   - Connect LC fiber uplink to TP-Link camera switch
   - Turn on port (enable via UDM dashboard)

2. UDM Dashboard Configuration:
   ```
   Ports > SFP+ (fiber uplink to TP-Link)
     VLAN Mode: Trunk
     Tagged VLANs: 60 (cameras)
     Description: "TP-Link Camera Island"
   ```

3. **Port Configuration for Trunk**:
   ```
   Uplink from USW to TP-Link:
     Tagged: VLAN 60 (cameras)
     Untagged: None
     Priority: Normal
   ```

4. **TP-Link Trunk Reception**:
   - TP-Link receives VLAN 60 tagged frames
   - TP-Link internal ports (to cameras): Untagged, VLAN 60 only
   - Result: Cameras appear as if connected directly to VLAN 60

### Phase 3: Port Mapping

| Port | Device | VLAN | Purpose |
|------|--------|------|---------|
| USW SFP+ slot 2 | Fiber uplink to TP-Link | 60 (tagged trunk) | Camera island connection |
| TP-Link Ports 1-4 | 4× legacy cameras | 60 (untagged) | Camera connectivity |
| TP-Link Port 5 | Fiber uplink (back to USW) | 60 (tagged trunk) | Trunk reception |

### Phase 4: Verification (Nov 23)

1. **STP Status**:
   - UDM dashboard: Verify STP root is USW (4096 priority)
   - TP-Link dashboard: Verify STP designated bridge is USW (TP-Link is non-root)
   - No STP topology changes logged (stable)

2. **VLAN Tagging**:
   - Cameras get 10.60.0.x IPs (via DHCP on VLAN 60)
   - UDM firewall: Verify VLAN 60 rules apply to legacy cameras too
   - Verify firewall rule allows cameras → Verkada cloud (HTTPS 443)

3. **Connectivity**:
   - Ping from UDM: 10.60.0.100 (test camera IP)
   - Verify cameras can reach Verkada cloud (DNS resolution + HTTPS)

---

## Acceptance Criteria

✅ **Criterion 1**: TP-Link STP enabled and aligned (priority > USW)  
✅ **Criterion 2**: Fiber trunk port active on USW and TP-Link  
✅ **Criterion 3**: VLAN 60 tagged on trunk (untagged on TP-Link ports)  
✅ **Criterion 4**: 4 legacy cameras obtain VLAN 60 IPs (10.60.0.x via DHCP)  
✅ **Criterion 5**: No STP topology changes or loop warnings (stable topology)  
✅ **Criterion 6**: Cameras can reach Verkada cloud (HTTPS 443 allowed by firewall)  
✅ **Criterion 7**: UDM dashboard shows TP-Link port utilization (for monitoring)  
✅ **Criterion 8**: Legacy cameras visible in monitoring dashboard (unified with Verkada)  

---

**Decision**: Proceed with TP-Link camera island integration as trunk port on USW with STP alignment.

**Next Review**: Post-deployment STP topology validation (December 4, 2025).

**Source**: Additional Considerations Addendum AUP.docx, Network Architecture STP specifications
