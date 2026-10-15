# 5. web framework selection

Date: 2024-05-07

## Status

Accepted

5 [7. api interface selection](0007-api-interface-selection.md)

## Context

The issue is to use a web framework to build the project. The web framework is a software framework designed to support the development of web applications, including web services, web resources, and web APIs. It provides a standard way to build and deploy web applications to implement the endpoints for the mentioned use cases.

### Pros and Cons of Various Web Frameworks:

####  Flask

##### Pros:
- **Code Readability**: Flask follows a minimalistic approach, is a simple approach  which reduces complexity and improves readability.
- **Solution Architecture and Code Design**: Flask allows for flexibility in designing the architecture of web applications. It doesn't enforce a specific architecture, so the developers need to decide a extensible architecture.
- **Testing Strategy**: Flask provides built-in support for testing through tools like Flask-Testing and pytest.
- **Performance**: Flask is lightweight and has low overhead,  suitable for building high-performance web applications.
- **Maintainability and Extensibility**: Flask's modular design and extensibility through Flask extensions make it easy to maintain and extend applications over time.

##### Cons:
- **Solution Architecture and Code Design**: The flexibility of Flask can lead to inconsistency in project structure and architecture, especially in larger projects. Without strict guidelines, it may result in codebase fragmentation and maintenance challenges.
- **Testing Strategy**: Developers need to manually configure and set up testing frameworks and tools. This can increase the initial setup time and complexity of testing setups.
- **Performance**: Flask's simplicity can sometimes result in lower performance compared to more opinionated frameworks like Django or FastAPI, especially for complex applications that require heavy computations or data processing.
- **Maintainability and Extensibility**: Without strict conventions, Flask applications may become harder to maintain as they grow in complexity. Lack of standardization can lead to inconsistencies and dependencies on third-party extensions, affecting long-term maintainability.

#### Django

##### Pros:
- **Code Readability**: Django is an opinionated framework that emphasizes the "Don't Repeat Yourself" (DRY) principle. It provides a structured to increase code readability.
- **Solution Architecture and Code Design**: Django follows the Model-View-Template (MVT) architecture, providing a well-defined structure for organizing code. It includes built-in components like ORM, forms, and templates,
to ensure consistency. The ORM provides a high-level API for interacting with databases, reducing boilerplate code.
- **Testing Strategy**: Django includes a robust testing framework, making it easy to write and execute tests for Django applications. It provides tools for writing unit tests, integration tests, and functional tests.
- **Performance**: Django's built-in caching mechanisms, middleware, and optimization features contribute to improved performance. It offers scalability options like database sharding and caching, enabling efficient handling of large-scale applications.
- **Maintainability and Extensibility**: Django's "batteries-included" approach and strong conventions make it easy to maintain and extend applications. It provides a rich ecosystem of reusable components and third-party packages, reducing development time and effort.

##### Cons:
- **Code Readability**: Steeper learning curve for beginners for Understanding Django's conventions and best practices.
- **Solution Architecture and Code Design**: Django's opinionated approach can sometimes be restrictive for developers who prefer more flexibility in designing the architecture of their applications. Customizing certain aspects may require overriding or extending Django's built-in functionality.
- **Testing Strategy**: While Django provides comprehensive testing tools, setting up and configuring tests can be complex, especially for complex applications. Managing test dependencies and **fixtures** may require additional effort.
- **Performance**: Django's feature-rich nature and specially ORM may introduce overhead in terms of memory usage and response times, especially for lightweight applications where some features are unnecessary.
- **Maintainability and Extensibility**: Django's strong conventions and built-in components may lead to dependency on specific Django patterns and workflows. Deviating from these conventions may complicate maintenance and future development.

#### FastAPI

##### Pros:
- **Code Readability**: FastAPI encourage Python type annotations resulting in readable and maintainable code.
- **Solution Architecture and Code Design**: Dependency Injection and Data Models built-in, promoting clean architecture and separation of concerns.
- **Testing Strategy**: FastAPI integrates seamlessly with testing frameworks like pytest and provides tools for testing endpoints, request validation, and response serialization. It provides built-in support for OpenAPI and JSON Schema, facilitating API testing and documentation.
- **Performance**: FastAPI is known for its high performance, using async capabilities.
- **Maintainability and Extensibility**: FastAPI's modular design. It encourages the use of reusable components and dependency injection.

### Cons:
- **Code Readability**: Requires effort to understand correctly Python type annotations and async syntax.
- **Solution Architecture and Code Design**: Although FastAPI promotes clean architecture, the guidelines will be not enough in some cases and architecture patterns will be required.
- **Testing Strategy**: Asynchronous testing can be challenging and may require additional setup and configuration.
- **Performance**: The overhead of async programming may not always be necessary for every project.
- **Maintainability and Extensibility**: FastAPI's reliance on async programming may limit interoperability with synchronous codebases or libraries. Integrating synchronous components into an async FastAPI application may require additional effort and workarounds.


## Decision

Considering these factors, FastAPI is well-suited for projects requiring clean, readable code, efficient testing strategies, high performance, and easy maintainability and extensibility.

## Consequences

Using FastAPI will require to follow architectural patterns and guidelines to ensure consistency and maintainability. Developers will need to familiarize themselves with Python type annotations and async programming to leverage FastAPI's full potential. Testing strategies will need to be adapted to support asynchronous testing, and performance optimizations should consider the benefits of async programming. Overall, the decision to use FastAPI will lead to a modern, high-performance web application with a strong emphasis on code readability, testing, and maintainability.
