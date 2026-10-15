# ADR-012: Google Workspace SSO (Future Enhancement)

**Status:** Proposed (Not Phase 1)  
**Date:** 2025-12-05  
**T3-ETERNAL Impact:** Secrets (Carter) — Future identity management  
**Timeline:** Q2 2026 (after Phase 1 stabilization)

---

## Context

Current **Student-WiFi** SSID uses **WPA2-PSK** (pre-shared key) for authentication. While functional, this approach has limitations:

### Current State (WPA2-PSK)

✅ **Pros:**
   - Simple deployment (single passphrase)
   - No infrastructure required (no RADIUS server)
   - Chromebook-compatible (all models)

⚠️ **Cons:**
   - No per-user accountability (all students share passphrase)
   - Password rotation requires re-configuring 150+ devices
   - Cannot revoke individual student access
   - No audit trail (who connected when)

---

## Decision

**Phase 1 (Current):** Continue with WPA2-PSK for initial deployment  
**Phase 2 (Future):** Implement 802.1X with Google Workspace LDAP + RADIUS

### Why Not Phase 1?

1. **Deployment complexity:** RADIUS setup adds 4-8 hours implementation time
2. **Risk management:** Focus Phase 1 on core network stability
3. **Chromebook compatibility:** Older models (AUE <2026) may not support EAP-PEAP
4. **Support burden:** 802.1X credential issues = "WiFi down" for students

### Why Phase 2?

1. **Per-user authentication:** student@aplusup.org credentials
2. **Automatic credential rotation:** Synced with Google Workspace
3. **Audit trail:** Track which student connected to which AP
4. **Revocation:** Unenroll device → WiFi access revoked immediately

---

## Implementation Plan (Future)

### Prerequisites

- **Google Workspace Enterprise license** (required for Secure LDAP)
- **Ubuntu 24.04 LXC container** on VLAN 50 (10.50.0.5)
- **FreeRADIUS 3.2+** with Google LDAP backend
- **4-8 hours implementation time**

### Architecture

```
Chromebook (802.1X EAP-PEAP)
    ↓ student@aplusup.org credentials
UniFi AP (RADIUS client)
    ↓ authentication request
FreeRADIUS (10.50.0.5)
    ↓ LDAP bind
Google Secure LDAP (ldaps://ldap.google.com)
    ↓ authentication result
FreeRADIUS → AP → Chromebook: Access-Accept/Reject
```

### Steps

```bash
# 1. Deploy FreeRADIUS on Ubuntu LXC
lxc launch ubuntu:24.04 radius-server
lxc exec radius-server -- apt install freeradius freeradius-ldap

# 2. Configure Google Secure LDAP
# Google Admin Console → Security → API Controls → LDAP
#   - Enable Secure LDAP
#   - Download certificate
#   - Generate LDAP credentials

# 3. Point FreeRADIUS to Google LDAP backend
# /etc/freeradius/3.0/mods-available/ldap
ldap {
  server = "ldaps://ldap.google.com:636"
  identity = "cn=radius,ou=System"
  password = "<google-ldap-password>"
  base_dn = "dc=aplusup,dc=org"
  user {
    filter = "(uid=%{%{Stripped-User-Name}:-%{User-Name}})"
  }
}

# 4. Configure UniFi RADIUS settings (Student-WiFi SSID)
# UniFi UI → Settings → WiFi → Student-WiFi
#   Security: WPA2-Enterprise
#   RADIUS Profile: radius-server (10.50.0.5:1812)
#   RADIUS Secret: <shared-secret>

# 5. Deploy 802.1X certificates to Chromebooks
# Google Admin Console → Devices → Chrome → Settings
#   WiFi Networks → Add Network:
#     - SSID: Student-WiFi
#     - Security: WPA2-Enterprise (EAP-PEAP)
#     - Identity: ${DEVICE_USER}@aplusup.org
#     - Password: ${DEVICE_USER_PASSWORD}
#     - CA Certificate: google-ldap-ca.pem

# 6. Pilot with 10 devices, then full rollout
```

---

## Benefits (Phase 2)

✅ **Per-user authentication**
   - Each student uses student@aplusup.org credentials
   - No shared passphrase to rotate

✅ **Automatic credential rotation**
   - Synced with Google Workspace password changes
   - No manual re-configuration of devices

✅ **Audit trail**
   - FreeRADIUS logs: Who connected when
   - Per-student bandwidth tracking
   - Incident response: Identify specific student

✅ **Revocation on unenrollment**
   - Device removed from Google Admin Console
   - RADIUS authentication fails immediately
   - No WiFi access for unenrolled devices

---

## Risks (Phase 2)

