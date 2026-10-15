# ADR 008: Product Service Module

**Status:** Accepted  
**Date:** 2025-06-21  
**Authors:** E-commerce Development Team  
**Reviewers:** Architecture Review Board

## Context

The E-Commerce platform requires a robust product management system to handle product catalog operations, inventory management, and product purchasing workflows. As part of our microservices architecture, we need a service that can manage product data while ensuring transactional consistency for inventory operations.

### Business Requirements
- Product catalog management (CRUD operations)
- Category-based product organization
- Real-time inventory tracking and management
- Atomic product purchase operations for order processing
- High-performance product search and retrieval
- Integration with order and payment services

### Technical Context
- Existing microservices architecture with Spring Boot
- Relational database requirements for transactional consistency
- Service discovery via Eureka Discovery Server
- Centralized configuration management via Config Server
- Need for ACID transactions for inventory operations
- Integration with other services (Order Service, Payment Service)

## Decision

We will implement the Product Service as an independent microservice with the following architectural decisions:

### 1. Service Architecture
- **Technology Stack:** Spring Boot 3.x with Spring Data JPA
- **Database:** Relational database (PostgreSQL/MySQL) for ACID compliance
- **ORM:** JPA/Hibernate for entity management
- **API Design:** RESTful APIs following REST conventions
- **Validation:** Bean Validation (JSR-303) for request validation

### 2. Data Model Design
```sql
-- Core entities with relationships
Product {
    id: Integer (Primary Key, Auto-generated)
    name: String (NOT NULL)
    description: String
    availableQuantity: Double (NOT NULL, >= 0)
    price: BigDecimal (NOT NULL, >= 0)
    category_id: Integer (Foreign Key)
}

Category {
    id: Integer (Primary Key, Auto-generated)
    name: String (NOT NULL, UNIQUE)
    description: String
}

-- Relationship: Product MANY-TO-ONE Category
```

### 3. Core Business Operations

#### Product Management
- **Create Product:** Add new products with category association
- **Retrieve Products:** Individual and bulk product retrieval
- **Update Product:** Modify product details and inventory
- **Category Management:** Organize products by categories

#### Inventory Management
- **Stock Tracking:** Real-time available quantity management
- **Purchase Processing:** Atomic multi-product purchase operations
- **Inventory Validation:** Prevent overselling through stock checks

### 4. API Design Patterns
```
POST   /api/v1/products           - Create new product
GET    /api/v1/products           - List all products
GET    /api/v1/products/{id}      - Get product by ID
POST   /api/v1/products/purchase  - Process product purchases (bulk)
```

### 5. Transaction Management Strategy
- **ACID Transactions:** Use JPA transactions for inventory operations
- **Optimistic Locking:** Prevent concurrent inventory conflicts
- **Rollback Strategy:** Complete transaction rollback on any purchase failure
- **Isolation Level:** READ_COMMITTED for inventory operations

## Implementation Details

### Key Components

#### 1. ProductController
- RESTful API endpoints for product operations
- Request validation using Bean Validation
- Standardized HTTP response codes and error handling

#### 2. ProductService
- **Business Logic Layer:** Core product and inventory management
- **Transaction Management:** `@Transactional` for atomic operations
- **Purchase Algorithm:** Multi-product atomic purchase processing
  ```java
  @Transactional(rollbackFor = ProductPurchaseException.class)
  public List<ProductPurchaseResponse> purchaseProducts(...)
  ```

#### 3. Data Access Layer
- **ProductRepository:** JPA repository with custom query methods
- **Custom Queries:** Optimized bulk operations (`findAllByIdInOrderById`)
- **Entity Relationships:** JPA entity mappings for Product-Category

#### 4. Domain Model
- **Product Entity:** Core product with inventory tracking
- **Category Entity:** Product categorization with cascade operations
- **Purchase DTOs:** Request/Response objects for purchase operations

### Purchase Operation Workflow
1. **Validation Phase:** Verify all requested products exist
2. **Stock Check Phase:** Validate sufficient inventory for each product
3. **Inventory Update Phase:** Atomically reduce available quantities
4. **Response Generation:** Create purchase confirmation responses
5. **Rollback Mechanism:** Automatic rollback on any failure

