# DECISION-LYNX-002: Phase 4 Cell Execution Protocol + Allowed Cell Tools

**Status:** Approved  
**Date:** 2026-01-27  
**Version:** 1.0.0  
**Related Documents:**
- PRD-LYNX-003 (HYBRID BASIC)
- ADR-LYNX-001 (MCP Architecture)
- TSD-LYNX-001 (Technical Specification)

---

## Context

Phase 3 (Cluster MCPs - Draft Creation) is complete. We have:
- ✅ 12 Domain MCPs (read-only)
- ✅ 3 Cluster MCPs (draft creation)
- ✅ Draft Protocol with full invariants
- ✅ 65/65 tests passing

**Phase 4 represents a governance milestone:** we are about to allow Lynx to **change reality** through Cell MCPs (execution layer). This requires a strict **Cell Execution Protocol** that is as rigorous as the Draft Protocol.

---

## Decision

### 1. Cell Execution Protocol (Non-Negotiable Invariants)

A Cell MCP may **only execute** when all of the following conditions are met:

1. **Draft Exists & Tenant Match**
   - Draft must exist in draft storage
   - Draft `tenant_id` must match execution context `tenant_id`
   - Draft must not be in `CANCELLED` status

2. **Draft Status is APPROVED** (or policy allows bypass with reason)
   - Draft status must be `APPROVED` (from `DraftStatus.APPROVED`)
   - Exception: Policy may allow bypass with explicit reason logged
   - Bypass requires: `bypass_reason`, `bypass_authorized_by`, `bypass_timestamp`

3. **Permissions Pass** (role/scope)
   - User role must have required permissions for the Cell tool
   - Required scope must be present in execution context
   - Permission check must be logged (success/denial)

4. **Policy Passes** (thresholds, gates)
   - All policy gates must pass (amount thresholds, risk flags, etc.)
   - Policy snapshot from draft must be validated
   - Policy failures must be logged with reason

5. **Execution is Idempotent**
   - Same `request_id` must yield same `execution_id`
   - Re-execution with same `request_id` must return existing execution record
   - Execution state must not be mutated on repeat requests

6. **Audit is Append-Only**
   - Log execution start event before execution
   - Log execution completion event after execution (success/failure)
   - All audit events must be immutable (append-only)
   - Audit trail must include: `execution_id`, `draft_id`, `tool_id`, `tenant_id`, `actor_id`, `status`, `result_payload`, `created_at`

7. **Rollback Strategy Exists**
   - At minimum: compensating state must be defined
   - Execution must log rollback instructions if failure occurs
   - High-risk executions must have explicit rollback plan

### 2. Execution Record Model

All Cell executions must create an **Execution Record**:

```python
class ExecutionRecord:
    execution_id: str  # Unique execution identifier
    draft_id: str  # Source draft ID
    tool_id: str  # Cell MCP tool ID
    tenant_id: str  # Tenant ID (enforces isolation)
    actor_id: str  # User ID who executed
    status: ExecutionStatus  # started|succeeded|failed|denied
    result_payload: Dict[str, Any]  # Execution result (JSON)
    created_at: str  # ISO timestamp
    completed_at: Optional[str]  # ISO timestamp (if completed)
    error_message: Optional[str]  # Error message (if failed)
    rollback_instructions: Optional[Dict[str, Any]]  # Rollback plan
```

### 3. Allowed Cell MCPs (Phase 4 - HYBRID BASIC)

**Total: 3 Cell MCPs** (minimum viable set to prove end-to-end value)

#### 3.1 `docs.cell.draft.submit_for_approval`
- **Purpose:** Submit a document draft for approval
- **Risk Level:** Low (changes draft state only, no production mutation)
- **Input:** `draft_id`
- **Output:** Draft status changed to `SUBMITTED`
- **Side-effect:** Draft state transition only (still "safe execution")
- **Why First:** Lowest operational risk; proves workflow gating

#### 3.2 `workflow.cell.draft.publish`
- **Purpose:** Publish an approved workflow draft as a production workflow
- **Risk Level:** Medium (creates production workflow record)
- **Input:** `draft_id`
- **Output:** `workflow_id` (production workflow ID)
- **Side-effect:** Creates "published workflow" record (first real production object)
- **Why Second:** Creates governed runtime workflows; unlocks approvals

