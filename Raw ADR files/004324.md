## Architectural Decision Record (ADR)

### Context

The project aims to build a full-stack financial management application, focusing on learning Java, Spring, React.js, Clean Architecture, CI/CD, and testing. The system should support authentication, CRUD operations for resources (transactions, budget, recurring accounts), a dashboard with charts, and optional evolutions such as integration with external APIs and PDF report generation.

### Decision

We will adopt the following architectural decisions for the project:

1. **Code Organization (Backend):** The code will be organized in a modular fashion, with each entity having its own directory. Each directory will contain:
    - **Entity (Model):** Represents the application's data and domain.
    - **Controller:** Handles HTTP requests and interacts with the service layer.
    - **Service:** Contains business logic, orchestrating interaction between the Controller and Repository.
    - **Repository:** Manages database communication (data access).
    - **DTOs:** Data Transfer Objects, used for input and output in APIs.
2. **Frameworks and Languages:**
    - Spring Boot 3.4.4 with Java 17, following Clean Architecture and SOLID principles.
    - Layered architecture: Controller → Service → Repository.
3. **Authentication and Security:**
    - JWT with Spring Security for stateless authentication and support for roles (USER, ADMIN).
    - CORS configuration and protection against SQL Injection.
4. **Frontend:**
    - React.js with Vite (or Angular as an alternative), integrated with the backend via REST APIs.
5. **Database:**
    - H2 for development; PostgreSQL for production, managed with Flyway.
6. **CI/CD:**
    - GitHub Actions for linting, tests (unit, integration, E2E), static analysis (CodeQL, SonarQube), and deployment (manual/automatic) to AWS.
7. **Testing:**
    - Coverage ≥ 80% with JUnit 5, Mockito, and Cypress (frontend E2E).
8. **Documentation:**
    - OpenAPI for APIs and ADRs for architectural decisions.
9. **Infrastructure:**
    - Docker and Docker Compose for local environment; AWS for production, managed with Terraform.
10. **Optional Evolutions:**
    - Cache with Redis, PDF report generation, and external integrations.

### Pedagogical Objective

Practice full-stack development and DevOps, including Infrastructure as Code (IaC).

### Scope

MVP with CRUD operations, authentication, and dashboard; evolutions with external integrations.

### Terraform Details

Deployment to AWS requires configuration of resources such as EC2 (for the application), RDS (PostgreSQL), and VPC (secure network), which must be provisioned in an automated, versioned, and reproducible manner to support CI/CD and scalability.

### Alternatives Considered

### Infrastructure Management

- **Terraform:**
    - **Pros:** Declarative, multi-cloud, active community, GitHub Actions integration, versioned with Git.
    - **Cons:** Learning curve for HCL syntax, need to manage state (.tfstate).
- **AWS CloudFormation:**
    - **Pros:** Native to AWS, direct integration with services.
    - **Cons:** Less flexible for multi-cloud, more verbose syntax (JSON/YAML).
- **AWS CDK:**
    - **Pros:** Uses languages like Java, allows programmatic logic.
    - **Cons:** More complex for teams focused on declarative IaC.

### Backend Framework

- **Spring Boot 3.4:**
    - **Pros:** Large community, native support for REST, Security, JPA.
    - **Cons:** Initially complex advanced configuration.
- **Quarkus:**
    - **Pros:** Fast startup, lower memory consumption.
    - **Cons:** Less adoption, less documentation for beginners.
- **Choice:** Spring Boot (aligns with pedagogical and career objectives).

### Authentication

- **JWT + Spring Security:**
    - **Pros:** Stateless, scalable, easy integration.
    - **Cons:** Logout and refresh tokens require additional implementation.
- **OAuth 2.0:**
    - **Pros:** Supports SSO, robust for delegated authentication.
    - **Cons:** Unnecessary complexity for MVP.
- **Choice:** JWT (simplicity and scope adequacy).

### Frontend

- **React.js + Vite:**
    - **Pros:** Lightweight, fast startup.
    - **Cons:** Manual state management.
- **Angular:**
    - **Pros:** Structured, includes integrated tools (e.g., CLI, RxJS).
    - **Cons:** Steeper learning curve.
- **Vue.js:**
    - **Pros:** Simple, lightweight, good documentation.
    - **Cons:** Less adoption in corporate projects.
- **Choice:** Angular, as it is more commonly used with Java in corporate projects.

### Database

- **H2 (dev) + PostgreSQL (prod):**
    - **Pros:** H2 is lightweight for development; PostgreSQL is robust, scalable, widely used.
    - **Cons:** Migration configuration requires care.
