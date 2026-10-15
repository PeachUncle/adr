# ADR: Tasks CLI Evidence Schema v1.0

**Status**: ACCEPTED
**Date**: 2025-11-11
**Authority**: ContextForge Work Codex - "Trust Nothing, Verify Everything"
**Related Tests**: `test_tasks_cli_evidence_diff.py`, `test_tasks_cli_reads.py`
**Constitution Rules**: Dry-run suppression, deterministic hashing, JSON purity

---

## Context

The Tasks CLI (`tasks_cli.py`) implements authoritative Postgres-only task management with enriched evidence logging. All write operations (create/update) must emit structured JSONL evidence records enabling full audit trails and reproducibility. This ADR documents the evidence schema version 1.0, including emission rules, hashing strategy, diff semantics, and quality contracts.

## Decision

### Evidence Schema v1.0

All evidence events emitted to `logs/evidence/db_writes.jsonl` MUST conform to this canonical structure:

```json
{
  "schema_version": "1.0",
  "event": "task_upsert" | "task_update",
  "table": "tasks",
  "op": "create" | "update",
  "id": "<task_id>",
  "row_hash": "<sha256_hex_64_chars>",
  "correlation_id": "<uuid>",
  "executed": true | false,
  "operation_result": "success" | "failure",
  "duration_ms": <float>,
  "timestamp": "<ISO8601_UTC>",
  "changes": ["<field_name>", ...],
  "row_after": {<task_row_dict>},
  "diff": {
    "changed_fields": ["<field>", ...],
    "notes_mode": "set" | "append" | "none",
    "minutes_added": <int>,
    "before": {<id_title_status_actual_minutes_subset>},
    "after": {<id_title_status_actual_minutes_subset>}
  }
}
```

### Field Definitions

#### Core Fields (always present)
- **`schema_version`**: String literal `"1.0"` for this version
- **`event`**: Event type identifier (`task_upsert`, `task_update`)
- **`table`**: Database table name (always `"tasks"`)
- **`op`**: Operation type (`create` for INSERT, `update` for UPDATE)
- **`id`**: Task identifier (primary key)
- **`correlation_id`**: UUID linking related operations within a session
- **`executed`**: Boolean - `true` when DB mutation occurred, `false` for dry-run
- **`operation_result`**: `"success"` or `"failure"` indicating operation outcome
- **`timestamp`**: UTC ISO8601 timestamp of operation execution

#### Hashing & Integrity
- **`row_hash`**: SHA-256 hex digest (64 chars) computed over canonical JSON representation (sorted keys) of the composed row payload **before** DB insertion/update
  - Algorithm: `hashlib.sha256(json.dumps(row, sort_keys=True).encode('utf-8')).hexdigest()`
  - Enables deterministic verification and change detection
  - Computed even for dry-run operations

#### Timing
- **`duration_ms`**: Floating-point milliseconds elapsed during operation execution
  - Measured via `TimingCapture` context manager
  - Includes DB connection, query execution, commit time
  - Always present; 0.0 if timing unavailable

#### Change Tracking
- **`changes`**: Array of string field names/labels that were modified
  - Example: `["status", "actual_minutes", "notes_append"]`
  - Includes synthetic labels like `notes_append`, `notes_overwrite` when mutations applied
  - Empty array for create operations or no-op updates

- **`row_after`**: Complete task row dictionary after successful operation
  - Only present when `executed=true` and `operation_result="success"`
  - Contains all canonical task columns: `id`, `title`, `project_id`, `sprint_id`, `priority`, `status`, `owner`, `notes`, `created_at`, `updated_at`, `actual_minutes`
  - Absent for dry-run or failure cases

