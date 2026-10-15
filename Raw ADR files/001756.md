# ADR-004 — Media Upload Safety & AV Scanning

> **File:** docs/adr/ADR-004-media-upload-safety-and-av-scanning.md  
> **Purpose:** Define a secure pipeline for handling user media (images/videos) to prevent malware and abuse content from entering the system.

---

id: ADR-004
title: "Media Upload Safety & AV Scanning"
status: "Accepted"
date: "2025-10-14"
owners: ["Dr. Konstantinos Pilpilidis"]
version: "1.0"
links:

- PRD: "docs/1. Product Requirements Document.md#security--privacy"
- TDD: "docs/2. Technical Design Document v2.md#media-handling--object-storage"
- QA: "docs/3. Testing and Quality Assurance Plan.md#security-tests-and-slos"

---

## Context

MVP and future phases allow users to upload media (e.g., exercise photos). File uploads introduce risks: malware, poisoned payloads, abusive content, and storage abuse. We need a **defense‑in‑depth** pipeline compatible with the SPA and our object storage (S3/MinIO).

## Decision

Implement a **quarantine → scan → transform → publish** pipeline with strict **allow‑list**, **content‑sniffing**, and **ClamAV** scanning. No file is served until it clears the pipeline.

### Pipeline

1. **Pre‑Upload Checks (Client & Edge)**
   - Max size: **10 MB** (MVP).
   - Allowed types: `image/jpeg`, `image/png`, `image/webp`, `video/mp4` (Phase 2).
   - Use presigned POST to **quarantine bucket** with server‑generated object key; deny public access.
2. **Ingestion (Backend)**
   - Validate MIME via **server‑side sniffing** (magic bytes).
   - Store metadata row with `status="quarantined"`.
3. **AV Scanning**
   - **ClamAV** daemon scans new objects; on **malware detected** → delete object, mark row `status="rejected"`, alert.
   - Keep **signature DB** updated on a schedule.
4. **Transformations**
   - Strip **EXIF**, normalize color space, resize to sensible resolutions.
   - Re‑encode to safe formats; disallow active content (SVG with scripts, PDFs with JS).
5. **Publish**
   - Move to **public bucket** with immutable names; serve via CDN with **Content‑Disposition** and **Content‑Type** set explicitly.
   - Attach **Object Lock/retention** optional; use short **cache‑control** for revocation agility.
6. **Abuse & Content Controls (Phase 2+)**
   - Optional ML nudity/abuse detection; human review queue.

### Security Controls

- **Allow‑list only**, block everything else.
- **Rate limiting** per user/IP; total storage quotas.
- **Signed URLs** short‑lived; no direct bucket listing.
- **CSP** headers on media domains to prevent content sniffing in browsers.
- **No SVG uploads** in MVP; consider sanitized SVG later.
- **Checksum** on upload (SHA‑256) and store content hash to detect duplicates.

### Observability

- Metrics: `uploads_quarantined_total`, `uploads_rejected_total`, scan latency p95, transform failures.
- Audit log for every state change (quarantine→scanned→published).

## Consequences

- Strong malware protection and safer media serving.
- Slight latency added between upload and publish; extra infra (ClamAV workers).

## Alternatives Considered

- **Inline scanning** at upload: Higher perceived latency, fewer retries.
- **Third‑party scanning service**: Less ops, but vendor coupling/cost.

## QA & Acceptance

- E2E: infected EICAR file is rejected and deleted.
- Ensure invalid MIME/extension mismatches rejected.
- Privacy: EXIF stripped; GPS data never stored.

## Backout Plan

If ClamAV throughput is a bottleneck, scale workers horizontally or temporarily switch to **inline scanning** with queue back‑pressure.

## Change Log

- **1.0 (2025-10-14)** Initial acceptance.