### Error Handling Strategy
- **ProductPurchaseException:** Custom exception for purchase failures
- **EntityNotFoundException:** Standard JPA exception for missing products
- **Global Exception Handler:** Centralized error response formatting
- **Validation Errors:** Bean validation with detailed error messages

## Integration Patterns

### Service Discovery
- Register with Eureka Discovery Server
- Service-to-service communication via service names
- Load balancing through Ribbon/Spring Cloud LoadBalancer

### Configuration Management
- Externalized configuration via Config Server
- Environment-specific database configurations
- Feature flags for experimental features

### Inter-Service Communication
- **Synchronous:** REST calls for immediate operations
- **Circuit Breaker:** Resilience patterns for external service calls
- **Event Publishing:** Consider async events for inventory changes

## Consequences

### Positive Consequences
✅ **ACID Compliance:** Relational database ensures data consistency for financial operations  
✅ **Atomic Purchases:** Multi-product purchases are fully atomic (all-or-nothing)  
✅ **Performance:** JPA optimizations and custom queries for efficient operations  
✅ **Scalability:** Stateless service design enables horizontal scaling  
✅ **Data Integrity:** Foreign key constraints ensure referential integrity  
✅ **Inventory Accuracy:** Real-time stock tracking prevents overselling

### Challenges and Mitigation Strategies

#### 1. Database Performance and Scalability
**Challenge:** High read/write load on product inventory  
**Mitigation:**
- Implement database connection pooling (HikariCP)
- Add database indexes on frequently queried fields
- Consider read replicas for product catalog queries
- Implement query optimization and monitoring

#### 2. Concurrent Purchase Operations
**Challenge:** Race conditions during simultaneous product purchases  
**Mitigation:**
- Use optimistic locking with `@Version` field
- Implement retry mechanisms for failed transactions
- Consider pessimistic locking for high-contention scenarios
- Monitor and alert on transaction rollback rates

#### 3. Cross-Service Transaction Consistency
**Challenge:** Maintaining consistency across Order and Product services  
**Mitigation:**
- Implement Saga pattern for distributed transactions
- Use event-driven architecture for eventual consistency
- Implement compensating actions for rollback scenarios
- Consider two-phase commit for critical operations

#### 4. Inventory Synchronization
**Challenge:** Real-time inventory updates across multiple channels  
**Mitigation:**
- Implement event publishing for inventory changes
- Use message queues for reliable event delivery
- Consider CQRS pattern for read/write separation
- Implement inventory reconciliation processes

#### 5. Service Dependencies
**Challenge:** Dependencies on Config Server and Discovery Server  
**Mitigation:**
- Implement circuit breaker patterns
- Use local fallback configurations
- Design for graceful degradation
- Implement health checks and monitoring

### Data Consistency Considerations
- **Product Creation:** Ensure category exists before product creation
- **Category Deletion:** Cascade delete or prevent if products exist
- **Purchase Operations:** Maintain strict ACID properties
- **Inventory Updates:** Implement audit trails for inventory changes

### Performance Characteristics
- **Read Operations:** Optimized for high-frequency product lookups
- **Write Operations:** Transactional safety over pure performance
- **Bulk Operations:** Efficient batch processing for purchase operations
- **Caching Strategy:** Consider Redis for frequently accessed product data

## Security Considerations
- **Input Validation:** Comprehensive request validation
- **SQL Injection:** JPA parameterized queries for safety
- **Authorization:** Role-based access for administrative operations
- **Audit Logging:** Track all inventory-changing operations

## Monitoring and Observability
- **Metrics:** Transaction success/failure rates, response times
- **Logging:** Structured logging with correlation IDs
- **Health Checks:** Database connectivity and service health
- **Alerting:** Low inventory, high transaction failure rates

## Future Considerations
- **Product Search:** Integration with Elasticsearch for advanced search
- **Product Images:** Integration with file storage services
- **Product Reviews:** Extension for customer review functionality
- **Price History:** Audit trail for price changes
- **Bulk Import:** Administrative tools for product catalog management



## Review and Update Schedule
This ADR will be reviewed quarterly or when significant changes to product requirements, performance characteristics, or integration patterns occur.

---
*Last Updated: 2025-06-21*  
