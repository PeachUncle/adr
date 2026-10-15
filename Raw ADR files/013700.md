# 📁 ADR-009: Introduce `BaseId`, `BaseEntity`, and `BaseAggregateRoot` for Enterprise-Grade Identity Modeling in the Domain

**Status:** Accepted  
**Date:** 2025-04-06  
**Author:** Sardul3  
**Decision Scope:** Applies to all domain entities and aggregates across bounded contexts  
**Target Audience:** Domain architects, backend engineers, DDD practitioners

---

### Context

As our domain model evolves, entity identity has increasingly become a core architectural concern. Initially, domain entities such as `Participant` used raw `UUID` fields for identity. While this worked for simple use cases, the following issues were identified:

- Primitive Obsession: Raw `UUID` or `Long` values leaked into multiple layers (DTOs, services, APIs), leading to type confusion and weak domain boundaries.
- Redundant Identity Logic: Every entity had to reimplement `equals()`, `hashCode()`, and `toString()`.
- Lack of Semantic Identity: The use of `UUID` as a type lacks clarity—`UUID` could represent `UserId`, `InvoiceId`, `ParticipantId`, etc.
- No Extensibility: No way to introduce lifecycle metadata (e.g., `createdAt`, domain events, audit info) at the entity or aggregate root level.

To resolve these concerns and support enterprise-scale modeling, we are introducing a standardized identity abstraction using `BaseId<T>`, `BaseEntity<ID>`, and `BaseAggregateRoot<ID>`. These abstractions align with Domain-Driven Design principles and Hexagonal Architecture.

---

### Decision

We are introducing the following abstractions:

#### 1. `BaseId<T>`

A generic, type-safe identity wrapper class to represent IDs of all domain objects.

**Properties:**
- Strong typing via generics (`BaseId<UUID>`)
- Implements `equals`, `hashCode`, `toString` on the underlying value
- Enforces non-null identity values and immutability
- Prepared for Jackson and JPA serialization (via custom serializers or converters in the adapter layer)

**Example:**
```java
public class ParticipantId extends BaseId<UUID> {
    private ParticipantId(UUID value) { super(value); }

    public static ParticipantId generate() {
        return new ParticipantId(UUID.randomUUID());
    }

    public static ParticipantId of(UUID id) {
        return new ParticipantId(id);
    }
}
```

---

#### 2. `BaseEntity<ID extends BaseId<?>>`

An abstract base class for all domain entities with identity-based equality and shared infrastructure.

**Responsibilities:**
- Stores the identity field of type `BaseId<?>`
- Implements identity-based `equals()` and `hashCode()`
- Exposes a standard `getId()` method
- Serves as the parent type for all non-root entities

---

#### 3. `BaseAggregateRoot<ID extends BaseId<?>>`

A specialization of `BaseEntity` for aggregate roots, prepared to support advanced behavior.

**Responsibilities:**
- Inherits all identity handling from `BaseEntity`
- Ready for future enhancements such as:
    - Domain event collection
    - Audit metadata
    - Versioning
    - Lifecycle transitions

---

### Updated Modeling Standards

- All new or existing domain entities (e.g., `Participant`, `ExpenseGroup`) must extend either `BaseEntity<ID>` or `BaseAggregateRoot<ID>`.
- Each entity must define a specific ID class that extends `BaseId<T>` (e.g., `ParticipantId extends BaseId<UUID>`).
- Factory methods should be used for creation (`Participant.withEmail(...)`) instead of public constructors.
- Raw usage of `UUID` or `Long` for identity is discouraged across domain layers.

---

### Benefits

| Category       | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| Type Safety     | Prevents misuse of generic `UUID` or `Long` across bounded contexts        |
| DRY Principle   | Removes redundant `equals`, `hashCode`, and `toString` logic from entities |
| Domain Clarity  | Makes code more expressive (`ParticipantId` instead of `UUID`)             |
| Testability     | Improves assertion clarity and object creation in unit tests               |
| Event-Sourcing  | Provides a base for domain event recording and lifecycle hooks             |
| Adapter Control | Enables clean JSON serialization and JPA conversion via custom strategies |

---

### Trade-offs and Considerations

| Concern                         | Mitigation Strategy                                           |
|----------------------------------|---------------------------------------------------------------|
| Adds abstraction complexity      | Acceptable tradeoff for scalability and correctness           |
| Jackson serialization overhead   | Handled via `@JsonCreator` and `@JsonValue` on ID classes     |
| JPA persistence complexity       | Can be managed via `@Converter` or `@Embeddable` in adapters  |
| Slight increase in boilerplate  | Tooling or code generation can be used where applicable       |

---

### Migration Plan

- Implement `BaseId`, `BaseEntity`, and `BaseAggregateRoot` in `io.github.sardul3.shared.domain`
- Refactor `Participant` to extend `BaseEntity<ParticipantId>` and replace `UUID` with `ParticipantId`
- Create corresponding ID classes for all entities (`ExpenseGroupId`, `TransactionId`, etc.)
- Update test utilities to support ID creation and entity comparison
- Integrate Jackson and JPA serialization logic in the infrastructure layer

---

### References

- Eric Evans, *Domain-Driven Design*
- Vaughn Vernon, *Implementing Domain-Driven Design*
- https://dddcommunity.org/
- Current domain model: `Participant`, `ParticipantId`, `Money`, `BaseEntity`