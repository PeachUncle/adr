# ADR-003: Grid Layout and Timeline Orientation

**Status:** Accepted
**Date:** 2025-01-13
**Phase:** Phase 4 - Allocation Grid (Read-Only Display)

## Context

The Allocation Grid is the core interface for viewing and editing engineer time allocations across a quarter. We needed to make several critical design decisions:

1. **Timeline Orientation**: Should time flow vertically (weeks as rows) or horizontally (weeks as columns)?
2. **Layout Technology**: What CSS approach should we use for the grid layout?
3. **Sticky Headers**: How to keep both row and column headers visible during scroll?
4. **Multi-week Projects**: How to visually connect cells for projects spanning multiple weeks?
5. **Cell Dimensions**: What size should cells be for optimal usability?

These decisions significantly impact usability, implementation complexity, and future editability features.

## Decision

### 1. Horizontal Timeline Orientation

**Time flows horizontally (left to right), with weeks as columns and engineers as rows.**

```
       Week 1   Week 2   Week 3   ...
Alice  [Cell]   [Cell]   [Cell]   ...
Bob    [Cell]   [Cell]   [Cell]   ...
Carol  [Cell]   [Cell]   [Cell]   ...
```

**Rationale:**
- **Industry Standard**: Gantt charts, calendars, and project management tools use horizontal timelines
- **Natural Reading**: Left-to-right matches English reading direction for temporal progression
- **Better Screen Utilization**: Monitors are wider than tall (16:9, 16:10 aspect ratios)
- **Easier Multi-Week Visualization**: Horizontal connected cells are more intuitive for duration
- **Compact Vertical Space**: Engineer list can be long (10-20 people), horizontal saves vertical space

### 2. CSS Grid for Layout

**We use CSS Grid with dynamic column templates:**

```css
.allocation-grid {
  display: grid;
  grid-template-columns: 180px repeat(13, 120px);  /* Dynamic week count */
  grid-auto-rows: 48px;
}
```

**Why CSS Grid over alternatives:**

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **CSS Grid** | Native browser support, simple sticky positioning, automatic cell alignment, handles colspan/rowspan | Less flexible than canvas | **✅ Chosen** |
| HTML Table | Semantic, built-in row/column support | Harder to style, poor sticky support, layout inflexibility | ❌ |
| Flexbox | Good browser support, flexible | Requires nested containers, verbose for 2D grids | ❌ |
| Canvas/WebGL | Maximum flexibility, better performance at massive scale | No DOM (harder interactivity), accessibility challenges, re-implement everything | ❌ |
| Virtualized Grid (react-window) | Performance for huge datasets | Added complexity, harder to implement sticky headers | ❌ (premature optimization) |

**CSS Grid wins because:**
- Native sticky positioning for headers (`position: sticky`)
- Automatic cell sizing and alignment
- Simple to implement and understand
- Good performance for expected dataset sizes (up to ~50 weeks × 20 engineers = 1000 cells)
- Easy to add/remove rows and columns dynamically
- Accessibility built-in (DOM-based)

### 3. Sticky Headers with Z-Index Layering

**Both column headers (weeks) and row headers (engineers) remain visible during scroll:**

```css
.grid-header-corner {
  position: sticky;
  top: 0;
  left: 0;
  z-index: 3;  /* Highest - always on top */
}

.grid-week-header {
  position: sticky;
  top: 0;
  z-index: 2;  /* Above cells and row headers */
}

.grid-row-header {
  position: sticky;
  left: 0;
  z-index: 1;  /* Above cells, below column headers */
}
```

**Key Insight:** Z-index layering ensures the corner cell stays on top when scrolling both directions.

### 4. Multi-Week Cell Connection

**Visual continuity for projects spanning multiple weeks:**

- **First cell**: Rounded left edge, square right edge
- **Middle cells**: Square all edges, subtle border to show connection
- **Last cell**: Square left edge, rounded right edge, duration badge (e.g., "3w")

```
[  Project A  ][  Project A  ][  Project A  ]
 rounded-left    square-all    rounded-right (3w)
```

**Implementation:**
- Detect consecutive weeks with same project for same engineer
- Apply `CellPosition` enum: `First`, `Middle`, `Last`, `Standalone`
- CSS classes control border radii

### 5. Cell Dimensions

**Grid cells: 120px width × 48px height**

**Width (120px):**
- Fits project names with up to ~12-15 characters
- Allows room for percentage badge (e.g., "80%")
- 13 weeks × 120px = 1560px (fits on most laptop screens with scrolling)
- Not so wide that multi-week spans are hard to see

**Height (48px):**
- Fits project name, allocation percentage, and has breathing room
- Tall enough for comfortable click targets (WCAG 2.1 recommends 44px minimum)
- Allows stacking of text elements in split cells

**Row Headers (180px):**
- Fits "Firstname Lastname" + role badge
- Space for capacity indicator (progress bar + text)

## Alternatives Considered

### Alternative 1: Vertical Timeline (Weeks as Rows)

```
         Alice   Bob   Carol   ...
Week 1   [Cell]  [Cell] [Cell]  ...
Week 2   [Cell]  [Cell] [Cell]  ...
Week 3   [Cell]  [Cell] [Cell]  ...
```

**Rejected because:**
- Wastes vertical space (weeks can be 13-26 rows = lots of scrolling)
- Horizontal names don't fit well in narrow columns
- Multi-week projects harder to visualize vertically
- Less intuitive (timelines conventionally flow horizontally)
- Monitors are wider than tall - this fights aspect ratio

**Could work for:**
- Very few weeks (4-6) and many engineers (30+)
- Portrait displays
- Mobile/tablet layouts (future consideration)

### Alternative 2: Virtual Scrolling Grid

**Use react-window or similar for performance:**

