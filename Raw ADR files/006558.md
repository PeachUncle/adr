# ADR-003: Toast Notification System

## Context
Following FE-104, users need immediate visual confirmation when they perform actions (add/delete tasks, create/delete lists). Silent actions create uncertainty about whether the system registered the command. Additionally, users should be able to delete all lists to achieve an empty workspace state.

## Decision
**Implement a global Toast Notification system using Context API pattern**, consistent with the existing TaskContext architecture (ADR-001).

## Alternatives Considered

### 1. Third-party Toast Library (e.g., react-toastify) (Rejected)
- **Pros:** Battle-tested; feature-rich (stacking, positioning, types); well-documented
- **Cons:** Adds external dependency; increases bundle size (~15KB); violates "keep it lightweight" principle; potential security vulnerabilities from third-party code
- **Reason for Rejection:** Technical constraint emphasizes minimal dependencies; custom solution is ~2KB and meets all MVP requirements

### 2. Component-level State for Toasts (Rejected)
- **Pros:** Simple; no context needed; contained within component
- **Cons:** Violates "no prop-drilling" constraint; toasts would be scoped to specific components, not global; can't show toasts from reducer actions; poor UX (toasts might appear in wrong location)
- **Reason for Rejection:** Doesn't meet requirement for "global action feedback"; would require passing toast trigger through 4+ component levels

### 3. ToastContext with Context API (Selected)
- **Pros:** Consistent with existing architecture (ADR-001); zero dependencies; predictable behavior; full control over UX; lightweight (~2KB); accessible from anywhere in component tree
- **Cons:** Requires boilerplate code; manual implementation of auto-dismiss and animations
- **Reason for Selection:** Best alignment with technical constraints and existing patterns; maintainable; extensible for future needs

## Implementation Details

### Architecture
```typescript
// Toast context structure
interface ToastContextValue {
  showToast: (message: string) => void;
}

// Toast state (internal to provider)
interface Toast {
  id: string;
  message: string;
}
```

### Component Structure
- **ToastContext.tsx**: Context provider with toast state management
- **Toast.tsx**: Presentational component with auto-dismiss and animations
- **Toast.module.css**: Styling with CSS keyframe animations

### Integration Pattern
```typescript
// In components/reducers
const { showToast } = useToast();
dispatch({ type: 'DELETE_LIST', payload: listId });
showToast(`List '${listName}' deleted`);
```

### Toast Behavior
- **Positioning**: Fixed at bottom-right (20px from edges)
- **Auto-dismiss**: 3-second timer with cleanup on unmount
- **Animation**: 0.3s fade-in, 0.3s fade-out
- **Spam Prevention**: Single toast at a time; newest replaces current
- **Text Handling**: CSS text-overflow ellipsis for messages > 100 characters
- **Accessibility**: role="status" and aria-live="polite" for screen readers

### Zero-List State Changes
- **Guardrail Removal**: Delete the check in `DELETE_LIST` reducer that prevents deleting the last list
- **State Handling**: Set `activeListId` to `null` when `lists.length === 0`
- **UI Adaptation**: TaskList component already handles `null` activeListId; message updated to prompt list creation
- **Persistence**: localStorage correctly saves and loads empty `lists: []` array

### Toast Triggers
1. **ADD_TASK**: "Task '[description]' added" (truncated if > 50 chars)
2. **DELETE_TASK**: "Task deleted"
3. **CREATE_LIST**: "List '[name]' created"
4. **DELETE_LIST**: "List '[name]' deleted"

## Consequences

### Positive
- Users receive immediate confirmation for all CRUD actions
- Consistent UX pattern across all operations
- No external dependencies added
- Follows established Context pattern (ADR-001)
- Zero-list state enables true workspace reset
- Accessible to screen reader users
- Lightweight implementation (~2KB total)

### Negative
- Additional state management layer (mitigated by simplicity of implementation)
- Manual animation implementation required (mitigated by using CSS keyframes)
- Single toast at a time may hide rapid actions (acceptable for MVP per requirements)

### Trade-offs
- **Chosen:** Single toast replacement over toast queue (simpler MVP, prevents screen clutter)
- **Chosen:** Context API over third-party library (zero dependencies, smaller bundle)
- **Chosen:** CSS animations over JS animations (better performance, declarative)
- **Chosen:** Fixed position over portal (simpler DOM structure, meets requirements)

## Validation Criteria
- [ ] Toast appears on ADD_TASK with correct message
- [ ] Toast appears on DELETE_TASK with correct message
- [ ] Toast appears on CREATE_LIST with correct message
- [ ] Toast appears on DELETE_LIST with correct message
- [ ] Toast auto-dismisses after 3 seconds
- [ ] Toast has fade-in and fade-out animations
- [ ] Toast positioned at bottom-right
- [ ] Long task names truncate with ellipsis in toast
- [ ] User can delete last list without error
- [ ] Empty workspace shows appropriate message
- [ ] "New List" button remains functional with zero lists
- [ ] Empty state persists across page reloads
- [ ] All existing tests pass
- [ ] No security vulnerabilities introduced

## Date
2024-12-26

## Status
**Accepted**

## Related
- Extends ADR-001 (Context + useReducer pattern)
- Extends ADR-002 (Multi-list architecture)
- Implements FE-104 requirements
