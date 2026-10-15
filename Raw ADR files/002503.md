# ADR - Testing Plan

## Context
The advanced library management system uses a microservices architecture with Next.js, Express.js, and MongoDB to manage borrowing, returning, and wishlist features. A comprehensive testing strategy is essential to ensure the functionality, reliability, and security of the system.

## Problem Statement
Without a well-defined testing plan, the advanced library management system could face challenges such as undetected bugs and integration problems. These challenges may impact key functionalities, including borrowing, returning, and wishlist management, as well as the overall security and scalability of the system. Therefore, implementing a structured testing strategy is crucial to ensure the system meets its functional and non-functional requirements while delivering a smooth and reliable user experience.

## Decision For Testing Plan

To ensure the system is robust, reliable, and meets the expected functional and non-functional requirements, the following testing strategies will be implemented:

### Unit Testing
Unit tests will be implemented for all individual components, ensuring that each unit of the system behaves as expected in isolation. This includes testing key functions within each microservice, such as borrowing logic, return handling, and wishlist management. Mocking dependencies will be used to isolate units and test them independently of external services, such as databases or external APIs.

- **Scope**:
  - Testing functions and methods in isolation
  - Testing validation and business logic for key features
  - Mocking database interactions to ensure accurate unit tests

### API Testing
API tests will be conducted to validate the functionality, security, and reliability of the RESTful APIs exposed by the system. This will include ensuring that all endpoints for borrowing, returning, and managing wishlists respond correctly and handle edge cases appropriately.

- **Scope**:
  - Testing all REST API endpoints (GET, POST, PUT, DELETE)
  - Validating input/output formats, status codes, and response times
  - Ensuring proper error handling and security (e.g., authentication, authorization)

### Integration Testing
Integration tests will be implemented to verify that the individual components of the system work together as expected. This includes testing interactions between the microservices, such as communication between the frontend (Next.js) and backend (Express.js), as well as integration with the MongoDB database. These tests will ensure that data flows correctly between services and that the system functions as a cohesive whole.

- **Scope**:
  - Validating service-to-service communication
  - Simulating real-world scenarios (e.g., borrowing, returning books, managing wishlist) to ensure smooth interactions between microservices

### Non-functional Requirements Testing
To ensure the system meets non-functional requirements, various performance and security testing strategies will be applied. This will include load testing to assess the system’s performance under heavy traffic, security testing to identify vulnerabilities, and scalability testing to ensure the system can grow with increasing user demand.

- **Scope**:
  - **Accessibility Testing**: Accessibility testing ensures that the library management system is usable by all users, including those with disabilities. This includes ensuring that the system is compliant with accessibility standards such as WCAG 2.1.
  - **Performance Testing**: Assessing response times and throughput under varying loads.
  - **Security Testing**: Testing for vulnerabilities like operation's not being able to be done until a user has logged in to check if the access control systems
  - **Scalability Testing**: Ensuring the system can scale horizontally with increasing users or data size.
