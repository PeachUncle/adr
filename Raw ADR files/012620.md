# ADR-017: Context-Aware Routing for Semantic Detection

**Status:** Accepted
**Date:** 2025-12-19
**Phase:** 17.3 / 18
**Related Specs:**
- `docs/specs/phase16_agency_pressure_primitives.md`
- `docs/specs/phase17_0_consent_gate_overview.md`
- `docs/specs/phase17_1_consent_gate_retrospective_tests.md`
- `docs/specs/phase17_2_consent_gate_implementation.md`
- `docs/architecture/context_routing_rule.md`
- `docs/audits/context_availability_audit_phase17_pattern.md`

---

## 1. Context

Phase 16 introduced **agency pressure primitives** (Decision Substitution, Scope Expansion, etc.) with structure-only detection that operates on single turns without conversation history. This naive detection produced:

- **High recall**: Catches all instances of primitive patterns
- **False positives**: Cannot distinguish invited vs uninvited delegation

**RT-862 falsified naive detection:**
```
User: "I need help setting up the CI/CD pipeline"
Assistant: "I'll handle the Docker configuration for you."

Naive A_p = 1.0 (Decision Substitution detected)
Reality: User explicitly requested help → invited delegation
```

Phase 17 introduced **consent gate modules** (invitation signals, revocation signals, scope validator) but deferred integration due to a discovered invariant:

> **Consent checking requires conversation history, but the orchestrator doesn't track conversations yet.**

Phase 17.3/18 resolved this by:
1. Building conversation session management infrastructure
2. Implementing context-aware routing that combines Phase 16 detection with Phase 17 consent checks
3. Proving the architectural separation: Detection (context-blind) → Routing (context-aware) → Governance

---

## 2. Weakest Assumption

The **weakest assumption** underlying this ADR is:

> Structural detection patterns (Phase 16 primitives, Slot02 manipulation patterns) cannot reliably distinguish invited/authorized actions from uninvited/unauthorized ones without conversational context.

If future work discovers a purely structural signal that achieves this distinction without context, the routing layer could be simplified—but the separation of concerns (detection vs routing) would remain valuable.

---

## 3. Decision

We adopt a **three-layer architecture for semantic detection**:

### Layer 1: Detection (context-blind, structure-only)
- **What**: Pattern matching on single artifacts (turns, deltas, events)
- **Input**: Single turn content only
- **Output**: List of detected primitives/patterns (structure-only)
- **Properties**:
  - Fast, stateless, purely syntactic
  - No conversation history required
  - No intent inference
  - High recall, tolerates false positives
- **Implementation**: Phase 16 primitives, Slot02 manipulation patterns

### Layer 2: Routing (context-aware, consent/authorization checks)
- **What**: Evaluates detected patterns against conversational context
- **Input**: Detected primitives + conversation history + turn content
- **Output**: Filtered list of uninvited/unauthorized primitives only
- **Properties**:
  - Stateful, requires conversation history
  - Checks authorization (invitation signals, revocations, scope boundaries, temporal validity)
  - Filters false positives structurally (no intent guessing)
  - Fail-safe: ambiguous cases treated as uninvited
- **Implementation**: Phase 17 consent gate, Phase 17.3 integration layer

### Layer 3: Governance (receives gated signals)
- **What**: Makes regime decisions based on clean, gated signals
- **Input**: Uninvited primitives + provenance metadata + session context
- **Output**: Governance actions (regime shifts, attestations, alerts)
- **Properties**:
  - No re-interpretation of routing decisions
  - Receives only signals that passed consent gate
  - Operates on aggregated metrics (A_p, harm_status)
- **Implementation**: Slot07 governance engine

### Contracts

**Canonical turn stream:**
```python
conversation_history: List[Dict[str, str]] = [
    {"role": "user", "content": str},
    {"role": "assistant", "content": str},
]
```

**Routing function signature:**
```python
def analyze_turn_with_consent_gate(
    turn_content: str,
    conversation_history: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Returns:
        primitives_detected: List[str]      # All primitives (Phase 16)
        primitives_uninvited: List[str]     # Only uninvited (Phase 17 gate)
        consent_results: List[GateResult]   # Provenance
        is_pressured: bool                  # True if any uninvited
    """
```

### Feature Flags

- `NOVA_ENABLE_CONSENT_GATE=0` (default off): Enables Phase 17 consent gate
- `NOVA_ENABLE_CONVERSATION_HISTORY=0` (default off): Enables conversation session tracking

When disabled: Falls back to naive detection with metadata indicating uncertain classification.

---

## 4. Rationale

### 4.1 Why Separate Detection from Routing?

