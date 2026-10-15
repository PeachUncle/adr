# ADR-002: Adopt Layered Architecture Pattern

## Status

**Accepted** - December 2024

## Context

As the receiptscan-backend grows, we need a clear architectural pattern to organize code and maintain separation of concerns. Without a structured approach, the codebase could become difficult to test, maintain, and scale.

We need an architecture that:
- Separates business logic from infrastructure concerns
- Makes code testable by isolating dependencies
- Provides clear boundaries between different responsibilities
- Scales well as the application grows
- Is familiar to most developers

## Decision

We will adopt a **layered architecture pattern** with the following layers:

```
┌─────────────────┐
│   Controllers   │  ← HTTP request/response handling
├─────────────────┤
│    Services     │  ← Business logic
├─────────────────┤
│  Repositories   │  ← Data access
├─────────────────┤
│     Models      │  ← Data structures
└─────────────────┘
```

### Layer Responsibilities

1. **Controllers** (`src/controllers/`)
   - Handle HTTP requests and responses
   - Validate request data
   - Call appropriate services
   - Format responses

2. **Services** (`src/services/`)
   - Contain business logic
   - Orchestrate operations
   - Call repositories for data
   - Transform data between layers

3. **Repositories** (`src/repositories/`)
   - Handle data persistence
   - Interact with databases
   - Abstract database implementation details

4. **Models** (`src/models/`)
   - Define data structures
   - Provide type definitions
   - Include validation schemas

## Consequences

### Positive

- **Clear Separation of Concerns**: Each layer has a single, well-defined responsibility
- **Testability**: Layers can be tested independently with mocks
- **Maintainability**: Easy to locate and modify specific functionality
- **Flexibility**: Can swap implementations (e.g., different databases) without affecting other layers
- **Scalability**: Can scale specific layers independently
- **Team Productivity**: Multiple developers can work on different layers simultaneously

### Negative

- **Boilerplate Code**: May require more code than a simpler architecture
- **Initial Complexity**: Requires more upfront planning
- **Over-Engineering Risk**: May be too complex for very simple operations

### Neutral

- **Learning Curve**: Team needs to understand and follow the pattern
- **Discipline Required**: Developers must maintain layer boundaries

## Implementation Example

```typescript
// Controller (receipt.controller.ts)
export const getReceiptById = async (req: Request, res: Response) => {
  try {
    const receipt = await receiptService.getById(req.params.id, req.user.uid);
    res.json({ status: 'success', data: { receipt } });
  } catch (error) {
    res.status(404).json({ status: 'error', message: error.message });
  }
};

// Service (receipt.service.ts)
export const getById = async (id: string, userId: string): Promise<Receipt> => {
  const receipt = await receiptRepository.getReceiptById(id, userId);
  if (!receipt) {
    throw new Error('Receipt not found');
  }
  return receipt;
};

// Repository (receipt.repository.ts)
export const getReceiptById = async (id: string, userId: string): Promise<Receipt | null> => {
  const doc = await db.collection('receipts').doc(id).get();
  if (!doc.exists || doc.data()?.userId !== userId) {
    return null;
  }
  return doc.data() as Receipt;
};
```

## Alternatives Considered

1. **MVC (Model-View-Controller)**: Traditional web framework pattern, but we don't have views in an API
2. **Hexagonal Architecture**: More complex, might be overkill for our needs
3. **Feature-Based Structure**: Organize by features instead of layers; less clear separation of concerns
4. **Flat Structure**: All code in one place; doesn't scale well

## Guidelines

### Communication Rules

- Controllers can call Services
- Services can call Repositories
- Repositories can access Models
- **Never skip layers** (e.g., Controllers shouldn't call Repositories directly)

### Dependency Direction

```
Controllers → Services → Repositories → Database
                ↓
              Models (used by all layers)
```

## References

- [Layered Architecture Pattern](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
