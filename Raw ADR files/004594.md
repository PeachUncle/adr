# UI Architecture Cleanup Plan

**Date:** December 7, 2025  
**Status:** Planned - To be executed after Phase 2.2 stable tag  
**Priority:** HIGH - Foundation for future feature development  

---

## Executive Summary

The current interactive editor UI has **mixed communication patterns** and **loose coupling** that makes changes difficult and error-prone. While functionality works, the architecture needs cleanup before adding advanced features (sensitivity analysis, predictive control, etc.).

**Core Issues:**
1. Three different communication patterns (signals, callbacks, direct references)
2. Views directly access controller and model (violates MVC)
3. Circular and hard-to-trace event flow
4. Unclear responsibility boundaries

---

## Current Architecture Problems

### Problem 1: Mixed Communication Patterns

The code uses **THREE** different communication mechanisms:

**Qt Signals (proper pattern):**
```python
# In primitive_panel_pyqtgraph.py
self.primitive_changed.emit(index, primitive, new_value)
self.diagnostic_marker_placed.emit(nearest_idx, prim, clicked_value)

# In interactive_editor.py
self.primitive_panel.primitive_changed.connect(self._on_primitive_changed)
```

**Callback Functions (inconsistent):**
```python
# In interactive_editor.py
self.primitive_panel.on_primitive_preview = self._on_primitive_preview
self.primitive_panel.on_primitive_reset = self._on_primitive_reset

# In primitive_panel_pyqtgraph.py
if self.on_primitive_preview:
    self.on_primitive_preview(index, primitive, new_value)
```

**Direct References (coupling violation):**
```python
# In controller.py
self.primitive_panel.controller = self

# In primitive_panel_pyqtgraph.py
if self.controller and index in self.controller.model.modified_primitives:
    # View directly accessing model through controller
```

**Impact:** Developers must remember which pattern to use where. Changes require searching multiple files. Hard to test components in isolation.

---

### Problem 2: Tight Coupling - Views Access Model Directly

**Current (Wrong):**
```python
# controller.py line 48
self.primitive_panel.controller = self

# primitive_panel_pyqtgraph.py line 757
if self.controller and index in self.controller.model.modified_primitives:
    # View is reading model state directly
```

**Why This Is Bad:**
- View has knowledge of model's internal structure (`modified_primitives`)
- Can't test view without a controller and model
- Can't swap model implementation without changing view
- Violates MVC principle: Views should only know about what they display

---

### Problem 3: Circular Event Flow

**Example: User drags a marker**
```
1. User drags marker in primitive panel
2. PrimitivePanel._on_drag_end() called
3. Checks self.controller.model.modified_primitives (direct access)
4. Calls self.on_primitive_preview() (callback function)
5. Calls Controller.on_primitive_preview()
6. Controller updates model
7. Emits primitive_changed signal
8. Controller.on_primitive_changed() receives signal (connected in __init__)
9. Controller tells view to update
```

**Problems:**
- Flow goes: View → Controller → View → Controller → View
- Hard to debug (callbacks + signals + direct calls)
- Can't trace execution path without stepping through multiple files

---

### Problem 4: Gauge-Based Primitive Editing (Planned v2.4 Fix)

**Current Implementation:**
- Primitive values edited by dragging gauges
- Imprecise (hard to set exact values like 7.2)
- Multiple gauge widgets increase UI complexity

**Planned Solution: Spinbox Primitive Editor**

**Architecture:**
```python
# Single shared spinbox widget
class PrimitiveSpinboxWidget(QWidget):
    value_changed = Signal(float)  # Clean signal interface
    
    def __init__(self):
        self.spinbox = QDoubleSpinBox()
        self.label = QLabel("Editing: (none)")
        self.active_primitive = None
        self.active_event_id = None
    
    def set_active_primitive(self, primitive_name, event_id, current_value):
        """Called when user clicks primitive label/marker"""
        self.active_primitive = primitive_name
        self.active_event_id = event_id
        self.label.setText(f"Editing: {primitive_name}")
        self.spinbox.setValue(current_value)
        self.spinbox.setEnabled(True)
    
    def clear_active(self):
        """Called when event deselected or no primitive active"""
        self.active_primitive = None
        self.active_event_id = None
        self.label.setText("Editing: (none)")
        self.spinbox.setEnabled(False)

# In controller
class EditorController:
    def __init__(self):
        self.active_primitive_state = {
            'primitive': None,  # 'v', 'r', 'f', 'a', 'S'
            'event_id': None,
            'event_time': None
        }
    
    def on_primitive_selected(self, primitive_name, event_id):
        """Update active primitive tracking"""
        event_time = self.model.events[event_id]['time']
        current_value = self.model.get_primitive_value(event_id, primitive_name)
        
        self.active_primitive_state = {
            'primitive': primitive_name,
            'event_id': event_id,
            'event_time': event_time
        }
        
        # Update spinbox widget
        self.spinbox_widget.set_active_primitive(
            primitive_name, event_id, current_value
        )
        
        # Log to State Viewer
        self.state_log.log_primitive_selection(
            event_id=event_id,
            primitive=primitive_name,
            value=current_value
        )

# Signal flow (clean, unidirectional)
PrimitiveLabel.clicked → Controller.on_primitive_selected() → SpinboxWidget.set_active_primitive()
SpinboxWidget.value_changed → Controller.on_spinbox_value_changed() → Model.update_primitive()
Model.data_changed → Controller.update_views() → SpinboxWidget.setValue() [if still active]
```

