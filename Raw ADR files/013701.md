
# 📁ADR-011: Introduce `@AggregateRoot` Annotation to Define and Enforce Aggregate Root Semantics

**Status:** Accepted  
**Date:** 2025-04-06  
**Author:** Sardul3  
**Scope:** Domain Model — Aggregate Design, Modeling Practices, and Annotation Semantics  
**Applies to:** All domain aggregates across bounded contexts

---

### Context

In Domain-Driven Design (DDD), **Aggregates** are foundational modeling concepts. They represent clusters of domain objects (entities and value objects) that must be treated as a **unit of consistency**. The **Aggregate Root** is the **only entry point** into an aggregate and is responsible for enforcing all invariants and domain rules across its internal structure.

Until now, our codebase used naming conventions and inheritance (via `BaseAggregateRoot`) to model aggregates but lacked **explicit semantic indicators** to:
- Document intent
- Enforce design consistency
- Guide engineers unfamiliar with the domain model

To solve this, we introduce the `@AggregateRoot` annotation, which explicitly marks a class as an aggregate root and defines metadata such as its **bounded context** and **domain responsibilities**.

---

### Decision

We will introduce and mandate usage of the `@AggregateRoot` annotation on all classes that serve as aggregate roots.

This annotation will:
- Provide **semantic clarity** within the domain model
- Document the **bounded context** and **description** of each aggregate
- Align with and complement our existing `@DomainEntity` and `@ValueObject` annotations
- Enable potential tooling support for architecture validation (e.g., ArchUnit, custom processors)

All aggregate roots must also extend `BaseAggregateRoot<ID>` which encapsulates identity and future extensibility (e.g., domain events, versioning).

---

### Annotation Specification

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface AggregateRoot {
    String description() default "";
    String boundedContext() default "";
}
```

---

### Key Principles of Aggregate Roots

| Characteristic              | Description |
|----------------------------|-------------|
| Single entry point         | Only the root is accessible from outside the aggregate |
| Identity                   | Each root has a globally unique and stable identifier |
| Invariant enforcement      | The root ensures that all rules across its entities/VOs are valid |
| Transactional boundary     | The aggregate is loaded, validated, and persisted as a single unit |
| Consistency boundary       | All operations that must remain consistent reside within the root |
| Encapsulation              | Inner entities and collections must not be exposed or mutated directly |
| Event emission (optional)  | Domain events can be emitted via the root to signal important changes |

---

### Guidelines for Creating Aggregate Roots

1. **Must Extend**:  
   `BaseAggregateRoot<ID>` where `ID` extends `BaseId<T>`

2. **Must Be Annotated**:  
   Use `@AggregateRoot` to document the aggregate's purpose and context

3. **Should Use Factory Methods**:  
   Static `create(...)` or `from(...)` methods to enforce invariants on creation

4. **Should Not Expose Internals**:  
   Use intention-revealing methods (`addItem(...)`, `assign(...)`, etc.) to mutate state

5. **Should Not Accept Full External Aggregates as Fields**:  
   Interactions with other aggregates must occur via their identifiers (`ParticipantId`, `OrderId`)

6. **Should Not Leak Persistence Concerns**:  
   Domain model remains persistence-agnostic — no JPA/Hibernate annotations

7. **Should Emit Domain Events** (optional):  
   For important changes (e.g., `GroupActivatedEvent`), roots may track events internally

---

### Example: `ExpenseGroup` as Aggregate Root

```java
@AggregateRoot(
    description = "Represents a group of participants collaborating on shared expenses",
    boundedContext = "expense-management"
)
public class ExpenseGroup extends BaseAggregateRoot<ExpenseGroupId> {

    private final GroupName groupName;
    private final ParticipantId groupCreatorId;
    private final Set<ParticipantId> participantIds = new HashSet<>();
    private boolean isActivated = false;

    private ExpenseGroup(ExpenseGroupId id, GroupName name, ParticipantId creator) {
        super(id);
        this.groupName = name;
        this.groupCreatorId = creator;
        this.participantIds.add(creator);
    }

    public static ExpenseGroup from(String name, Participant creator) {
        return new ExpenseGroup(
            ExpenseGroupId.generate(),
            GroupName.withName(name),
            creator.getParticipantId()
        );
    }

    public void addParticipant(ParticipantId id) {
        if (participantIds.contains(id)) {
            throw new IllegalArgumentException("Participant already added");
        }
        participantIds.add(id);
    }

    public boolean isActivated() {
        return isActivated;
    }

    public Set<ParticipantId> getParticipantIds() {
        return Set.copyOf(participantIds);
    }
}
```

---

### Pros

| Benefit                     | Description |
|----------------------------|-------------|
| Domain clarity             | Developers can immediately recognize roots and their responsibilities |
| Enforced boundaries        | Prevents improper modeling like exposing or mutating internal state directly |
| Supports automation        | Enables ArchUnit or custom static analysis to validate aggregate rules |
| Standardized documentation | Serves as built-in documentation for team members and reviewers |
| Prepared for growth        | Future domain events, timestamps, and versioning can be introduced consistently |

---

### Cons / Trade-offs

| Trade-off                   | Mitigation |
|----------------------------|------------|
| Slight annotation overhead | Provides high ROI via clarity and tooling support |
| Requires team alignment    | Architectural documentation and onboarding materials will support adoption |

---

### Migration Plan

1. Add `@AggregateRoot` annotation class under `account.domain`
2. Annotate all existing aggregate roots (`ExpenseGroup`, `Order`, etc.)
3. Validate all annotated classes extend `BaseAggregateRoot`
4. Add optional ArchUnit rule to enforce this structure
5. Document usage in engineering onboarding and modeling standards

---

### References

- Eric Evans – *Domain-Driven Design*
- Vaughn Vernon – *Implementing Domain-Driven Design*
- https://dddcommunity.org/
- Current: `ExpenseGroup`, `Participant`, `BaseAggregateRoot`

---
