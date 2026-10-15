# ADR 0001: Core Data Model and Migrations

- Status: Accepted
- Date: 2025-10-04

## Context
The MVP requires persistence for the 12-week transformation workflow (vision → plan → execution → AI WAM). The PRD mandates strict constraints: a single personal/professional goal per cycle, week locking after Week 6, auditable change history, and Supabase-ready RLS. No prior schema existed in the repository.

## Decision
We introduced migration `202510041230_core_schema.sql` implementing:
- Normalized tables for `vision`, `cycle`, `goal`, `weekly_plan`, `task`, `plan_item`, `audit_log`, `chat_session`, and `chat_message`.
- Enum types capturing constrained domains (goal type, workflow mode, plan item status, actor and chat roles).
- Database triggers to enforce the 6/6 lock rule and maintain timestamps.
- Baseline row-level security policies relying on `auth.uid()` to isolate tenant data.
- Seed fixtures (`202510041235_sample_data.sql`) to accelerate local development and support regression checks.
- Documentation for schema overview and rollback to aid DevOps and reviewers.

## Consequences
- ✅ Backend and frontend teams can share Zod schemas derived from the new structure, enabling early API work.
- ✅ Security posture improves with audit logging foundations and RLS policies in place before auth work begins.
- ⚠️ Future migrations must preserve trigger behavior or adjust application logic if lock rules evolve.
- ⚠️ Supabase policies rely on `auth.uid()`; non-Supabase environments must emulate the function or adjust policies during testing.

## Alternatives Considered
- **Single `jsonb` plan document**: rejected because it complicates relational constraints and RLS enforcement.
- **Deferring RLS**: rejected to avoid late security retrofits and align with PRD §5.3 requirements.

## References
- [PRD §4, §5.3, §9–§11](../../PRD.md)
- [Migration](../../supabase/migrations/202510041230_core_schema.sql)
- [Schema Overview](../schema/overview.md)
- [Rollback Guide](../schema/rollback.md)
