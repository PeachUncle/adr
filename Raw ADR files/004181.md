# ADR 0007: logmanager-filesink-path-reopen

- **Status**: Accepted
- **Date**: 2025-09-30
- **Owners**: Tasqly Team
- **Related**: Phase04 — Slice02 (Logging Rotation Reliability)
- **Tags**: logging, filesink, rotation, ci-consistency, testing

---

## Context
During CI runs, the test `LogManagerExtendedTest.RotatesWhenFileExceedsMaxSize` failed consistently, although it passed locally.  
The root cause investigation showed two intertwined issues:

1. **FileSink Path Handling**  
   - `LogManager::enableFileSink` did not reopen the file if a different path was passed while a previous file was still open.  
   - As a result, all log lines were written to the first sink (e.g., `test.log`) while the test monitored another file (`rotation_test.log`), leaving it empty and causing rotation checks to fail.  
   - Locally, leftover `rotation_test.log.1` files from previous runs created a false impression of success.

2. **Test Environment Pollution**  
   - `LogManagerExtendedTest` did not clean its temp directory (`tasqly_log_test_ext`) before runs.  
   - Stale rotated files could make local runs succeed even when no new rotation happened.  
   - CI environments (clean state) correctly exposed the failure.

---

## Decision
- **FileSink Behavior Fix**:  
  - Modified `LogManager::enableFileSink` to close and reopen the file if the provided path changes, ensuring logs are always written to the intended file.  
- **Test Environment Hygiene**:  
  - Updated `LogManagerExtendedTest::SetUp` to fully clean and recreate its temp directory at the start of each test.  
  - Rotation tests now start from a guaranteed clean state.  
- **Test Robustness**:  
  - Rotation test explicitly disables any default sink, then enables its own dedicated file sink.  
  - Concurrent logging test relies on the default `test.log` sink set in `SetUp`.

---

## Consequences
- ✅ **Consistency**: Local and CI results now align. No false positives due to stale files.  
- ✅ **Correctness**: Logs always go to the expected sink file; rotation policies are applied to the right file.  
- ⚠️ **Drawback**: Slight overhead from reopening file handles if `enableFileSink` is called with different paths in runtime.  
- 🔄 **Trade-off**: Prioritizing correctness and test determinism over negligible performance costs.

---

## References
- Commit: `fix/logmanager-filesink-reopen`  
- File: `infra/logging/LogManager.cpp` (modified `enableFileSink`)  
- File: `tests/integration/logging/test_log_manager_extended.cpp` (clean tmpDir + sink handling)  
- Related Tests: `RotatesWhenFileExceedsMaxSize`, `HandlesConcurrentLogging`  
