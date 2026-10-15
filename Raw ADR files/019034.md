# ADR-005: Update Operation Strategy

**Date**: 2025-12-29
**Feature**: 001-update-task
**Status**: Accepted

## Context

Need to implement task update functionality that modifies title and/or description while preserving other fields (id, status, created_at).

## Decision

Create new Task instance with updated values, replace in storage list.

## Details

### Options Considered

1. **In-place modification with new Task instance** (chosen)
   - Pros: Maintains immutability semantics (dataclass), clear what changed, consistent with existing patterns
   - Cons: Creates new object even for small changes (negligible for in-memory)

2. **Mutable Task with setters**
   - Pros: True in-place modification, no object creation
   - Cons: Violates immutability best practices, harder to track changes, inconsistent with existing Task dataclass design

3. **Task.copy_with() method**
   - Pros: Functional approach, explicit
   - Cons: Adds complexity to Task model, different pattern than existing code

### Implementation

```python
def update(self, task_id: int, title: str | None = None,
           description: str | None = None) -> Task | None:
    """Update task by ID, returning updated Task or None if not found."""
    for i, task in enumerate(self._tasks):
        if task.id == task_id:
            updated_task = Task(
                id=task.id,
                title=title.strip() if title is not None else task.title,
                description=description if description is not None else task.description,
                status=task.status,  # Preserved
                created_at=task.created_at  # Preserved
            )
            self._tasks[i] = updated_task
            return updated_task
    return None
```

### Rationale

- Consistent with existing `delete()` pattern (modifies storage, not task)
- Task dataclass remains simple (no copy methods or setters)
- Clear validation boundary (CLI validates, storage just stores)
- Easy to test (compare before/after Task instances)

## Consequences

- **Positive**: Maintains immutability of Task dataclass
- **Positive**: Consistent with existing architecture
- **Neutral**: Slight object creation overhead (negligible for in-memory use)

## Related

- ADR-006: Optional Parameter Handling (None vs Sentinel)