- **MySQL:**
    - **Pros:** Popular, easy configuration.
    - **Cons:** Fewer advanced features than PostgreSQL.
- **Choice:** H2 and PostgreSQL (balance between rapid development and robustness in production).

### Consequences

### Positive

- **Scalability:** Stateless architecture and AWS deployment allow future growth.
- **Quality:** CI/CD from Sprint 1, with linting, tests, and static analysis, ensures robust code.
- **Learning:** Stack (Spring Boot, React, CI/CD) covers modern full-stack development fundamentals.
- **Documentation:** OpenAPI and ADRs facilitate maintenance and technical presentation.
- **Flexibility:** Clean Architecture and well-defined layers allow evolutions (Redis, PDF, Google Sheets) without major refactoring.

### Negative

- **Initial Complexity:** Configuring Spring Security, Flyway, and GitHub Actions may be challenging for beginners.
- **Maintenance:** Managing refresh tokens (JWT) and Flyway migrations requires attention.
- **Learning Curve:** Angular and E2E tests (Cypress) may require extra effort for less experienced teams.
- **Cost:** Deployment on AWS may incur additional costs (beyond pedagogical scope).

### Implementation Plan

1. **Sprint 1: Setup and Quality**
    - Configure Spring Boot project with H2, Flyway, and JPA entities.
    - Create GitHub Actions pipeline (Lint, Unit Tests, CodeQL, SonarQube).
    - Document ADRs and initial modeling (ER Diagram).
2. **Sprint 2: Authentication**
    - Implement /auth endpoints (register, login, me) with JWT.
    - Configure CORS and integration tests (MockMvc).
3. **Sprints 3–5: CRUD and Tests**
    - Develop Controllers, Services, and Repositories for Transactions, Budget, Envelopes, and Recurring Accounts.
    - Implement DTOs, validations, and global error handling (@ControllerAdvice).
    - Unit tests, integration tests (Testcontainers), and coverage ≥80%.
## 4. **Sprint 6: Front-end**

- **Angular Setup**: Configure the Angular project using the latest version compatible with Java 17. Utilize the Angular CLI for project scaffolding and development.
- **UI Development**: Develop user interfaces for login, CRUD operations, and dashboard using Angular components, services, and routing.
- **E2E Testing with Cypress**: Implement end-to-end tests for the front-end to ensure the application functions as expected across different user scenarios.

## 5. **Sprint 7: DevOps**

- **Docker Multi-stage Build**: Create a multi-stage Dockerfile to optimize the image size and build process. The first stage compiles the application, and the second stage packages it into a minimal runtime image.[Java Tech Blog](https://javanexus.com/blog/docker-compose-spring-boot-postgresql?utm_source=chatgpt.com)
- **Docker Compose**: Set up a `docker-compose.yml` file to define and run multi-container Docker applications, including services for the application, PostgreSQL database, and Redis cache.
- **GitHub Actions CI/CD Pipeline**: Configure GitHub Actions workflows for continuous integration and deployment. The pipeline should include steps for code checkout, JDK setup, Maven build, artifact archiving, and deployment to AWS EC2 instances using SCP and SSH.[Medium](https://medium.com/%40muhibgazi/spring-boot-application-deployment-to-aws-ec2-with-github-actions-731ce940a135?utm_source=chatgpt.com)
- **Health Checks with Spring Boot Actuator**: Integrate Spring Boot Actuator to provide production-ready features such as health checks, metrics, and application information. Configure health endpoints to monitor the application's status.

## 6. **Sprint 8: Optimizations**

- **Redis Caching**: Implement caching mechanisms using Redis to improve application performance by reducing a database load for frequently accessed data.
- **PDF Reports Generation**: Develop functionality to generate PDF reports for financial summaries, transaction histories, and other relevant data.
- **Google Sheets Integration**: Integrate with Google Sheets API to allow users to export data directly to spreadsheets for further analysis and reporting.
- **Automatic Deployment on Merge**: Configure GitHub Actions to trigger automatic deployment to AWS upon merging changes into the main branch, ensuring continuous delivery.
- **Final Documentation**: Complete the project documentation, including OpenAPI specifications for the API endpoints, a comprehensive README file, and a technical demo showcasing the application's features and architecture.

---
This ADR outlines the architectural decisions and implementation plan for the full-stack financial management application. The focus is on leveraging modern technologies and best practices to ensure scalability, maintainability, and a robust learning experience.