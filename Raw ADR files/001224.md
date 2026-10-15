# Use JUnit and Kotest for Testing

- Status: Accepted
- Deciders: [List everyone involved in the decision]
- Date: [YYYY-MM-DD e.g., 2023-01-01]
- Technical Story: [Description or ticket/issue URL]

## Context and Problem Statement

As we are building software that is robust and reliable, it is necessary to have a testing strategy in place. So, the question is: "Which testing libraries should be used for our
Kotlin project?"

## Considered Options:

- JUnit
- Kotest
- Hamkrest
- Strikt
- MockK
- Mockito

## Decision Outcome:

Chosen option: "JUnit and Kotest", because they provide well-rounded, feature-rich, and mature solutions well-suited for writing and running tests in a Kotlin project.

## Consequences:

**Positive Consequences**

- JUnit is a reliable and well-known library, offering broad IDE integration and a wealth of online resources.
- Kotest provides a flexible and feature-rich environment that supports multiple testing styles with a Kotlin idiomatic API.

**Negative Consequences**

- The learning curve might be steeper for team members not familiar with JUnit and Kotest.
- Integration of multiple testing libraries could increase the complexity of test cases.

## Pros and Cons of the Options:

### JUnit

- Good, because it's widely-used, stable, and has a rich set of assertions and testing functionalities.
- Good, because it is supported out of the box by all major IDEs and build tools.
- Bad, because its syntax and API are not always very Kotlin-friendly.

### Kotest

- Good, because it's a Kotlin-specific testing framework with idiomatic and easy-to-use syntax.
- Good, because it has powerful assertions and supports Behavior-Driven Development (BDD) style.
- Bad, because newcomers to the framework might have a steep learning curve.

### Other Libraries (Hamkrest, Strikt, MockK, Mockito)

- Good, provide alternative testing styles and assertion libraries for Kotlin.
- Bad, could lead to inconsistencies in test cases if not used correctly, reduce the learning curve.

## Links:

- [JUnit Documentation](https://junit.org/junit5/docs/current/user-guide/)
- [Kotest Documentation](https://kotest.io/docs/framework/framework.html)
