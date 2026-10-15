# ADR-002: PHI Rings and Data Minimization

**Status:** Accepted
**Date:** 2025-10-24
**Deciders:** Engineering Team, Compliance
**Context:** HIPAA compliance, local compute policy

---

## Context and Problem Statement

Vantage processes **Protected Health Information (PHI)** including:
- Raw imaging (VIS photos, retinal OCT, DEXA scans)
- Identifiers (name, DOB, SSN)
- Derived biomarkers (visceral fat %, retinal layer thickness)

HIPAA requires:
- **Minimum necessary:** Only use/share the minimum PHI needed
- **Encryption:** At-rest and in-transit
- **Access controls:** Role-based, auditable
- **BAA coverage:** Vendors touching PHI must sign Business Associate Agreements

**Problem:** Without clear boundaries, developers may accidentally:
- Log PHI in traces/metrics (violation)
- Send raw images to non-BAA vendors (violation)
- Store PHI in public S3 buckets (breach)
- Push PHI in mobile notifications (insecure)

We need a **simple mental model** that maps technical controls to data sensitivity.

---

## Decision

We adopt a **PHI Rings model** with four concentric rings, inspired by security domains. Data moves **outward only** (sensor → edge → workstation → cloud) with explicit policy gates.

### Ring Definitions

| Ring | Data Examples | Storage | Allowed Transitions |
|:--|:--|:--|:--|
| **Ring 0 (Sensor)** | Live photons, raw video buffers | Ephemeral (RAM) | → Ring 1 (Edge temp buffer) |
| **Ring 1 (Local PHI)** | Raw images, DICOM files, session events with identifiers | Edge/Workstation encrypted storage | → Ring 2 (after de-identification or masking)<br>→ Cloud (only with BAA + encryption + consent) |
| **Ring 2 (Derived Features)** | Segmentation masks, embeddings, QC scores, de-identified metadata | Cloud storage (encrypted) | ↔ Cloud freely (BAA-covered services only) |
| **Ring 3 (Public Analytics)** | Aggregates, trends, de-identified cohorts, open models | Public S3, GitHub | Open sharing (MIT license) |

### Movement Rules

**Rule 1:** Never move inward (e.g., cannot reconstruct Ring 1 from Ring 2)
**Rule 2:** Outward movement requires explicit gate:
- Ring 1 → Ring 2: De-identification or masking (irreversible)
- Ring 1 → Cloud: BAA + encryption + patient consent + audit log
- Ring 2 → Ring 3: Statistical disclosure control (k-anonymity)

**Rule 3:** Logs/APM/metrics contain Ring 2+ only (opaque IDs, no PHI)

### Storage Controls by Ring

#### Ring 0 (Sensor)
- **Location:** Camera RAM, video buffers
- **Retention:** Seconds (until preprocessed)
- **Encryption:** N/A (ephemeral)
- **Access:** Device firmware only

#### Ring 1 (Local PHI)
- **Location:**
  - Edge: `/data/ring1` (LUKS encrypted SSD)
  - Workstation: MinIO bucket `ring1-{tenantId}` (SSE-KMS)
- **Retention:** 90 days local → archive to cloud with BAA
- **Encryption:** AES-256 at-rest, TLS 1.3 in-transit
- **Access:**
  - Workstation services via mTLS client certs
  - Audit log: all reads/writes to CloudWatch/Datadog (with BAA)

#### Ring 2 (Derived Features)
- **Location:** Cloud S3 `ring2-{tenantId}` (SSE-KMS)
- **Retention:** 7 years (HIPAA requirement for derived data)
- **Encryption:** AES-256 at-rest, TLS 1.3 in-transit
- **Access:**
  - Cloud services with BAA (Temporal, Flowise, RunPod workers)
  - tRPC API with RBAC (Patient sees own data; Clinician sees assigned patients)

#### Ring 3 (Public Analytics)
- **Location:** Public S3, GitHub releases
- **Retention:** Indefinite
- **Encryption:** Optional (public data)
- **Access:** Open (MIT license)

### Logs, Metrics, and Push Notifications

**All logs/APM/push contain Ring 2+ only:**

