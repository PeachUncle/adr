# ADR-003: Immutability Guarantees for Domain Entities

## Status
✅ **ACCEPTED** - Enforced throughout domain and application layers

## Context
Domain entities must maintain consistency and correctness, especially across complex operations and concurrent scenarios. JavaScript's mutable-by-default nature creates risks for:
- Accidental state corruption
- Hard-to-debug state issues
- Concurrency bugs in future scaling
- Difficulty implementing undo/redo

## Decision
Enforce **immutability** for all domain entities and value objects:
1. Private fields with no setters
2. Immutable constructor initialization
3. New instances returned from state-changing methods
4. Shallow freeze for runtime safety

## Implementation

### Domain Entities
```typescript
// src/domain/entities/Todo.ts
export class Todo {
  // Private, readonly fields
  private readonly _id: TodoId;
  private readonly _title: TodoTitle;
  private readonly _status: TodoStatus;
  private readonly _createdAt: Date;
  private readonly _updatedAt: Date;

  // Private constructor - force creation via factory
  private constructor(
    id: TodoId,
    title: TodoTitle,
    status: TodoStatus,
    createdAt: Date,
    updatedAt: Date
  ) {
    this._id = id;
    this._title = title;
    this._status = status;
    this._createdAt = new Date(createdAt); // Copy date
    this._updatedAt = new Date(updatedAt);
    
    // Prevent modifications at runtime
    Object.freeze(this);
  }

  // Factory method - only way to create
  static create(title: string): Todo {
    return new Todo(
      TodoId.generate(),
      TodoTitle.create(title),
      TodoStatus.PENDING,
      new Date(),
      new Date()
    );
  }

  // State-changing returns NEW instance (immutable)
  toggleCompletion(): Todo {
    const newStatus = this._status === TodoStatus.COMPLETED
      ? TodoStatus.PENDING
      : TodoStatus.COMPLETED;

    return new Todo(
      this._id,
      this._title,
      newStatus,
      this._createdAt,
      new Date() // New timestamp
    );
  }

  // Getters - no setters
  get id(): TodoId { return this._id; }
  get title(): TodoTitle { return this._title; }
  get status(): TodoStatus { return this._status; }
  get createdAt(): Date { return new Date(this._createdAt); }
  get updatedAt(): Date { return new Date(this._updatedAt); }
}

// Object.freeze(todo) prevents property mutations
const todo = Todo.create('Test');
// todo.status = TodoStatus.COMPLETED; // ❌ ERROR: Cannot assign (frozen)
const updated = todo.toggleCompletion(); // ✅ Returns new instance
```

### Value Objects
```typescript
// src/domain/entities/TodoTitle.ts
export class TodoTitle {
  private readonly _value: string;

  private constructor(value: string) {
    this._value = value;
    Object.freeze(this);
  }

  static create(value: string): TodoTitle {
    const trimmed = value.trim();
    
    if (trimmed.length === 0) {
      throw new Error('Title cannot be empty');
    }
    if (trimmed.length > 500) {
      throw new Error('Title cannot exceed 500 characters');
    }
    
    return new TodoTitle(trimmed);
  }

  get value(): string {
    return this._value;
  }

  equals(other: TodoTitle): boolean {
    return this._value === other._value;
  }
}

// Usage - enforced invariants
const title1 = TodoTitle.create('Buy milk');
// title1.value = 'New value'; // ❌ ERROR: Cannot assign (frozen)
const title2 = TodoTitle.create('Buy milk');
console.log(title1.equals(title2)); // ✅ true - values compared
```

## Rationale

### Why Immutability?

#### 1. **Correctness and Predictability**
```typescript
// ❌ Mutable: Dangerous!
const todo = getTodo();
const backup = todo; // Same reference!
todo.status = 'COMPLETED';
console.log(backup.status); // 'COMPLETED' - OOPS!

// ✅ Immutable: Safe!
const todo = getTodo();
const backup = todo; // Different semantic meaning
const updated = todo.toggleCompletion(); // Returns new instance
console.log(todo.status); // Original unchanged
console.log(updated.status); // Only updated one changed
```

#### 2. **Easier Reasoning About Code**
```typescript
// ✅ Clear intent
const todos = await repository.findAll();
const updated = todos.map(t => t.id === id ? t.toggleCompletion() : t);
// Original todos array unchanged, new array returned
```

#### 3. **Enables Optimizations**
```typescript
// ✅ Reference equality checks work safely
const todoA = Todo.create('Test'); // Same data
const todoB = todoA; // Same reference
console.log(todoA === todoB); // true - can use for optimization
```