**Rejected because:**
- Premature optimization (expected max: ~1000 cells, modern browsers handle this fine)
- Adds significant complexity
- Harder to implement sticky headers
- Interferes with CSS Grid's automatic layout
- Can add later if performance becomes an issue

**Reconsider if:**
- Supporting 50+ weeks or 50+ engineers
- Performance profiling shows render bottlenecks
- Planning for very large organizations

### Alternative 3: HTML Table

```html
<table>
  <thead>
    <tr><th></th><th>Week 1</th><th>Week 2</th></tr>
  </thead>
  <tbody>
    <tr><td>Alice</td><td>Cell</td><td>Cell</td></tr>
  </tbody>
</table>
```

**Rejected because:**
- Sticky positioning harder to implement reliably
- Less flexible styling (harder to customize cell appearance)
- Semantic mismatch (this isn't tabular data, it's a grid UI)
- Colspan/rowspan are awkward for multi-week cells

**Tables are better for:**
- Actual tabular data (our Roadmap view uses tables appropriately)
- Simpler layouts without complex sticky requirements

### Alternative 4: Canvas/WebGL Rendering

**Rejected because:**
- Massive engineering effort
- Lose accessibility (screen readers, keyboard navigation)
- Lose DOM benefits (hover, click, context menus)
- Harder to implement tooltips, modals, interactivity
- No need for performance at this scale

**Canvas would be appropriate for:**
- Hundreds of thousands of cells
- Custom visualizations (Gantt charts with dependencies)
- Games or real-time simulations

## Consequences

### Positive

- **Intuitive UX**: Horizontal timeline matches user mental models
- **Efficient Screen Use**: Wide layouts work well on modern displays
- **Simple Implementation**: CSS Grid is straightforward and well-supported
- **Accessible**: DOM-based, works with screen readers and keyboard navigation
- **Performant**: Good performance for expected dataset sizes
- **Maintainable**: Standard CSS, no complex virtualization logic
- **Future-Proof**: Easy to add features like drag-and-drop, context menus, tooltips

### Negative

- **Fixed Performance Ceiling**: CSS Grid may struggle with 100+ weeks or 100+ engineers
  - Mitigation: Virtual scrolling can be added later if needed
- **Horizontal Scrolling**: Wide grids require horizontal scroll
  - Mitigation: Sticky row headers keep engineer names visible
- **Browser Compatibility**: Requires modern browser with CSS Grid support
  - Acceptable: Target modern browsers (Chrome, Firefox, Safari from last 2 years)

### Neutral

- **Mobile Experience**: Horizontal timeline may be challenging on small screens
  - Future: Consider vertical timeline or simplified view for mobile (Phase 18)

## Implementation Details

### Dynamic Column Generation

```rust
let grid_template_columns = format!("180px repeat({}, 120px)", weeks.len());

rsx! {
    div {
        class: "allocation-grid",
        style: "grid-template-columns: {grid_template_columns};",
        // Grid content...
    }
}
```

### Cell Rendering Order

CSS Grid automatically places cells in the correct positions. We render in this order:

1. Corner cell (top-left)
2. Week headers (top row)
3. For each engineer:
   - Row header (engineer info)
   - Cells for each week

### Sticky Header Z-Index Strategy

```
┌─────────────┬──────┬──────┐
│ Corner (3)  │ Wk 1 │ Wk 2 │  ← Column headers (z-index: 2)
├─────────────┼──────┼──────┤
│ Alice (1)   │ Cell │ Cell │  ← Row headers (z-index: 1)
│ Bob (1)     │ Cell │ Cell │
└─────────────┴──────┴──────┘

Corner has highest z-index so it overlaps everything
Column headers overlap row headers
```

### Multi-Week Detection (Future)

Currently deferred to Phase 6 (Editing), but component structure supports it:

```rust
enum CellPosition {
    Standalone,  // Single week
    First,       // Start of multi-week
    Middle,      // Middle of multi-week
    Last,        // End of multi-week
}
```

Detection algorithm (future):
1. For each engineer, sort allocations by week
2. Group consecutive weeks with same project
3. If group size > 1, mark as First/Middle/Last
4. Add duration badge to Last cell

## Performance Characteristics

**Expected performance:**
- **13 weeks × 10 engineers**: ~130 cells, excellent performance
- **26 weeks × 20 engineers**: ~520 cells, good performance
- **52 weeks × 20 engineers**: ~1040 cells, acceptable performance
- **52 weeks × 50 engineers**: ~2600 cells, may need optimization

**Optimization strategies (if needed):**
1. Virtual scrolling for rows (engineers)
2. Memoize cell components
3. Lazy render cells outside viewport
4. Consider canvas rendering for very large grids

## Testing Considerations

- Test with varying week counts (13, 26, 52)
- Test with varying engineer counts (5, 10, 20, 50)
- Test sticky headers on actual scroll
- Test on different screen sizes (1280px, 1920px, 2560px)
- Test browser compatibility (Chrome, Firefox, Safari, Edge)

## Future Considerations

1. **Virtual Scrolling**: If performance becomes an issue with large datasets
2. **Mobile Layout**: Consider vertical timeline or simplified view for mobile (Phase 18)
3. **Zoom Levels**: Allow user to adjust cell size (narrow = more weeks visible, wide = more detail)
4. **Week Grouping**: Option to group weeks by sprint or month
5. **Gantt Dependencies**: If we add project dependencies, might need Gantt-like connectors

## References

- UI Design Spec: `docs/ui-design.md` (section 5.3, 7.3)
- Grid architecture: `docs/grid-architecture.md`
- CSS implementation: `assets/styling/main.css`
- GridCell component: `src/components/ui/grid_cell.rs`
- AllocationView: `src/components/views/allocation_view.rs`
