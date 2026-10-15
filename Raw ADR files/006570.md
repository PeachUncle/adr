# ADR-002: Component Organization Principles

## Status

**Accepted** - Implemented December 2024

## Context

As the Algorithm Visualization Platform grew to support multiple algorithms, the component directory structure needed to clearly communicate:

1. **Which components are reusable** across multiple algorithms
2. **Which components are algorithm-specific** and tied to a single algorithm
3. **Where new components should be placed** when adding algorithms

The initial structure mixed both types in a single `visualizations/` directory:

```
components/visualizations/
├── ArrayView.jsx              # Reusable ✓
├── TimelineView.jsx           # Reusable ✓
├── BinarySearchState.jsx      # Algorithm-specific ✗
└── IntervalCoverageState.jsx  # Algorithm-specific ✗
```

This created ambiguity:
- **New developers** couldn't tell which components were reusable
- **Component purpose** wasn't obvious from directory structure
- **Mental model** required reading component code to understand scope
- **Naming inconsistency** didn't distinguish between types

## Decision

**Organize components by reusability into two distinct directories with clear naming conventions.**

### Directory Structure

```
components/
├── algorithm-states/        # Algorithm-specific state components
│   ├── BinarySearchState.jsx
│   ├── IntervalCoverageState.jsx
│   └── index.js
└── visualizations/          # Reusable visualization building blocks
    ├── ArrayView.jsx
    ├── TimelineView.jsx
    └── index.js
```

### Naming Conventions

**Algorithm-Specific Components:** `{Algorithm}State.jsx`
- Examples: `BinarySearchState.jsx`, `MergeSortState.jsx`, `DijkstraState.jsx`
- Suffix `State` indicates algorithm-specific logic
- One component per algorithm (1:1 mapping)
- Lives in `algorithm-states/` directory

**Reusable Components:** `{Concept}View.jsx`
- Examples: `ArrayView.jsx`, `TimelineView.jsx`, `GraphView.jsx`
- Suffix `View` indicates generic display component
- Used by multiple algorithms (1:N mapping)
- Lives in `visualizations/` directory

### Architectural Principles

1. **Self-Evident Organization**
   - Directory name answers: "What goes here?"
   - File name answers: "Is this reusable?"
   - No need to read code to understand purpose

2. **Separation by Reusability**
   - `visualizations/`: Generic building blocks, algorithm-agnostic
   - `algorithm-states/`: Custom displays, algorithm-specific
   - Clear boundary = clear mental model

3. **Registry Integration**
   - `visualizations/` components registered in `visualizationRegistry.js`
   - `algorithm-states/` components registered in `stateRegistry.js`
   - Different registries = different purposes

4. **Scalability Focus**
   - Adding 100 algorithms = 100 files in `algorithm-states/`
   - NOT 100 directories (avoid `binary-search/`, `merge-sort/`, etc.)
   - Flat structure scales better than deep nesting

## Alternatives Considered

### Alternative 1: Keep Everything in visualizations/
**Approach:** Single directory for all visualization-related components

```
components/visualizations/
├── ArrayView.jsx
├── TimelineView.jsx
├── BinarySearchState.jsx
├── IntervalCoverageState.jsx
└── MergeSortState.jsx
```

**Pros:**
- Simple, flat structure
- All visualization code in one place
- No need to decide which directory

**Cons:**
- Ambiguous purpose (reusable vs specific?)
- Doesn't scale (100 algorithms = 100+ files in one directory)
- Mental model requires reading code
- "Can I reuse this?" question requires investigation

**Rejected Because:** Lack of clarity at scale; doesn't communicate intent

---

### Alternative 2: Organize by Algorithm
**Approach:** One directory per algorithm containing all its components

```
components/
├── binary-search/
│   ├── BinarySearchState.jsx
│   ├── BinarySearchVisualization.jsx
│   └── index.js
├── interval-coverage/
│   ├── IntervalCoverageState.jsx
│   ├── IntervalCoverageVisualization.jsx
│   └── index.js
└── shared/
    ├── ArrayView.jsx
    └── TimelineView.jsx
```

**Pros:**
- Algorithm code co-located
- Easy to find all files for one algorithm
- Clear ownership boundaries

**Cons:**
- Duplicates shared visualization components
- 100 algorithms = 100 directories (unwieldy)
- Registry pattern already organizes by algorithm
- Harder to identify reusable patterns
- Doesn't align with registry architecture

**Rejected Because:** Conflicts with registry pattern; over-fragments codebase

---

### Alternative 3: Organize by Feature
**Approach:** Group by UI feature (panels, modals, controls, displays)

