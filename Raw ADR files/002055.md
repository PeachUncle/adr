## Context
The UI Kit currently re-exports Sonner's `toast` function directly. While functional, this pattern:
- Couples consumers to Sonner's specific API
- Lacks centralized default configuration
- Makes testing/mocking more difficult
- Doesn't provide React-idiomatic patterns

## Goals / Non-Goals
- **Goals:**
  - Provide a React hook wrapper around Sonner's toast functionality
  - Enable configurable defaults per-hook instance
  - Maintain type safety with app-specific toast patterns
  - Remove direct `toast` export to enforce consistent usage patterns

- **Non-Goals:**
  - Replace Sonner with a custom implementation
  - Add Redux or global state management (violates UIKIT rules)

## Decisions

### Hook API Design
The `useToast` hook will return an object with typed methods:

```typescript
interface UseToastOptions {
  defaultDuration?: number;
  defaultPosition?: ToastPosition;
}

interface UseToastReturn {
  toast: (message: string, options?: ToastOptions) => string | number;
  success: (message: string, options?: ToastOptions) => string | number;
  error: (message: string, options?: ToastOptions) => string | number;
  warning: (message: string, options?: ToastOptions) => string | number;
  info: (message: string, options?: ToastOptions) => string | number;
  loading: (message: string, options?: ToastOptions) => string | number;
  promise: <T>(promise: Promise<T> | (() => Promise<T>), options: ToastPromiseOptions<T>) => Promise<T>;
  dismiss: (toastId?: string | number) => void;
}
```

**Rationale:** This mirrors Sonner's API but through a hook pattern, allowing:
1. Future customization without changing call sites
2. Potential default merging from context or config
3. Better tree-shaking if methods aren't used

### File Location
`packages/uikit/src/hooks/useToast.ts`

**Rationale:** Following the pattern of other hook exports in uikit, keeps hooks separate from base components.

### Alternatives Considered

1. **Context Provider + Hook**
   - Pros: Global configuration, theme-aware defaults
   - Cons: Requires provider wrapper, adds complexity, violates "no state management" rule
   - Decision: Rejected for V1, can be added later if needed

2. **Factory Function (createToast)**
   - Pros: No React dependency, works outside components
   - Cons: Not React-idiomatic, harder to use with component lifecycle
   - Decision: Rejected in favor of hook pattern

3. **Keep Direct Export + Add Hook**
   - Pros: No breaking changes, gradual migration
   - Cons: Inconsistent usage patterns, potential confusion
   - Decision: Rejected in favor of clean break to hook-only pattern

## Risks / Trade-offs

- **Breaking Change**: All consumers using `toast` directly must migrate
  - Mitigation: Clear migration path, hook API mirrors Sonner's methods

- **React-Only Usage**: Toast can only be triggered from React components
  - Mitigation: This aligns with the app's React-first architecture

## Migration Plan

1. Create `useToast` hook with full toast functionality
2. Remove `toast` export from base/sonner.tsx and index.ts
3. Update all consumers to use the hook pattern
4. Update demo component to showcase new pattern

## Open Questions

- Should we add a `ToastProvider` context for global defaults? (Deferred to future iteration)
- Should toast types be strict enums or remain string literals? (Keep Sonner's patterns for now)
