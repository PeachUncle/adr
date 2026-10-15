# Story 2.8 Scope Decision: Progress Tracking

**Decision:** API + Basic Console Output
**Date:** 2025-10-27
**Owner:** Bob (Scrum Master) - Prep Sprint Task #7
**Status:** ✅ APPROVED

---

## Context

Story 2.8 (Optimization Progress Tracking) needs to track and report optimization progress. Two options:

**Option A:** API-only (callback function)
- Progress available via callback for Epic 3 UI integration
- No console output

**Option B:** API + Console (callback + stdout)
- Progress available via callback AND printed to console
- Helps debugging during development

---

## Decision

✅ **Selected: Option B (API + Basic Console Output)**

### Deliverables

**1. Progress Callback API** (Required for Epic 3)

```python
def progress_callback(
    iteration: int,
    best_metric: float,
    improvement_pct: float,
    budget_used: dict,
    time_elapsed: float
) -> None:
    """
    Called every 100 iterations to report progress.

    Args:
        iteration: Current iteration number
        best_metric: Best metric value found so far
        improvement_pct: Percentage improvement vs baseline
        budget_used: {"unallocated": X, "respec": Y}
        time_elapsed: Seconds since optimization started
    """
```

**2. Basic Console Output** (Development aid)

```
Optimization Progress
====================
Iteration 100/1000  | Best: +12.3% DPS | Budget: 8/15 unallocated, 2/12 respec | 15.2s elapsed
Iteration 200/1000  | Best: +15.1% DPS | Budget: 15/15 unallocated, 5/12 respec | 31.8s elapsed
Iteration 300/1000  | Best: +16.8% DPS | Budget: 15/15 unallocated, 8/12 respec | 48.1s elapsed

Converged: No improvement for 3 iterations
Final Result: +16.8% DPS improvement (82.5s total)
```

**Format:**
- One line per 100 iterations
- Simple text output (no fancy progress bars for MVP)
- Can be disabled via `verbose=False` flag

---

## Rationale

### Why API is Required

✅ **Epic 3 Integration**
- Story 3.5 (Optimization Progress Display) consumes this callback
- UI needs live updates without polling
- Callback enables SSE (Server-Sent Events) or AJAX updates

✅ **Testability**
- Unit tests can capture progress events
- Validate progress reporting logic

✅ **Flexibility**
- Callback can be None (headless mode)
- Different UIs can implement different visualizations

### Why Console Output is Beneficial

✅ **Development Debugging**
- Immediately see if optimization is working
- No need to open UI during development
- Faster iteration during Stories 2.1-2.7

✅ **Testing Convenience**
- Integration tests show progress in pytest output
- Easier to diagnose convergence issues
- Performance profiling more visible

✅ **Minimal Cost**
- ~5 lines of code to add print statements
- Negligible performance impact (print every 100 iterations = ~0.001ms overhead)

✅ **CLI Use Case**
- Future: Users may want to run optimizer from command line
- Console output provides immediate feedback
- No UI required for basic usage

### Why Not "Console Only"

❌ **Blocks Epic 3**
- Story 3.5 explicitly requires "real-time progress without page refresh"
- Console output cannot drive UI updates
- Must have callback API

---

## Implementation Details

### Progress Tracker Module

```python
# src/optimizer/progress.py

class ProgressTracker:
    """Tracks and reports optimization progress."""

    def __init__(
        self,
        callback: Optional[Callable] = None,
        verbose: bool = True,
        report_interval: int = 100
    ):
        """
        Args:
            callback: Optional callback function for UI updates
            verbose: If True, print progress to console
            report_interval: Report progress every N iterations
        """
        self.callback = callback
        self.verbose = verbose
        self.report_interval = report_interval
        self.start_time = time.time()

    def update(
        self,
        iteration: int,
        best_metric: float,
        improvement_pct: float,
        budget: BudgetState
    ) -> None:
        """Update progress and report if interval reached."""

        if iteration % self.report_interval != 0:
            return  # Not time to report yet

        time_elapsed = time.time() - self.start_time

        # Invoke callback (for UI)
        if self.callback:
            self.callback(
                iteration=iteration,
                best_metric=best_metric,
                improvement_pct=improvement_pct,
                budget_used={
                    "unallocated": budget.unallocated_used,
                    "respec": budget.respec_used
                },
                time_elapsed=time_elapsed
            )

        # Print to console (for development)
        if self.verbose:
            print(
                f"Iteration {iteration:4d} | "
                f"Best: +{improvement_pct:5.1f}% | "
                f"Budget: {budget.unallocated_used}/{budget.unallocated_available} unallocated, "
                f"{budget.respec_used}/{budget.respec_available or 'unlimited'} respec | "
                f"{time_elapsed:.1f}s elapsed"
            )

    def finalize(self, result: OptimizationResult) -> None:
        """Print final result summary (if verbose)."""
        if self.verbose:
            print(f"\nConverged: {result.convergence_reason}")
            print(
                f"Final Result: +{result.improvement_pct:.1f}% improvement "
                f"({result.time_elapsed_seconds:.1f}s total)"
            )
```

### Usage

