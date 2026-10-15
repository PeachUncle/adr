# ADR-002: CQRS (Command Query Responsibility Segregation) Pattern

## Status
✅ **ACCEPTED** - Implemented across all user stories

## Context
The application handles different types of operations with different concerns:
- **State-changing operations** (Create, Toggle, Delete) - Commands
- **Read-only operations** (Display todos) - Queries

We needed clear separation to enable testing, logging, and future optimization independently.

## Decision
Implement **CQRS Pattern** - separate command and query models through distinct handlers.

## Pattern Structure

### Commands (State-Changing)
```typescript
// src/application/commands/CreateTodoCommand.ts
export interface CreateTodoCommand {
  readonly title: string;
}

export interface ToggleTodoCompletionCommand {
  readonly todoId: string;
}

export interface DeleteTodoCommand {
  readonly todoId: string;
}
```

### Command Handlers
```typescript
// src/application/handlers/CreateTodoCommandHandler.ts
export class CreateTodoCommandHandler {
  constructor(private todoRepository: ITodoRepository) {}

  async handle(command: CreateTodoCommand): Promise<Todo> {
    const todo = Todo.create(command.title);
    await this.todoRepository.save(todo);
    logger.info('Todo created', { id: todo.id, title: command.title });
    return todo;
  }
}
```

### Queries (Read-Only)
```typescript
// src/application/queries/index.ts
export interface GetAllTodosQuery {}

export interface GetTodoByIdQuery {
  readonly todoId: string;
}
```

### Query Handlers
```typescript
// src/application/handlers/GetAllTodosQueryHandler.ts
export class GetAllTodosQueryHandler {
  constructor(private todoRepository: ITodoRepository) {}

  async handle(_query: GetAllTodosQuery): Promise<Todo[]> {
    logger.info('Fetching all todos');
    return await this.todoRepository.findAll();
  }
}
```

## Rationale

### Why Separate Commands and Queries?

#### 1. **Different Concerns**
```
Commands              Queries
─────────────        ────────
Create               Read list
Modify               Filter
Delete               Sort
Validate             Aggregate
Log events           Cache
```

#### 2. **Scalability Opportunities**
- **Commands**: Complex validation, audit logging, event publishing
- **Queries**: Can be optimized separately, cached independently, replicated to read database

#### 3. **Testability**
```typescript
// Easy to test command handling
it('should create todo with valid title', async () => {
  const handler = new CreateTodoCommandHandler(mockRepository);
  const result = await handler.handle({ title: 'Test' });
  expect(mockRepository.save).toHaveBeenCalled();
});

// Easy to test queries independently
it('should return all todos', async () => {
  const handler = new GetAllTodosQueryHandler(mockRepository);
  const result = await handler.handle({});
  expect(result).toEqual([todo1, todo2]);
});
```

#### 4. **Performance Optimization**
- Commands use write-optimized models
- Queries can use read-optimized views
- Future: Separate read and write databases

### Rejected Alternatives

#### ❌ Single Service for Everything
```typescript
// BAD: Mixed concerns
class TodoService {
  createTodo(title: string) { /* ... */ }
  updateTodo(id, title) { /* ... */ }
  getTodos() { /* ... */ }
  getTodoById(id) { /* ... */ }
}
```
**Problems**: Hard to optimize independently, mixed concerns, harder to test

#### ❌ Anemic Handlers
```typescript
// BAD: No real logic
class CreateTodoHandler {
  async handle(command) {
    return this.repository.save(command); // Just passes through
  }
}
```
**Problems**: Commands become just data transfer objects, no validation

## Implementation

