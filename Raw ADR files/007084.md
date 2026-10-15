# ADR-000: Use Architecture Decision Records (ADRs) to Document All Architecturally Significant Decisions

## Status
Accepted

## Context

The BlueZone application is designed as a cross-language, modular reference implementation of the **"Ports and Adapters"** architecture pattern. This pattern supports **Set-Based Engineering (SBE)** by decoupling core logic from infrastructure concerns, enabling multiple viable options for any given adapter, environment, or toolchain.

Set-Based Engineering emphasizes **preserving multiple alternatives** as long as possible, and **deliberate convergence** only after sufficient exploration. In software architecture, this requires conscious awareness of when a design decision constrains future choices.

In practice, however, many architectural decisions are made based on personal experience, library conventions, or undocumented assumptions. This leads to:
- Hidden commitments that narrow design space without explicit discussion.
- Divergent implementations that are difficult to reason about or compare.
- Difficulty onboarding new developers or migrating to new environments.

To address this, we need a lightweight but structured mechanism for making such decisions visible, explainable, and revisitable.

## Decision

We will use **Architecture Decision Records (ADRs)** to document all **architecturally significant decisions** in the BlueZone application and its associated tooling.

- ADRs must be maintained in version control and kept close to the source code.
- Each ADR must explain:
  - The context and forces behind the decision.
  - The options considered and the rationale for the chosen path.
  - Any consequences or limitations introduced by the decision.
- ADRs may exist at two levels:
  - **Common ADRs**, applicable to all language implementations.
  - **Language-Specific ADRs**, applicable only within a given ecosystem (e.g., Python, TypeScript).

### Naming Convention

Common architectural decisions that apply to all language implementations are recorded as `adr-XXX.md`.

Language-specific decisions are recorded using the format `adr-<language>-XXX.md`, for example:
- `adr-py-001.md` for Python-specific decisions.
- `adr-ts-001.md` for TypeScript-specific decisions.

This convention avoids numbering conflicts and keeps language concerns clearly scoped, while maintaining a unified decision record structure.

## Consequences

- Architectural reasoning becomes **explicit, inspectable, and revisitable**.
- Future contributors can understand **why** the system is structured as it is, not just **how**.
- BlueZone remains aligned with **Set-Based Engineering** principles by documenting turning points that reduce the number of viable paths.
- Implementation variants are easier to compare and validate against shared principles.

## References

- [Michael Nygard's ADR Pattern](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html)
- [adr GitHub project](https://github.com/npryce/adr-tools)
