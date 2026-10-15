# ADR-002: Single-Tenant Architecture Strategy

## Status

Accepted

## Context

We need to define the multi-tenancy strategy for the platform to determine:

- How to isolate data and access between different users
- The complexity of user management and authorization systems
- Database design and data partitioning strategies
- Billing and resource allocation approaches
- Scaling and operational considerations

The platform serves as a personal portfolio with potential for future collaborators, requiring clear tenant boundaries while maintaining simplicity.

## Decision

We will implement a **Single-Tenant Architecture** where **each user is their own tenant**:

- **No organization or team concepts** initially
- **User-level data isolation** for all applications and resources
- **Individual user permissions** without complex role hierarchies
- **Per-user resource allocation** and access controls
- **No cross-tenant data sharing** mechanisms needed

## Rationale

- **Simplicity**: Eliminates complex multi-tenant data partitioning and isolation concerns
- **Security**: Natural isolation boundary prevents accidental data leaks between users
- **Development Velocity**: Reduces complexity in data access patterns and authorization logic
- **Scale Appropriateness**: Matches the personal portfolio scale and expected user count
- **Clear Ownership**: Each user has complete control over their data and applications
- **Privacy**: Natural privacy boundaries align with GDPR and data protection requirements

## Implementation Strategy

### Database Design

- **User-scoped tables**: All data tables include user_id as a primary partitioning key
- **Row-level security**: Database policies enforce user-level access controls
- **Separate schemas**: Consider per-user schemas for complete isolation if needed

### Authorization Model

- **Simple RBAC**: User is admin of their own tenant space
- **Resource ownership**: All resources are owned by and accessible only to the creating user
- **API design**: All API endpoints include user context from authentication

### Data Isolation

- **Application level**: All queries filtered by authenticated user ID
- **Event sourcing**: Events are user-scoped with no cross-user event streams
- **Projections**: Read models are user-specific and isolated

## Architectural Consequences

### Positive

- **Simplified Security Model**: No complex tenant-aware authorization logic needed
- **Development Speed**: Faster feature development without multi-tenant complexity
- **Data Privacy**: Natural isolation supports compliance requirements
- **Testing**: Easier to test without complex tenant scenarios
- **Backup/Recovery**: User-specific backup and recovery strategies possible

### Negative

- **Limited Collaboration**: No built-in team or organization features
- **Resource Efficiency**: May not optimize shared resources as effectively
- **Feature Limitations**: Some enterprise features (team management, etc.) not supported
- **Future Migration**: Moving to multi-tenant later would require significant refactoring

## Cross-Tenant Scenarios

**Explicitly NOT supported in this architecture:**

- User groups or teams
- Shared projects or resources
- Cross-user data access
- Organization-level administration
- Resource sharing between users

## Security Implications

- **Authentication boundary**: Each user authenticates independently
- **Authorization boundary**: User can only access their own resources
- **Data isolation**: Complete separation of user data at all levels
- **Audit logging**: Per-user audit trails with no cross-contamination

## Future Evolution Path

If the platform needs to support teams or organizations in the future:

1. **Additive Approach**: Add organization layer on top of existing user-tenant model
2. **Migration Strategy**: Users become organization owners, maintaining backward compatibility
3. **Hybrid Model**: Support both individual users and organization users
4. **Data Migration**: Existing user data remains isolated during transition

## Alternatives Considered

- **Organization-based Multi-tenancy**: Too complex for current needs and scale
- **Shared Multi-tenancy**: Inappropriate for personal portfolio use case
- **Hierarchical Tenancy**: Adds complexity without clear benefit at current scale
- **No Tenancy (Single User)**: Too limiting for future growth potential

## Implementation Guidelines

- **Database queries**: Always include user context in WHERE clauses
- **API design**: Include user ID in all data operations
- **Event sourcing**: User ID as part of aggregate identity
- **Caching**: User-scoped cache keys to prevent data leaks
- **Monitoring**: Per-user metrics and alerting where appropriate

## Success Criteria

- **Zero cross-user data access**: No user can access another user's data
- **Simple permission model**: Single role (owner) per user tenant
- **Fast development**: New features can be developed without complex tenant logic
- **Compliance ready**: Data isolation supports privacy regulation compliance
