# ADR 004: React Artifacts Architecture

**Date:** 2025-10-19
**Status:** Accepted

## Context

AI Learning Agent needs to support interactive React components as artifacts to enable students to learn:
- **Level 4:** Recharts graphs (line, bar, area charts)
- **Level 5:** Animated diagrams (P-V diagrams, Otto cycle animations)
- **Level 6:** (future) 3D models with Three.js/React Three Fiber

The existing artifact system supports static types (markdown, code, images) and simple interactive types (plots via Plotly, calculators via Math.js), but lacks infrastructure for rendering custom React components.

**Constraints:**
- Frontend uses Vite bundler (not Webpack)
- Components must load dynamically (code splitting)
- Must handle component errors gracefully
- Must support props passing from artifact config
- Backend uses YAML frontmatter for artifact metadata

## Decision

Implement React artifacts using **React.lazy + Suspense + Static Registry Pattern**:

1. **ReactArtifact.jsx** - Main wrapper component using React.lazy and Suspense
2. **Static Registry** - Centralized mapping of component IDs to lazy imports
3. **Error Boundary** - Component-level error handling
4. **Flat YAML Frontmatter** - Simple metadata format for backend

## Rationale

### 1. React.lazy + Suspense (Industry Standard)

React.lazy is the official React API for code splitting and dynamic imports. It's:
- Built into React core (no external dependencies)
- Industry best practice for lazy loading components
- Integrates perfectly with Suspense for loading states
- Supports automatic code splitting in production builds

### 2. Static Registry Pattern (Vite Requirement)

Vite's build-time analysis requires **static import paths**. This code fails:
```javascript
// ❌ DOESN'T WORK with Vite
const componentId = 'hello-react';
const Component = lazy(() => import(`./templates/${componentId}.jsx`));
```

Vite cannot analyze dynamic string concatenation at build time. Solution:
```javascript
// ✅ WORKS with Vite
export const REACT_COMPONENTS = {
  'hello-react': lazy(() => import('./HelloReact.jsx')),
  'recharts-line': lazy(() => import('./RechartsLine.jsx')),
  // All paths are static strings
};
```

### 3. Error Boundary (Prevent App Crashes)

React Error Boundaries catch errors in component trees and display fallback UI instead of crashing the entire app. Critical for educational platform where:
- Students may trigger edge cases
- Components may have bugs during development
- User experience must remain stable

### 4. Flat YAML Frontmatter (Parser Simplicity)

Backend uses simple YAML parser that struggles with nested objects. Flat structure is more reliable:
```yaml
# ✅ Works reliably
componentId: hello-react
propsTitle: React Artifacts Test
propsMessage: Component working!

# ❌ Complex for simple parser
config:
  id: hello-react
  props:
    title: React Artifacts Test
```

## Consequences

### Advantages

✅ **Code Splitting** - Each React component loads on-demand, reducing initial bundle size

✅ **Type Safety** - React.lazy provides TypeScript support for lazy-loaded components

✅ **Loading States** - Suspense gives automatic loading UI during component fetch

✅ **Error Isolation** - Error Boundary prevents component errors from crashing app

✅ **Vite Compatible** - Static registry works perfectly with Vite's build-time analysis

✅ **Scalable** - Easy to add new components (just add one line to registry)

✅ **Standard Practice** - Uses official React APIs, easy for developers to understand

### Disadvantages

⚠️ **Manual Registration** - Each new component requires adding to registry (1 line of code)

⚠️ **No True Dynamic Imports** - Cannot load arbitrary components from user input (security feature, not a bug)

⚠️ **Flat Frontmatter Limitation** - Complex props require multiple YAML fields (propsTitle, propsMessage, etc.)

## Alternatives Considered

### Alternative 1: Fully Dynamic Import Paths

**Approach:**
```javascript
const Component = lazy(() => import(`./templates/${componentId}.jsx`));
```

**Pros:**
- No registry needed
- Truly dynamic component loading

**Cons:**
- **Breaks Vite build** - Vite cannot analyze dynamic paths
- Security risk - could load arbitrary files
- No TypeScript support

**Why rejected:** Incompatible with Vite bundler. Would require switching to Webpack (major infrastructure change).

### Alternative 2: Import All Components Eagerly

**Approach:**
```javascript
import HelloReact from './templates/HelloReact.jsx';
import RechartsLine from './templates/RechartsLine.jsx';
// ... import all components

const COMPONENTS = {
  'hello-react': HelloReact,
  'recharts-line': RechartsLine,
};
```

**Pros:**
- Simple mapping
- No lazy loading complexity

**Cons:**
- **Huge initial bundle** - All components load upfront
- Slow page load for users who don't use React artifacts
- Defeats code splitting benefits

**Why rejected:** Poor performance for large component library. Lesson viewer should be fast even if React artifacts aren't used.

### Alternative 3: iframe with Dynamic Component Loading

**Approach:**
Render each React component in an isolated iframe with its own bundle.

**Pros:**
- Complete isolation between components
- Could load truly dynamic code