#### Structured Diff
- **`diff`**: Nested object providing compact before/after comparison
  - **`changed_fields`**: Sorted unique array of changed column/synthetic labels
  - **`notes_mode`**: Enum indicating notes mutation strategy
    - `"set"`: Notes overwritten entirely (via `--set-notes`)
    - `"append"`: Notes appended to existing (via `--append-notes`)
    - `"none"`: No notes mutation
  - **`minutes_added`**: Integer minutes delta added this operation
    - `0` when no `--actual-hours` provided
    - Reflects only the current operation's contribution (not cumulative total)
  - **`before`**: Subset snapshot `{id, title, status, actual_minutes}` before mutation (null for create)
  - **`after`**: Subset snapshot `{id, title, status, actual_minutes}` after mutation (null when not executed)

### Emission Rules (Constitution-Enforced)

#### Rule 1: Dry-Run Suppression (MANDATORY)
Evidence events MUST NOT be emitted when `execute=False` (dry-run mode).

**Rationale**: Dry-run operations simulate changes without persistence; emitting evidence would create false audit trails suggesting DB mutations occurred.

**Test Coverage**: `test_dry_run_emits_no_evidence` validates zero evidence lines written during dry-run update.

#### Rule 2: Failure Suppression (MANDATORY)
Evidence events MUST NOT be emitted when `operation_result="failure"`.

**Rationale**: Failed operations do not mutate state; evidence emission is reserved for successful executions only.

**Implementation**: `_emit_evidence_event` is only called within success path after commit confirmation.

#### Rule 3: Deterministic Hashing (MANDATORY)
The `row_hash` field MUST be computed via SHA-256 over canonical JSON (sorted keys).

**Rationale**: Enables reproducible verification; identical input rows always produce identical hashes regardless of dict ordering.

**Algorithm**:
```python
row_hash = hashlib.sha256(
    json.dumps(row, sort_keys=True).encode('utf-8')
).hexdigest()
```

**Test Coverage**: `test_upsert_create_emits_set_notes_and_minutes` and `test_update_append_accumulates_minutes_and_diff` validate hash presence and 64-char hex format.

#### Rule 4: Minutes Accumulation Semantics (MANDATORY)
The `diff.minutes_added` field MUST reflect only the delta contributed by the current operation, not cumulative totals.

**Examples**:
- Create with `--actual-hours 0.25` → `minutes_added: 15`, `row_after.actual_minutes: 15`
- Update existing task (40 minutes) with `--actual-hours 0.5` → `minutes_added: 30`, `row_after.actual_minutes: 70`

**Test Coverage**: `test_update_append_accumulates_minutes_and_diff` validates incremental accumulation (10 initial + 30 added = 40 final).

#### Rule 5: Zero-Minute No-Op (MANDATORY)
When `--actual-hours` is omitted or `0`, the `actual_minutes` field MUST NOT appear in `changes` or `changed_fields`.

**Rationale**: Zero-minute updates are semantic no-ops for time tracking; including them pollutes change logs.

**Implementation**: `_build_evidence_diff` excludes `actual_minutes` from `changed_fields` when `minutes_added=0`.

### Notes Mutation Semantics

#### Set Mode (`notes_mode: "set"`)
- Triggered by: `--set-notes "<text>"`
- Behavior: Replaces entire notes field
- Change label: `notes_overwrite` added to `changes` and `changed_fields`

#### Append Mode (`notes_mode: "append"`)
- Triggered by: `--append-notes "<text>"`
- Behavior: Appends line to existing notes (newline-separated)
- Change label: `notes_append` added to `changes` and `changed_fields`

#### Conflict Resolution
When both `--set-notes` and `--append-notes` provided, `set` takes precedence (overwrite wins).

**Test Coverage**: `test_upsert_create_emits_set_notes_and_minutes` validates `notes_mode: "set"` with `notes_overwrite` label; `test_update_append_accumulates_minutes_and_diff` validates `notes_mode: "append"` with `notes_append` label.

---

## Consequences

### Positive