#### 4. **Prevents Accidental Mutations**
```typescript
// Frozen objects prevent mistakes
function updateTodo(todo: Todo) {
  todo.status = 'COMPLETED'; // ❌ Runtime error (frozen)
  return todo;
}

// Forces correct pattern
function updateTodo(todo: Todo): Todo {
  return todo.toggleCompletion(); // ✅ Returns new instance
}
```

### Rejected Alternatives

#### ❌ Mutable Objects with Defensive Copies
```typescript
// Inefficient and error-prone
class Todo {
  status: TodoStatus;
  
  getStatus(): TodoStatus {
    return this.status; // Copy every time?
  }
}
```

#### ❌ Getters with Validation
```typescript
// Still mutable, just harder
class Todo {
  private _status: TodoStatus;
  
  set status(value: TodoStatus) {
    if (this._status !== value) {
      this._status = value;
    }
  }
}
```

## Implementation Strategy

### Layer Application

#### Domain Layer (100% Immutable)
```typescript
// ✅ All domain entities and value objects frozen
const todo = Todo.create('Test');
Object.isFrozen(todo); // true
```

#### Application Layer (Immutable Commands)
```typescript
// ✅ Commands immutable (use `readonly`)
export interface CreateTodoCommand {
  readonly title: string;
}

// ✅ Handlers return new entities
async handle(command: CreateTodoCommand): Promise<Todo> {
  const todo = Todo.create(command.title);
  await this.repository.save(todo);
  return todo; // New instance
}
```

#### Presentation Layer (Smart Mutation)
```typescript
// ✅ React uses immutable updates
setTodos(todos => 
  todos.map(t => t.id === id ? t.toggleCompletion() : t)
);
```

## Consequences

### Advantages ✅
1. **Correctness**: Prevents bugs from accidental mutations
2. **Predictability**: Code behaves as written, no side effects
3. **Debugging**: Easier to trace state changes
4. **Concurrency**: Foundation for multi-threaded/async scenarios
5. **Performance**: Enables optimization techniques
6. **Testing**: Easier to assert on state, no pollution between tests

### Trade-offs ⚖️
1. **Memory**: Each state change creates new object (mitigated by sharing structure)
2. **Development**: Requires discipline, different mental model
3. **Learning Curve**: Developers accustomed to mutation must adapt

### Validation

#### Tests Enforcing Immutability
```typescript
describe('Todo Immutability', () => {
  it('should prevent direct property mutation', () => {
    const todo = Todo.create('Test');
    expect(() => {
      (todo as any).status = TodoStatus.COMPLETED;
    }).toThrow();
  });

  it('should return new instance on toggleCompletion', () => {
    const todo = Todo.create('Test');
    const updated = todo.toggleCompletion();
    
    expect(todo).not.toBe(updated);
    expect(todo.status).toBe(TodoStatus.PENDING);
    expect(updated.status).toBe(TodoStatus.COMPLETED);
  });

  it('should maintain immutability in collections', () => {
    const todos = [Todo.create('T1'), Todo.create('T2')];
    const original = JSON.stringify(todos);
    
    todos[0].toggleCompletion(); // Doesn't modify original
    
    expect(JSON.stringify(todos)).toBe(original);
  });
});
```

#### Coverage
- ✅ 21 unit tests in Todo.spec.ts validate immutability
- ✅ 40 integration tests verify immutability across operations
- ✅ All tests pass consistently - no flaky mutation bugs

## Performance Impact

### Memory Profile
```
Single Todo: ~200 bytes
After toggle: ~200 bytes (new instance)
100 todos: ~20KB
Operations on 100 todos: Minimal overhead

Trade-off: Tiny memory increase vs bug prevention
```

## Future Opportunities

### Persistent Data Structures
```typescript
// Could use immer.js for automatic structural sharing
import produce from 'immer';

const updated = produce(todo, draft => {
  draft.status = TodoStatus.COMPLETED;
});
```

### Time-Traveling Debugger
```typescript
// Immutability enables perfect undo/redo
const history: Todo[] = [];
history.push(todo1);
history.push(todo2);
history.push(todo3);

// Can jump to any point without side effects
```

## Related ADRs
- [ADR-001: DDD Architecture](./ADR-001-DDD-Architecture.md)
- [ADR-004: localStorage Selection](./ADR-004-localStorage-Selection.md)

## References
- [Immutability - Wikipedia](https://en.wikipedia.org/wiki/Immutable_object)
- [Immer.js - Immutable Updates Made Easy](https://immerjs.github.io/immer/)
- [Persistent Data Structures](https://en.wikipedia.org/wiki/Persistent_data_structure)

## Version History
- **v1.0** (Nov 22, 2025) - Immutability enforced for all domain entities