**Cons:**
- **Complex communication** - Need postMessage protocol for props
- **Poor UX** - iframe scrolling, styling issues
- **Development overhead** - Separate build process for iframe bundles

**Why rejected:** Over-engineered for educational platform. Error Boundary provides sufficient isolation.

### Alternative 4: Nested YAML Config with Custom Parser

**Approach:**
Write custom YAML parser to handle nested objects correctly.

**Pros:**
- Cleaner frontmatter structure
- More intuitive config format

**Cons:**
- **Engineering time** - Custom parser is complex
- **Maintenance burden** - Must maintain parser
- **Flat structure works fine** - propsTitle, propsMessage is clear enough

**Why rejected:** Not worth the engineering effort. Flat YAML works reliably with existing parser.

## Implementation Notes

### Registry Structure

Location: `frontend/src/templates/react/registry.js`

```javascript
import { lazy } from 'react';

// Static mapping for Vite build-time analysis
export const REACT_COMPONENTS = {
  'hello-react': lazy(() => import('./HelloReact.jsx')),
  // Add new components here as one-liners
};

export function getReactComponent(componentId) {
  return REACT_COMPONENTS[componentId] || null;
}

export function hasReactComponent(componentId) {
  return componentId in REACT_COMPONENTS;
}
```

### ReactArtifact Wrapper

Location: `frontend/src/components/artifacts/ReactArtifact.jsx`

```javascript
import { Suspense } from 'react';
import { getReactComponent, hasReactComponent } from '../../templates/react/registry';
import ReactArtifactErrorBoundary from './ReactArtifactErrorBoundary';

export default function ReactArtifact({ componentId, props: componentProps = {} }) {
  if (!hasReactComponent(componentId)) {
    return <div className="artifact-not-found">Component not found: {componentId}</div>;
  }

  const LazyComponent = getReactComponent(componentId);

  return (
    <ReactArtifactErrorBoundary componentId={componentId}>
      <Suspense fallback={<LoadingFallback componentId={componentId} />}>
        <LazyComponent {...componentProps} />
      </Suspense>
    </ReactArtifactErrorBoundary>
  );
}
```

### YAML Frontmatter Format

Location: `docs/artifacts/hello-react.md`

```yaml
---
id: hello-react
title: Hello React Test Component
type: react-component
componentId: hello-react
propsTitle: React Artifacts Test
propsMessage: React.lazy + Suspense working!
propsTimestamp: 1729350000000
---
```

Backend builds config object:
```python
# backend/main.py
if meta.get("type") == "react-component":
    config_dict = {
        "type": "react-component",
        "id": meta.get("componentId", artifact_id),
        "props": {
            "title": meta.get("propsTitle"),
            "message": meta.get("propsMessage"),
            "timestamp": int(meta.get("propsTimestamp", 0))
        }
    }
```

### Adding New Components (3-Step Process)

**Step 1:** Create component file
```bash
frontend/src/templates/react/MyNewComponent.jsx
```

**Step 2:** Register in registry
```javascript
// frontend/src/templates/react/registry.js
export const REACT_COMPONENTS = {
  'hello-react': lazy(() => import('./HelloReact.jsx')),
  'my-new-component': lazy(() => import('./MyNewComponent.jsx')), // Add this line
};
```

**Step 3:** Create artifact file
```bash
docs/artifacts/my-new-component.md
```

## Future Considerations

### When to Review This Decision

- **If Vite adds support for dynamic import patterns** - Could simplify to remove registry
- **If we need 100+ React components** - Manual registration becomes tedious, might need automation
- **If we add user-generated components** - Would need sandboxing (iframe or Web Workers)
- **If backend parser upgrades** - Could switch to nested YAML config

### Potential Improvements

1. **Auto-generate registry** - Script to scan `templates/react/` and build registry automatically
2. **TypeScript for props** - Define PropTypes or TypeScript interfaces for each component
3. **Component versioning** - Support multiple versions of same component (v1, v2)
4. **Hot reload improvements** - Vite HMR sometimes requires manual refresh

## Related Decisions

- ADR 001: Why OpenRouter - Related to AI integration philosophy
- (Future) ADR 005: Recharts vs Chart.js - Which library for Level 4 graphs
- (Future) ADR 006: 3D Artifact Architecture - Three.js integration for Level 6

## References

### Official Documentation
- React.lazy: https://react.dev/reference/react/lazy
- Suspense: https://react.dev/reference/react/Suspense
- Error Boundaries: https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary
- Vite Dynamic Import: https://vitejs.dev/guide/features.html#dynamic-import

### Implementation Files
- `frontend/src/components/artifacts/ReactArtifact.jsx`
- `frontend/src/components/artifacts/ReactArtifactErrorBoundary.jsx`
- `frontend/src/templates/react/registry.js`
- `frontend/src/templates/react/HelloReact.jsx`
- `backend/models.py` (ArtifactType enum)
- `backend/main.py` (artifact loading logic)

### Related Documentation
- `react-artifacts-roadmap.md` - Full project roadmap
- `CHANGELOG.md` - Phase 1 implementation details
