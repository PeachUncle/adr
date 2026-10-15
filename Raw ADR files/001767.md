# ADR-017: Avatar Handling & Media Storage (Object Storage + AV Scan)

**Date:** 2025-10-14  
**Status:** Accepted  
**Author:** Reviewer  
**Cross-References:** PRD §5 Security/Privacy, §6 Media & Files, §7 Engineering Standards; TDD §5.1.6 (uploads), §6.2 (schema), §7.9 (media access), §10 (ops); QA §2–§12 (CI gates, security), §11 (performance), §14 (perf regression)

---

## Context

Earlier drafts stored avatars as **base64 blobs in the DB**, which increases row size, complicates caching, and weakens scanning and access controls. The PRD and TDD require **object storage in production** (S3-compatible or GCS), **antivirus scanning**, **re-encoding to safe image formats**, strict **size/type limits**, and **private-by-default** access via signed URLs or a media proxy. QA enforces security scanning, performance budgets, and E2E coverage for the upload/change avatar flow.

This ADR standardizes avatar handling and media storage in a way that is privacy-first, performant, and testable under CI.

---

## Decision

1. **Storage & Access**
   - **Production:** Store images in **object storage** (S3-compatible/GCS) in a **private bucket**.
   - **Development:** Store under local `./uploads` with the same interface (adapter pattern).
   - **Access:** Serve via **short-lived signed URLs** (preferred) or a **server proxy** that checks authorization and sets cache headers.

2. **Upload Flow (Server-Mediated)**
   1. Client `POST /api/v1/users/{id}/avatar` (multipart).
   2. Server validates authn/z, **rate limits**, and content-type/size.
   3. Server streams to temp storage, performs **AV scan**.
   4. Server **re-encodes** and **strips EXIF**; generates derivative sizes (**128, 256, 512** px square) using letterboxing/cropping rules.
   5. Server uploads originals/derivatives to object storage with keys (see §4).
   6. Metadata record created in DB; user profile points to the active asset.
   7. Old assets are scheduled for deletion (grace window ≤ 24h) and invalidated from caches/CDN.

   > Optional: For large media, support **pre-signed POST** initiation, but finalization still goes through server validation & AV scan before activation.

3. **Constraints & Validation**
   - **Accepted types:** `image/jpeg`, `image/png`, `image/webp`.
   - **Max size:** **5 MB** (request rejected otherwise).
   - **Dimensions:** min 64×64; max 4096×4096; auto-resize to derivative set.
   - **MIME sniffing** by magic number; filename extensions are advisory only.

4. **Object Keys & Versioning**
   - Bucket structure: `avatars/{user_ulid}/{sha256[:16]}/{size}.webp` where `size ∈ {orig,128,256,512}`.
   - Keys are **content-addressed** (hash-based) to enable cache-busting; the **user record references the active key**.
   - On update, the pointer changes; old keys are deleted after grace window and lifecycle rules purge from storage/CDN.

5. **Database Model**
   - Table: `media_assets` with fields:
     - `id (ulid)`, `owner_user_id (ulid)`, `kind ('avatar')`, `bucket`, `key_prefix`, `format`, `size_bytes`, `width`, `height`, `hash_sha256`, `created_at`, `deleted_at` (nullable).
   - `users.avatar_asset_id` references `media_assets.id`.
   - Derivatives share `key_prefix`; each file stored separately.

6. **Security & Privacy**
   - **AV scan** must pass before any asset is activated.
   - **Private-by-default**: no public ACLs; signed URLs expire quickly (e.g., ≤ 10 min).
   - **EXIF/metadata stripped** to avoid location/device leakage.
   - **CSP** ensures images load from the media domain only.
   - **Logging:** No PII; record asset IDs and correlation IDs only.

7. **Caching & CDN**
   - Set `Cache-Control` on media responses; leverage CDN with **origin shielding**.
   - Client-side `ETag`/`If-None-Match` supported by the proxy; for signed URLs, rely on key changes to invalidate caches.
   - Derivative sizes reduce layout shifts and improve LCP.

8. **Deletion & DSR**
   - User-triggered avatar removal marks the asset as `deleted_at` and removes pointers.
   - Objects and derivatives are deleted from storage; **backups** purge within **≤14 days** per retention policy.
   - Signed URLs or cached versions naturally expire; no PII is exposed via object names.

9. **Performance & Budgets**
   - Upload endpoints are tracked separately from general API p95; **target p95 ≤ 1200 ms** end-to-end for a 1–3 MB image in staging parity.
   - General API budgets remain **p95 < 300 ms**; avatar reads via CDN should be ≤ 100 ms p95.

10. **Operations & Secrets**
    - Separate **IAM role** for media read/write; **least privilege**.
    - Rotating access keys; CI uses OIDC federation or environment-scoped secrets.
    - Bucket **lifecycle rules** remove orphaned objects and incomplete uploads.

11. **Feature Flags & Fallbacks**
    - **Feature flag** guards S3/GCS use in non-prod; dev defaults to filesystem adapter.
    - If user has no avatar, render a **generated letter avatar** based on display name or a neutral silhouette.

---

## Consequences

**Positive**

- Privacy-first and scalable; fast delivery via CDN; safe formats and sizes.
- Clear cache-busting and easy revocation via key rotation.
- Testable under CI with deterministic adapters and DB schema.

**Negative / Trade-offs**

- Requires object storage credentials and AV infrastructure.
- Slight complexity around derivatives and lifecycle rules.

**Operational**

- Monitor AV scan performance and failure rates; alert on upload spikes and 5xx from the media proxy.
- Track storage growth; enable lifecycle reports and cost alerts.

---

## Alternatives Considered

| Option                    | Description                       | Reason Rejected                                                    |
| ------------------------- | --------------------------------- | ------------------------------------------------------------------ |
| **DB base64 blobs**       | Store raw base64 in a text column | Bloats DB, poor cacheability, harder scanning; contradicts PRD/TDD |
| **Public bucket**         | Public-read objects               | Violates private-by-default and revocation requirements            |
| **Client-direct S3 only** | Browser uploads straight to S3    | Hard to enforce AV scan/authz; server must still gate activation   |

---

## References

- PRD: Media/storage requirements, security & privacy baselines, engineering standards
- TDD: Upload flow, schema, media access model, operations
- QA: CI gates (security/perf), E2E upload tests, regression budgets

---

## Status Log

| Version | Date       | Change                                                                               | Author   |
| ------- | ---------- | ------------------------------------------------------------------------------------ | -------- |
| v1.0    | 2025-10-14 | Adopt object storage, AV scan, derivatives, signed access; remove DB base64 approach | Reviewer |
