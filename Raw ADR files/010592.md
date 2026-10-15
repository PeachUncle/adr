# ADR-0007: UI/UX Refresh — Guided Stepper with Sticky Results Preview (Option A)

Status: Accepted
Date: 2025-09-10

## Context

v1 shipped a guided stepper and custom SVG bars. For v2 we want an Apple‑style minimal, focused UI that makes per‑GPU vRAM visualization the hero while keeping interactions fast and accessible. There was uncertainty about committing to a full split (Canvas) layout.

## Decision

Adopt Option A for v2: Keep the guided stepper and introduce a sticky results preview panel that appears once GPUs are selected and remains visible throughout the flow. Defer a full Canvas (split) mode to a later toggle.

## Alternatives Considered

- Option B: Split (Canvas) layout — Controls left, bars right. Pros: power‑user friendly; always‑visible bars. Cons: more layout complexity and polish required; potential density issues on small screens.
- Option C: Context Drawer — Full‑width stepper with a right drawer showing bars after GPU selection. Pros: focused flow; good on small screens. Cons: drawer ergonomics and motion need careful tuning.

## Rationale

Option A balances clarity for first‑time users with minimal changes to v1, reduces implementation risk, and still keeps the visualization prominent post GPU selection. It fits the Apple‑style minimalism goal by avoiding heavy layout chrome while ensuring quick feedback.

## Consequences

- UI adds a compact preview panel that shares the same bar componentry as the Results step.
- Need careful focus order, ARIA labels, and keyboard Left/Right navigation across segments.
- On small screens, bar width is limited; we will provide a compact density and prioritize readability.
- No new runtime dependencies; if a positioning library becomes necessary, a separate ADR is required.
- Suggestions become adjustable prior to applying (numeric stepper seeded with the suggestion; +/- nudge, direct input). Apply uses the adjusted value.

## Implementation Notes

- Reuse `app/controller.buildPerGpuBars` for both preview and results; do not duplicate logic in UI.
- Provide a minimal Top Bar with title plus theme and unit toggles (persisted via localStorage).
- Persist theme and unit preference in localStorage.
- Use CSS transforms and opacity for subtle transitions; avoid layout thrash in sticky containers.
- Maintain boundaries per `ARCH-v2.md`: UI→App; App→Domain|Data|Shared; Domain→Shared; Data→Shared.
- For adjustable suggestions, either bind directly to `state.deployments[i].maxNumSeqs/maxModelLen` prior to Apply, or provide a thin App setter to keep UI lean; ensure min/step constraints (seqs ≥1, len step 128 by default) and disable Apply when invalid.
- Adjustable suggestions should use temporary UI state to support live preview without mutating App state; commit to App state only on Apply.

## Palette Tokens (v2)

Define a muted, Apple‑like palette with AA contrast in light/dark. UI uses these CSS variables (see `src/styles/tokens.css`).

Light mode

- `--color-bg`:        #FFFFFF
- `--color-surface`:   #F5F5F7   (Apple gray)
- `--color-text`:      #1D1D1F   (primary text)
- `--color-muted`:     #6E6E73   (secondary text)
- `--color-primary`:   #0071E3   (accent blue)
- `--color-success`:   #34C759
- `--color-warning`:   #FF9F0A
- `--color-danger`:    #FF3B30

Domain (light)

- `--color-weights`:   #5E5CE6   (indigo)
- `--color-kv`:        #BF5AF2   (purple)
- `--color-reserve`:   #A1A1A6   (secondary gray)
- `--color-unallocated`: #D2D2D7 (tertiary gray)
- `--color-free`:      #30D158   (green)

Dark mode

- `--color-bg`:        #000000
- `--color-surface`:   #1C1C1E
- `--color-text`:      #F5F5F7
- `--color-muted`:     #A1A1A6
- `--color-primary`:   #0A84FF
- `--color-success`:   #30D158
- `--color-warning`:   #FFD60A
- `--color-danger`:    #FF453A

Domain (dark)

- `--color-weights`:   #7D7AFF   (indigo)
- `--color-kv`:        #C678F7   (purple)
- `--color-reserve`:   #636366   (secondary gray)
- `--color-unallocated`: #3A3A3C (tertiary gray)
- `--color-free`:      #30D158   (green)

Notes

- Bars render labels with white text on colored segments; chosen hues maintain sufficient contrast in both themes.
- Reserve/unallocated use neutral grays to avoid confusing semantic colors.

## Testing

- Domain tests remain unchanged.
- Add UI smoke tests for: preview visibility after GPU selection, per‑GPU bar rendering, keyboard navigation across segments, and Apply suggestion actions.
