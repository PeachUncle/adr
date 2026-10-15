# ADR-004: State Management

## Status

Accepted

## Context

Rule Bound is a rules reference application that needs to manage:

- **Rules Content**: Data from the Riftbound Core Rules PDF
- **UI State**: Navigation, search, filters, bookmarks
- **User Preferences**: Theme, font size, favorites
- **Application State**: Loading states, errors, current view

As a reference application (not a complex SaaS), the state management needs are relatively straightforward:

- Mostly read-heavy operations (displaying rules)
- Some local state (search, filters, preferences)
- No complex server synchronization
- Potential for offline access
- Need for good performance on mobile

## Options Considered

### 1. React Context + Hooks (Built-in)

- **Pros:**
  - No additional dependencies
  - Simple, built into React
  - Good TypeScript support
  - Sufficient for simple state
  - Easy to understand
- **Cons:**
  - Can cause unnecessary re-renders if not careful
  - No built-in devtools
  - Can become verbose with multiple contexts
  - No middleware system

### 2. Zustand

- **Pros:**
  - Minimal boilerplate
  - Excellent TypeScript support
  - Small bundle size (~1KB)
  - Simple API (hooks-based)
  - Good performance
  - Middleware support
  - DevTools available
  - Can persist state easily
- **Cons:**
  - Additional dependency (very small)
  - Less prescriptive than Redux

### 3. Redux Toolkit

- **Pros:**
  - Industry standard
  - Excellent DevTools
  - Strong patterns and best practices
  - Good for large-scale apps
  - Comprehensive ecosystem
- **Cons:**
  - More boilerplate
  - Larger bundle size
  - May be overkill for this app
  - Steeper learning curve

### 4. Jotai / Recoil

- **Pros:**
  - Atomic state management
  - Flexible and powerful
  - Good TypeScript support
- **Cons:**
  - More complex mental model
  - Less established than alternatives
  - May be over-engineered for our needs

## Decision

We will use a **hybrid approach**:

1. **React Context + Hooks** for simple, localized state (UI state, theme)
2. **Zustand** for global application state (rules data, user preferences, bookmarks)

**Key reasons:**

1. **Pragmatic**: Use built-in tools where they suffice, add Zustand only where needed
2. **Performance**: Zustand won't trigger unnecessary re-renders
3. **Simple**: Minimal boilerplate, easy to understand
4. **TypeScript**: Excellent type inference and safety
5. **Size**: Very small bundle impact (~1KB for Zustand)
6. **Persistence**: Easy to persist user preferences to localStorage
7. **DevTools**: Available when needed for debugging
8. **Appropriate Scale**: Perfect fit for an application of this complexity

## Consequences

### Positive

- Simple, maintainable state management
- Good performance on mobile (minimal re-renders)
- Easy to persist user preferences
- Low bundle size impact
- TypeScript provides excellent autocomplete and type safety
- Easy to test state logic
- Flexible: can use Context for simple cases, Zustand for complex

### Negative

- Need to decide when to use Context vs Zustand (documentation will clarify)
- Slightly less prescriptive than Redux (need to establish patterns)

### Neutral

- Will have multiple state management approaches (but clearly separated)
- Developers need to learn both Context and Zustand (both are simple)

### Implementation Guidelines

#### Use React Context + Hooks for:

- Theme/dark mode toggle
- UI-only state (modals, dropdowns, temporary form state)
- State that's only needed in a small component tree
- State that doesn't change frequently

Example:

```typescript
// ThemeContext for dark mode toggle
const ThemeContext = createContext<ThemeContextType | null>(null);
```

#### Use Zustand for:

- Rules content data
- User bookmarks/favorites
- User preferences (font size, accessibility settings)
- Search state and filters
- Any state that needs localStorage persistence
- State that's accessed by many components

Example:

```typescript
// Store for rules data and user preferences
interface RulesStore {
  rules: Rule[];
  bookmarks: string[];
  addBookmark: (ruleId: string) => void;
  removeBookmark: (ruleId: string) => void;
}

const useRulesStore = create<RulesStore>((set) => ({...}));
```

#### Persistence Strategy

- Use Zustand's `persist` middleware for user preferences
- Store in localStorage with versioning
- Implement migration strategy for schema changes

#### Performance Considerations

- Use Zustand's selector pattern to avoid unnecessary re-renders
- Keep state normalized (avoid deeply nested structures)
- Use immer middleware for easier immutable updates
