# ADR-009 — Global Exercise Library Ownership Model

> **File:** docs/adr/ADR-009-global-exercise-library-ownership-model.md  
> **Purpose:** Balance a curated global exercise catalog with user customization and extension.

---

id: ADR-009
title: "Global Exercise Library Ownership Model"
status: "Proposed"
date: "2025-10-13"
owners: ["Dr. Konstantinos Pilpilidis"]
version: "1.0"
links:

- TDD §4.3: "Exercises module"
- TDD §6.2.6: "Data modeling choices"

---

## Context

FitVibe ships a **global exercise library** (curated by admins) but must allow users to define custom exercises. We require a model that avoids naming conflicts, supports localization, and keeps admin updates from clobbering user customizations.

## Decision

Use **admin‑owned global records** where `owner_id IS NULL`. **User‑owned** exercises have `owner_id = <user_id>`. Enforce **normalized uniqueness**: `UNIQUE (lower(name), COALESCE(owner_id, '00000000-0000-0000-0000-000000000000'))`.

### Rules

- Global exercises: created/edited by admins; visible to all.
- Users may **fork** a global exercise to customize fields (name, cues, defaults). Forks become **user‑owned** records linked by `source_exercise_id`.
- Lookup order: prefer **user‑owned** overrides; fall back to global.
- De-duplication: app suggests globals when a user creates a similar (case/locale-insensitive) name.
- Localization: names and cues stored in `exercise_translations` per locale; uniqueness applies to a **canonical slug**.

### Data Model (key fields)

- `exercises(id, owner_id NULLABLE, source_exercise_id NULLABLE, slug, primary_muscle, equipment, created_at, updated_at)`
- Constraint for normalized uniqueness as above.

## Consequences

- Clean separation of curated vs. personal content.
- Admin updates do not override user customizations.
- Slightly more complex lookups and uniqueness checks.

## Alternatives Considered

- **Single global set only**: Blocks personalization.
- **Per-user only**: No shared catalog; duplicates proliferate.

## QA & Acceptance

- Tests for uniqueness across global/user scopes.
- Forking keeps links; renames maintain uniqueness constraints.
- Search returns user fork first if present.

## Backout Plan

If forks add too much complexity, fallback to **global + per-user alias table** while keeping uniqueness on slugs.

## Change Log

- **1.0 (2025-10-13):** Initial proposal.