```
components/
├── panels/
│   ├── LeftPanel.jsx
│   └── RightPanel.jsx
├── displays/
│   ├── ArrayView.jsx
│   ├── BinarySearchState.jsx
│   └── IntervalCoverageState.jsx
└── controls/
    ├── ControlBar.jsx
    └── AlgorithmSwitcher.jsx
```

**Pros:**
- Groups by UI responsibility
- Aligns with component hierarchy
- Clear feature boundaries

**Cons:**
- Still mixes reusable and specific in `displays/`
- Feature categories arbitrary (is StateComponent a "display"?)
- Doesn't solve original problem (reusability distinction)
- More directories = more navigation

**Rejected Because:** Doesn't address core issue of reusability distinction

---

### Alternative 4: Organize by Panel
**Approach:** Mirror physical UI layout

```
components/
├── left-panel/
│   ├── ArrayView.jsx
│   └── TimelineView.jsx
├── right-panel/
│   ├── BinarySearchState.jsx
│   └── IntervalCoverageState.jsx
└── shared/
    ├── ControlBar.jsx
    └── AlgorithmSwitcher.jsx
```

**Pros:**
- Mirrors visual structure
- Clear which panel uses which component
- Separation is physical and obvious

**Cons:**
- Couples components to layout (what if panels rearrange?)
- "left" and "right" don't describe purpose
- Doesn't scale to multi-panel layouts
- Names are positional, not semantic

**Rejected Because:** Physical layout is implementation detail; organize by purpose, not position

## Consequences

### Positive

1. **Instant Clarity**
   - Directory name tells you: "algorithm-specific" vs "reusable"
   - File name tells you: `State` vs `View`
   - Zero ambiguity for developers

2. **Onboarding Simplified**
   - New developers answer "Where does my component go?" in 5 seconds
   - Pattern is self-documenting
   - No need to read organizational guidelines

3. **Scalability Achieved**
   - 100 algorithms = 100 files in flat `algorithm-states/` directory
   - Manageable at scale (editors handle this well)
   - No nested directory explosion

4. **Mental Model Clarity**
   - "Need to visualize data generically?" → Look in `visualizations/`
   - "Need algorithm-specific state display?" → Look in `algorithm-states/`
   - "Adding a new algorithm?" → Create `{Algorithm}State.jsx` in `algorithm-states/`

5. **Consistency with Registry Pattern**
   - `algorithm-states/` components → `stateRegistry.js`
   - `visualizations/` components → `visualizationRegistry.js`
   - Directory structure mirrors architecture

### Negative

1. **Migration Required**
   - Existing components needed to be moved
   - Import paths needed updates
   - One-time cost during refactoring

2. **Two Locations to Check**
   - Finding a component requires knowing if it's reusable or specific
   - Could argue everything in one place is simpler
   - Mitigated by: Clear naming convention makes it obvious

3. **Judgment Calls**
   - Edge cases: "Is this component reusable or specific?"
   - Requires understanding component purpose
   - Mitigated by: Naming convention provides guidance

### Mitigation Strategies

For migration concerns:
- Performed as Phase 5 of systematic refactoring
- Comprehensive grep verification of import paths
- Zero functional regressions

For two-location concerns:
- Index files provide clean imports: `import { BinarySearchState } from '@/components/algorithm-states'`
- IDE "Go to Definition" works regardless of location
- README documents both directories clearly

For judgment call concerns:
- Rule of thumb: "Does it know about a specific algorithm?" → `algorithm-states/`
- Rule of thumb: "Could it display any algorithm's data?" → `visualizations/`
- When in doubt: Start in `algorithm-states/`, extract to `visualizations/` if reuse pattern emerges

## Implementation Details

### File Structure

**algorithm-states/index.js:**
```javascript
/**
 * Algorithm State Components Index
 *
 * These components are NOT reusable - each is tailored to one algorithm.
 * Naming convention: {Algorithm}State.jsx
 */

export { default as BinarySearchState } from './BinarySearchState';
export { default as IntervalCoverageState } from './IntervalCoverageState';
```

**visualizations/index.js:**
```javascript
/**
 * Visualization Components Index
 *
 * Reusable visualization components only.
 * These are generic, algorithm-agnostic building blocks.
 * Naming convention: {Concept}View.jsx
 */

export { default as TimelineView } from './TimelineView';
export { default as ArrayView } from './ArrayView';
```

### Import Patterns

**Before Phase 5:**
```javascript
import BinarySearchState from '../components/visualizations/BinarySearchState';
import IntervalCoverageState from '../components/visualizations/IntervalCoverageState';
```

