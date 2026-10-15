# ADR 0002: Supabase Auth, RLS, and Audit Baseline

- Status: Accepted
- Date: 2025-10-04

## Context

The PRD mandates Supabase-powered authentication with strict RLS, audit trails, and support for
emergency unlock workflows (PRD §5.3, §9, §11, §12, §15). Prior commits delivered the relational
schema and policies but no application integration, leaving the product without sign-in flows,
session management, or documented security posture.

## Decision

- Adopt a workspace-based Next.js App Router project (`apps/web`) using `@supabase/auth-helpers-*`
  for cookie management and session hydration.
- Centralize Supabase client creation (`lib/supabase/*`) with Zod-validated environment parsing to
  prevent secret leakage and ensure consistent configuration.
- Introduce middleware that stamps correlation IDs, bootstraps Supabase sessions, and protects
  authenticated routes.
- Provide audit scaffolding (`recordAuditLog`) writing to the existing `audit_log` table using the
  service role key while normalizing unauthenticated actors to a zero UUID sentinel.
- Add regression tests ensuring the baseline migration retains `auth.uid()`-scoped RLS policies.
- Document security posture, privacy controls, and the W7–W12 emergency unlock playbook in
  `docs/security/baseline.md`.

## Consequences

- ✅ Teams now have a functioning Supabase auth flow with magic-link sign-in, session-aware server
  components, and sign-out instrumentation.
- ✅ Correlation IDs + audit logging provide an initial observability/audit foundation without
  exposing sensitive user data.
- ✅ Regression tests guard against accidental removal of RLS or policy drift in future migrations.
- ⚠️ Service-role usage requires hardened deployment environments; follow-up work must add secrets
  rotation and runtime vaulting.
- ⚠️ Emergency unlock still requires a privileged UI/action—documented runbook mitigates the gap
  but needs implementation.

## Alternatives Considered

- **NextAuth.js + Supabase adapter:** rejected to minimize moving parts and align with Supabase
  managed auth policies.
- **Custom cookie/session store:** rejected; Supabase helpers already satisfy requirements and keep
  parity with RLS policies.

## References

- [Auth Implementation](../../apps/web)
- [Security Baseline](../security/baseline.md)
- [Migration](../../supabase/migrations/202510041230_core_schema.sql)
- [PRD](../../PRD.md)
