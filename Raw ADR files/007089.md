# ADR-006: Provide Full Support for Strong Typing Without Enforcing It

## Status
Accepted

## Context

Modern programming languages offer a spectrum of typing disciplines. Languages such as TypeScript, Kotlin, Rust, Swift, and Python (with type hints) support strong or optional static typing. Others, like JavaScript or Ruby, emphasize dynamic typing and runtime flexibility.

Strong typing brings several benefits:
- Early detection of errors at compile time.
- Improved readability and navigability via IDE support.
- Safer refactoring and clearer contracts between components.
- Better documentation through type annotations.

However, dynamic typing remains popular and offers advantages in certain contexts:
- Faster prototyping and experimentation.
- Simpler syntax and fewer constraints during early development.
- Lower initial setup cost for small-scale or throwaway systems.

The BlueZone application is designed as a showcase of the "Ports and Adapters" architectural pattern and adheres to the principles of **Set-Based Engineering (SBE)**. In this context, architectural choices should **maximize the number of viable options** rather than prematurely converge on a single solution.

## Decision

1. **Strong typing is supported but not required.**
   - Implementations of the BlueZone application in a given language may choose to use static typing where it adds value.
   - All architectural components—application core, ports, adapters, and test infrastructure—should be definable in a statically typed manner when desired.

2. **Dynamic typing remains fully supported.**
   - No aspect of the architecture will require or assume the use of strong typing.
   - Dynamically typed development styles remain valid and encouraged where appropriate.

3. **Test code is included in this scope.**
   - Language implementations may apply strong typing in test suites (e.g., typed `World` classes in Cucumber-based tests).
   - However, this remains an optional design choice, not a mandated convention.

## Consequences

- Language-specific implementations can align with the idioms and strengths of their ecosystem.
- Developers working in statically typed environments can benefit from type safety without architectural obstacles.
- Dynamically typed implementations can remain lightweight and flexible.
- This ADR lays the foundation for future decisions that enable typed infrastructure (e.g., test world selection by tag), while maintaining flexibility across all variants.