```typescript
// ✅ CORRECT: Opaque IDs only
logger.info('Session started', { sessionId: 'sess_abc', userId: 'usr_xyz', locationId: 'nyc-soho' })

// ❌ FORBIDDEN: PHI in logs
logger.error('Upload failed for patient John Doe, DOB 1985-03-12')

// ✅ CORRECT: Push notification (Ring 2)
await expo.sendPush({
  to: userToken,
  body: 'Your report is ready to view.' // No PHI
})
// App fetches details via authenticated tRPC call

// ❌ FORBIDDEN: PHI in push
await expo.sendPush({
  body: 'Your visceral fat is 18.2% (high risk)'
})
```

### De-identification Process (Ring 1 → Ring 2)

```typescript
// packages/policy/src/de-identify.ts
export function deIdentifyCapture(capture: Capture): DeIdentifiedCapture {
  return {
    // Keep Ring 2 safe fields
    captureId: capture.id,
    sessionId: capture.sessionId, // Opaque CUID
    deviceType: capture.deviceType,
    timestamp: capture.createdAt,
    qualityScore: capture.qualityScore,

    // Remove Ring 1 PHI
    // NO: patientName, dob, rawImageUrl

    // Include derived features (Ring 2)
    features: capture.aiAnalysis?.features, // e.g., embeddings
    masks: capture.aiAnalysis?.segmentationMasks, // No raw pixels
  }
}
```

### Enforcement

**Automated checks:**
- Pre-commit hook: `grep -r "patientName\|dob\|ssn" src/` fails build
- CI/CD: Static analysis with custom ESLint rules (no PHI fields in logs)
- Runtime: OpenTelemetry redaction filter strips PHI patterns from traces

**Manual reviews:**
- Weekly: Audit S3 bucket policies (Ring 1 buckets = KMS + private only)
- Quarterly: Compliance review of Datadog logs (sample 1000 log lines for PHI)

---

## Consequences

### Positive

- **Simple mental model:** Engineers understand "Ring 1 = PHI stays local" without reading 100-page HIPAA guide
- **Auditable:** Ring transitions logged; compliance can verify no Ring 1 → Cloud without BAA
- **Privacy-safe by default:** Logs/metrics/push use Ring 2 (opaque IDs) so no accidental PHI exposure
- **Cost-efficient:** Ring 2 features (10 KB) upload to cloud vs Ring 1 raw images (10 MB)
- **Patient-visible:** Narrative Layer shows privacy badges ("Processing locally" = Ring 1)

### Negative

- **De-identification irreversible:** Once Ring 1 → Ring 2, cannot reconstruct original
  - *Mitigation:* Keep Ring 1 local for 90 days; clinicians review raw images on workstation
- **Ring 2 definition evolves:** New regulations may reclassify some derived data as PHI
  - *Mitigation:* Treat Ring 2 as "BAA-covered" by default; update policy if needed
- **Performance overhead:** Encryption/decryption adds latency (~5 ms per file)
  - *Mitigation:* Acceptable for sub-second SLAs; use hardware AES acceleration

---

## Alternatives Considered

### Alternative 1: Binary "PHI" vs "Non-PHI" Classification

**Pros:** Simpler (2 categories instead of 4)
**Cons:** No nuance for derived features; unclear if segmentation masks = PHI

**Decision:** Rejected. Rings provide gradations needed for practical engineering.

### Alternative 2: Per-Field Tagging ("PII: true/false" on every DB column)

**Pros:** Fine-grained control
**Cons:** Brittle (forget one tag = breach); hard to reason about in logs/queries

**Decision:** Rejected. Rings are coarser but easier to enforce.

### Alternative 3: Encrypt Everything with Same Key

**Pros:** Simple (one KMS key for all data)
**Cons:** Cannot share Ring 2 with researchers without exposing Ring 1

**Decision:** Rejected. Separate KMS keys per ring enable selective sharing.

---

## Related Decisions

- **ADR-001:** Local Compute Decision Policy (uses Ring privacy levels to decide target)
- **ADR-003:** Narrative Layer Architecture (surfaces ring status to patients)
- **Week 0 Checklist:** HIPAA compliance prerequisites

---

## References

- [HIPAA Privacy Rule](https://www.hhs.gov/hipaa/for-professionals/privacy/index.html)
- [De-identification Guidance](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html)
- Temporal Cloud: [Security & BAA](https://docs.temporal.io/cloud/security#hipaa-compliance)

---

**Document Version:** 1.0
**Last Updated:** 2025-10-24
**Maintained By:** Vantage Engineering + Compliance
