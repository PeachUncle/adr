# Use Screenplay-Actor Pattern for Test Automation

- Status: Accepted
- Deciders: [List everyone involved in the decision]
- Date: [YYYY-MM-DD, e.g., 2023-01-01]
- Technical Story: [Description or ticket/issue URL]

## Context and Problem Statement

We want to ensure that our application behaves as expected, end-to-end. Therefore, "Which design pattern should be adopted for structuring our automated test cases?"

## Considered Options:

- Page Object Model (POM)
- Screenplay-Actor Pattern
- Keyword Driven Testing

## Decision Outcome:

Chosen option: "Screenplay-Actor Pattern", because it enables us to write tests in a more maintainable and readable manner. Also, it promotes good practices like single
responsibility principle and composition over inheritance.

## Consequences:

**Positive Consequences**

- Tests will be more maintainable due to single responsibility principle.
- Better readability of tests as tests will tell a story involving "actors" and their "goals".
- Scalability in terms of development due to the modularity of this pattern.

**Negative Consequences**

- It may take some time for team members unfamiliar with this pattern to learn and adopt it correctly.
- Test writing process might be a bit longer compared to traditional ways.

## Pros and Cons of the Options:

### Page Object Model (POM)

- Good, because it offers a clear separation between test code and page specific code.
- Good, because it enhances test maintenance and reduces code duplication.
- Bad, because it may lead to "fat" page objects if not designed mindfully.

### Screenplay-Actor Pattern

- Good, because it improves test readability and allows for better structuring of test code.
- Good, because it adheres to SOLID principles of object-oriented design.
- Bad, because it may introduce a steeper learning curve than traditional models.

### Keyword Driven Testing

- Good, because tests are written in a simple language that can be understood by non-developers.
- Good, because it allows business analysts or other stakeholders to write tests.
- Bad, because keyword-based nature might introduce complexity when dealing with more technical scenarios.

## Links:

- [Screenplay-Actor Pattern](https://serenity-bdd.github.io/theserenitybook/0.0.0/screenplay-pattern.html)
- [Page Object Model (POM)](https://martinfowler.com/bliki/PageObject.html)
- [Keyword Driven Testing](https://www.softwaretestinghelp.com/keyword-driven-testing-framework-introduction/)