#### 3.3 `vpm.cell.payment.execute`
- **Purpose:** Execute an approved payment draft
- **Risk Level:** High (creates payment record + status transitions)
- **Input:** `draft_id`
- **Output:** `payment_id`, `status`
- **Side-effect:** Creates payment record + status transitions + audit event
- **Why Third:** This is the money move, must be last
- **Note:** For Phase 4, this creates **internal payment record + status** for later settlement. No bank API integration yet (lower risk, same architecture).

### 4. Approval Requirement Rules

**Default Rule:** All Cell executions require draft status = `APPROVED`

**Exceptions (Policy-Based Bypass):**
- Policy may allow bypass for low-risk operations with explicit authorization
- Bypass requires:
  - `bypass_reason`: String explaining why bypass is allowed
  - `bypass_authorized_by`: User ID or role who authorized bypass
  - `bypass_timestamp`: ISO timestamp
  - `bypass_policy_reference`: Policy rule that allows bypass

**Approval Workflow:**
1. Draft created (status: `DRAFT`)
2. Draft submitted (status: `SUBMITTED`) via `docs.cell.draft.submit_for_approval`
3. Draft approved (status: `APPROVED`) via external approval process (not a Cell MCP)
4. Draft executed (status: remains `APPROVED`, execution record created) via Cell MCP

---

## Consequences

### Positive
- **Governance:** Strict execution protocol ensures no unauthorized state changes
- **Auditability:** Full execution trail with append-only audit logs
- **Safety:** Idempotency and rollback strategies prevent data corruption
- **Scalability:** Protocol is extensible to future Cell MCPs

### Negative
- **Complexity:** Cell execution requires more validation than Cluster drafts
- **Performance:** Multiple checks (draft, approval, permission, policy) add latency
- **Maintenance:** Execution records must be maintained and queryable

### Risks Mitigated
- **Unauthorized Execution:** Draft approval + permission checks prevent unauthorized actions
- **Data Corruption:** Idempotency + rollback strategies prevent duplicate/malformed executions
- **Audit Gaps:** Append-only audit logs ensure complete execution trail
- **Tenant Isolation:** Draft tenant match + execution context validation enforce isolation

---

## Implementation Plan

### Phase 4.1: Cell Execution Protocol Base
1. Create `lynx/mcp/cell/execution/base.py` with:
   - `ExecutionRecord` model
   - `ExecutionStorage` interface
   - `execute_cell_tool()` shared function
   - Execution validation logic

### Phase 4.2: First Cell MCP (`docs.cell.draft.submit_for_approval`)
1. Implement `docs.cell.draft.submit_for_approval` handler
2. Register tool in MCP server
3. Add integration tests

### Phase 4.3: Second Cell MCP (`workflow.cell.draft.publish`)
1. Implement `workflow.cell.draft.publish` handler
2. Register tool in MCP server
3. Add integration tests

### Phase 4.4: Third Cell MCP (`vpm.cell.payment.execute`)
1. Implement `vpm.cell.payment.execute` handler
2. Register tool in MCP server
3. Add integration tests

### Phase 4.5: Test Suite
1. Create `tests/integration/test_cell_execution.py`
2. Implement 6 core tests:
   - `test_cell_denies_unapproved_draft`
   - `test_cell_executes_only_for_same_tenant`
   - `test_cell_is_idempotent`
   - `test_cell_logs_started_and_completed_audit_events`
   - `test_cell_refuses_on_policy_fail`
   - `test_cell_refuses_on_permission_fail`
3. Add tool-specific tests for each Cell MCP

---

## Approval

**Decision Status:** ✅ **APPROVED**

**Approved By:** Development Team  
**Approval Date:** 2026-01-27

---

## References

- PRD-LYNX-003: HYBRID BASIC PRD
- ADR-LYNX-001: MCP Architecture Decision
- TSD-LYNX-001: Technical Specification Document
- Draft Protocol: `lynx/mcp/cluster/drafts/base.py`

