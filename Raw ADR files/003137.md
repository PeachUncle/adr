# ADR 004: Date Timezone Strategy - UTC for Day-of-Week, Local for User-Facing Dates

**Status**: Accepted
**Date**: 2025-11-04
**Context**: Feature #063 Phase 8 - Gamification timezone bug fix
**Decision Makers**: Claude Code (implementation), CodeRabbit AI (review feedback)
**Related**: PR #72 (timezone bug fix)

---

## Context

PayPlan stores dates as ISO date-only strings (`YYYY-MM-DD`) for simplicity and human readability. However, JavaScript has a **historical spec error** in how it parses these strings:

**ECMAScript Behavior** (contradicts ISO 8601):
- Date-only strings (`'2025-10-27'`) → Parsed as **UTC midnight**
- DateTime strings (`'2025-10-27T00:00:00'`) → Parsed as **local midnight**

This causes timezone-dependent bugs:
```javascript
// In America/New_York (UTC-5):
new Date('2025-10-27').getDay()    // Returns 0 (Sunday) ❌ Wrong!
new Date('2025-10-27').getUTCDay() // Returns 1 (Monday) ✅ Correct!
```

**The Problem**:
- Gamification insights use day-of-week logic (weekend vs weekday spending)
- Using `getDay()` causes incorrect classifications in non-UTC timezones
- Test failed because Oct 27 Monday was classified as Sunday

---

## Decision

**For date-only strings (`YYYY-MM-DD`)**: Use **UTC methods**
- `getUTCDay()` for day-of-week
- `getUTCMonth()` for month
- `getUTCDate()` for day-of-month
- `getUTCFullYear()` for year

**For user-facing date display**: Use **local timezone**
- Display dates in user's local timezone
- Use `toLocaleDateString()` for formatting
- Accept that internal storage is UTC-based

**For test environment**: Set **`TZ=UTC`**
- Eliminates timezone variability
- Matches CI environment
- Makes tests deterministic

---

## Rationale

### Why UTC Methods for Date-Only Strings?

1. **Accepts spec behavior**: ECMAScript parses date-only strings as UTC (cannot be changed)
2. **Consistency**: Internal logic matches parsing behavior
3. **Correctness**: Oct 27 is Monday in UTC (day=1) regardless of local timezone
4. **Predictability**: Same date string → same day-of-week calculation globally

### Why Not Append 'T00:00:00'?

While `new Date(date + 'T00:00:00')` forces local parsing, it:
- Fights the spec instead of accepting it
- Requires string manipulation everywhere
- Adds complexity and potential bugs
- Doesn't align with how we store dates (date-only format)

### Why TZ=UTC for Tests?

- **CI consistency**: GitHub Actions runs in UTC by default
- **Determinism**: Tests produce same results on all developer machines
- **Prevents flakiness**: No timezone-dependent failures
- **Industry standard**: Most teams run tests in UTC

---

## Consequences

### Positive

✅ **Eliminates timezone bugs**: Day-of-week logic works correctly globally
✅ **Test determinism**: Tests pass reliably in all timezones
✅ **Spec-compliant**: Accepts ECMAScript behavior instead of fighting it
✅ **Well-documented**: ADR + inline comments explain the quirk
✅ **Future-proof**: Clear strategy for all date-based logic

### Negative

⚠️ **Cognitive overhead**: Developers must understand UTC vs local distinction
⚠️ **Inconsistency**: Some code uses local time (streak tracking), some uses UTC (insights)
⚠️ **Documentation burden**: Must explain ECMAScript quirk to all new developers

### Neutral

- Date storage format unchanged (`YYYY-MM-DD`)
- User experience unchanged (dates still display in local timezone)
- Requires `TZ=UTC` in test scripts (already added in PR #72)

---

## Implementation

### Files Changed
- `frontend/src/features/dashboard/lib/gamification.ts` - Use `getUTCDay()` with docs
- `frontend/src/features/dashboard/lib/__tests__/gamification.test.ts` - Fix test data
- `frontend/package.json` - Add `TZ=UTC` to test scripts

### Code Pattern
```typescript
// ✅ CORRECT: Use UTC methods for date-only strings
const day = new Date(transaction.date).getUTCDay(); // YYYY-MM-DD → UTC

// ❌ WRONG: Local methods with date-only strings (timezone-dependent)
const day = new Date(transaction.date).getDay(); // Fails in non-UTC timezones
```

---

## Exceptions

**Streak tracking** (`updateStreakData`) intentionally uses **local timezone**:
```typescript
// Local date for user-friendly streak logic
const today = `${now.getFullYear()}-${now.getMonth() + 1}-${now.getDate()}`;
```

**Rationale**: Streaks should match user's perception of "today"
- User in California logs in at 11 PM Oct 30 local time
- UTC would be Oct 31 → streak broken unfairly ❌
- Local time is Oct 30 → streak continues fairly ✅

**Rule**: Use **local timezone** when logic is tied to user's perception of time (streaks, "today"), use **UTC** when logic is tied to calendar dates (day-of-week, month-of-year).

---

## Alternatives Considered

### 1. Store DateTime Strings (`YYYY-MM-DDTHH:MM:SS`)
**Rejected**: Adds unnecessary precision, breaks existing data format

### 2. Use Date Library (date-fns, dayjs)
**Rejected**: Adds dependency for single quirk, overkill for Phase 1

### 3. Parse as Local Time Everywhere
**Rejected**: Requires string manipulation (`+ 'T00:00:00'`) everywhere, error-prone

### 4. Keep Using `getDay()` (Original)
**Rejected**: Fails in non-UTC timezones, causes production bugs

---

## References

- **ECMAScript Spec**: [Date Time String Format](https://tc39.es/ecma262/multipage/numbers-and-dates.html#sec-date-time-string-format)
- **MDN**: [Date Constructor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date)
- **Historical Context**: [Fixing JavaScript Date: Web Compatibility and Reality](https://maggiepint.com/2017/04/11/fixing-javascript-date-web-compatibility-and-reality/)
- **PR #72**: Timezone bug fix implementation
- **Feature #063**: Business Logic Test Coverage

---

## Review and Update

This ADR should be reviewed if:
- We change date storage format (e.g., move to DateTime strings)
- We add a date library (date-fns, dayjs)
- We encounter new timezone-related bugs
- User feedback indicates timezone issues

**Last Reviewed**: 2025-11-04 (initial creation)
