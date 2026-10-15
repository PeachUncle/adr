# ADR-004: State Management Approach

## Status
Accepted

## Context

ToDoApp needs a strategy for managing application state (task list, UI state, form state) that is simple, maintainable, and supports the layered architecture while avoiding unnecessary complexity.

### Key Considerations:
- MVP scope with limited features
- No framework (vanilla JavaScript)
- Layered architecture with clear separation
- Multiple UI components need access to task list
- UI must stay synchronized with data changes
- Must support undo/redo in future (post-MVP)
- Team familiar with event-driven patterns

### Requirements Driving This Decision:
- FR-001 to FR-005: All CRUD operations must update UI
- NFR-006: Clear visual feedback for all actions
- NFR-009: Operations complete within 100ms
- Architecture requires separation between layers

### State Types to Manage:
1. **Application State**: Task list, current filters (post-MVP)
2. **UI State**: Modal visibility, form state, loading indicators
3. **Temporary State**: Form inputs, validation errors

## Decision

We will use a **centralized state management pattern** implemented through:

1. **Single Source of Truth**
   - TaskManager class owns the task list state
   - All components read from TaskManager
   - No duplicate state across components

2. **Observer Pattern for Reactivity**
   - Components subscribe to state changes
   - TaskManager notifies subscribers on updates
   - Simple pub/sub for UI synchronization

3. **Unidirectional Data Flow**
   - User actions → TaskManager → Storage → State Update → UI Update
   - No direct component-to-component communication
   - All state changes flow through TaskManager

4. **Component-Local State**
   - UI-specific state (hover, focus) stays in components
   - Form state managed locally until submit
   - No global state for temporary UI concerns

### Implementation Pattern:

```javascript
// TaskManager acts as state manager
class TaskManager {
    constructor(storageService) {
        this.storageService = storageService;
        this.tasks = [];
        this.subscribers = [];
    }
    
    // Subscribe to state changes
    subscribe(callback) {
        this.subscribers.push(callback);
        return () => {
            this.subscribers = this.subscribers.filter(cb => cb !== callback);
        };
    }
    
    // Notify all subscribers
    notifySubscribers() {
        this.subscribers.forEach(callback => callback(this.tasks));
    }
    
    // State mutation methods
    async addTask(taskData) {
        const task = this.createTask(taskData);
        this.tasks.push(task);
        await this.storageService.saveTasks(this.tasks);
        this.notifySubscribers();
        return task;
    }
    
    async updateTask(id, updates) {
        const index = this.tasks.findIndex(t => t.id === id);
        if (index !== -1) {
            this.tasks[index] = { ...this.tasks[index], ...updates };
            await this.storageService.saveTasks(this.tasks);
            this.notifySubscribers();
        }
    }
    
    // Getters for state access
    getTasks() {
        return [...this.tasks]; // Return copy to prevent mutation
    }
    
    getTask(id) {
        return this.tasks.find(t => t.id === id);
    }
}
```

## Consequences

### Positive

1. **Simplicity**
   - No external state management library
   - Easy to understand for small team
   - Minimal boilerplate
   - No learning curve

2. **Centralized State**
   - Single source of truth
   - Easy to debug (one place to look)
   - Consistent state across components
   - No state synchronization issues

3. **Reactive Updates**
   - UI automatically updates on state changes
   - Components don't need to poll for changes
   - Efficient (only notify when needed)

4. **Testability**
   - Easy to test TaskManager in isolation
   - Mock subscribers for testing
   - Predictable state mutations
   - No framework-specific testing needed

5. **Performance**
   - Minimal overhead
   - No virtual DOM diffing
   - Direct DOM updates when needed
   - Subscribers only called on actual changes

6. **Future-Proof**
   - Pattern compatible with Redux/MobX if needed later
   - Easy to add middleware (logging, undo/redo)
   - Supports time-travel debugging

### Negative

1. **Manual Implementation**
   - Need to implement observer pattern manually
   - No built-in dev tools
   - More code than using a library

2. **Limited Features**
   - No built-in middleware
   - No time-travel debugging (initially)
   - No immutability enforcement
   - Must implement undo/redo manually

3. **Potential for Mistakes**
   - Developers must remember to notify subscribers
   - Risk of forgetting to update state properly
   - No compile-time checks

4. **Scalability Concerns**
   - Pattern may become complex with many state types
   - No built-in state normalization
   - Manual optimization needed

## Alternatives Considered

### Alternative 1: Redux
Popular state management library with predictable state updates.

**Pros:**
- Battle-tested pattern
- Excellent dev tools
- Time-travel debugging
- Large community

**Rejected because:**
- Overkill for MVP scope
- Adds ~6KB to bundle
- Significant boilerplate
- Learning curve for team
- Not needed for current complexity

**Reconsider when:**
- App has >20 components
- Complex state interactions
- Need advanced debugging

### Alternative 2: MobX
Reactive state management with less boilerplate.

**Pros:**
- Less boilerplate than Redux
- Automatic reactivity
- Good developer experience

**Rejected because:**
- Still adds dependency
- Magic reactivity can be confusing
- Not needed for MVP
- Team prefers explicit patterns

### Alternative 3: Event Bus Pattern
Global event emitter for all state changes.

**Pros:**
- Very simple to implement
- Loose coupling
- Familiar to most developers

**Rejected because:**
- Less structured than observer pattern
- Harder to track state changes
- No central state owner
- Can lead to event spaghetti

**Partial acceptance:** Used for some UI events (notifications)

### Alternative 4: Component State Only
Each component manages its own state.

**Pros:**
- Simple per-component
- No global state management
- No dependencies

**Rejected because:**
- State duplication
- Synchronization issues
- Hard to maintain consistency
- Doesn't fit layered architecture

