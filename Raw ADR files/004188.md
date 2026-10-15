# ADR 0003: NavigationService RetryLast Behavior Fix

## Status
Accepted

## Context
During Phase0 slice testing of the `NavigationService` and `NavigateTo` subsystems,  
we discovered failing unit and integration tests:

- `RetryLastValidRouteSucceeds`
- `NavigateToRetryWithInvalidRouteFails`
- `NavigateToExecuteStoresLastRoute`

### Problem
The failures revealed that:

1. **`m_lastAttempt` was not properly utilized:**
   - It was set in `navigateTo()`, but `retryLast()` only called `navigateTo(m_lastAttempt)` again.
   - No guarantee that a signal (`navigated` / `navigationFailed`) would be emitted,  
     causing tests to timeout without receiving expected events.

2. **Invalid routes were not differentiated:**
   - Calling `retryLast()` after an invalid attempt did not emit a clear failure signal.  
   - Tests expecting `navigationFailed("No last route")` were not satisfied.

3. **Event loop timing issues:**
   - Signals emitted indirectly via `navigateTo()` were not reaching the test spies reliably.  
   - This resulted in false negatives in `QSignalSpy::wait()`.

---

## Decision
We modified the implementation of `retryLast()` to **emit signals directly**:

```cpp
// 🔁 Retry the last attempted navigation
void NavigationService::retryLast()
{
  if (m_lastAttempt.isValid()) {
    // 📝 Push again into stack and emit directly
    m_stack.push(m_lastAttempt);

    if (m_logger) {
      m_logger->log(Level::Info,
                    "navigation",
                    QString("Retried route: %1").arg(m_lastAttempt.toString()));
    }

    emit navigated(m_lastAttempt);
  } else {
    if (m_logger) {
      m_logger->log(Level::Warn,
                    "navigation",
                    "Retry failed: no valid last route");
    }
    emit navigationFailed("No last route to retry.");
  }
}
```

Additionally, tests were adjusted to ensure event loop cycles process signals:

```cpp
QCoreApplication::processEvents(QEventLoop::AllEvents, 1000);
ASSERT_GT(spy.count(), 0);
```

---

## Consequences
- ✅ **Retry logic stabilized:**  
  Valid last routes now reliably trigger `navigated` signals.  
- ✅ **Error handling improved:**  
  Invalid retry attempts emit `navigationFailed("No last route to retry.")`.  
- ✅ **Tests pass consistently:**  
  All 6 extended tests for NavigationService & NavigateTo now succeed.  
- 🔁 **Behavioral change:**  
  `retryLast()` no longer depends solely on `navigateTo()` to propagate signals;  
  it explicitly emits signals itself.

---

## Alternatives Considered
- Keeping existing design and only extending timeouts in tests → ❌ unreliable.  
- Wrapping `navigateTo()` with retry guard logic → ❌ redundant, harder to maintain.  
- Direct emit approach (chosen) → ✅ simplest, most deterministic.

---

## References
- File: `NavigationService.cpp`
- Tests:  
  - `test_navigation_service_extended.cpp`  
  - `test_navigation_service_unit.cpp`  
  - `test_navigation_service.cpp`
