# Use Tiny Types and Sum Types in Domain Modeling

- Status: Accepted
- Deciders: [List everyone involved in the decision]
- Date: [YYYY-MM-DD, e.g., 2023-01-01]
- Technical Story: [Description or ticket/issue URL]

## Context and Problem Statement

Creating richer and safer domain models requires us to represent our domain concepts explicitly and deal with their business rules. "How can we effectively incorporate these
concepts in our software design?"

## Considered Options:

- Use primitive types or simple classes
- Adopt tiny types
- Use sum types

## Decision Outcome:

Chosen option: "Adopt Tiny Types and Sum Types", because they create a stronger and richer domain model, are explicit about their intent, and provide better type safety.

## Consequences:

**Positive Consequences**

- Better clarity due to explicit definitions of domain concepts.
- Enhances type safety which can prevent bugs at the source code level.
- Easier to enforce invariants and business rules in domain models.

**Negative Consequences**

- May introduce initial complexity in the codebase.
- Requires careful design and domain knowledge to implement correctly.

## Pros and Cons of the Options:

### Use primitive types or simple classes

- Good, because it's simple to use and understand.
- Good, because it requires less coding.
- Bad, because it lacks expressiveness and does not use the compiler to enforce business rules.

### Adopt Tiny Types

- Good, because they provide an explicit representation for each unique concept in the domain model.
- Good, because they enforce type safety preventing bugs that can be caused by incorrect usage of primitive types.
- Bad, because they can lead to verbosity and might create a lot of classes.

### Use Sum Types

- Good, because they can model domain concepts that have mutually exclusive states.
- Good, because they can prevent invalid states in domain models.
- Bad, because they might increase complexity and learning curve as they are not a native concept in some languages.

## Links:

- [Tiny Types](http://darrenhobbs.com/2007/04/11/tiny-types/)
- [Sum Types](https://medium.com/@johnmcclean/sum-types-in-java-and-kotlin-3bf6385cfc4e)
