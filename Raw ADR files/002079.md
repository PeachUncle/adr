# ADR: Todo Web Application Architecture

## Context

For the Todo Web Application, we needed to make several key architectural decisions regarding technology stack, authentication, data management, and security. This ADR documents the decisions made and the rationale behind them.

## Decisions

### 1. Technology Stack
- **Frontend**: Next.js 16+ with TypeScript and Tailwind CSS
- **Backend**: Python FastAPI with SQLModel ORM
- **Database**: PostgreSQL
- **Rationale**: Next.js provides excellent developer experience and performance, FastAPI offers automatic API documentation and type validation, and PostgreSQL is a robust, scalable database choice.

### 2. Authentication Approach
- **Decision**: Custom JWT-based authentication instead of Better Auth (as initially specified)
- **Rationale**: While the spec mentioned Better Auth, implementing a custom JWT solution allowed for better control over token expiration (7 days), user data isolation, and integration with the SQLModel-based user model.

### 3. Data Isolation Strategy
- **Decision**: User ID validation in every endpoint to ensure data isolation
- **Rationale**: Each API call validates that the user can only access their own data by checking the user ID in the JWT token against the requested resource.

### 4. API Design
- **Decision**: RESTful API with user-specific endpoints (`/api/users/{user_id}/tasks`)
- **Rationale**: This design makes data isolation explicit in the API contract and provides clear boundaries between user data.

### 5. Frontend State Management
- **Decision**: Custom React Context for authentication state management
- **Rationale**: For this application size, a custom context provides sufficient functionality without the complexity of additional state management libraries.

## Consequences

### Positive
- Clear separation of concerns between frontend and backend
- Secure data isolation between users
- Scalable architecture that can handle multiple users
- Comprehensive API documentation via FastAPI
- Type safety across the stack

### Negative
- Custom authentication requires more implementation work than using a ready-made solution
- Additional complexity in ensuring all endpoints properly validate user permissions