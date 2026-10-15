# ADR 004: Layered Architecture with Feature Separation

**Status:** Accepted

**Date:** 2025-10-18

**Context:**

WCAG Explorer is a single-page React application with multiple concerns:
- UI components and presentation
- Business logic and data transformation
- API communication
- State management and persistence
- Routing and navigation
- Accessibility features

We needed an architectural pattern that would:
- Keep code organized as the application grows
- Separate concerns clearly
- Make testing easier
- Enable multiple developers to work without conflicts
- Maintain good performance
- Support accessibility requirements

Common architectural approaches for React applications include:
- Flat structure (all files in one directory)
- Feature-based structure (group by feature)
- Layered structure (group by technical role)
- Feature-sliced design (hybrid approach)

**Decision:**

We will use a **layered architecture** with clear separation between:

1. **Presentation Layer** (`/components`, `/pages`)
   - React components responsible for rendering UI
   - Receive data via props, emit events via callbacks
   - No direct API calls or business logic

2. **Business Logic Layer** (`/lib`)
   - Pure functions and utilities
   - Type definitions
   - API client logic
   - State management utilities
   - No React dependencies

3. **Integration Layer** (`/utils`)
   - Cross-cutting concerns (accessibility announcements)
   - Browser API wrappers
   - Thin integration code

4. **Static Content** (`/public`)
   - Markdown files
   - Assets served directly

### Directory Structure

```
src/
├── components/          # Presentation components
│   ├── CriterionCard.tsx
│   ├── Filters.tsx
│   └── ...
├── pages/              # Route-level components
│   ├── AdminPage.tsx
│   └── SettingsPage.tsx
├── lib/                # Business logic (no React)
│   ├── api.ts
│   ├── types.ts
│   ├── urlUtils.ts
│   └── ...
├── utils/              # Cross-cutting utilities
│   └── announce.ts
├── App.tsx             # Main container
└── main.tsx            # Entry point
```

**Consequences:**

### Positive

1. **Clear Separation of Concerns:**
   - Components focus on presentation
   - Business logic is isolated and testable
   - Easy to find where specific code lives

2. **Testability:**
   - Can test business logic without React
   - Can test components with mocked dependencies
   - Pure functions in `/lib` are trivial to unit test

3. **Maintainability:**
   - Changes to UI don't affect business logic
   - API changes are localized to `/lib/api.ts`
   - Type changes propagate clearly through layers

4. **Reusability:**
   - Components can be reused in different contexts
   - Utilities are framework-agnostic
   - Business logic could be shared with other interfaces

5. **Team Collaboration:**
   - Clear boundaries reduce merge conflicts
   - New developers understand where to put code
   - Component library could be extracted easily

6. **Performance:**
   - Can optimize layers independently
   - Tree-shaking works well with clear modules
   - Code splitting follows natural boundaries

7. **Progressive Enhancement:**
   - Business logic doesn't depend on React
   - Could add SSR without major refactoring
   - Could build CLI or API consumer reusing `/lib`

### Negative

1. **Not Feature-Oriented:**
   - Related code is split across directories
   - To understand a feature, must look in multiple places
   - Harder to delete entire features cleanly

2. **Potential Over-Abstraction:**
   - Simple components may have unnecessary layers
   - Can lead to "pass-through" code
   - Utilities might be overkill for one-time use

3. **File Navigation:**
   - More directories to navigate
   - Import paths can be longer
   - Need good IDE navigation or aliases

4. **Learning Curve:**
   - New developers need to understand layer responsibilities
   - Must decide which layer owns new code
   - Can lead to inconsistency if guidelines unclear

5. **Container/Presentational Split:**
   - Some components straddle the line (Filters.tsx has API calls)
   - Not always clear where container ends and presentation begins
   - Can lead to "god components" (App.tsx)

### Design Principles

1. **Components should be dumb:**
   - Receive data via props
   - Emit events via callbacks
   - No business logic or calculations
   - Exception: Local UI state (open/closed, hover)