### Alternative 5: URL-based State
Store state in URL query parameters.

**Pros:**
- Shareable state
- Browser back/forward support
- Bookmarkable

**Rejected because:**
- Not applicable to task list data
- localStorage is the source of truth
- Adds unnecessary complexity

**Partial acceptance:** May use for filters/sorting (post-MVP)

## Implementation Notes

### TaskManager with Observer Pattern:
```javascript
class TaskManager {
    constructor(storageService) {
        this.storageService = storageService;
        this.tasks = [];
        this.subscribers = new Map();
        this.nextSubscriberId = 0;
    }
    
    // Subscribe to all state changes
    subscribe(callback) {
        const id = this.nextSubscriberId++;
        this.subscribers.set(id, callback);
        
        // Return unsubscribe function
        return () => this.subscribers.delete(id);
    }
    
    // Subscribe to specific events
    on(event, callback) {
        if (!this.eventListeners) {
            this.eventListeners = new Map();
        }
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }
    
    emit(event, data) {
        if (this.eventListeners && this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(cb => cb(data));
        }
    }
    
    // Notify all subscribers
    notifySubscribers() {
        const tasksCopy = [...this.tasks];
        this.subscribers.forEach(callback => {
            callback(tasksCopy);
        });
    }
    
    // State mutations
    async addTask(taskData) {
        const task = this.createTask(taskData);
        this.tasks.push(task);
        await this.persist();
        this.emit('taskAdded', task);
        this.notifySubscribers();
        return task;
    }
    
    async persist() {
        await this.storageService.saveTasks(this.tasks);
    }
}
```

### Component Subscription:
```javascript
class TaskListView {
    constructor(taskManager) {
        this.taskManager = taskManager;
        this.element = document.getElementById('task-list');
        
        // Subscribe to state changes
        this.unsubscribe = taskManager.subscribe((tasks) => {
            this.render(tasks);
        });
    }
    
    render(tasks) {
        // Update DOM with new task list
        this.element.innerHTML = tasks.map(task => 
            this.renderTask(task)
        ).join('');
    }
    
    destroy() {
        // Cleanup subscription
        this.unsubscribe();
    }
}
```

### Handling Async State Updates:
```javascript
class TaskManager {
    async updateTask(id, updates) {
        // Optimistic update
        const index = this.tasks.findIndex(t => t.id === id);
        if (index === -1) return;
        
        const oldTask = { ...this.tasks[index] };
        this.tasks[index] = { ...oldTask, ...updates };
        
        // Update UI immediately
        this.notifySubscribers();
        
        try {
            // Persist to storage
            await this.storageService.saveTasks(this.tasks);
        } catch (error) {
            // Rollback on error
            this.tasks[index] = oldTask;
            this.notifySubscribers();
            throw error;
        }
    }
}
```

### Future: Adding Middleware
```javascript
class TaskManager {
    constructor(storageService, middlewares = []) {
        this.middlewares = middlewares;
        // ... rest of constructor
    }
    
    applyMiddlewares(action, payload) {
        let result = payload;
        for (const middleware of this.middlewares) {
            result = middleware(action, result);
        }
        return result;
    }
    
    async addTask(taskData) {
        // Apply middlewares (logging, validation, etc.)
        const processedData = this.applyMiddlewares('ADD_TASK', taskData);
        // ... rest of method
    }
}

// Example middleware: Logging
const loggingMiddleware = (action, payload) => {
    console.log(`[${action}]`, payload);
    return payload;
};

// Example middleware: Validation
const validationMiddleware = (action, payload) => {
    if (action === 'ADD_TASK') {
        validateTask(payload);
    }
    return payload;
};
```

## State Structure

### Application State:
```javascript
{
    tasks: [
        { id, title, description, completed, createdAt, updatedAt }
    ],
    // Future: filters, sorting, view preferences
}
```

### UI State (component-local):
```javascript
{
    isModalOpen: boolean,
    editingTaskId: string | null,
    formData: { title: string, description: string },
    validationErrors: { title?: string, description?: string }
}
```

## Validation Against Tech Architect Principles

✅ **Simplicity**: No external dependencies, easy to understand  
✅ **Separation of Concerns**: State logic separate from UI  
✅ **Testability**: Easy to test state mutations  
✅ **Performance**: Minimal overhead, efficient updates  
✅ **Maintainability**: Clear patterns, single source of truth  
✅ **Extensibility**: Easy to add features (middleware, undo/redo)  
✅ **Team-Friendly**: Familiar patterns, no steep learning curve  

## Success Metrics

### Functional Metrics:
- All UI components stay synchronized with state
- No duplicate state across components
- All state changes properly persisted

### Performance Metrics:
- State updates: <10ms
- UI updates after state change: <50ms
- No unnecessary re-renders

### Code Quality Metrics:
- Single source of truth maintained
- All state mutations go through TaskManager
- No direct state manipulation in components

## References

- [ADR-001: Architectural Style](./ADR-001-architectural-style.md)
- [ADR-002: Frontend Technology](./ADR-002-frontend-technology.md)
- [NFR-006: Visual Feedback](../../requirements/business-requirements-document.md#52-usability)
- [EPIC-001: Task CRUD Operations](../../tasks/epics/EPIC-001-task-crud-operations.md)

## Related ADRs

- [ADR-001: Architectural Style](./ADR-001-architectural-style.md)
- [ADR-003: Data Persistence](./ADR-003-data-persistence.md)
- [ADR-005: Testing Strategy](./ADR-005-testing-strategy.md)

---

**Date:** 2025-11-19  
**Author:** Tech Architect Team  
**Reviewers:** Development Team Lead, Product Owner
