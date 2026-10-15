# ADR-001: Persistent Marker Objects

**Date**: 2025-12-06  
**Status**: Accepted  
**Context**: PySide6 migration refactor, incremental updates architecture

---

## Context

The interactive editor allows users to drag markers to edit primitive values. Currently, the system destroys and recreates all marker objects on every edit operation, taking 200-500ms when it should take <50ms.

### Current Behavior
```python
def display_primitives(self):
    # Clear everything
    for ax in self.axes:
        ax.clear()
    
    # Recreate all 50 markers
    for event_idx, event in enumerate(self.model.events):
        for prim in ['v', 'r', 'f', 'a', 'S']:
            marker = DraggablePoint(ax, event_idx, event[prim], ...)
            # Marker object is created but not stored
```

Called on every edit → 50 marker creations × ~10ms = 500ms overhead

### Performance Impact
- **Current (50 events)**: 200-500ms per edit ❌
- **Projected (1000 events)**: 4000-10000ms per edit ❌ (unusable)
- **State loss**: Double-click arming state lost on marker recreation

---

## Decision

**Store marker objects in a persistent dictionary and update them incrementally instead of recreating on every edit.**

### Implementation
```python
class PrimitivePanel:
    def __init__(self):
        self._markers = {}  # {(event_idx, prim): DraggablePoint}
    
    def display_primitives(self):
        """Full rebuild - only on initialization."""
        self._markers.clear()
        
        for event_idx, event in enumerate(self.model.events):
            for prim in ['v', 'r', 'f', 'a', 'S']:
                marker = DraggablePoint(ax, event_idx, event[prim], ...)
                self._markers[(event_idx, prim)] = marker  # Store
    
    def update_marker(self, event_idx, prim, value, is_modified):
        """Incremental update - on every edit."""
        marker = self._markers[(event_idx, prim)]
        marker.update_position(value)
        marker.set_modified(is_modified)
        self.canvas.draw_idle()
```

---

## Rationale

### Why Persistent Objects?

**1. Performance**
- Creating DraggablePoint is expensive (~10ms each)
- Updating existing marker is cheap (<1ms)
- O(1) incremental update vs O(n) full rebuild

**2. State Preservation**
- DraggablePoint maintains double-click state (`_click_count`)
- Hover state, selection state preserved across updates
- No need to reconstruct state after every edit

**3. Memory Efficiency**
- One-time allocation: 50 markers × ~1KB = 50KB
- Recreating: 50 markers × 100 edits = 5000 allocations
- Reduces GC pressure

**4. Architecture Alignment**
- Follows P4 (Persistent Objects principle)
- Follows P3 (Incremental Updates principle)
- Enables scaling to 1000+ events

---

## Alternatives Considered

### Alternative 1: Keep Full Rebuilds, Optimize Creation
**Approach**: Make DraggablePoint creation faster

**Pros**:
- Minimal code changes
- Simple architecture

**Cons**:
- Fundamental O(n) operation can't become O(1)
- Still loses state on every edit
- Doesn't scale to 1000 events
- GC pressure from repeated allocations

**Decision**: Rejected - doesn't solve root problem

---

### Alternative 2: Partial Rebuilds
**Approach**: Only rebuild markers for modified events

**Pros**:
- Better than full rebuild
- Somewhat simpler than full persistence

**Cons**:
- Still O(k) where k = number of modified events
- Loses state on edits
- Doesn't scale if many events modified
- More complex than true incremental updates

**Decision**: Rejected - complexity without full benefits

---

### Alternative 3: Virtual Rendering
**Approach**: Only render markers in visible viewport

**Pros**:
- Scales to unlimited events
- Minimal memory footprint

**Cons**:
- Much more complex to implement
- Requires viewport management, scroll handling
- Overkill for current 50 events
- Can add later on top of persistent markers

**Decision**: Deferred to Phase 2.1 (1000+ events)

---

## Consequences

### Positive

**Performance**: Edit operations become <50ms (10x faster)
```python
# Before: 200-500ms
controller.on_primitive_value_changed(5, 'r', 0.85)

# After: <50ms
controller.on_primitive_value_changed(5, 'r', 0.85)
```

