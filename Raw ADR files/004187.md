# ADR 0001: Test File Output Unification

## Status
Accepted

## Context
During development, multiple test suites (unit, integration) were writing temporary files to inconsistent locations:
- `QTemporaryFile` and `QTemporaryDir` scattered under system temp.
- `QFile` and `QSettings` writing directly into project root or user AppConfig (e.g., `%APPDATA%/Tasqly`).
- Some logs and INI files persisted after test runs, polluting both developer environment and CI runners.

This created several issues:
- ❌ Tests interfering with real user configuration (AppConfigLocation).
- ❌ Residual files left under project root after running tests.
- ❌ Inconsistent cleanup strategies (some temp dirs auto-clean, others not).
- ❌ CI instability due to untracked file artifacts.

## Decision
We will standardize all test-generated files under a dedicated **`tests_tmp/`** folder located at `QCoreApplication::applicationDirPath() + "/tests_tmp"`.

### Rules:
1. All file-based tests (logging, settings, persistence) must resolve their paths into `tests_tmp/`.
2. Each test fixture ensures `QDir().mkpath("tests_tmp")` before use and removes its own files in `SetUp`/`TearDown`.
3. Special cases:
   - `QTemporaryDir` remains acceptable for scenarios explicitly testing failure/permissions, since it self-cleans.
   - Rotation / fallback tests may still use `QTemporaryDir` when testing error scenarios.
4. CI/CD will add a pre/post step to clean `tests_tmp/` to guarantee a reproducible environment.

## Consequences
- ✅ Tests no longer pollute project root or user environment.
- ✅ Easier cleanup: one directory (`tests_tmp/`) to purge locally and in CI.
- ✅ Consistent developer experience across OS (Windows/Linux).
- ⚠️ Requires modifying all existing tests that directly used `QTemporaryFile`, `QFile`, or `QSettings` paths.
- ⚠️ Must monitor performance impact of frequent setup/teardown file operations (minimal expected).

## Alternatives Considered
- Leaving behavior as-is: rejected due to pollution and CI instability.
- Using only `QTemporaryDir` for all cases: rejected because some tests require persistent paths across test runs (e.g., settings reload).
- Introducing a custom `TestFileManager` utility class: postponed for now to keep scope minimal.

## Related Work
- Modified test files:
  - `test_error_reporter_feature_flag.cpp`
  - `test_feature_flag_logging.cpp`
  - `test_qml_error_to_toast_and_log.cpp`
  - `test_appsettingsmanager.cpp`
  - `test_theme_persistence.cpp`
  - `test_autoflush.cpp`
  - `test_concurrency.cpp`
  - `test_log_manager_misc.cpp`
  - `test_masking*.cpp`
  - `test_rotation_policy.cpp`
  - `test_app_settings_manager.cpp`

## Future Improvements
- Introduce a centralized `TestFileHelper` to abstract path resolution and cleanup.
- Automate cleanup in CI pipeline with a `before_script`/`after_script` job.
- Extend to cover snapshot/image outputs in future UI test phases.