1. **Complete Audit Trail**: Every successful write operation generates traceable evidence with cryptographic integrity (SHA-256 hash)
2. **Reproducibility**: Deterministic hashing enables verification; replaying operations with identical inputs yields identical hashes
3. **Incremental Minutes Tracking**: `minutes_added` captures per-operation deltas, enabling accurate time allocation analysis
4. **Dry-Run Safety**: Suppression rules prevent false evidence during simulation modes
5. **Structured Diffs**: Compact before/after snapshots enable efficient change analysis without full row storage

### Negative

1. **Storage Overhead**: Every write operation generates a JSONL line (~500-1000 bytes); high-frequency updates accumulate evidence quickly
2. **JSON Purity Dependency**: Read commands (`show`, `list`, `status_counts`) must implement `--json` flag correctly to avoid contaminating parseable output with log lines
3. **Schema Evolution Friction**: Changes to evidence structure require version bumps and migration tooling

### Mitigation

- **Storage**: Implement evidence rotation/archival for logs older than 90 days
- **JSON Purity**: Constitution rule enforces suppression of all non-JSON output when `json_output=True`; validated by parseable outputs in tests
- **Schema Evolution**: Reserve schema version field for future extensions; implement backward-compatible readers

---

## Validation Status

### Test Coverage (10/10 PASSING)

#### Evidence Diff Suite (`test_tasks_cli_evidence_diff.py`)
- ✅ `test_upsert_create_emits_set_notes_and_minutes`: Validates create operation with `notes_mode: "set"`, `minutes_added: 15`, `actual_minutes: 15`
- ✅ `test_update_append_accumulates_minutes_and_diff`: Validates update with `notes_mode: "append"`, incremental minutes (30 added to 10 = 40 final), `changed_fields` includes `status`, `notes_append`, `actual_minutes`
- ✅ `test_dry_run_emits_no_evidence`: Validates zero evidence lines emitted during dry-run update operation

#### Read Path Suite (`test_tasks_cli_reads.py`)
- ✅ `test_task_show_json_success`: Validates show command JSON output structure
- ✅ `test_task_show_not_found`: Validates error exit on missing task
- ✅ `test_task_list_basic_filters`: Validates list filtering and result count
- ✅ `test_task_list_pagination`: Validates limit/offset behavior
- ✅ `test_task_list_sort_allowlist`: Validates sort column validation
- ✅ `test_task_status_counts_deterministic_hash`: Validates identical `counts_hash` across runs (SHA-256)
- ✅ `test_task_status_counts_structure`: Validates counts response shape (`items`, `total`)

### Constitution Compliance

All evidence emission logic adheres to session rules established via `vibe-check-mcp.update_constitution`:
1. ✅ Dry-run operations emit no evidence
2. ✅ Evidence emitted only on successful, executed writes
3. ✅ JSON outputs contain no extra lines when `--json` flag active
4. ✅ Deterministic SHA-256 hashing for `row_hash` and `counts_hash`
5. ✅ Diff semantics accurate: `minutes_added` reflects delta only; `notes_mode` matches mutation strategy
6. ✅ Zero-minute updates produce no `actual_minutes` diff entry

---

## References

- **Implementation**: `tasks_cli.py` lines 1-800 (Phase 0 restoration; `_execute_authoritative_upsert`, `_emit_evidence_event`, `_build_evidence_diff`)
- **Test Suite**: `tests/test_tasks_cli_evidence_diff.py`, `tests/test_tasks_cli_reads.py`
- **ContextForge Work Codex**: Core Philosophy #3 "Logs First" - structured evidence generation for all material operations
- **Terminal Output Standard**: Rich library integration for non-JSON console output (banners, progress, tables)

---

## Approval

**Architect**: Solution Architecture Specialist (Documentation Lead)
**Validated By**: Software Quality Engineer (Test Evidence Review)
**Effective Date**: 2025-11-11
**Next Review**: After quality gates pass (pytest + ruff + mypy)
