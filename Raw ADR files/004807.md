# ADR 001: Clean Architecture for Acode

**Date**: 2025-01-03
**Status**: Accepted
**Deciders**: Project Team

## Context

Acode is a complex system that will evolve significantly over multiple epics. The codebase needs an architecture that:

- Supports long-term maintainability
- Enables independent testing of business logic
- Allows infrastructure to be swapped without affecting core logic
- Facilitates parallel development across teams
- Maintains clear boundaries between concerns

## Decision

We will use **Clean Architecture** (also known as Onion Architecture or Ports and Adapters) with the following layers:

### Layer Structure

```
CLI → Infrastructure → Application → Domain
```

**Dependencies flow inward** (toward Domain). Outer layers depend on inner layers, never the reverse.

### Domain Layer (Core)

- **Location**: `src/Acode.Domain/`
- **Purpose**: Business entities, value objects, domain services
- **Dependencies**: None (except pure abstractions)
- **Rules**:
  - No external dependencies
  - No references to other Acode projects
  - Defines interfaces that outer layers implement

### Application Layer

- **Location**: `src/Acode.Application/`
- **Purpose**: Use cases, orchestration, application-specific business rules
- **Dependencies**: Domain only
- **Rules**:
  - References only `Acode.Domain`
  - Defines application service interfaces
  - Implements use cases using domain objects

### Infrastructure Layer

- **Location**: `src/Acode.Infrastructure/`
- **Purpose**: External integrations, technical implementations
- **Dependencies**: Domain and Application
- **Rules**:
  - Implements interfaces defined in Domain/Application
  - All I/O happens here (file system, network, process execution)
  - Model provider adapters live here

### CLI Layer (Presentation)

- **Location**: `src/Acode.Cli/`
- **Purpose**: User interface, command parsing, output formatting
- **Dependencies**: All other layers
- **Rules**:
  - Thin layer that delegates to Application
  - Wires up dependency injection
  - Handles user input/output

## Consequences

### Positive

- **Testability**: Domain and Application can be tested without any infrastructure (file system, network, etc.)
- **Flexibility**: Infrastructure can be swapped (e.g., change model providers) without touching business logic
- **Maintainability**: Clear boundaries make it obvious where code belongs
- **Parallel Development**: Teams can work on different layers independently
- **Dependency Direction**: All dependencies point inward, preventing coupling to volatile infrastructure

### Negative

- **Initial Overhead**: More boilerplate and indirection than a flat structure
- **Learning Curve**: Team must understand Clean Architecture principles
- **More Files**: Interfaces in Domain/Application, implementations in Infrastructure
- **Discipline Required**: Easy to violate boundaries if not enforced

### Mitigations for Negatives

- **Tooling**: Project references enforce layer boundaries at compile time
- **Documentation**: REPO_STRUCTURE.md clearly explains where code belongs
- **Code Review**: PR template includes architecture checklist
- **Tests**: Architecture tests will verify layer boundaries (Epic 11)

## Alternatives Considered

### Alternative 1: MVC Pattern

**Pros**: Familiar, less overhead
**Cons**: Doesn't scale well for complex business logic, hard to test controllers

**Rejected**: Acode's business logic (agent orchestration, safety checks, mode enforcement) is too complex for MVC.

### Alternative 2: Layered Architecture (3-tier)

**Pros**: Simpler than Clean Architecture
**Cons**: Allows business logic to leak into presentation and data layers

**Rejected**: We need strict boundaries to ensure safety logic cannot be bypassed.

### Alternative 3: Microservices

**Pros**: Maximum decoupling
**Cons**: Overkill for a monolithic CLI tool, adds deployment complexity

**Rejected**: Acode is a single binary, not a distributed system.

## Validation

We will validate this decision by:

1. **Compile-time enforcement**: Project references prevent illegal dependencies
2. **Test coverage**: Domain and Application layers have >80% test coverage without touching infrastructure
3. **Developer feedback**: Monitor ease of development and adjust guidelines as needed
4. **Architecture tests**: Add NDepend or ArchUnit tests to enforce boundaries (Epic 11)

## References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [docs/REPO_STRUCTURE.md](../REPO_STRUCTURE.md) - Layer descriptions
- Task 000 - Project bootstrap implementing this architecture

## Notes

- This ADR establishes the foundation. Future ADRs will detail specific patterns within each layer.
- As Acode grows, we may introduce sublayers (e.g., Application.Contracts) but must maintain inward dependency flow.