### Application Service Orchestration
```typescript
// src/application/services/TodoApplicationService.ts
export class TodoApplicationService {
  constructor(
    private todoRepository: ITodoRepository,
    private eventPublisher: IEventPublisher
  ) {}

  // Command handlers
  async createTodo(command: CreateTodoCommand): Promise<Todo> {
    const handler = new CreateTodoCommandHandler(this.todoRepository);
    return handler.handle(command);
  }

  async toggleTodoCompletion(
    command: ToggleTodoCompletionCommand
  ): Promise<Todo> {
    const handler = new ToggleTodoCompletionCommandHandler(
      this.todoRepository
    );
    return handler.handle(command);
  }

  // Query handlers
  async getAllTodos(query: GetAllTodosQuery): Promise<Todo[]> {
    const handler = new GetAllTodosQueryHandler(this.todoRepository);
    return handler.handle(query);
  }
}
```

### In React Components
```typescript
// src/presentation/hooks/useTodoList.ts
export const useTodoList = () => {
  const [todos, setTodos] = useState<Todo[]>([]);
  const appService = useApplicationService();

  // Execute commands
  const createTodo = async (title: string) => {
    const newTodo = await appService.createTodo({ title });
    setTodos([...todos, newTodo]);
  };

  const toggleCompletion = async (todoId: TodoId) => {
    const updated = await appService.toggleTodoCompletion({ todoId });
    setTodos(todos.map(t => t.id === todoId ? updated : t));
  };

  // Execute queries
  useEffect(() => {
    appService.getAllTodos({}).then(setTodos);
  }, []);

  return { todos, createTodo, toggleCompletion };
};
```

## Consequences

### Advantages ✅
1. **Clear Intent**: Code clearly shows what's being modified vs read
2. **Independent Optimization**: Commands and queries can be optimized separately
3. **Easier Testing**: Each handler tested in isolation
4. **Better Logging/Auditing**: Can log commands differently than queries
5. **Scalability**: Foundation for future event sourcing, read replicas
6. **Composition**: Handlers can be composed, decorated, or modified

### Trade-offs ⚖️
1. **More Classes**: Command, CommandHandler, Query, QueryHandler per feature
2. **Indirection**: Extra layer between UI and domain
3. **Learning Curve**: Developers must understand CQRS concepts

### Validation

#### Test Coverage
```
Command Handlers: 15 tests
  ✓ Create with valid title
  ✓ Reject invalid title
  ✓ Persist to repository
  ✓ Log operations
  ✓ Handle errors

Query Handlers: 9 tests
  ✓ Return all todos
  ✓ Return empty list
  ✓ Handle repository errors
  ✓ Log queries

Integration: 40 tests
  ✓ Full CQRS flow
  ✓ State consistency
```

## Future Opportunities

### Event Sourcing
```typescript
// Commands publish events
const handler = new CreateTodoCommandHandler(repository);
const result = await handler.handle(command);
await eventPublisher.publish(result.getDomainEvents());
```

### Read Replicas
```typescript
// Queries eventually point to read-optimized database
class CachedGetAllTodosQueryHandler {
  async handle(query): Promise<Todo[]> {
    const cached = await cache.get('todos');
    if (cached) return cached;
    
    const fresh = await this.repository.findAll();
    await cache.set('todos', fresh, TTL);
    return fresh;
  }
}
```

### Command Logging/Audit
```typescript
// Commands automatically logged
class AuditingCreateTodoCommandHandler {
  async handle(command: CreateTodoCommand): Promise<Todo> {
    const result = await this.delegate.handle(command);
    await this.auditLog.record({
      type: 'CREATE_TODO',
      userId: getCurrentUser(),
      command,
      result,
      timestamp: new Date()
    });
    return result;
  }
}
```

## Related ADRs
- [ADR-001: DDD Architecture](./ADR-001-DDD-Architecture.md)
- [ADR-005: Command vs Query Boundaries](./ADR-005-Command-Query-Boundaries.md)

## References
- [CQRS Pattern - Microsoft Docs](https://docs.microsoft.com/en-us/azure/architecture/patterns/cqrs)
- [CQRS - Martin Fowler](https://martinfowler.com/bliki/CQRS.html)

## Version History
- **v1.0** (Nov 22, 2025) - CQRS implemented for US1-US3, fully tested
