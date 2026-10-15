# ADR-001: Use Hexagonal Architecture

## Status

**Accepted** - October 2025

## Context

We need to design a transaction reconciliation service that integrates with YNAB and various bank APIs. The system must be maintainable, testable, and adaptable to changing requirements.

## Decision

We will use Hexagonal Architecture (Ports and Adapters) as our primary architectural pattern.

## Rationale

### ✅ **Benefits**

- **Domain Purity**: Business logic remains framework-independent
- **Testability**: Easy to test business logic in isolation
- **Flexibility**: Can swap implementations without affecting business logic
- **Maintainability**: Clear separation of concerns
- **Evolution**: Easy to add new adapters (banks, APIs, storage)

### 🏗️ **Implementation Structure**

```
domain/          # Pure business logic
├── model/       # Entities and Value Objects
├── api/         # Inbound ports (use cases)
├── spi/         # Outbound ports (repositories, clients)
└── usecase/     # Business logic implementation

infrastructure/  # Framework adapters
├── web/         # REST API adapters
├── persistence/ # Database adapters
├── client/      # External API adapters
└── config/      # Spring configuration
```

### 🧪 **Testing Strategy**

- **Domain**: Pure unit tests with high mutation coverage
- **Infrastructure**: Integration tests with real adapters
- **Architecture**: ArchUnit validation of dependency rules

## Consequences

### ✅ **Positive**

- High testability (94% mutation coverage achieved)
- Clear boundaries and responsibilities
- Framework independence in domain
- Easy to reason about and maintain
- Supports Domain-Driven Design principles

### ⚠️ **Trade-offs**

- Initial complexity higher than layered architecture
- More interfaces and abstractions
- Learning curve for team members
- Additional ceremony for simple operations

## Alternatives Considered

### **Layered Architecture**

- **Pros**: Simple, well-understood
- **Cons**: Tight coupling, difficult to test, framework leakage

### **Microservices**

- **Pros**: Independent deployment, scaling
- **Cons**: Overkill for single domain, complexity overhead

### **Event-Driven Architecture**

- **Pros**: Loose coupling, scalability
- **Cons**: Eventual consistency complexity, debugging challenges

## Implementation Notes

### **Framework Independence**

- Domain module has zero framework dependencies
- Maven Enforcer Plugin prevents accidental framework imports
- ArchUnit tests validate architectural boundaries

### **Dependency Injection**

- Infrastructure layer wires dependencies
- Domain layer receives dependencies through constructor injection
- No framework annotations in domain layer

### **Error Handling**

- Domain defines business exceptions
- Infrastructure maps to appropriate HTTP status codes
- Clean error propagation through layers

## Validation

This decision will be validated through:

- ✅ ArchUnit tests ensuring no framework dependencies in domain
- ✅ High test coverage (>90% line, >70% mutation)
- ✅ Maven Enforcer Plugin preventing violations
- ✅ Code review process
- ✅ Architectural documentation

## References

- [Hexagonal Architecture by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Ports and Adapters Pattern](https://jmgarridopaz.github.io/content/hexagonalarchitecture.html)
