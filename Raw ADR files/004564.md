# ADR 001: Testing Strategy for Platform-Heavy Flutter Applications

**Status**: Accepted
**Date**: 2025-01-XX
**Context**: WAssistant integrates Firebase, native platform plugins, and UI-heavy widgets

---

## Decision

**Adopt a 17% baseline coverage target focused on business logic over absolute percentage metrics.**

### Rationale

1. **Platform Dependencies**: WAssistant heavily uses Firebase services (Analytics, Crashlytics, Messaging, Performance, Remote Config) and native platform APIs (local_auth, share_plus, image_picker). These require device/emulator context and cannot run in standard unit test environments.

2. **ROI Analysis**: Testing Services/Repositories that are thin wrappers around platform plugins yields minimal value compared to testing Providers and business logic.

3. **Industry Standards**: Flutter apps with Firebase integration typically achieve 60-75% coverage when including integration tests. Unit-only coverage of 17-25% is acceptable when:
   - All Providers (state management) are tested
   - All Validators (input sanitization) are tested
   - All utility functions are tested

4. **Functional Purity**: WAssistant uses `Either<Failure, Success>` pattern from `fpdart`. This makes Provider logic deterministic and highly testable without mocks.

---

## Test Coverage Breakdown

| Layer             | Coverage | Justification                                                                                         |
| ----------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| **Providers**     | 100%     | Core business logic. WhatsAppToolProvider (12 tests), HistoryProvider, TemplateProvider fully covered |
| **Validators**    | 100%     | Security-critical input sanitization. Phone/email/URL validation tested exhaustively                  |
| **Services**      | ~5%      | Firebase wrappers. Tested via integration tests only (not counted in unit coverage)                   |
| **Repositories**  | ~10%     | Thin persistence layer. SharedPreferences wrappers - minimal logic to test                            |
| **Pages/Widgets** | ~0%      | UI-heavy code. Tested via manual QA and integration tests                                             |

**Total Unit Coverage**: 17.51% (329/1879 lines)

---

## Consequences

### Benefits

- **Fast CI/CD**: Unit tests run in ~10s (no emulator needed)
- **High Signal/Noise**: 91 tests, all meaningful
- **Maintainable**: No brittle UI widget tests that break with theme changes

### Drawbacks

- **Low Percentage Optics**: 17% looks bad on coverage badges
- **Integration Gaps**: Firebase integration errors only caught in manual testing
- **UI Regressions**: No automated UI validation

### Mitigation

- Set CI threshold at 17% to prevent regression
- Maintain comprehensive integration test suite (7 tests)
- Manual QA checklist for Firebase features
- Document coverage strategy in README

---

## Alternatives Considered

1. **80%+ Coverage with Mocks**: Rejected - creates false confidence, mocks hide platform integration bugs
2. **Widget Testing**: Rejected - brittle, slow, high maintenance overhead for UI-heavy app
3. **Integration-Only Testing**: Rejected - too slow for CI, requires emulator/device

---

## Related Documents

- [test/unit/whatsapp_tool_provider_test.dart](../../test/unit/whatsapp_tool_provider_test.dart)
- [CI Workflow](../../.github/workflows/flutter_ci.yml)
