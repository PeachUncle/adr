# ADR-0014: Authentication System Implementation

## Status
Accepted

## Context
The Nucleus project requires a secure authentication and authorization system to protect API endpoints and provide role-based access control for the admin dashboard. This system must integrate seamlessly with the existing ASP.NET Core backend and Vue.js frontend.

## Decision
Implement a comprehensive JWT-based authentication system with the following components:

### Backend Implementation
- **JWT Token Service**: Custom implementation using System.IdentityModel.Tokens.Jwt
- **Password Hashing**: BCrypt implementation for secure password storage
- **Role-based Access Control**: Admin, Reviewer, and Guest roles with authorization attributes
- **User Management**: Entity Framework entities with tenant support
- **Data Seeding**: Automatic creation of default admin user

### Frontend Integration
- **Vue.js Authentication Store**: Pinia store for managing authentication state
- **JWT Token Management**: Automatic token storage and refresh handling
- **Route Protection**: Vue Router guards for protected routes
- **Login Interface**: Modern login form with validation

### Security Features
- **Environment-based Configuration**: JWT secret key via environment variables
- **Token Expiration**: Configurable access and refresh token lifetimes
- **Password Validation**: Strong password requirements with FluentValidation
- **Audit Logging**: Comprehensive logging of authentication events

## Consequences

### Positive
- **Secure Authentication**: JWT tokens provide stateless, secure authentication
- **Role-based Access**: Granular control over user permissions
- **Scalable Architecture**: Clean separation of concerns with proper dependency injection
- **Frontend Integration**: Seamless integration with Vue.js and Pinia
- **Production Ready**: Environment-based configuration for deployment

### Negative
- **Complexity**: JWT implementation requires careful token management
- **Security Responsibility**: Proper secret management is critical
- **Token Storage**: Frontend must securely store and manage tokens

### Neutral
- **Stateless Design**: JWT tokens eliminate server-side session storage
- **Cross-platform**: JWT tokens work across different platforms and services

## Implementation Details

### Backend Services
```csharp
// Core authentication services
IAuthenticationService - Main authentication logic
IJwtTokenService - JWT token generation and validation
IPasswordHasher - Password hashing and verification
IDataSeeder - Database seeding for default users
```

### Frontend Store
```javascript
// Pinia authentication store
auth.js - Manages login state, tokens, and user information
```

### API Endpoints
```
POST /api/auth/login - User authentication
POST /api/auth/register - User registration (future)
GET /api/auth/profile - Get current user profile
POST /api/auth/refresh - Refresh access token
```

### Security Configuration
- JWT secret key stored in environment variables
- BCrypt work factor of 12 for password hashing
- Token expiration: 15 minutes (access), 7 days (refresh)
- CORS configuration for frontend integration

## Related Decisions
- ADR-0002: ASP.NET Core Architecture
- ADR-0009: Vue.js Admin Dashboard
- ADR-0011: Git Workflow

## References
- [Issue #8: Authentication System](../github-issues/templates/issue-124-authentication-system.md)
- [JWT Authentication Documentation](https://jwt.io/)
- [BCrypt Security](https://en.wikipedia.org/wiki/Bcrypt) 