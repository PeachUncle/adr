# ADR-010 — Public/Link/Private Visibility Model

> **File:** docs/adr/ADR-010-public-link-private-visibility-model.md  
> **Purpose:** Define resource visibility for sessions, plans, and profiles with privacy‑first defaults.

---

id: ADR-010
title: "Public/Link/Private Visibility Model"
status: "Proposed"
date: "2025-10-13"
owners: ["Dr. Konstantinos Pilpilidis"]
version: "1.0"
links:

- TDD §4.7: "Feed & sharing"
- TDD §7.8: "Security & privacy controls"

---

## Context

Users need to keep data **private by default**, share via **unlisted (link)** URLs, or make some content **public** (e.g., for a community feed). We must support **revocable links** and feature‑flagged public discovery to remain privacy‑first.

## Decision

Introduce `visibility` enum on shareable resources with values: **`private` (default)**, **`link`**, **`public`**. Implement **link tokens** for unlisted sharing and **feature flags** for public discovery surfaces.

### Model

- Column: `visibility visibility_enum NOT NULL DEFAULT 'private'`.
- `link` visibility uses `share_links(resource_id, token, expires_at, revoked_at, created_at)`; tokens are random and **revocable**.
- `public` visibility enables inclusion in public feeds **only if** feature `public_feed_enabled` is on.

### Access Rules

- **private**: owner and authorized roles only.
- **link**: anyone with valid token; token may expire or be revoked.
- **public**: visible to all; indexed by feed, but **no PII beyond what user consents** in profile settings.

### Security & Abuse

- Rate limiting on token endpoints; audit logs for token creation and revocation.
- Tokens are **single‑resource** scoped; cannot escalate privileges.
- Public feeds moderated; report/removal pipeline (Phase 2).

## Consequences

- Clear, privacy‑first sharing semantics with revocation.
- Additional tables and checks for tokens and flags.

## Alternatives Considered

- **Only private/link**: Simpler but limits community features.
- **Public by default**: Violates privacy‑by‑default principle.

## QA & Acceptance

- E2E: token sharing grants access; revocation immediately blocks.
- Public feed only returns `public` items when feature flag is on.
- GDPR: visibility changes propagate to caches/CDN within SLA.

## Backout Plan

Disable `public_feed_enabled`; fall back to private/link only while preserving tokens.

## Change Log

- **1.0 (2025-10-13):** Initial proposal.
