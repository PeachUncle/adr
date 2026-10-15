# ADR-003 — Data Retention & GDPR Backup Purge Window

> **File:** docs/adr/ADR-003-data-retention-and-gdpr-backup-purge.md  
> **Purpose:** Define lawful data retention, deletion, and backup purge policies to meet GDPR and FitVibe’s PRD/SEC requirements.

---

id: ADR-003
title: "Data Retention & GDPR Backup Purge Window"
status: "Accepted"
date: "2025-10-14"
owners: ["Dr. Konstantinos Pilpilidis"]
version: "1.0"
links:

- PRD: "docs/1. Product Requirements Document.md#security--privacy-gdpr"
- TDD: "docs/2. Technical Design Document v2.md#data-model--persistence"
- QA: "docs/3. Testing and Quality Assurance Plan.md#compliance-and-data-governance-tests"
- Related:
  - "docs/adr/ADR-002-authentication-token-strategy.md"
  - "docs/adr/ADR-005-partitioning-sessions-audit-log.md"

---

## Context

FitVibe processes user accounts, session logs, health-related workout data, and device/session metadata. GDPR requires **purpose limitation**, **data minimization**, **storage limitation**, and **the right to erasure** (Art. 5 & 17). We must define concrete **retention windows**, a **backup purge policy**, and a **restorable deletion** model that keeps backups lawful while enabling operational recovery.

## Decision

Adopt a **two‑phase deletion** (soft → hard) with **anonymization/pseudonymization** for analytics, and a **time‑boxed backup purge window**. Backups are encrypted and rotated; PII is purged from restorable media after the purge horizon.

### Retention & Deletion Model

- **Soft delete** user‑facing aggregates (e.g., sessions) via `deleted_at`.
- **Hard delete** PII after grace periods; replace with anonymized aggregates when useful.
- **User Account Deletion (Right to Erasure)**:
  - Immediate **account lock**, sessions revoked.
  - Within **T+7 days**: hard delete credentials (`auth.credentials`), refresh tokens, access grants.
  - Within **T+30 days**: hard delete PII in `auth.users` (email, names). Keep non‑identifying aggregates only if anonymized (e.g., workout stats without links to `user_id`).
  - **Backup purge horizon**: **35 days** after T (≥ the longest online backup retention) to ensure erased data ages out from rotation.
- **Device/session metadata**: retain **90 days** for security/audit, then purge or anonymize (IP hashes truncated).
- **Audit trail for admin/security** (non‑content): retain **365 days**, then aggregate counts + drop PII.

### Backup & Restore Policy

- **Backups**: Daily logical backups (pg_dump) + weekly base with daily WAL (if PITR enabled). **AES‑256** at rest; keys in KMS.
- **Retention**: **14 days** rolling window. After day 35, backups containing erased PII are no longer retained.
- **Restore Handling**: On restore older than T+35, a **post‑restore erasure job** re-applies tombstones from `system.erasure_ledger` to ensure previously erased subjects stay erased.
- **Retention**: **14 days** rolling window. After day 14, backups containing erased PII are no longer retained.
- **Restore Handling**: On restore older than T+14, a **post-restore erasure job** re-applies tombstones from `system.erasure_ledger` to ensure previously erased subjects stay erased.

### Data Map & Windows (MVP)

| Domain   | Table(s)                               | Data Type                   | Retention                                                      | Deletion Mode                              |
| -------- | -------------------------------------- | --------------------------- | -------------------------------------------------------------- | ------------------------------------------ |
| Identity | `auth.users` (PII), `auth.credentials` | Email, names, password hash | Delete on request; otherwise **active + 24 months** inactivity | Hard delete PII; pseudonymize references   |
| Sessions | `core.sessions`, `core.sets`           | Workout logs                | User delete → soft (immediate), hard at **30 days**            | Soft→Hard, aggregate anonymized stats kept |
| Security | `auth.sessions`, `auth.refresh_tokens` | Device/session              | **90 days** rolling                                            | Hard delete                                |
| Audit    | `system.audit_trails`                  | Events (low PII)            | **365 days**                                                   | Aggregate & drop PII                       |
| Metrics  | time‑series                            | Non‑PII labels              | **13 months**                                                  | Natural TTL in TSDB                        |

### Anonymization & Pseudonymization

- Replace `user_id` with random surrogate keys in analytics tables.
- Hash emails for dedup where strictly needed (salted).
- Drop or bin precise timestamps when aggregating (e.g., day‑level).

### Operational Controls

- **Erasure Ledger**: `system.erasure_ledger(subject_id, issued_at, completed_at, scope)` used to replay deletes after restores.
- **DPO Review**: Changes to retention windows require DPO approval and ADR amendment.
- **Access Controls**: Only compliance role can view `erasure_ledger` contents.

## Consequences

- Satisfies storage minimization and erasure obligations while remaining operable.
- Backup purge horizon prevents indefinite storage of PII in cold media.
- Extra operational complexity (erasure replay on restores).

## Alternatives Considered

- **Immediate hard deletion incl. backups**: Non‑viable with realistic restore needs.
- **Indefinite backups**: Non‑compliant (storage limitation).

## QA & Acceptance

- Unit/integration tests for erasure flow.
- Quarterly restore drill must replay `erasure_ledger` without residual PII.
- Compliance checks confirming retention jobs remove data by schedule.

## Backout Plan

If purge horizon causes operational risk, temporarily extend to **45 days** and document; never reduce without ensuring all existing rotations meet the new shorter window.

## Change Log

- **1.0 (2025-10-14)** Initial acceptance.
