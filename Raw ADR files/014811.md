# ADR 0001: Dedicated Parity Phase (Phase X)

**Status:** Accepted  
**Date:** 2025-11-04  
**Decision Makers:** Purrfect Chess Team

## Context

The Purrfect Chess project is undergoing a migration from a Vite-based vanilla TypeScript/JavaScript application to a Next.js + React architecture. As of this ADR:

- **Phase 1 (Skeleton Setup)**: ✅ Complete
- **Phase 2 (Core Migration)**: ✅ Complete
  - Board rendering with piece images
  - Click-to-select and drag-and-drop interaction
  - Time controls and game clocks
  - Game controls (FEN/PGN I/O, reset)
  - Move history display
- **Phase 3 (Advanced Features)**: ✅ Complete
  - Stockfish engine integration with UCI protocol
  - Engine analysis panel with multi-PV display
  - Appearance customization (piece/square theming)
  - Hidden "gmmamun" Easter egg

The **legacy Vite app** in `src/` remains functional and serves as the source of truth for behavior and UX.

### Problem

Before proceeding to **Phase 4 (Testing & Cleanup)**, we need confidence that the Next.js app achieves **functional and visual parity** with the legacy app. Without a dedicated parity validation phase, we risk:

1. **Subtle UX regressions**: Minor behavior differences that feel "off" to users
2. **Visual inconsistencies**: Pixel differences, layout shifts, theme mismatches
3. **Functional bugs**: Edge cases in chess logic, I/O formats, engine behavior
4. **Late discovery**: Issues surfacing in production rather than during migration
5. **Difficult debugging**: Hard to pinpoint when/where parity was lost

### Current Gaps

While Phases 2 and 3 implemented most features, **parity validation** has not been systematic:

- **Arrow drawing**: Not yet implemented in Next.js (exists in legacy)
- **Evaluation bar**: Component stub exists but not wired/rendered
- **FEN/PGN format**: Need to validate exact output format matches legacy
- **UCI parsing**: Need to validate engine output format matches legacy
- **Visual appearance**: Need pixel-perfect comparison of themes and layouts
- **Performance**: Need benchmarking to ensure Next.js ≥ legacy speed

## Decision

We will introduce **Phase X: Functional + Visual Parity Development** as a required gate between Phase 3 and Phase 4.

Phase X focuses on:

1. **Documentation**: Consolidate parity requirements, acceptance criteria, validation procedures
2. **Fixtures**: Create comprehensive test corpuses (FEN positions, PGN games)
3. **Validation**: Side-by-side manual testing and automated parity tests
4. **Implementation**: Complete missing features (arrow drawing, evaluation bar)
5. **Verification**: Ensure ≤2px visual tolerance and identical behavior

Phase X is **complete** when:

- All acceptance criteria met
- All fixtures pass in both apps
- Side-by-side comparison shows no meaningful deltas
- Automated parity tests pass
- Performance benchmarks pass

## Consequences

### Positive

1. **Quality assurance**: High confidence before removing legacy code
2. **User experience**: Preserves familiar UX from legacy app
3. **Regression prevention**: Catches issues early in structured way
4. **Documentation**: Clear acceptance criteria for contributors
5. **Testability**: Fixtures and tests serve as regression suite
6. **Smooth transition**: Users won't notice the migration

### Negative

1. **Time investment**: Additional phase adds time before Phase 4
2. **Upfront work**: Creating fixtures and parity tests takes effort
3. **Maintenance burden**: Parity tests need updating as features change

### Neutral

1. **Legacy preservation**: `src/` directory remains until Phase X complete
2. **Dual maintenance**: Both apps functional during Phase X
3. **Testing overhead**: Manual side-by-side testing required

## Alternatives Considered

### Alternative 1: Skip parity validation, proceed to Phase 4

**Rejected:** Too risky. Without validation, subtle bugs could persist to production.

### Alternative 2: Ad-hoc parity testing during Phase 4

**Rejected:** Parity validation should gate Phase 4, not happen during it. Phase 4 assumes parity is achieved.

### Alternative 3: Automated visual regression tests only

**Rejected:** Visual tests alone miss behavioral and functional differences. Need comprehensive approach.

## Implementation

Phase X will be tracked in [Issue #40](https://github.com/purrfectsoft/purrfect-chess/issues/40) with the following deliverables:

### Documentation

- `docs/phase-x-parity.md` - Master parity document
- `docs/adr/0001-phase-x-parity-approach.md` - This ADR
- `docs/runbooks/side-by-side.md` - Side-by-side validation guide
- `docs/contributing-phase-x.md` - Contributor guide
- Update `MIGRATION.md` to reference Phase X

### Fixtures

- `docs/fixtures/fen/` - 25 FEN positions (edge cases, special positions)
- `docs/fixtures/pgn/` - 10 PGN games (various game lengths, scenarios)

### Test Scaffolds

- `tests/parity/fenpgn.roundtrip.test.ts` - FEN/PGN I/O validation
- `tests/parity/board.visual.test.tsx` - Visual snapshot tests
- `tests/engine/uci-parser.test.ts` - UCI parsing validation

### Component Completion

- Implement arrow drawing system
- Wire EvaluationBar component
- Validate all appearance customization

## Success Metrics

Phase X is successful when:

- ✅ All 14 workstreams validated (see `docs/phase-x-parity.md`)
- ✅ All fixtures produce identical output in both apps
- ✅ Visual comparison shows ≤2px differences
- ✅ Performance benchmarks: Next.js ≥ legacy
- ✅ Automated parity tests pass
- ✅ Manual validation checklist complete

## References

- [Issue #31](https://github.com/purrfectsoft/purrfect-chess/issues/31) - Modernization roadmap (master issue)
- [Issue #40](https://github.com/purrfectsoft/purrfect-chess/issues/40) - Phase X tracking issue
- `MIGRATION.md` - Migration guide and status
- `NEXT_STEPS_ISSUE.md` - Original next steps (now outdated, to be updated)
- `module-map.md` - Module extraction strategy (now outdated, to be updated)

---

**Last Reviewed:** 2025-11-04  
**Status:** Active implementation
