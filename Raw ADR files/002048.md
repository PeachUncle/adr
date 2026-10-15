## Context
The plugin currently offers two roster views (inline and cards) with a toggle. This change simplifies the UI to a single expandable inline view that matches the reference design in `eldrìlas-profile-compact.html`.

### Reference Design (eldrìlas-profile-compact.html)
The reference uses:
- A header row that is clickable to expand/collapse
- CSS `max-height` transition for smooth animation
- An expand/collapse icon (chevron) that rotates on state change
- Dark theme with gold accent (`#dca54a` in our case)

### Data Source
All required data is available from the Raider.IO API endpoint:
```
https://raider.io/api/v1/characters/profile?region=eu&realm=<realm>&name=<name>&fields=mythic_plus_scores_by_season:current,mythic_plus_best_runs
```

This provides:
- `mythic_plus_scores_by_season` - Current M+ score
- `mythic_plus_best_runs` - Array of best dungeon runs (dungeon, short_name, mythic_level, score, background image URL)

## Goals / Non-Goals
**Goals:**
- Single, cohesive inline expandable view
- Smooth CSS-animated expand/collapse matching the reference
- Mobile-first responsive design
- Reduced code complexity (remove cards view and toggle)

**Non-Goals:**
- Adding new data fields
- Changing the color scheme (already defined in CSS)
- Server-side rendering changes beyond markup structure

## Decisions

### Decision 1: Replace `<details>` with JS-controlled expansion
**What:** Use a clickable header with JS toggle and CSS `max-height` transition instead of native `<details>` element.

**Why:** The native `<details>` element doesn't support smooth height animations. The reference design uses `max-height` transitions for a polished expand/collapse effect.

**Implementation:**
- Header gets `onclick` handler that toggles `.expanded` class on the profile card
- Expandable content uses `max-height: 0` (collapsed) → `max-height: 600px` (expanded) with transition
- Chevron icon rotates 180° when expanded

### Decision 2: Remove view toggle entirely
**What:** Remove the inline/cards toggle buttons and all cards-related code.

**Why:** Simplifies the UI and reduces maintenance. Users prefer the inline view.

**Alternatives considered:**
- Keep toggle but default to inline: Rejected - adds unnecessary complexity
- Hide toggle via CSS: Rejected - leaves dead code

### Decision 3: Click target is the header row
**What:** The entire header row (avatar, name, score section) is clickable to expand/collapse the details section.

**Why:** Matches the reference design. Large click target improves usability, especially on mobile.

**Note:** The "Profile" CTA button should NOT trigger expand/collapse (stopPropagation).

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Users who preferred cards view lose that option | Cards view was underutilized; inline view provides more information |
| JS-based expand requires JS enabled | Fallback: details section starts expanded when JS is disabled |
| Animation may be janky on low-end devices | Use `will-change: max-height` and hardware-accelerated transitions |

## Migration Plan
1. Update PHP renderer to output new markup
2. Update CSS with expand/collapse animation styles
3. Update JS to handle expand/collapse clicks
4. Remove all cards-related code
5. Test on mobile devices
6. Sync dist/staging files

**Rollback:** Git revert if issues arise.

## Open Questions
None - design is fully specified by the reference file.
