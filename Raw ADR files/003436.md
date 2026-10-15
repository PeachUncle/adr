# ADR-0010: Dependency Injection Pattern

## Status
Accepted

## Context
We need to manage dependencies between layers (services, repositories) in a way that:
- Enables easy testing with mocks
- Reduces coupling between components
- Allows swapping implementations
- Maintains type safety

## Decision
We will use constructor-based dependency injection with interfaces:

### Dependency Injection Pattern

```typescript
// Service depends on repository interface
class HealthService {
  constructor(
    private chatRepository: IChatRepository,
    private ragClient: IRagClient
  ) {}
  
  async askQuestion(query: string, userId: string) {
    // Use injected dependencies
  }
}

// Create instances with dependencies
const chatRepository = new FirestoreChatRepository();
const ragClient = new VertexRagClient();
const healthService = new HealthService(chatRepository, ragClient);
```

### Dependency Container

We'll create a simple dependency container for managing instances:

```typescript
// lib/di/container.ts
class Container {
  private services = new Map();
  
  register<T>(key: string, factory: () => T): void {
    this.services.set(key, factory);
  }
  
  resolve<T>(key: string): T {
    const factory = this.services.get(key);
    if (!factory) throw new Error(`Service ${key} not found`);
    return factory();
  }
}
```

### Rationale

1. **Testability**: Easy to inject mock dependencies in tests
2. **Flexibility**: Can swap implementations without changing service code
3. **Decoupling**: Services don't know about concrete implementations
4. **Type Safety**: TypeScript ensures correct dependencies
5. **Single Responsibility**: Each class has clear dependencies

## Consequences

### Positive
- Easy to test with mock dependencies
- Reduced coupling between layers
- Can swap implementations easily
- Clear dependency relationships

### Negative
- More setup code
- Need to manage dependency container
- Slightly more complex initialization

## Alternatives Considered

1. **Direct instantiation**: Rejected - too tightly coupled
2. **Service locator pattern**: Rejected - hides dependencies
3. **Full DI framework (InversifyJS)**: Rejected - too complex for our needs

