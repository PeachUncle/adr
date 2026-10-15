# ADR-002: 3-Tier Architecture Design

**Date**: 2025-07-17
**Status**: Accepted
**Deciders**: Architecture Team

## Context
We need to design a maintainable, scalable architecture for the trailer rental platform that separates concerns and allows for independent development and deployment.

## Decision
We will implement a 3-tier architecture with the following layers:

### 1. Presentation Layer (Frontend)
- **Angular SPA**: Single-page application for user interface
- **Responsibilities**: 
  - User interaction and experience
  - Data presentation and validation
  - Authentication state management
  - API communication

### 2. Business Logic Layer (Backend API)
- **ASP.NET Core Web API**: RESTful API services
- **Responsibilities**:
  - Business rule enforcement
  - Data validation and processing
  - Authentication and authorization
  - External service integration

### 3. Data Access Layer (Database)
- **Entity Framework Core**: ORM for data access
- **PostgreSQL**: Persistent data storage
- **Responsibilities**:
  - Data persistence and retrieval
  - Data integrity constraints
  - Database schema management
  - Query optimization

## Architecture Diagram
`
    HTTP/REST        EF Core    
   Angular SPA     ASP.NET Core      PostgreSQL    
  (Presentation)                  (Business Logic)                 (Data Access)  
                               
`

## Implementation Details

### Frontend Structure
`
src/frontend/
 src/app/
    core/           # Singleton services, guards
    shared/         # Reusable components
    features/       # Feature modules
    layouts/        # Page layouts
`

### Backend Structure
`
src/backend/
 API/                # Web API controllers
 Business/           # Business logic services
 Data/               # Data access layer
 Models/             # Domain models and DTOs
 Infrastructure/     # Cross-cutting concerns
`

## Consequences

### Positive
- Clear separation of concerns
- Independent layer development and testing
- Scalable and maintainable codebase
- Technology flexibility within layers
- Easier troubleshooting and debugging

### Negative
- Increased complexity compared to monolithic approach
- Potential performance overhead from layer communication
- More initial setup and configuration required

## Security Considerations
- **Authentication**: JWT tokens handled at API layer
- **Authorization**: Role-based access control in business layer
- **Data Protection**: Input validation at both frontend and backend
- **API Security**: CORS, rate limiting, HTTPS enforcement
