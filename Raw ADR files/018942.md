# ADR 005: Use of NSubstitute for Mocking

## Status
Accepted

## Context
Unit testing requires isolating the System Under Test (SUT) from its dependencies. Mocking frameworks allow us to create test doubles for interfaces and abstract classes.

The .NET ecosystem has three major mocking libraries, all marked as "Must Know" in the roadmap:
1.  **NSubstitute**
2.  **Moq**
3.  **FakeItEasy**

We need to choose one as the primary mocking library for consistency across the codebase.

## Alternatives Considered

### 1. Moq
*   **Description**: The most widely adopted mocking library in .NET (since 2007).
*   **Syntax Example**:
    ```csharp
    var mock = new Mock<IMovieRepository>();
    mock.Setup(x => x.GetById(1)).Returns(new Movie { Id = 1 });
    var result = mock.Object.GetById(1);
    mock.Verify(x => x.GetById(1), Times.Once);
    ```
*   **Pros**: Mature, extensive documentation, large community.
*   **Cons**: Verbose syntax (`Mock<T>`, `.Object`, `.Setup()`). Less idiomatic for modern C#.

### 2. FakeItEasy
*   **Description**: A mocking library focused on simplicity and discoverability.
*   **Syntax Example**:
    ```csharp
    var fake = A.Fake<IMovieRepository>();
    A.CallTo(() => fake.GetById(1)).Returns(new Movie { Id = 1 });
    ```
*   **Pros**: Clean syntax, good documentation.
*   **Cons**: Smaller community than Moq/NSubstitute. Less familiar to most .NET developers.

## Decision
We decided to use **NSubstitute** as the primary mocking library.

**Syntax Example**:
```csharp
var substitute = Substitute.For<IMovieRepository>();
substitute.GetById(1).Returns(new Movie { Id = 1 });
var result = substitute.GetById(1);
substitute.Received(1).GetById(1);
```

## Consequences

### Positive
*   **Readability**: The syntax reads like natural language. `substitute.GetById(1).Returns(...)` is immediately understandable.
*   **Modern C# Idioms**: Works seamlessly with async/await, expression-bodied members, and modern language features.
*   **Low Ceremony**: No need for `.Object` or `new Mock<T>()`. You work directly with the substitute.
*   **Community**: Well-maintained, active development, good documentation.

### Negative
*   **Learning Curve**: Developers coming from Moq will need to learn a different API (though it's simpler).
*   **Ecosystem**: Some third-party libraries may have examples using Moq, requiring translation.
