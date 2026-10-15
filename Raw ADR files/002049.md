# Design: Screen Lazy-Loading

## Context

HAI3 currently loads all screen components eagerly through direct imports at screenset registration time. As applications grow with more screensets and screens, this creates larger initial bundles and slower startup times.

**Current Flow:**
```typescript
// Eager import
import { HelloWorldScreen } from './screens/helloworld/HelloWorldScreen';

// Direct component reference
menu: [{
  menuItem: { id: 'hello', label: '...', icon: '...' },
  screen: HelloWorldScreen  // Loaded immediately
}]
```

**Constraints:**
- Must maintain backward compatibility with existing screensets
- Cannot require configuration changes in existing code
- Must work with React 18 and Vite 6
- Should align with event-driven architecture
- Must not break TypeScript strict mode

**Stakeholders:**
- Screenset authors (simplified API)
- End users (faster load times)
- Framework maintainers (uicore package)

## Goals / Non-Goals

**Goals:**
- ✅ Enable code-splitting for screen components
- ✅ Reduce initial bundle size
- ✅ Improve time-to-interactive
- ✅ Provide declarative API (no manual React.lazy usage)
- ✅ Ensure consistent performance across all screens
- ✅ Maintain type safety
- ✅ Simplify implementation (no runtime type checking)

**Non-Goals:**
- ❌ Maintain backward compatibility (breaking change accepted)
- ❌ Support mixing eager and lazy screens
- ❌ Optimize lazy-loading of other resources (icons, translations)
- ❌ Implement route-based code-splitting (already handled by Vite)
- ❌ Add preloading or prefetching strategies (future enhancement)
- ❌ Change screenset registration flow or event architecture

## Decisions

### Decision 1: Mandatory Lazy-Loading (Breaking Change)

**Choice:** Require all screens to use lazy loaders

```typescript
export type ScreenLoader = () => Promise<{ default: React.ComponentType }>;

export interface MenuScreenItem {
  menuItem: MenuItem;
  screen: ScreenLoader;  // Only lazy loaders allowed
}
```

**Alternatives considered:**
1. **Union type:** `screen: React.ComponentType | ScreenLoader`
   - ❌ More complex implementation (runtime type checking)
   - ❌ Inconsistent performance (some screens fast, some lazy)
   - ❌ Future maintenance burden (two code paths)

2. **Optional loader property:** `screen: Component, loader?: ScreenLoader`
   - ❌ Confusing API (two ways to specify screen)
   - ❌ Error-prone (both could be set)

3. **Separate interfaces:** `MenuScreenItemEager` and `MenuScreenItemLazy`
   - ❌ Breaks existing code
   - ❌ Requires changes to screenset registry logic

**Rationale:**
- Simpler implementation (no runtime type checking needed)
- Consistent performance characteristics across all screens
- Future-proof architecture
- Only 2 screensets currently exist (minimal migration cost)
- Clear, single way to define screens (principle of least surprise)

### Decision 2: Lazy Wrapping in Screen Component

**Choice:** Wrap lazy loaders with `React.lazy()` in the Screen component (not registry)

```typescript
// In Screen.tsx
const LazyComponent = React.lazy(screenLoader);
```

**Alternatives considered:**
1. **Wrap in registry during `getScreens()`**
   - ❌ Registry becomes aware of React implementation details
   - ❌ Violates separation of concerns
   - ❌ Harder to test

2. **Require screenset authors to use React.lazy()**
   - ❌ Not declarative
   - ❌ More boilerplate
   - ❌ Easier to get wrong

**Rationale:** Screen component already renders the component, so it's the natural place for React.lazy. Registry remains a simple data structure. No runtime type checking needed since all screens are lazy.

### Decision 3: Suspense Boundary and Fallback UI

**Choice:** Wrap lazy components with Suspense in Screen component, provide minimal fallback

```tsx
<Suspense fallback={<ScreenLoadingFallback />}>
  <LazyComponent />
</Suspense>
```

**Fallback Design:**
- Minimal spinner or skeleton
- Consistent with HAI3 design system
- No flash of loading state for fast loads
- Respects theme tokens

**Alternatives considered:**
1. **No fallback (let Suspense use null)**
   - ❌ Poor user experience
   - ❌ Layout shift

