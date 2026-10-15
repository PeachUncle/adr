# ADR-012: De-stub Mirror/TRI Integration
**Status**: Accepted
**Date**: 2025-09-24
**Deciders**: Nova Architecture Team

## Context
Slots 03, 05, and 08 contained outdated TODO comments referencing missing Semantic Mirror and TRI adapter functionality. These components have been operational since Phase 3 but slots continued using environment variable stubs instead of real integration.

**Problem**:
- Slot03 used `SLOT07_PHASE_LOCK` env var instead of Semantic Mirror pressure readings
- Slot05 used `TRI_COHERENCE` env var instead of TRI_REPORT@1 contract calls
- Slot08 used similar phase_lock stubs instead of mirror-aware repair sensitivity

**Evidence of readiness**:
- `orchestrator/semantic_mirror.py` fully implemented with `get_semantic_mirror()` API
- Slot4 produces `TRI_REPORT@1` with coherence data
- Slot7 publishes `slot07.pressure_level` via Semantic Mirror
- Enhanced adapters already demonstrate mirror consumption patterns

## Decision
**Replace environment variable stubs with real Semantic Mirror and TRI adapter integration** across Slots 03, 05, and 08.

### Implementation approach
1. **Priority hierarchy**: TRI phase coherence > Slot7 pressure modulation > env fallbacks > conservative defaults
2. **API compatibility**: Support both `get_context(key, requester)` and `get_context(key, default=...)` signatures
3. **Graceful degradation**: Maintain env var fallbacks and conservative defaults for production safety
4. **Observability**: Add metrics for mirror reads vs fallback usage

### Specific changes
- **Slot03**: Phase lock from mirror pressure modulation [0.45..0.60] range
- **Slot05**: TRI signals from `slot04.coherence` and `slot04.phase_jitter`
- **Slot08**: Repair sensitivity from pressure-aware phase lock [0.40..0.60] range

## Consequences
### Positive
- **Better inter-slot coordination**: Real-time pressure/coherence awareness
- **Removes technical debt**: Eliminates outdated TODO comments and stubs
- **Maintains safety**: Graceful fallbacks preserve production stability
- **Enables observability**: Mirror usage metrics for health monitoring

### Negative
- **Minor complexity**: API compatibility shims required
- **Dependency risk**: Mirror import failures need handling
- **Testing overhead**: Integration test coverage for fallback paths

### Risks & Mitigations
- **Semantic Mirror unavailable** → **Mitigation**: Conservative fallbacks
- **API signature changes** → **Mitigation**: Compatibility shim pattern
- **Performance impact** → **Mitigation**: Lazy imports, cached instances

## Validation
**Test coverage**: 17 new integration tests, 167 total tests passing (2 skipped)
- Slot03: 6 mirror integration scenarios
- Slot05: 5 TRI adapter scenarios
- Slot08: 6 repair sensitivity scenarios

**Rollback mechanism**: `NOVA_USE_SEMANTIC_MIRROR=0` flag for instant disable

## Implementation Notes
- Created `orchestrator/mirror_utils.py` for centralized compatibility patterns.
- Added CI guard `scripts/guards/no-mirror-tri-stubs.sh` to prevent regression.
- All slots maintain `NOVA_LIGHTCLOCK_DEEP=0` disable capability.

## References
- META_LENS_TETHER_CONFIRMATION.md — Architectural integration patterns
- `orchestrator/semantic_mirror.py` — Mirror implementation
- `src/nova/slots/slot04_tri_engine/` (legacy shim namespace) - TRI_REPORT@1 contract source
