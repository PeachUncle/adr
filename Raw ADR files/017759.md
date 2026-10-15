# ADR-003: Layered Architecture with Spring Boot

## Status

Accepted

## Context

The project requires a well-structured architecture that follows Spring Boot best practices and provides clear separation of concerns. We considered several architectural patterns:

- **Layered Architecture**: Traditional controller-service-repository pattern
- **Hexagonal Architecture**: Ports and adapters pattern
- **Clean Architecture**: Dependency inversion with use cases
- **Microservices Architecture**: Distributed services approach
- **Monolithic Architecture**: Single deployable unit

Key requirements:
- Clear separation of concerns
- Testability and maintainability
- Spring Boot best practices compliance
- Support for rule engine integration
- Scalability for future enhancements

## Decision

We chose to implement a **Layered Architecture** following Spring Boot conventions with the following structure:

```
com.example.springdroolsintegration/
├── config/          # Configuration classes (@Configuration)
├── controller/      # REST API controllers (@RestController)
├── service/         # Business logic services (@Service)
├── model/           # Domain models and DTOs
│   ├── dto/         # Data Transfer Objects
│   ├── entity/      # Domain entities
│   └── request/     # API request models
├── exception/       # Custom exceptions and handlers
├── util/           # Utility classes
└── health/         # Custom health indicators
```

### Key Architectural Principles

1. **Constructor Injection**: All dependencies injected through constructors
2. **Package-private visibility**: Default visibility for internal components
3. **Immutable DTOs**: Using Java records where appropriate
4. **Centralized exception handling**: Global exception handler with @RestControllerAdvice
5. **Configuration externalization**: Using @ConfigurationProperties

## Consequences

### Positive

- **Familiar pattern**: Well-understood by Spring Boot developers
- **Clear boundaries**: Each layer has distinct responsibilities
- **Testability**: Easy to unit test individual layers
- **Spring Boot alignment**: Follows framework conventions and best practices
- **Maintainability**: Clear structure makes code easy to navigate and modify
- **Dependency management**: Constructor injection ensures proper initialization
- **Configuration management**: Externalized configuration supports different environments

### Negative

- **Potential over-engineering**: May be more complex than needed for simple use cases
- **Layer coupling**: Risk of tight coupling between layers if not carefully managed
- **Boilerplate code**: May require more code for simple operations
- **Performance overhead**: Multiple layers can introduce latency

### Neutral

- **Scalability**: Can be extended but may require refactoring for complex scenarios
- **Team learning**: Requires understanding of layered architecture principles

## Implementation Details

### Controller Layer
- Handle HTTP requests and responses
- Input validation using Bean Validation
- OpenAPI documentation annotations
- Proper HTTP status code handling

### Service Layer
- Business logic implementation
- Rule engine integration
- Transaction management
- Async processing support

### Configuration Layer
- Drools engine configuration
- Security configuration
- Application properties binding

### Exception Handling
- Global exception handler
- ProblemDetail (RFC 7807) responses
- Structured error logging

## References

- [Spring Boot Reference Documentation](https://docs.spring.io/spring-boot/docs/current/reference/html/)
- [Spring Framework Architecture Guidelines](https://spring.io/guides/gs/architecture/)
- [Clean Code Architecture Principles](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)