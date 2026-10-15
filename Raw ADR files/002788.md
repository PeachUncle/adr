---
doc_id: "ADR-008"
tech_stack: ["spring", "java", "mongodb"]
title: "ADR-008: Layered Architecture Pattern"
version: "1.0.0"
last_updated: "2025-12-19"
status: "accepted"
category: "Architecture Decision"
audience: ["Backend Developers", "Architects"]
prerequisites: ["ADR-006-Spring-Boot-Framework.md"]
related_docs: ["Architecture/Backend-Refactoring.md", "backend/docs/BACKEND_DOCUMENTATION_PLAN.md"]
maintainer: "Development Team"
---

# <ADR-008-Layered Architecture Pattern>

## Status

**Accepted** - Layered Architecture (Controller → Service → Repository → Domain) is the primary architectural pattern.

## Context

The MyTechPortfolio backend required a clear architectural pattern that:
- Separates concerns into distinct layers
- Makes code testable and maintainable
- Follows industry-standard patterns
- Enables team collaboration
- Supports scalability
- Makes onboarding easier

### Alternatives Considered

1. **Hexagonal Architecture (Ports & Adapters)**
   - Pros: Framework-agnostic, testable, clear boundaries
   - Cons: More complex, may be overkill for portfolio

2. **Clean Architecture**
   - Pros: Dependency inversion, testable, maintainable
   - Cons: More layers, complex for simple CRUD

3. **MVC (Model-View-Controller)**
   - Pros: Simple, widely understood
   - Cons: Less suitable for REST APIs, no clear service layer

4. **Layered Architecture**
   - Pros: Clear separation, industry standard, Spring Boot friendly
   - Cons: Can lead to anemic domain models if not careful

5. **Microservices**
   - Pros: Independent scaling, technology diversity
   - Cons: Overkill for portfolio, operational complexity

## Decision

We chose **Layered Architecture** with the following layers:
- **Controller Layer**: Handles HTTP requests/responses
- **Service Layer**: Contains business logic
- **Repository Layer**: Data access
- **Domain Layer**: Domain entities

### Rationale

1. **Clear Separation of Concerns**
   - Each layer has a single responsibility
   - Controllers handle HTTP, Services handle business logic
   - Repositories handle data access
   - Easy to understand and navigate

2. **Testability**
   - Each layer can be tested independently
   - Easy to mock dependencies
   - Clear test boundaries
   - Supports TDD workflow

3. **Spring Boot Alignment**
   - Natural fit with Spring Boot structure
   - Leverages Spring's dependency injection
   - Uses Spring Data repositories
   - Follows Spring Boot conventions

4. **Industry Standard**
   - Widely understood pattern
   - Easy onboarding for new developers
   - Common in enterprise applications
   - Well-documented pattern

5. **Maintainability**
   - Changes isolated to specific layers
   - Easy to locate code
   - Clear dependency flow
   - Scalable structure

6. **Team Collaboration**
   - Clear boundaries for parallel work
   - Consistent structure across codebase
   - Easy code reviews
   - Predictable organization

## Consequences

### Positive

- **Clear Structure**: Easy to understand and navigate
- **Testability**: Each layer can be tested independently
- **Maintainability**: Changes isolated to specific layers
- **Onboarding**: New developers understand structure quickly
- **Spring Boot Fit**: Natural alignment with Spring Boot
- **Scalability**: Structure supports growth

### Negative

- **Anemic Domain Models**: Risk of putting all logic in services
- **Layer Violations**: Need discipline to maintain boundaries
- **Boilerplate**: More classes and interfaces
- **Over-Engineering**: May be too much for simple CRUD

### Neutral

- **Performance**: Minimal performance impact
- **Complexity**: Adds some complexity but improves maintainability

## Implementation Details

### Layer Structure

```
com.mytechfolio.portfolio/
├── controller/          # REST Controllers (HTTP layer)
│   ├── ProjectController.java
│   └── base/
│       └── AbstractCrudController.java
│
├── service/            # Business Logic Layer
│   ├── ProjectService.java
│   └── BaseService.java
│
├── repository/         # Data Access Layer
│   ├── ProjectRepository.java
│   └── ...
│
└── domain/             # Domain Entities
    ├── Project.java
    └── ...
```

### Layer Responsibilities

#### Controller Layer
- Handle HTTP requests/responses
- Request validation
- Response formatting
- Error handling
- API documentation (Swagger)

**Example**:
```java
@RestController
@RequestMapping(ApiConstants.PROJECTS_ENDPOINT)
public class ProjectController extends AbstractCrudController<...> {
    @GetMapping
    public ResponseEntity<PageResponse<ProjectResponse>> getAllProjects(...) {
        // Delegate to service
    }
}
```

#### Service Layer
- Business logic
- Transaction management
- Data transformation (Entity ↔ DTO)
- Validation
- Exception handling

**Example**:
```java
@Service
public class ProjectService implements BaseService<Project, ...> {
    public ProjectResponse create(ProjectCreateRequest request) {
        // Business logic
        // Validation
        // Entity creation
        // Return DTO
    }
}
```

#### Repository Layer
- Data access
- Database queries
- CRUD operations
- Custom queries

**Example**:
```java
@Repository
public interface ProjectRepository extends MongoRepository<Project, String> {
    List<Project> findByTitleContaining(String title);
}
```

#### Domain Layer
- Domain entities
- Business rules (if any)
- Entity relationships
- Value objects

**Example**:
```java
@Document(collection = "projects")
public class Project {
    @Id
    private String id;
    private String title;
    // ...
}
```

### Dependency Flow

```
Controller → Service → Repository → Domain
     ↓          ↓          ↓
   DTOs      DTOs      Entities
```

### Data Flow

1. **Request**: HTTP Request → Controller → Service → Repository → Database
2. **Response**: Database → Repository → Service (Entity → DTO) → Controller → HTTP Response

### Base Classes

- `AbstractCrudController`: Base controller with CRUD operations
- `BaseService`: Base service interface
- `BaseServiceImpl`: Base service implementation
- `MongoRepository`: Spring Data repository interface

## Best Practices

1. **Layer Boundaries**: Don't skip layers (Controller → Service, not Controller → Repository)
2. **DTOs**: Use DTOs between Controller and Service layers
3. **Entities**: Keep entities in domain layer, don't expose directly
4. **Business Logic**: Keep business logic in service layer
5. **Data Access**: Keep data access in repository layer
6. **Validation**: Validate at controller and service layers

## Anti-Patterns to Avoid

1. **Anemic Domain Models**: Don't put all logic in services, use domain models when appropriate
2. **Layer Skipping**: Don't call repository from controller
3. **Business Logic in Controllers**: Keep controllers thin
4. **Data Access in Services**: Use repositories for data access
5. **Tight Coupling**: Use interfaces and dependency injection

## Related Decisions

- [ADR-006: Spring Boot Framework](./ADR-006-Spring-Boot-Framework.md)
- [ADR-007: MongoDB Database](./ADR-007-MongoDB-Database.md)
- [Backend Refactoring Summary](../Architecture/Backend-Refactoring.md)

## References

- [Spring Boot Best Practices](https://spring.io/guides)
- [Layered Architecture Pattern](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html)
- [Backend Documentation Plan](../../backend/docs/BACKEND_DOCUMENTATION_PLAN.md)

---

**Decision Date**: 2025-11-17  
**Decided By**: Development Team  
**Review Date**: TBD (review if architecture becomes too complex)

