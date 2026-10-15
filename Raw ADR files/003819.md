# Architecture Decision Record (ADR)

## Project: E-commerce System

### Context and Overview
This project implements an e-commerce system that handles product management, basket management, discount application, and order processing. The project follows **Domain-Driven Design (DDD)** principles to ensure scalability, maintainability, and separation of concerns. Several key design patterns have been employed to structure the business logic and interactions between entities.

### 1. Key Design Decisions

#### 1.1. Repository Pattern
**Decision**: 
- Implement the **Repository Pattern** to abstract the database operations for various entities such as `Product`, `Basket`, and `Discount`.

**Reasoning**:
- The **Repository Pattern** encapsulates data access logic and separates it from business logic, making the codebase easier to maintain and test.
- It hides the underlying database technology (EF Core, SQL, etc.) from the domain layer, promoting loose coupling.

**Impact**:
- Improves testability of services by allowing mocking of repositories.
- Allows easier switching of data access technologies in the future.

#### 1.2. Domain Event Pattern
**Decision**: 
- Utilize the **Domain Event Pattern** to decouple the domain logic from side effects, allowing for more modular and extensible code.

**Reasoning**:
- The **Domain Event Pattern** is used to trigger domain events such as `BasketCompletedEvent`, `DiscountAppliedEvent`, and `ProductStockUpdatedEvent` when significant changes occur in the system. This allows different parts of the system to react to domain changes without tightly coupling the code.
- The **Domain Event Pattern** enables the system to be easily extended by adding new event handlers without modifying existing domain logic.

**Impact**:
- Reduces code duplication and promotes cleaner separation of concerns.
- Allows for side effects like stock updates, notifications, and order creation to be handled separately from core domain logic.

#### 1.3. Dependency Injection Pattern
**Decision**: 
- Leverage the **Dependency Injection (DI) Pattern** for injecting services, repositories, and event handlers across the application.

**Reasoning**:
- Using **DI** promotes loose coupling between components, making the system more modular and testable. It also makes it easier to configure and swap dependencies (such as different repository implementations) without modifying the business logic.

**Impact**:
- Enhances the testability of the system by allowing mock dependencies in unit tests.
- Simplifies the configuration of event consumers, repositories, and services.

### 2. Architectural Patterns

#### 2.1. Domain-Driven Design (DDD)
**Decision**: 
- Use **Domain-Driven Design (DDD)** principles to model the business logic of the e-commerce system, focusing on entities such as `Product`, `Basket`, `Discount`, and `Order`.

**Reasoning**:
- DDD ensures that the domain logic is at the center of the design and helps align the software architecture with the business needs. It facilitates better communication between developers and business stakeholders.

**Impact**:
- Promotes a deep understanding of the domain and models complex business rules effectively.
- Ensures the code remains flexible and extensible as new business requirements emerge.

### 3. Technologies and Frameworks

- **ASP.NET Core**: The primary framework used for building the web API.
- **Entity Framework Core (EF Core)**: Used for data persistence and managing the database with migrations.
- **MassTransit**: Implemented to handle messaging for domain events and RabbitMQ integration.
- **RabbitMQ**: Used for event-driven communication between different parts of the system, particularly for domain events.

### 4. Key Modules and Components

#### 4.1. Product Module
- **Responsibilities**: Manage product catalog, stock levels, and pricing.
- **Key Entities**: `Product`
- **Key Patterns**: Repository Pattern, Domain Event Pattern

#### 4.2. Basket Module
- **Responsibilities**: Manage customer shopping baskets, handle adding/removing items, apply discounts.
- **Key Entities**: `Basket`, `BasketItem`
- **Key Patterns**: Repository Pattern, Domain Event Pattern

#### 4.3. Discount Module
- **Responsibilities**: Apply and manage customer-specific discounts, track discount usage, and handle discount rules (e.g., 5% off next purchase).
- **Key Entities**: `Discount`
- **Key Patterns**: Repository Pattern, Domain Event Pattern

#### 4.4. Order Module
- **Responsibilities**: Process orders, create order records from baskets, and handle stock updates.
- **Key Entities**: `Order`
- **Key Patterns**: Repository Pattern, Domain Event Pattern

### 5. Future Considerations

#### 5.1. Eventual Consistency
In the future, the system might benefit from **eventual consistency** using messaging to ensure that changes propagate across different microservices or external systems without requiring immediate consistency.

#### 5.2. CQRS Pattern
As the system grows, consider implementing the **Command Query Responsibility Segregation (CQRS)** pattern to separate the read and write concerns, especially for complex querying and reporting needs.

### 6. Conclusion
This document outlines the key design decisions made for this e-commerce system and explains the reasoning behind each choice. The use of well-known design patterns such as **Repository**, **Domain Events**, and **Dependency Injection** ensures that the system is modular, scalable, and maintainable over time.

---

### Author: Ahmad Khojasteh
### Date: 10-22-2024