2. **Configurable fallback per screenset**
   - ❌ Over-engineering
   - ❌ Inconsistent UX across app

3. **Full screen loading overlay**
   - ❌ Too heavy for screen transitions
   - ❌ Blocks UI unnecessarily

**Rationale:** Single, consistent fallback provides good UX without complexity. Can be enhanced later if needed.

### Decision 4: Error Handling

**Choice:** Rely on existing error boundary pattern, don't add screen-specific error handling

**Rationale:**
- HAI3 should have application-level error boundary
- Lazy loading errors (network failures, chunk load errors) are rare
- Better handled at app level with retry logic
- Keeps Screen component simple

**Future Enhancement:** Add `errorElement` to `MenuScreenItem` if needed.

## Risks / Trade-offs

### Risk: Breaking Changes
- **Risk:** Type changes could break existing TypeScript code
- **Mitigation:** Union type is additive, not breaking. Existing `React.ComponentType` values still valid.
- **Testing:** Validate with existing screensets before merging.

### Risk: Runtime Errors
- **Risk:** Lazy loading can fail (network issues, 404s on chunks)
- **Mitigation:** Rely on error boundaries. Document best practices.
- **Future:** Add retry mechanism or error recovery.

### Risk: Flash of Loading State
- **Risk:** Fast networks might show loading spinner briefly (poor UX)
- **Mitigation:** Use CSS transitions with delay (e.g., `opacity: 0` for 150ms)
- **Acceptable:** Modern bundlers and CDNs make loads fast enough.

### Trade-off: Complexity vs Performance
- **Trade-off:** Adds React.lazy and Suspense complexity
- **Benefit:** Measurable performance improvement for large apps
- **Verdict:** Worth it. Pattern is well-understood in React ecosystem.

## Migration Plan

### Phase 1: Update Core Types (Breaking)
1. Update `MenuScreenItem.screen` type to `ScreenLoader` only
2. Update Screen component with Suspense
3. Update screenset registry to handle loaders
4. Run type-check to identify all breaking changes

### Phase 2: Convert Existing Screensets (Required)
1. Convert demo screenset (4 screens)
   - HelloWorldScreen
   - CurrentThemeScreen
   - ProfileScreen
   - UIKitElementsScreen
2. Convert chat screenset (1 screen)
   - ChatScreen
3. Update screen exports to use default export pattern
4. Test all screensets in browser

### Phase 3: Update Documentation
1. Update CLAUDE.md with lazy-loading pattern
2. Update screenset creation examples
3. Update `/new-screenset` command template
4. Add migration notes

### Example Migration:

**Before:**
```typescript
import { HelloWorldScreen } from './screens/helloworld/HelloWorldScreen';

menu: [{
  menuItem: { id: 'hello', label: '...', icon: '...' },
  screen: HelloWorldScreen  // Direct reference
}]
```

**After (Screen File):**
```typescript
// Add default export to screen file
export const HelloWorldScreen: React.FC = () => { /* ... */ };
export default HelloWorldScreen;  // Add this line
```

**After (Screenset Config):**
```typescript
// No top-level import needed anymore
menu: [{
  menuItem: { id: 'hello', label: '...', icon: '...' },
  screen: () => import('./screens/helloworld/HelloWorldScreen')  // Dynamic import
}]
```

### Rollback Plan
- Revert type changes in `MenuScreenItem`
- Remove dynamic imports from screensets
- Restore direct imports
- Remove Suspense wrapper from Screen component
- No database or state migration needed (all in code)

## Open Questions

1. **Should we provide a helper function for creating loaders?**
   - e.g., `createScreenLoader(() => import('./Screen'))`
   - Decision: Defer until we see if it's needed. Current API is simple enough.

2. **Should we preload screens on menu hover?**
   - Potential UX improvement
   - Decision: Future enhancement. Not critical for MVP.

3. **Should we track lazy loading metrics?**
   - Useful for performance monitoring
   - Decision: Can add event emissions later if needed. Not required for initial implementation.

4. **Should fallback UI be customizable?**
   - Some apps might want branded loading states
   - Decision: Start with single fallback. Add customization if requested.