2. **Business logic should be pure:**
   - No React hooks or components
   - No side effects (except I/O clearly marked as async)
   - Fully testable without DOM

3. **One-way data flow:**
   - Data flows down through props
   - Events bubble up through callbacks
   - URL is source of truth for app state

4. **Explicit dependencies:**
   - Clear import paths
   - No circular dependencies
   - Minimal coupling between layers

**Alternatives Considered:**

### Flat Structure
- **Pros:** Simple, no decisions about where to put files
- **Cons:** Becomes unwieldy as project grows, hard to navigate
- **Reason for rejection:** Not scalable for a project of this size

### Feature-Based Structure (Vertical Slices)
```
src/
├── features/
│   ├── search/
│   │   ├── SearchBar.tsx
│   │   ├── searchApi.ts
│   │   └── searchUtils.ts
│   ├── filters/
│   └── favorites/
```
- **Pros:**
  - Related code together
  - Easy to delete features
  - Clear feature ownership
- **Cons:**
  - Shared components/utils need special handling
  - More directories
  - Can duplicate common logic
- **Reason for rejection:** WCAG Explorer features are highly interconnected (filters, search, results all work together). Vertical slices would create artificial boundaries.

### Feature-Sliced Design (FSD)
```
src/
├── app/        # App-level initialization
├── pages/      # Route-level
├── widgets/    # Large components
├── features/   # Business features
├── entities/   # Domain models
├── shared/     # Shared code
```
- **Pros:**
  - Scales very well
  - Clear dependencies (upper layers import from lower)
  - Good for large teams
- **Cons:**
  - Overkill for small/medium apps
  - Steep learning curve
  - More ceremony and boilerplate
- **Reason for rejection:** Too complex for current needs. May reconsider if app grows significantly.

### Atomic Design (UI Components)
```
src/
├── atoms/      # Button, Input
├── molecules/  # SearchBar
├── organisms/  # CriterionCard
├── templates/  # Page layouts
└── pages/      # Final pages
```
- **Pros:**
  - Great for design systems
  - Clear component hierarchy
  - Encourages reusability
- **Cons:**
  - Focused only on UI layer
  - Doesn't address business logic organization
  - Boundary between atoms/molecules/organisms can be fuzzy
- **Reason for rejection:** Solves UI organization but not full application architecture. Could be combined with layered approach if needed.

### Monolithic (Everything in App.tsx)
- **Pros:** Simple, no indirection
- **Cons:** Unmaintainable, untestable, unscalable
- **Reason for rejection:** Already past this point with 16+ components

**Implementation Guidelines:**

### When Adding New Code

1. **Components** → Put in `/components` if:
   - It renders UI
   - It's reusable across pages
   - It has local state only (UI state)

2. **Pages** → Put in `/pages` if:
   - It's a route-level component
   - It coordinates multiple features
   - It's a distinct screen/view

3. **Library** → Put in `/lib` if:
   - It's pure business logic
   - It has no React dependencies
   - It's a utility function or type
   - It communicates with external systems

4. **Utils** → Put in `/utils` if:
   - It's a cross-cutting concern
   - It integrates with browser APIs
   - It doesn't fit cleanly in other categories

### Import Rules

```typescript
// ✅ Good: Components import from lib
import { getCriteria } from '../lib/api';
import type { Criterion } from '../lib/types';

// ✅ Good: Lib modules import other lib modules
import type { QueryFilters } from './types';

// ❌ Bad: Lib importing components
import CriterionCard from '../components/CriterionCard';

// ❌ Bad: Circular dependencies
// types.ts imports from api.ts which imports from types.ts
```

**Notes:**

- This is a pragmatic layered architecture, not dogmatic
- Some flexibility is allowed (e.g., Filters.tsx fetches metadata)
- As app grows, we can refine boundaries or migrate to feature-sliced design
- Current structure works well for team size and application complexity
