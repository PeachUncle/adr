# ADR-015: Closed Network Security Posture

**Status:** Accepted
**Date:** 2024-10
**Updated:** 2025-11-11
**Deciders:** Development Team, Security Reviewer
**Related Issues:** N/A (design decision)
**Related Views:** `view-security-reliability.md`, `view-deployment.md`

---

## Context

DPM-V2 handles camera control on UAV platform. Security considerations:

1. **Network Exposure:** Is system internet-accessible?
2. **Authentication:** Do we need login/passwords?
3. **Encryption:** Do we need TLS/DTLS?
4. **Attack Surface:** What are the threats?

**Operational Environment:**
- Production: R16 wireless link (closed network, Air ↔ Ground only)
- Development: WiFi (closed lab network, no internet routing)
- No remote access from internet
- Physical security: UAV platform, handheld H16 tablet

---

## Decision

**Security Posture: Minimal Security (Development Phase)**

**Current Implementation:**
- ❌ No authentication (no login/password/API keys)
- ❌ No encryption (JSON plaintext over TCP/UDP)
- ❌ No authorization (all commands accepted)
- ✅ Closed network (R16 link not internet-routed)
- ✅ Physical security (UAV/tablet in operator control)

**Rationale:**
- Development/testing phase (not production deployment yet)
- Closed network environment (R16 link isolated)
- Physical access control (operator-controlled devices)
- Complexity vs. threat trade-off (focus on functionality first)

**Future Production Requirements:**
- TLS for TCP command channel
- HMAC signatures for commands
- Certificate-based mutual auth

---

## Threat Model

### Threat 1: Network Eavesdropping

**Threat:** Attacker intercepts wireless traffic, reads camera commands

**Likelihood:** LOW (R16 link encrypted at physical layer, WiFi WPA2)

**Impact:** LOW (camera commands not sensitive - ISO, shutter speed public knowledge)

**Mitigation (Current):** Physical-layer encryption (R16, WPA2)

**Mitigation (Future):** TLS on TCP, DTLS on UDP

---

### Threat 2: Command Injection

**Threat:** Attacker sends malicious commands to Air-Side

**Likelihood:** LOW (must be on same closed network)

**Impact:** MEDIUM (could disrupt camera operation, not damage hardware)

**Mitigation (Current):** PropertyLoader validation prevents invalid commands

**Mitigation (Future):** HMAC signature verification

---

### Threat 3: Denial of Service

**Threat:** Attacker floods Air-Side with requests

**Likelihood:** LOW (closed network)

**Impact:** MEDIUM (Air-Side becomes unresponsive)

**Mitigation (Current):** None (rely on physical network isolation)

**Mitigation (Future):** Rate limiting, connection limits

---

### Threat 4: Physical Device Access

**Threat:** Attacker gains physical access to Pi 5 or H16

**Likelihood:** VERY LOW (devices in operator possession)

**Impact:** HIGH (full system compromise)

**Mitigation:** Physical security (operator control), SSH key-only auth

---

## Alternatives Considered

### Alternative 1: Full Security from Day 1

**Approach:** Implement TLS, authentication, authorization in MVP

**Pros:**
- Secure by default
- No retrofitting later

**Cons:**
- ❌ **Development Slowdown:** SSL cert management, key distribution
- ❌ **Debugging Difficulty:** Can't inspect encrypted traffic with Wireshark
- ❌ **Complexity:** Authentication state management, token refresh
- ❌ **Premature:** Threat model doesn't justify full security yet

**Rejection:** Focus on functionality first, security when deploying to production

---

### Alternative 2: Basic Authentication (Username/Password)

**Approach:** Add HTTP Basic Auth to TCP commands

**Pros:**
- Simple to implement
- Industry standard

**Cons:**
- ⚠️ **Plaintext Credentials:** Without TLS, username/password sent in clear
- ⚠️ **False Security:** Gives illusion of security without real protection
- ⚠️ **User Management:** Must store/sync passwords

**Rejection:** Without encryption, Basic Auth provides minimal security. If we add encryption, use client certificates (stronger).

---

### Alternative 3: VPN Tunnel

**Approach:** Run all traffic through VPN (WireGuard, OpenVPN)

**Pros:**
- Network-level encryption (all traffic protected)
- Mature technology

**Cons:**
- ⚠️ **Latency:** VPN adds ~10-20ms latency (significant for real-time camera control)
- ⚠️ **Complexity:** VPN server setup, key distribution, routing
- ⚠️ **R16 Link:** May not support VPN passthrough

**Rejection:** R16 link already encrypted at physical layer. Adding VPN adds latency without significant security gain.

---

## Consequences

### Positive

✅ **Fast Development:** No security overhead during development
✅ **Easy Debugging:** Wireshark shows plaintext JSON (easy to troubleshoot)
✅ **No Key Management:** No SSL certs, no auth tokens to distribute
✅ **Simple Deployment:** One command (`docker run`), no config files

### Negative

⚠️ **Not Production-Ready:** Cannot deploy to untrusted networks
⚠️ **Security Debt:** Must add security before production (planned Phase 2)
⚠️ **Risk of Complacency:** Easy to forget security and ship insecure

**Mitigation:** Document clearly in README: "NOT FOR PRODUCTION USE WITHOUT SECURITY ENHANCEMENTS"

---

## Future Security Roadmap (Phase 2)

**Phase 2 Security Enhancements (Not Yet Implemented):**

1. **TLS for TCP Command Channel**
   - Client certificate authentication (Ground ↔ Air)
   - Mutual TLS (both sides verify each other)
   - Self-signed certs (no CA required for closed network)

2. **HMAC Signatures for Commands**
   - Shared secret between Ground and Air
   - Each command signed with HMAC-SHA256
   - Air-Side verifies signature before executing

3. **Rate Limiting**
   - Max 10 commands per second per client
   - Prevents DoS attacks

4. **SSH Key-Only Auth for Air-Side**
   - Disable SSH password authentication
   - Require key-based auth (already implemented)

5. **Audit Logging**
   - Log all commands with timestamp and source IP
   - Detect suspicious activity

---

## Security Checklist (Production Deployment)

**Before deploying to production:**
- [ ] Enable TLS on TCP port 5000
- [ ] Distribute client certificates to Ground-Side
- [ ] Implement HMAC signature verification
- [ ] Enable rate limiting (10 req/sec)
- [ ] Disable SSH password auth (keys only)
- [ ] Review audit logs for anomalies
- [ ] Penetration test on R16 network
- [ ] Document security model in ops manual

---

## Related Decisions

- **ADR-003:** TCP/UDP Protocol Split (plaintext JSON over TCP/UDP)
- **ADR-004:** Docker Containerization (isolation limits attack surface)
- **ADR-011:** JSON Protocol (plaintext, not encrypted)

---

## References

- Security & Reliability View: `view-security-reliability.md` (Full security section)
- Deployment View: `view-deployment.md` (Network topology)
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