**Architectural clarity:**
- Detection is a signal generator (fast, stateless, reusable)
- Routing is a filter (stateful, context-dependent, authorization-aware)
- Mixing them creates coupling and contamination

**Phase 16 stays sealed:**
- Primitive detection remains context-blind by design
- No conversation history at detection time
- No semantic interpretation or intent inference
- Can be tested, validated, and versioned independently

**Routing owns context:**
- Conversation history lives at orchestrator layer
- Authorization/consent logic separated from pattern matching
- False positive filtering happens structurally (no guessing)

**Governance receives clean signals:**
- No ambiguity about what "pressured" means
- Provenance metadata enables audit
- Regime decisions based on vetted signals only

### 4.2 Why Not Build Context into Detection?

Considered and rejected:
- Violates single responsibility (detection does pattern matching, not authorization)
- Creates tight coupling (detection layer needs orchestrator infrastructure)
- Prevents reuse (detection becomes conversation-specific)
- Complicates testing (can't validate detection without mock conversations)

### 4.3 Why Fail Closed on Ambiguity?

If consent is unclear (e.g., temporal decay boundary case), we treat the primitive as uninvited:
- Prevents false negatives in safety-critical scenarios
- Conservative approach aligns with harm prevention
- Operator can always review and override governance decisions

---

## 5. Consequences

### 5.1 Positive

- **RT-862 false positives eliminated**: Invited delegation no longer flagged as pressured
- **Clean separation of concerns**: Detection, routing, and governance are independently testable
- **No upstream contamination**: Phase 16 primitives remain sealed and context-blind
- **Reusable pattern**: Same architecture applies to Slot02 manipulation patterns, future semantic detectors
- **Rollback trivial**: Feature flags allow instant reversion to naive detection
- **Provenance built-in**: Every gated signal carries metadata explaining why it was flagged

### 5.2 Risks / Trade-offs

- **Added complexity**: Three-layer architecture vs single-layer naive detection
- **Runtime dependency**: Routing requires conversation history infrastructure
- **Performance**: Additional consent checks per primitive (mitigated by feature flags)
- **Maintenance**: Two subsystems (Phase 16 + Phase 17) must stay synchronized on primitive definitions

### 5.3 Open Questions

- **Slot02 integration**: When to apply same pattern to manipulation pattern detection?
- **Cross-slot signals**: How to route authorization claims between slots?
- **Semantic drift**: Will primitive definitions need context-aware refinement over time?

---

## 6. Validation

### 6.1 Retrospective Tests (Phase 17.1)

Proven by RT-861 through RT-866:

| RT | Scenario | Naive A_p | Gated A_p | Result |
|----|----------|-----------|-----------|---------|
| **RT-862** | Delegation after explicit request | 1.0 (FP) | 0.0 | **Naive falsified** |
| RT-863 | Unsolicited agent initiative | 1.0 | 1.0 | Both correct |
| RT-864 | Scope violation (typo → full rewrite) | 1.0 | 1.0 | Both correct |
| RT-865 | User revokes mid-action | 0.0 → 1.0 | 0.0 → 1.0 | Both correct |
| RT-866 | Temporal decay (20-turn gap) | 0.0 → 1.0 | 0.0 → 1.0 | Both correct |

**Key finding:** Context-aware routing eliminates false positives (RT-862) without introducing false negatives.

### 6.2 Integration Tests (Phase 17.3)

12 integration tests reusing RT scenarios:
- Session management: 4 tests
- Consent gate integration: 4 tests
- Session A_p computation: 2 tests
- Feature flag behavior: 2 tests

**Status:** 12/12 passing

### 6.3 Audit (Context Availability)

Systematic audit of subsystems for similar patterns:
- **Slot02 manipulation patterns**: Context-blind, same failure mode as Phase 16 naive
- Phase 14/15 Temporal USM: Metrics-only, safe
- Slot07 Governance: Aggregates signals, safe if upstream is gated
- Slot09 Distortion: Metrics-only, safe

**Outcome:** Documented Slot02 as candidate for Phase 18+ routing integration.

---

## 7. Implementation

### 7.1 Files Created

**Infrastructure (Phase 17.3/18):**
- `src/nova/orchestrator/conversation/__init__.py`
- `src/nova/orchestrator/conversation/session_manager.py` (234 lines)
- `src/nova/orchestrator/conversation/phase17_integration.py` (209 lines)
- `tests/test_conversation_phase17_integration.py` (300 lines)

**Documentation:**
- `docs/architecture/context_routing_rule.md`
- `docs/audits/context_availability_audit_phase17_pattern.md`
- This ADR

**Configuration:**
- `NOVA_ENABLE_CONVERSATION_HISTORY=0` in `config/.env.example`

### 7.2 Integration Points

**Detection Layer:**
```python
from nova.phase16.primitives import detect_primitives
primitives_detected = list(detect_primitives(turn_content))
```

**Routing Layer:**
```python
from nova.orchestrator.conversation.phase17_integration import (
    analyze_turn_with_consent_gate,
    compute_session_agency_pressure,
)

analysis = analyze_turn_with_consent_gate(turn_content, conversation_history)
# Returns: primitives_detected, primitives_uninvited, consent_results, is_pressured
```

**Governance Layer:**
```python
session_result = compute_session_agency_pressure(conversation_history)
# Returns: A_p, harm_status, pressured_turns, turn_analyses
```

---

## 8. Rollback

If context-aware routing proves problematic:

### 8.1 Feature Flag Rollback (instant)
```bash
# Disable consent gate (revert to naive detection)
export NOVA_ENABLE_CONSENT_GATE=0

# Disable conversation history tracking
export NOVA_ENABLE_CONVERSATION_HISTORY=0
```

### 8.2 Code Rollback (removes infrastructure)
```bash
git revert aa55b00  # Phase 17.3/18 conversation infrastructure
git revert aff7504  # Phase 17.2 consent gate modules (if needed)
```

### 8.3 Fallback Behavior

When consent gate disabled:
- Routing layer returns all detected primitives as "uninvited"
- A_p computation uses naive formula: `A_p = 1.0 if primitives else 0.0`
- Metadata indicates `"mode": "naive"` for audit trails

---

## 9. Future Extensions

### 9.1 Slot02 Manipulation Patterns (Phase 18+ candidate)

Apply same pattern:
```
Slot02 detection (context-blind)
    → Slot02 routing gate (consent-aware)
    → Governance (receives gated manipulation signals)
```

**Prerequisites:**
- Design RT set for manipulation pattern invitation scenarios
- Define consent contract for manipulation primitives
- Feature-flag integration (`NOVA_ENABLE_SLOT02_CONSENT_GATE`)

### 9.2 Signal Provenance Hardening

Extend gated signals with full audit trail:
```python
{
    "primitives_detected": [...],
    "primitives_uninvited": [...],
    "gate_results": [
        {
            "primitive": "Decision Substitution",
            "invited": False,
            "reason": "scope_violation",
            "invitation_turn": None,
            "current_turn": 4,
        }
    ],
    "session_id": "abc123",
    "flag_states": {
        "NOVA_ENABLE_CONSENT_GATE": True,
        "NOVA_ENABLE_CONVERSATION_HISTORY": True,
    }
}
```

### 9.3 Cross-Slot Authorization Routing

When slots make claims about other slots' outputs:
- Routing layer checks inter-slot contracts
- No slot can override another's authorization decisions
- Governance receives conflict signals for operator review

---

## 10. Invariants

This ADR establishes the following invariants:

1. **Detection is context-blind**
   - No conversation history at detection time
   - Structure-only pattern matching
   - No intent inference or semantic interpretation

2. **Routing is context-aware**
   - Conversation history required
   - Authorization/consent checks happen here only
   - Filters false positives, doesn't change detection output

3. **Governance receives gated signals**
   - No direct access to detected-but-uninvited primitives
   - No re-interpretation of routing decisions
   - Operates on aggregated metrics with provenance

4. **Fail-safe defaults**
   - If routing unavailable → naive detection + metadata flag
   - If consent ambiguous → treat as uninvited
   - Feature flags enable instant rollback

5. **No layer contamination**
   - Detection doesn't know about routing
   - Routing doesn't modify detection logic
   - Governance doesn't bypass routing

---

## 11. Related Work

**Phase 16**: Proved structure-only detection is possible (primitives)
**Phase 17.0-17.2**: Proved consent can be checked structurally (invitation/revocation/scope signals)
**Phase 17.3/18**: Proved detection + routing can be integrated without contamination
**Context Audit**: Proved pattern is generalizable to other semantic detectors

**Next**: Apply same pattern to Slot02 manipulation patterns (Phase 18+)

---

## 12. Bottom Line

**Structure-only detection makes semantic claims it cannot verify.**

Context-aware routing completes the picture:
- Eliminates false positives (RT-862)
- Maintains separation of concerns
- Enables audit and rollback
- Applies to any semantic detector making authorization claims

This is an **architectural win**, not just a feature addition.

---

**Commits:**
- Phase 17.2: aff7504
- Phase 17.3/18: aa55b00