⚠️ **Complexity**
   - RADIUS server management (FreeRADIUS, LDAP integration)
   - Debugging: "WiFi won't connect" = RADIUS logs required
   - Backup/HA: Single RADIUS server = single point of failure

⚠️ **Chromebook compatibility**
   - Older Chromebooks (AUE <2026) may not support EAP-PEAP
   - Chrome OS version: 89+ required for stable 802.1X
   - Test with pilot devices before full rollout

⚠️ **Support burden**
   - Password reset = "WiFi down" for student
   - RADIUS timeout = "WiFi authentication failed" error
   - Increased helpdesk tickets during initial rollout

⚠️ **Dependency on Google Secure LDAP**
   - Requires Google Workspace Enterprise license (~$20/user/month)
   - LDAP downtime = no student WiFi authentication
   - Must monitor Google LDAP service status

---

## Current Status (Phase 1)

### Student-WiFi SSID (WPA2-PSK)

```json
{
  "name": "Student-WiFi",
  "security": "wpapsk",
  "passphrase": "${WIFI_PASSWORD_STUDENTS}",
  "network_id": "VLAN10",
  "note": "WPA2-PSK for Phase 1 simplicity. Phase 2: 802.1X with Google Workspace SSO."
}
```

**Status:** ✅ Functional, deployed to 150+ Chromebooks

---

## Phase 2 Decision Criteria

Proceed with 802.1X deployment when:

1. ✅ **Phase 1 stable:** 30 days uptime with no major incidents
2. ✅ **Chromebook fleet refresh:** All devices AUE 2026+ (802.1X compatible)
3. ✅ **Google Workspace Enterprise:** License procured
4. ✅ **FreeRADIUS expertise:** Staff trained or consultant engaged
5. ✅ **Pilot validation:** 10 devices tested for 2 weeks without issues

**Estimated Timeline:** Q2 2026 (April-June)

---

## Alternatives Considered

### Option 1: Continue with WPA2-PSK (Current State)

**Pros:** Simple, no RADIUS overhead  
**Cons:** No per-user accountability, shared passphrase  
**Decision:** ✅ Phase 1 only — Not long-term solution

### Option 2: Captive Portal (Rejected)

**Pros:** No RADIUS, web-based authentication  
**Cons:** Requires open SSID (security risk), Chromebook compatibility issues  
**Decision:** ❌ Rejected — Less secure than WPA2-PSK

### Option 3: 802.1X with Google Workspace SSO (Selected for Phase 2)

**Pros:** Per-user authentication, audit trail, automatic credential sync  
**Cons:** RADIUS complexity, support burden  
**Decision:** ✅ Selected for Phase 2 — Best long-term solution

### Option 4: 802.1X with Local RADIUS (Rejected)

**Pros:** No dependency on Google Secure LDAP  
**Cons:** Manual user database management, no Google Workspace integration  
**Decision:** ❌ Rejected — Duplicates Google Workspace user management

---

## Validation (When Implemented)

```bash
# Test RADIUS authentication
radtest student@aplusup.org password 10.50.0.5 0 testing123
# Should return: Access-Accept

# Monitor RADIUS logs
tail -f /var/log/freeradius/radius.log
# Should show: Login OK: [student@aplusup.org] (from client udm-ap port 0)

# Test revocation
# 1. Unenroll Chromebook from Google Admin Console
# 2. Attempt WiFi connection from device
# 3. Should fail: Access-Reject (user not found in LDAP)

# Audit trail
grep "Login OK" /var/log/freeradius/radius.log | tail -100
# Should list: Timestamp, username, AP MAC, result
```

---

## References

- **Google Secure LDAP:** https://support.google.com/a/answer/9048516
- **FreeRADIUS + Google LDAP:** https://wiki.freeradius.org/guide/Google-LDAP
- **802.1X on Chromebooks:** https://support.google.com/chrome/a/answer/2634553
- **SSID Config (Phase 1):** `config/unifi/ssids.json`

---

## Timeline

- **2025-11-12:** Phase 1 deployed (WPA2-PSK)
- **2025-12-05:** Phase 1 stable, 30 days uptime
- **2026-Q2 (Planned):** Phase 2 Google Workspace SSO deployment

---

## Success Metrics (Phase 2)

When implemented:

✅ **100% Chromebooks** authenticate with student@aplusup.org credentials  
✅ **Per-user audit trail** for all WiFi connections  
✅ **Zero shared passphrases** (all credentials individual)  
✅ **Automatic revocation** on device unenrollment  
✅ **<5% helpdesk tickets** related to WiFi authentication (target after 90 days)

**Status:** Future work — Phase 1 (WPA2-PSK) sufficient for initial deployment.
