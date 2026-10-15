# Order State Flow

* Status: approved
* Deciders: Jaime Ochoa de Alda Cerdán
* Date: 2025-11-05

## Context and Problem Statement

The system must process customer orders through a strict sequence of three phases: preprocessing, authorization, and acceptance. Each phase must be completed successfully before moving to the next, and skipping steps is not allowed. This sequential validation is critical to prevent inconsistent order states and ensure that business rules tied to each phase are properly enforced. The architecture must support this flow in a way that is maintainable, extensible, and scalable under high load.

## Decision Drivers

* RF-04 Actualizar estado del pedido

## Considered Options

* 0008-1-Chain of Responsibility
* 0008-2-State Pattern

## Decision Outcome

Chosen option: 0008-1 – Chain of Responsibility.
This pattern models the order flow as a sequence of handlers, each responsible for validating and processing a specific phase. It enforces the required order by design and prevents business logic from being scattered across conditional branches. It also simplifies testing and supports future additions without modifying existing logic, which is beneficial under high load conditions where additional validation steps may be required in the future.

### Positive Consequences

* Each phase is isolated and testable.
* The flow is enforced structurally, reducing the risk of skipping steps.
* New phases can be introduced without modifying existing logic, reducing the risk of regressions.

### Negative Consequences

* Because the processing logic is split across multiple handlers, debugging may require tracing the entire processing flow to identify the failure point.
* Bad, because the processing order is implicitly defined by how handlers are chained, which may reduce readability as the number of phases grows.

## Pros and Cons of the Options

### 0008-1 – Chain of Responsibility.

Each phase of the order process is implemented as a handler in a chain. The order is passed from one handler to the next only if the current phase succeeds.

* Good, because it enforces sequential validation and prevents skipping steps.
* Good, because each phase is encapsulated, allowing independent testing and easier evolution of individual steps.
* Bad, because debugging failures may require inspecting multiple handlers.
* Bad, because the processing order is implicit, so understanding or modifying the sequence may require reviewing the entire chain.

## 0008-2-State Pattern

Each order phase is modeled as a state object, and the order transitions between states based on internal logic.

* Good, because it encapsulates behavior per state and reflects the current phase explicitly.
* Good, because it allows state-specific logic and transitions.
* Bad, because its flexibility allows defining multiple valid transition paths, which requires additional constraints to enforce a single immutable sequence.
* Bad, because applying the pattern can be overkill when the state machine is small and unlikely to change.