**Scaling**: O(1) operations work at any scale
- 50 events: <50ms ✅
- 1000 events: <50ms ✅
- 10,000 events: <50ms ✅ (rendering may need virtualization)

**State Preservation**: Double-click works reliably
- No more "sometimes double-click doesn't work"
- Hover effects persist correctly
- Selection state maintained

**Architecture Health**: Violates fewer principles
- P3 (Incremental Updates): ❌ → ✅
- P4 (Persistent Objects): ❌ → ✅
- P7 (Observable Flow): ❌ → ✅

---

### Negative

**Complexity**: Must manage object lifecycle
- When to create markers: initialization, file reload
- When to update markers: edits, resets
- When to destroy markers: event deletion, file close

**Memory**: Objects persist even when not visible
- 1000 events × 5 primitives = 5000 markers × ~1KB = 5MB
- Acceptable for Phase 2.1, may need virtualization for Phase 2.2 (10,000+ events)

**Error Handling**: Must handle missing markers gracefully
```python
def update_marker(self, event_idx, prim, value, is_modified):
    if (event_idx, prim) not in self._markers:
        logger.error(f"Marker {event_idx}, {prim} not found")
        # Rebuild or ignore?
```

**Testing**: More state to validate
- Must test marker persistence
- Must test lifecycle management
- Must test memory leaks

---

## Implementation Risks

### High Risk: Lifecycle Management
**Issue**: Markers must be created before first update, destroyed when no longer needed

**Mitigation**:
- Clear initialization: `display_primitives()` creates all markers
- Explicit cleanup: `clear_markers()` destroys all markers
- Defensive update: Check marker exists before updating

---

### Medium Risk: Memory Leaks
**Issue**: Markers hold references to matplotlib artists, may prevent GC

**Mitigation**:
- Test memory usage after 100 operations
- Explicit cleanup in `clear_markers()`
- Profiling with `psutil` to detect leaks

---

### Low Risk: Synchronization
**Issue**: `_markers` dict must stay in sync with Model state

**Mitigation**:
- Controller is single point of update
- Model is single source of truth for data
- Panel is pure view of Model state

---

## Validation

### Performance Test
```python
def test_persistent_marker_performance():
    times = []
    for i in range(10):
        start = time.perf_counter()
        controller.on_primitive_value_changed(5, 'r', 0.5 + i*0.01)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    
    avg = sum(times) / len(times)
    assert avg < 0.050, f"Average {avg*1000:.1f}ms exceeds 50ms target"
```

### Persistence Test
```python
def test_marker_identity_persists():
    marker_before = panel._markers[(5, 'r')]
    id_before = id(marker_before)
    
    controller.on_primitive_value_changed(5, 'r', 0.85)
    
    marker_after = panel._markers[(5, 'r')]
    id_after = id(marker_after)
    
    assert id_before == id_after, "Marker was recreated"
```

### Memory Test
```python
def test_no_memory_leaks():
    baseline = process.memory_info().rss / 1024 / 1024
    
    for i in range(100):
        controller.on_primitive_value_changed(5, 'r', 0.5 + (i % 10) * 0.01)
    
    after = process.memory_info().rss / 1024 / 1024
    growth = after - baseline
    
    assert growth < 10, f"Memory leak: {growth:.1f}MB growth"
```

---

## Related Decisions

- **ADR-002**: Single Source of Truth (Model as authority)
- **Future**: Virtualized rendering (Phase 2.1, 1000+ events)

---

## References

- `docs/architecture/01_PRINCIPLES.md` - P4: Persistent Objects
- `docs/architecture/02_INFORMATION_FLOW.md` - Target flow with incremental updates
- `docs/architecture/04_API_CONTRACTS.md` - `update_marker()` contract
- `docs/architecture/07_PERFORMANCE_TARGETS.md` - <50ms target
- `docs/architecture/refactors/2025-12-06_incremental_updates.md` - Full refactor plan

---

**Decision Maker**: Architecture team  
**Stakeholders**: Performance, UX, Scaling  
**Review Date**: After Phase 2.1 (1000 events) - reassess if virtualization needed