**Benefits:**
- Single communication pattern (Qt signals only)
- No circular dependencies (unidirectional flow)
- Testable in isolation (mock signals)
- Clear state ownership (controller tracks active primitive)
- Label architecture matches gamma_self plot pattern

**Integration Points:**
- Event selection: Existing event marker click mechanism
- Primitive selection: Click primitive label/marker
- Event Insertion Points: Hooks into same active primitive tracking
- Ctrl+Shift+Click: Modified events work same as normal events
- M1/M2 switching: Preserves active primitive name, updates value
- State Viewer: Logs all primitive selections and value changes

**State Viewer Logging:**
```python
# Selection logging
[PRIMITIVE_SELECT] perspective=M1, event_id=2, day=2.0, primitive=v, value=5.5

# Value change logging
[PRIMITIVE_EDIT] perspective=M1, event_id=2, day=2.0, primitive=v, old=5.5, new=7.2
```

**Gauge Removal:**
- Remove all gauge widget code after spinbox functional
- Optionally keep read-only primitive value labels for quick reference
- Alternative: Remove labels entirely (spinbox is only display)

**See:** [INTERACTIVE_EDITOR_CHANGELOG.md - v2.4-spinbox-primitive-editor](../INTERACTIVE_EDITOR_CHANGELOG.md#v24-spinbox-primitive-editor-planned)
- Difficult to add logging/telemetry

---

### Problem 4: Unclear Responsibilities

**Who creates connections?**
- `InteractiveEditor` connects some signals (line 77-78)
- `Controller` is passed panel references but doesn't own them
- Panels have callbacks set externally

**Who owns the data flow?**
- Controller orchestrates updates
- But views also call controller methods directly
- And views check model state directly

**Who decides when to update?**
- Controller schedules recomputation
- But views also trigger immediate updates
- Debouncing logic split between controller and views

---

## Proposed Solution: Clean MVC Architecture

### Principle 1: Single Communication Pattern - Qt Signals Only

**Remove all callback functions:**
```python
# DELETE these from views:
self.on_primitive_preview = None
self.on_primitive_reset = None
```

**Convert to Qt signals:**
```python
# In primitive_panel_pyqtgraph.py
class PrimitivePanelPyQtGraph(QWidget):
    # Existing
    primitive_changed = Signal(int, str, float)
    diagnostic_marker_placed = Signal(int, str, float)
    
    # NEW - convert callbacks to signals
    primitive_preview_requested = Signal(int, str, float)
    primitive_reset_requested = Signal(int, str)
```

**Benefits:**
- One consistent pattern throughout codebase
- Qt's signal/slot system is debuggable (can inspect connections)
- Signals are thread-safe and queue-able
- Standard pattern familiar to Qt developers

---

### Principle 2: Strict MVC Separation

**Model (Pure Data):**
```python
class EditorModel:
    """
    Pure data model - no UI knowledge.
    Emits signals when data changes.
    """
    # Signals
    events_changed = Signal()
    baseline_changed = Signal()
    trajectory_computed = Signal(list)  # gamma_self points
    
    # NO references to views or controller
    # NO Qt widget imports
```

**View (Pure UI):**
```python
class PrimitivePanelPyQtGraph(QWidget):
    """
    Pure UI - emits signals, receives update commands.
    """
    # Signals OUT (user actions)
    primitive_changed = Signal(int, str, float)
    diagnostic_marker_placed = Signal(int, str, float)
    
    # Public methods IN (display updates)
    def update_from_events(self, events: List[Event]):
        """Update display from event data."""
        pass
    
    # NO self.controller
    # NO self.model
    # NO business logic
```

**Controller (Coordination):**
```python
class EditorController:
    """
    Connects model and views.
    Handles all business logic.
    """
    def __init__(self, model, primitive_panel, trajectory_panel):
        self.model = model
        self.primitive_panel = primitive_panel
        self.trajectory_panel = trajectory_panel
        
        # Connect view signals to controller methods
        self.primitive_panel.primitive_changed.connect(self.on_primitive_changed)
        
        # Connect model signals to view updates
        self.model.events_changed.connect(self._update_primitive_panel)
        self.model.trajectory_computed.connect(self._update_trajectory_panel)
    
    # NO panel.controller = self
    # NO view.model = model
```

---

### Principle 3: Clear Data Flow

**One Direction: View → Controller → Model → Controller → View**

```
User Action (drag marker)
  ↓
View emits signal: primitive_changed(index, primitive, value)
  ↓
Controller receives signal: on_primitive_changed()
  ↓
Controller updates model: model.set_primitive(index, primitive, value)
  ↓
Model emits signal: events_changed()
  ↓
Controller receives signal: _update_primitive_panel()
  ↓
Controller updates view: primitive_panel.update_from_events(model.events)
  ↓
View renders new state
```

**No backwards flow, no circular references, no direct access.**

---

### Principle 4: Remove Direct References

**Current (Wrong):**
```python
# controller.py
self.primitive_panel.controller = self

# primitive_panel_pyqtgraph.py
if self.controller and index in self.controller.model.modified_primitives:
```

**Proposed (Correct):**
```python
# controller.py - pass data as signals/parameters
def _update_primitive_panel(self):
    modified = self.model.modified_primitives
    self.primitive_panel.set_modified_markers(modified)

# primitive_panel_pyqtgraph.py - receive data as parameters
def set_modified_markers(self, modified_indices: dict):
    """Display which events have modifications."""
    self._modified_indices = modified_indices
    self._update_marker_styles()
```

**View never accesses controller or model - only receives data.**

---

## Implementation Plan

### Phase 1: Add Missing Signals (Low Risk)
**Files:** `primitive_panel_pyqtgraph.py`, `trajectory_panel_pyqtgraph.py`

1. Add new signals for all callback patterns:
   - `primitive_preview_requested = Signal(int, str, float)`
   - `primitive_reset_requested = Signal(int, str)`

2. Emit new signals alongside existing callbacks (parallel implementation)

3. Test that both old and new patterns work

**Risk:** Low - additive only, doesn't break existing code

---

### Phase 2: Update Controller Connections (Medium Risk)
**Files:** `interactive_editor.py`, `controller.py`

1. Connect new signals in controller:
   ```python
   self.primitive_panel.primitive_preview_requested.connect(self.on_primitive_preview)
   self.primitive_panel.primitive_reset_requested.connect(self.on_primitive_reset)
   ```

2. Remove callback assignments:
   ```python
   # DELETE:
   self.primitive_panel.on_primitive_preview = self._on_primitive_preview
   self.primitive_panel.on_primitive_reset = self._on_primitive_reset
   ```

3. Test all user interactions still work

**Risk:** Medium - changing wiring, but functionality unchanged

---

### Phase 3: Remove Direct Model Access (High Risk)
**Files:** `controller.py`, `primitive_panel_pyqtgraph.py`

1. Add controller method to provide modified state:
   ```python
   # controller.py
   def _update_modified_markers(self):
       modified = self.model.modified_primitives
       self.primitive_panel.set_modified_markers(modified)
   ```

2. Add view method to receive state:
   ```python
   # primitive_panel_pyqtgraph.py
   def set_modified_markers(self, modified_indices: dict):
       self._modified_indices = modified_indices
   ```

3. Update view code to use local cached state:
   ```python
   # REPLACE:
   if self.controller and index in self.controller.model.modified_primitives:
   
   # WITH:
   if index in self._modified_indices:
   ```

4. Remove controller reference:
   ```python
   # DELETE from controller.py:
   self.primitive_panel.controller = self
   ```

5. Comprehensive testing of all marker states

**Risk:** High - changes data access patterns, could break marker display

---

### Phase 4: Cleanup and Documentation (Low Risk)

1. Remove unused callback function definitions:
   ```python
   # DELETE from views:
   self.on_primitive_preview = None
   self.on_primitive_reset = None
   ```

2. Update docstrings to reflect signal-based architecture

3. Add architecture diagram to docs

4. Update developer guide with MVC patterns

**Risk:** Low - cleanup only

---

## Testing Strategy

### Unit Tests
- **Model tests:** Pure data operations, no UI imports
- **View tests:** Signal emission on user actions (no controller needed)
- **Controller tests:** Mock model and views, verify connections

### Integration Tests
- Load scenario → verify all panels update
- Drag marker → verify model updated, trajectory recomputed
- Diagnostic marker → verify counterfactual preview works
- Undo/redo → verify state consistency

### Manual Testing Checklist
- [ ] Drag committed marker → baseline updates
- [ ] Drag diagnostic marker → preview trajectory shown
- [ ] Reset marker → returns to baseline
- [ ] Lock event → marker becomes non-draggable
- [ ] Insert event → new markers appear
- [ ] Delete event → markers removed, indices update
- [ ] Shift+click → diagnostic marker placed
- [ ] Save scenario → modifications persist
- [ ] Undo/redo → all states correct

---

## Benefits After Refactoring

### For Development:
- **Easier to add features:** New signals just get connected, no hunting for callbacks
- **Easier to debug:** Single signal pathway, can use Qt's signal spy
- **Easier to test:** Components fully isolated, can test independently
- **Easier to understand:** Standard MVC pattern, no special cases

### For Future Features:
- **Sensitivity analysis panel:** Just connects to existing model signals
- **Predictive control:** New controller logic, views unchanged
- **Multi-scenario comparison:** Multiple models, same views
- **Remote collaboration:** Network layer sits between controller and model

### For Maintainability:
- **Clear contracts:** Signals define interfaces between components
- **Safe refactoring:** Change model internals without touching views
- **Parallel development:** Different developers can work on model/view/controller independently
- **Documentation:** Signal signatures document data flow

---

## Risks and Mitigation

### Risk 1: Breaking Existing Functionality
**Mitigation:** Incremental implementation with parallel paths (keep old code until new verified)

### Risk 2: Regression in User Experience
**Mitigation:** Comprehensive manual testing checklist, compare before/after screen recordings

### Risk 3: Increased Complexity (More Signals)
**Mitigation:** Signals are self-documenting, better than hidden callbacks

### Risk 4: Time Investment
**Mitigation:** This is foundational work - pay now or pay 10x later when adding features

---

## Timeline Estimate

- **Phase 1 (Add signals):** 2-3 hours
- **Phase 2 (Update connections):** 2-3 hours  
- **Phase 3 (Remove direct access):** 4-6 hours
- **Phase 4 (Cleanup/docs):** 2-3 hours
- **Testing:** 4-6 hours

**Total:** 14-21 hours of focused work

**Recommendation:** Do this BEFORE adding sensitivity analysis or predictive features. Otherwise, those features will inherit the same architectural problems and be equally difficult to maintain.

---

## Success Criteria

### Code Quality:
- [ ] Zero callback functions in views
- [ ] Zero `self.controller` references in views
- [ ] Zero `view.model` or `view.controller.model` access
- [ ] All communication via Qt signals only

### Functionality:
- [ ] All existing features work identically
- [ ] No performance regression
- [ ] All manual tests pass

### Architecture:
- [ ] Model has zero UI imports
- [ ] Views have zero model/controller references
- [ ] Controller is only place where model and views connect
- [ ] Data flow is unidirectional and traceable

---

## Alternative: Don't Refactor (Risk Assessment)

**If we skip this refactoring:**

**Short-term (next 1-2 features):**
- Development will be slower (searching multiple files for connections)
- More bugs (unclear data flow makes mistakes easy)
- Harder code reviews (reviewers must understand multiple patterns)

**Medium-term (3-5 features):**
- Technical debt compounds (new features copy existing bad patterns)
- Increasing difficulty adding features (more interconnected spaghetti)
- Testing becomes nearly impossible (can't isolate components)

**Long-term (production use):**
- Maintenance nightmare (fixing bugs requires understanding entire system)
- Can't safely refactor (too many hidden dependencies)
- Difficult to onboard new developers (non-standard architecture)
- Hard to extend for robotics/AI applications (coupling prevents modularity)

**Recommendation:** Refactor now while codebase is still manageable (800-line files, not 3000-line files).

---

## Questions for Review

1. **Scope:** Should we refactor both primitive_panel AND trajectory_panel, or just primitive_panel first?
2. **Timing:** Do this before or after v2.2 stable tag?
3. **Testing:** Add automated tests during refactoring, or manual testing sufficient?
4. **Documentation:** Create architecture diagrams showing signal flow?
5. **Validation:** Should we have another AI review the refactored code for quality?

---

## Related Documents

- `docs/architecture/decisions/ADR-001-persistent-markers.md` - Marker lifecycle decisions
- `docs/interactive_editor_user_guide.md` - User-facing features (unchanged by refactoring)
- `docs/architecture_recommendations.md` - Architecture migration rationale

---

## Notes

This refactoring is **foundational infrastructure work** for the GRP project, which aims to be the open-source standard for relational AI. The code quality must be high enough for:
- Production robotics applications
- Clinical therapy tools
- Research validation by psychology/AI communities
- Long-term maintenance by future developers (human and AI)

Current architecture works but doesn't meet these standards. Clean architecture now = sustainable development later.
