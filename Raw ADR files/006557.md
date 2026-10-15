# ADR-001: Task Manager State Management with React Context + useReducer

## Context
Building a task management feature that requires:
- Priority-based task organization (High/Medium/Low)
- localStorage persistence across browser sessions
- Input validation and XSS protection
- Enterprise-grade scalability and maintainability

## Decision
**Use React Context API + useReducer pattern** for state management.

## Alternatives Considered

### 1. useState Only (Rejected)
- **Pros:** Simplest approach, minimal boilerplate
- **Cons:** Does not scale for enterprise; state logic scattered across components; difficult to test in isolation
- **Reason for Rejection:** Violates enterprise requirement for testable, maintainable architecture

### 2. Redux Toolkit (Rejected)
- **Pros:** Industry standard, excellent DevTools, middleware ecosystem
- **Cons:** Over-engineering for single-feature scope; adds ~150KB bundle size; requires additional learning curve
- **Reason for Rejection:** Violates "avoid over-engineering" principle; unnecessary complexity for this scope

### 3. Context + useReducer (Selected)
- **Pros:** Built-in React pattern; centralizes state logic; easily testable reducer functions; zero external dependencies; scales to moderate complexity
- **Cons:** Slightly more boilerplate than useState; requires understanding of reducer pattern
- **Reason for Selection:** Perfect balance of enterprise testability and simplicity; aligns with technical constraints

## Implementation Details

### State Structure
```typescript
interface Task {
  id: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  createdAt: number;
}

interface TaskState {
  tasks: Task[];
  error: string | null;
}
```

### Reducer Actions
- `ADD_TASK`: Validate and prepend task to list
- `DELETE_TASK`: Remove by ID
- `SET_ERROR`: Handle validation/storage errors
- `CLEAR_ERROR`: Reset error state

### Persistence Layer
- Synchronize state to localStorage on every reducer action
- Graceful fallback to memory-only mode if storage fails
- Initial hydration from localStorage on app mount

## Consequences

### Positive
- Reducer logic is pure and easily unit-testable (can mock localStorage)
- Clear separation: UI components consume context, business logic in reducer
- Type-safe with TypeScript discriminated unions
- No external dependencies or build-time complexity

### Negative
- Requires understanding of useReducer pattern (mitigated by clear documentation)
- Context re-renders all consumers on any state change (acceptable for single-feature scope)

### Trade-offs
- **Chosen:** Maintainability over minimal code (useReducer vs useState)
- **Chosen:** Zero dependencies over DevTools luxury (no Redux)
- **Chosen:** Explicit error handling over silent failures (localStorage errors surfaced to UI)

## Validation Criteria
- [ ] Reducer functions are pure (no side effects)
- [ ] Unit tests achieve >90% coverage on reducer logic
- [ ] localStorage failures do not crash the application
- [ ] XSS inputs are sanitized (React escapes by default; verified in tests)

## Date
2024-12-24

## Status
**Accepted**
