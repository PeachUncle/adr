# ADR: Encapsulation and Interface-Driven Behavior for Domain Types

Status
- Accepted

Context
- The domain model must reflect behavior, not data holders
- Clean Architecture and the project style guide require that methods be declared on interfaces and implemented by classes, avoiding public setters and anemic models
- Some domain types are simple single-value concepts that benefit from lightweight representations

Decision
- Every domain class encapsulates its attributes and exposes behavior through interfaces
- Public setters and data bags are not allowed in domain classes
- Classes are sealed by default, constructed via a single primary constructor, and immutable by design
- Methods are declared on interfaces and implemented by classes; public methods that do not implement an interface are avoided
- Exception: simple single-value models may be represented as `readonly record struct` without an interface when they only expose a single value and value semantics

Scope
- Domain and Application layers; does not prescribe API/DTO shapes

Rationale
- Prevents anemic domain model, keeps invariants close to behavior, and simplifies testing and evolution
- Aligns with DDD, Elegant Objects principles, and the repository's style guide

Consequences
- Interface-first design increases clarity of contracts and testability
- Constructors only assign fields; all processing happens in methods
- Value objects with single scalar semantics stay lightweight and allocation-friendly

Examples
```csharp
// Interface declares behavior
namespace CascVel.Modules.Evaluations.Management.Domain.Interfaces.Forms;

public interface IEvaluationForm
{
    FormStatus Status();
    FormGroupList Groups();
    FormCriteriaList Criteria();
    IRunFormSnapshot Snapshot();
}

// Sealed class encapsulates attributes and implements behavior
namespace CascVel.Modules.Evaluations.Management.Domain.Entities.Forms;

public sealed class EvaluationForm : IEvaluationForm
{
    private readonly EvaluationFormId _id;
    private readonly FormMeta _meta;
    // ... other fields

    public FormStatus Status() { /* behavior */ }
    public FormGroupList Groups() { /* behavior */ }
    public FormCriteriaList Criteria() { /* behavior */ }
    public IRunFormSnapshot Snapshot() { /* behavior */ }
}

// Exception for simple single-value concepts
namespace CascVel.Modules.Evaluations.Management.Domain.ValueObjects;

public readonly record struct OrderIndex(int Value);
```

Validation
- Code review checks for interface-backed public methods and sealed classes
- Static analysis enforces absence of public setters in domain classes
- Tests cover behavior and invariants rather than field access

Alternatives Considered
- Allowing public data models with setters — rejected due to anemic model risk
- Using inheritance for behavior variation — rejected in favor of composition and interfaces

References
- DDD tactical patterns (entities, value objects)
- Elegant Objects principles