**After Phase 5:**
```javascript
import BinarySearchState from '../components/algorithm-states/BinarySearchState';
import IntervalCoverageState from '../components/algorithm-states/IntervalCoverageState';
```

### Registry Integration

**stateRegistry.js** imports from `algorithm-states/`:
```javascript
import BinarySearchState from "../components/algorithm-states/BinarySearchState";
import IntervalCoverageState from "../components/algorithm-states/IntervalCoverageState";
```

**visualizationRegistry.js** imports from `visualizations/`:
```javascript
import ArrayView from "../components/visualizations/ArrayView";
import TimelineView from "../components/visualizations/TimelineView";
```

## Design Guidelines

### When to Create a New Component

**Create in `algorithm-states/` if:**
- Component displays state specific to ONE algorithm
- Component name naturally includes algorithm name
- Component is used ONLY in RIGHT panel
- Component is registered in `stateRegistry.js`

**Examples:**
- `BinarySearchState.jsx` - Shows binary search pointers and search space
- `IntervalCoverageState.jsx` - Shows call stack for interval coverage
- `MergeSortState.jsx` - Would show merge sort recursion tree

---

**Create in `visualizations/` if:**
- Component displays data in a generic way
- Component could be used by MULTIPLE algorithms
- Component is used in LEFT panel
- Component is registered in `visualizationRegistry.js`

**Examples:**
- `ArrayView.jsx` - Displays any array with states (used by Binary Search, Merge Sort, etc.)
- `TimelineView.jsx` - Displays any timeline with intervals (used by Interval Coverage)
- `GraphView.jsx` - Would display any graph structure (usable by DFS, BFS, Dijkstra, etc.)

### Naming Guidelines

**Algorithm-Specific Components:**
- Pattern: `{AlgorithmName}State.jsx`
- PascalCase algorithm name
- Always ends with `State`
- Examples:
  - `BinarySearchState.jsx` ✓
  - `MergeSortState.jsx` ✓
  - `DijkstraState.jsx` ✓
  - `BinarySearch.jsx` ✗ (missing `State`)
  - `SearchState.jsx` ✗ (too generic)

**Reusable Components:**
- Pattern: `{ConceptName}View.jsx`
- Describes what it displays, not which algorithm uses it
- Always ends with `View`
- Examples:
  - `ArrayView.jsx` ✓
  - `TimelineView.jsx` ✓
  - `GraphView.jsx` ✓
  - `TreeView.jsx` ✓
  - `Display.jsx` ✗ (too generic)
  - `BinarySearchArray.jsx` ✗ (algorithm-specific name)

## Validation

The organization principles were validated through:

1. **Successful Phase 5 Implementation** (December 2024)
   - Moved 3 files (2 state components + 1 test)
   - Updated 4 import paths
   - Zero functional regressions

2. **Developer Feedback**
   - "Immediately obvious where to put new components"
   - "Don't need to read code to understand purpose"
   - "Naming convention makes mental model clear"

3. **Code Metrics**
   - Clean separation: 0 algorithm-specific components in `visualizations/`
   - Clear exports: Index files document purpose
   - Maintainable: Flat structure scales to 100+ algorithms

## Related Decisions

- **ADR-001**: Registry-Based Architecture (explains why registries exist for both directories)
- **Backend Registry Pattern**: Organizational principles mirror backend algorithm registry structure

## Future Considerations

1. **Automatic Validation**
   - Build-time check: Components in `visualizations/` don't import from `algorithm-states/`
   - Linting rule: Enforce naming conventions (`State` vs `View` suffix)
   - CI/CD integration

2. **Documentation Generation**
   - Auto-generate component catalog from directory structure
   - Extract PropTypes for documentation
   - Show which algorithms use which visualizations

3. **Component Templates**
   - Provide templates: `template-algorithm-state.jsx`, `template-visualization.jsx`
   - Include boilerplate, PropTypes, and comments
   - Speed up new algorithm additions

4. **Refactoring Opportunities**
   - Extract common patterns from algorithm-specific components
   - Identify reusable pieces currently in `algorithm-states/`
   - Promote to `visualizations/` when pattern emerges

## References

- Implementation: Session 41 (December 14, 2024)
- Refactoring Plan: `docs/REFACTORING_FE_PHASED_PLAN.md` (Phase 5)
- Code Structure: `frontend/src/components/`
- This Document: `docs/ADR/FRONTEND/ADR-002-component-organization-principles.md`

---

**Author:** Development Team  
**Date:** December 14, 2024  
**Last Updated:** December 14, 2024