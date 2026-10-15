# ADR-0001: 7-12 Age Group as Primary Experience

- **Status**: Accepted
- **Date**: 2026-01-13
- **Decision Makers**: Product Team, Dev Team
- **Related Issues**: N/A

---

## Context

MuseumCheck originally exposes content for three age brackets (3-6, 7-12, 13-18) with separate preparation and child tasks per group. Maintaining three distinct curricula increases authoring, testing, and regression surface area. The current focus is on stabilizing and shipping consistent experiences for 7-12 year olds.

## Decision

We will temporarily treat the 7-12 age group as the single canonical experience:

- All user-facing flows (checklists, progress, badges, leaderboard logic) will surface the 7-12 content.
- The UI will continue to show the age selector but selecting any group will map to the 7-12 implementation under the hood.
- Future expansion to 3-6 and 13-18 will reuse this implementation as a baseline and layer additional content later.

## Alternatives Considered

### Option 1: Maintain three explicit age groups

**Pros**:
- Matches original specification
- No temporary compromises needed

**Cons**:
- High content maintenance cost
- Hard to keep regression suite consistent across all groups
- Slows down delivery of improvements to the most-used 7-12 experience

**Why not chosen**: Stabilizing the 7-12 experience is higher priority; replicating strict age segmentation now would split focus.

### Option 2: Remove age selector entirely

**Pros**:
- Simplifies UI
- Removes confusion about unsupported age groups

**Cons**:
- Losing the perception of tailored experiences
- Might require more communication for future expansion

**Why not chosen**: Keeping the selector preserves the promise of multi-age support and makes future expansion easier.

## Consequences

### Positive Consequences
- ✅ Focused testing surface (only 7-12 flows need immediate regression tests)
- ✅ Delivery speed improves for the most critical age group
- ✅ Maintains UI familiarity for future age group rollouts

### Negative Consequences
- ⚠️ 3-6 and 13-18 users see duplicated 7-12 content (mitigate via messaging that 7-12 is baseline)
- ⚠️ Need to revisit this ADR when new age-specific content is introduced

---

## Implementation

### Changes Required
- [x] Map age selector paths to 7-12 checklist logic in `script.js`
- [x] Document the temporary policy in the ADR
- [ ] Update regression tests / e2e flows to assert 7-12 content for all selectors

### Testing Changes
- [x] Primary regression suites already validate 7-12 content (e.g., `tests/museum-checkin.test.js`)
- [x] Confirm `tests/regression-homepage-events.test.js` still passes with selector scenario
- [ ] Add explicit regression to confirm other selectors are no-ops now if not already covered

### Deployment Changes
- [x] No deployment-specific work—changes live with next static release

---

## Validation

### Success Criteria
- ✅ Age selector always resolves to 7-12 content
- ✅ No regressions introduced for 7-12 workflows
- ✅ Future updates to 3-6 / 13-18 can branch off this baseline

### Monitoring
- Track user feedback mentioning age-specific expectations
- Monitor regression tests that rely on age selector behavior

---

## Reversibility

- [x] Yes, with significant effort

**Reversal plan**:
1. Implement per-age content (3-6, 13-18) in data + UI.
2. Update code paths to consult the actual selected age group.
3. Add ADR describing the return to full age support.

---

## References

- [Tech spec template](../TECH_SPEC_TEMPLATE.md)
- [Testing guide](../../guides/testing.md)
- [Current regression suites](https://github.com/jackandking/MuseumCheck/tree/dev/tests)
