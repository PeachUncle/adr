# ADR-059: Hint Registry Design

## Status
Accepted

## Context

Hints are currently hardcoded in various agent files (`src/graph/graph.py`, `scripts/prepare_handoff.py`, `pmagent/reality/check.py`, etc.) and treated as optional suggestions. This creates several problems:

1. **No contractual enforcement**: REQUIRED hints (like "DMS-only, no fallback") are treated the same as optional suggestions
2. **Scattered maintenance**: Hints live in code, making updates require code changes
3. **No audit trail**: No way to track which hints were applied to which flows
4. **Inconsistent application**: Different envelope generators apply hints differently

The DMS (Documentation Management System) already provides a registry pattern for documents (`control.doc_registry`). We should extend this pattern to hints.

## Decision

Implement a DMS-backed Hint Registry (`control.hint_registry`) that:

1. **Stores hints in Postgres** with REQUIRED vs SUGGESTED semantics
2. **Embeds hints into envelopes** (handoff, capability_session, reality_check, status) via DMS queries
3. **Enforces REQUIRED hints** via guards (`guard.hints.required`)
4. **Enables extensibility** - adding new hints requires only DMS INSERT, no code changes

### Schema Design

**Table**: `control.hint_registry`

- `hint_id` (UUID, primary key)
- `logical_name` (TEXT, unique) - e.g., "docs.dms_only", "status.local_gates_first"
- `scope` (TEXT) - e.g., "handoff", "status_api", "pmagent", "biblescholar"
- `applies_to` (JSONB) - selectors: must include `flow` key, may include `rule`, `agent`, `scope`
- `kind` (TEXT, CHECK constraint) - "REQUIRED", "SUGGESTED", "DEBUG"
- `injection_mode` (TEXT, CHECK constraint) - "PRE_PROMPT", "POST_PROMPT", "TOOL_CALL", "META_ONLY"
- `payload` (JSONB) - structured hint content: `{"text": "...", "commands": [...], "constraints": {...}, "metadata": {...}}`
- `enabled` (BOOLEAN, default TRUE)
- `priority` (INTEGER, default 0) - for ordering within same kind
- `created_at`, `updated_at` (TIMESTAMPTZ)

**Constraints**:
- `kind` must be one of: REQUIRED, SUGGESTED, DEBUG
- `injection_mode` must be one of: PRE_PROMPT, POST_PROMPT, TOOL_CALL, META_ONLY
- `applies_to` must include `flow` key (CHECK constraint)

**Indexes**:
- `scope` (WHERE enabled = TRUE)
- `applies_to` (GIN index for JSONB queries)
- `kind, priority` (for ordering)
- `applies_to->>'flow'` (for flow-based queries)

### Envelope Integration

Envelope generators query DMS and embed hints:

```python
hints = load_hints_for_flow(scope="handoff", applies_to={"flow": "handoff.generate"})
envelope = {
    "context": {...},
    "required_hints": hints["required"],
    "suggested_hints": hints["suggested"]
}
```

**Affected generators**:
- `scripts/prepare_handoff.py` - handoff markdown
- `pmagent/plan/next.py` - capability_session JSON
- `pmagent/reality/check.py` - reality check verdict
- `pmagent/status/snapshot.py` - status snapshot

### Guard Enforcement

**Guard**: `guard.hints.required`

- Queries DMS for REQUIRED hints for a given flow
- Checks that envelope contains all REQUIRED hints in `required_hints` array
- **Empty REQUIRED set is OK** - if no REQUIRED hints exist, guard passes
- **HINT mode**: If DB unavailable, emits HINT and passes (graceful degradation)
- **STRICT mode**: If DB unavailable, fails (fail-closed)

### Migration Strategy

1. **Step 0**: Discovery - scan codebase for hardcoded hints, classify REQUIRED vs SUGGESTED
2. **Step 1**: Create schema + ADR, seed registry with initial hints
3. **Step 2**: Implement helper module (`pmagent/hints/registry.py`)
4. **Step 3**: Wire envelope generators (parallel behavior, non-breaking)
5. **Step 4**: Implement guard, add to `reality.green STRICT`
6. **Step 5**: Fix any failing flows, ensure guard passes
7. **Step 6**: Remove legacy hardcoded hints
8. **Step 7**: Update rules/docs

## Related Rules

- Rule 050 (OPS Contract) - references hints in handoff format
- Rule 051 (Cursor Insight) - references hints in evidence blocks
- Rule 026 (System Enforcement Bridge) - guard enforcement pattern

## Consequences

### Positive

- **Contractual enforcement**: REQUIRED hints become enforceable via guards
- **Centralized management**: All hints in one place (DMS)
- **Extensibility**: Adding hints requires only DMS INSERT
- **Audit trail**: Track which hints applied to which flows
- **Consistency**: All envelope generators use same hint loading logic

### Negative

- **DB dependency**: Envelope generation now requires DB access (mitigated by graceful degradation)
- **Migration effort**: Need to discover and migrate existing hardcoded hints
- **Initial complexity**: More moving parts (registry, helper module, guard)

### Mitigations

- **Graceful degradation**: If DB unavailable, envelope generators fall back to empty hints array (don't crash)
- **Parallel behavior**: Step 3 maintains existing hardcoded hints alongside DMS hints during transition
- **Hermetic-friendly**: Guard works in HINT mode when DB unavailable

## Verification

- [ ] `control.hint_registry` table exists and is populated
- [ ] All envelope generators query DMS and embed hints
- [ ] `guard.hints.required` passes for all flows in STRICT mode
- [ ] Hardcoded hints removed from agent code
- [ ] Adding new hints requires only DMS INSERT (no code changes)

## References

- Migration: `migrations/054_control_hint_registry.sql`
- Helper module: `pmagent/hints/registry.py`
- Guard: `scripts/guards/hints_required.py`
- Discovery script: `scripts/governance/discover_hints.py`
- Seed script: `scripts/governance/seed_hint_registry.py`