```python
# Story 2.1: Hill Climbing
def optimize_build(config: OptimizationConfiguration) -> OptimizationResult:
    # Console output enabled by default
    progress = ProgressTracker(
        callback=config.progress_callback,
        verbose=True  # Can disable via config.verbose=False
    )

    while not converged:
        # ... optimization loop ...

        # Report progress every 100 iterations
        progress.update(iteration, best_metric, improvement_pct, budget.state)

    progress.finalize(result)
    return result
```

```python
# Epic 3: UI Integration
def run_optimization_with_ui_updates():
    def ui_callback(iteration, best_metric, improvement_pct, budget_used, time_elapsed):
        # Send SSE event to browser
        emit_sse_event({
            "iteration": iteration,
            "improvement": improvement_pct,
            "budget": budget_used,
            "elapsed": time_elapsed
        })

    config = OptimizationConfiguration(
        build=build,
        metric="dps",
        progress_callback=ui_callback,
        verbose=False  # Disable console in production UI
    )

    result = optimize_build(config)
```

---

## Acceptance Criteria Update

Story 2.8 ACs remain the same with implementation clarification:

✅ **AC-2.8.1:** Track current iteration number
- Implemented in ProgressTracker

✅ **AC-2.8.2:** Track best metric value found so far
- Passed via update() method

✅ **AC-2.8.3:** Track improvement percentage vs baseline
- Calculated in hill_climbing.py, passed to tracker

✅ **AC-2.8.4:** Track budget usage
- BudgetState passed directly

✅ **AC-2.8.5:** Provide progress callback for UI updates
- **NEW:** Callback signature defined, implemented in ProgressTracker

✅ **AC-2.8.6:** Update every 100 iterations (per FR-5.2)
- **NEW:** `report_interval` parameter (default=100)

**NEW AC-2.8.7:** Console output available for development/debugging
- Controlled via `verbose` flag (default=True)

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/optimizer/test_progress.py

def test_progress_callback_invoked():
    """Test callback is invoked with correct data"""
    events = []

    def mock_callback(**kwargs):
        events.append(kwargs)

    tracker = ProgressTracker(callback=mock_callback, verbose=False)
    tracker.update(100, 1000.0, 15.5, mock_budget)

    assert len(events) == 1
    assert events[0]["iteration"] == 100
    assert events[0]["improvement_pct"] == 15.5

def test_console_output_when_verbose():
    """Test console output printed when verbose=True"""
    # Use capsys pytest fixture to capture stdout
    tracker = ProgressTracker(verbose=True)
    tracker.update(200, 1500.0, 20.0, mock_budget)
    # Assert output contains "Iteration 200"

def test_no_output_when_not_verbose():
    """Test no console output when verbose=False"""
    tracker = ProgressTracker(verbose=False)
    tracker.update(300, 2000.0, 25.0, mock_budget)
    # Assert no stdout output
```

### Integration Tests

```python
# tests/integration/optimizer/test_hill_climbing.py

def test_progress_reporting_during_optimization():
    """Test progress updates emitted during real optimization"""
    progress_events = []

    def capture_progress(**kwargs):
        progress_events.append(kwargs)

    config = OptimizationConfiguration(
        build=test_build,
        metric="dps",
        progress_callback=capture_progress
    )

    result = optimize_build(config)

    # Verify progress events were captured
    assert len(progress_events) > 0
    assert all("iteration" in e for e in progress_events)
```

---

## Decision Log

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| **API Callback** | ✅ Required | Epic 3 integration |
| **Console Output** | ✅ Included | Development aid, minimal cost |
| **Verbose Flag** | ✅ Included | Allow disabling in production |
| **Report Interval** | 100 iterations | Per FR-5.2 spec |
| **Fancy Progress Bar** | ❌ Not included | Complexity not worth it for MVP |

---

## Epic 3 Handoff

**For Story 3.5 (Optimization Progress Display):**

Use the progress callback to drive UI updates:

```javascript
// Frontend: Listen for SSE events
const eventSource = new EventSource('/optimize/progress');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);

    // Update progress bar
    document.getElementById('progress-bar').style.width =
        `${(data.iteration / 1000) * 100}%`;

    // Update stats
    document.getElementById('iteration').textContent = data.iteration;
    document.getElementById('improvement').textContent =
        `+${data.improvement.toFixed(1)}%`;
    document.getElementById('budget').textContent =
        `${data.budget.unallocated}/${total_unallocated} unallocated, ` +
        `${data.budget.respec}/${total_respec} respec`;
};
```

**Backend:** Use callback to emit SSE events (see architecture doc Section 4.6).

---

## Open Questions Resolved

**Q:** Should progress tracking be API-only or include console output?
- ✅ **Answer:** API + console (both provide value, minimal cost)

**Q:** What should the callback signature be?
- ✅ **Answer:** Defined in this document

**Q:** How often should progress be reported?
- ✅ **Answer:** Every 100 iterations (FR-5.2 spec)

**Q:** Should console output be configurable?
- ✅ **Answer:** Yes, via `verbose` flag

---

**Approved by:** Bob (Scrum Master)
**Date:** 2025-10-27
**Status:** ✅ READY FOR IMPLEMENTATION
**Prep Sprint Task:** #7 COMPLETED
