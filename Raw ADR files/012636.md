# ADR-0013: Authentication Strategy for Multi-Tenant SaaS and Open Source

## Status
Proposed

## Context
Nucleus may evolve into both:
1. **Open Source Project**: Self-hosted instances with minimal authentication
2. **Multi-Tenant SaaS**: Cloud-hosted service with subscription management, tenant isolation, and advanced user management

The authentication system needs to support both scenarios without requiring a complete rewrite.

## Decision
**Open Source First, SaaS-Ready Architecture**

We will implement authentication with an open-source-first approach that can be extended for SaaS later:

### Phase 1: Open Source Foundation
- **Simple JWT Authentication**: Basic user registration/login with JWT tokens
- **Role-Based Access Control**: Admin, Reviewer, Guest roles
- **Local User Management**: User data stored in local PostgreSQL database
- **No Tenant Isolation**: Single-tenant architecture for self-hosted instances
- **Minimal Dependencies**: Standard ASP.NET Core Identity or custom implementation

### Phase 2: SaaS Extension (Future)
- **Tenant Isolation**: Add tenant/organization entities and multi-tenancy
- **Subscription Management**: Integrate with billing systems (Stripe, etc.)
- **Advanced User Management**: Invitations, team management, SSO
- **Cloud Identity Providers**: OAuth2/OIDC integration (Google, GitHub, etc.)

## Implementation Strategy

### Domain Model Design
```csharp
// Phase 1: Open Source
public class User : BaseEntity
{
    public string Email { get; set; }
    public string Username { get; set; }
    public string PasswordHash { get; set; }
    public UserRole Role { get; set; }
    public bool IsActive { get; set; }
}

// Phase 2: SaaS Extension (Future)
public class Tenant : BaseEntity
{
    public string Name { get; set; }
    public string Subdomain { get; set; }
    public SubscriptionPlan Plan { get; set; }
    public ICollection<User> Users { get; set; }
}

public class User : BaseEntity
{
    // ... existing properties
    public Guid? TenantId { get; set; }  // Null for open source
    public Tenant Tenant { get; set; }
}
```

### Authentication Flow
1. **Open Source**: Local JWT authentication with role-based access
2. **SaaS**: Tenant-aware authentication with subscription validation

### Database Schema
- Start with single-tenant tables
- Future migration to add tenant_id columns and tenant table
- Use conditional compilation or feature flags for SaaS features

## Consequences

### Positive
- **Open Source Friendly**: Simple setup for self-hosted instances
- **Incremental Migration**: Can add SaaS features without breaking existing deployments
- **Flexible Architecture**: Domain model supports both scenarios
- **Community Adoption**: Lower barrier to entry for open source users

### Negative
- **Initial Complexity**: Need to design for future extensibility
- **Migration Effort**: Future transition to multi-tenant requires data migration
- **Feature Parity**: SaaS features may not be available in open source version

### Risks
- **Over-Engineering**: Building SaaS features before they're needed
- **Migration Complexity**: Moving from single to multi-tenant can be complex
- **Maintenance Burden**: Supporting both deployment models

## Alternatives Considered

### 1. SaaS-First Architecture
- **Pros**: Built for scale from day one
- **Cons**: Overwhelming for open source users, higher complexity

### 2. Separate Codebases
- **Pros**: Clean separation of concerns
- **Cons**: Maintenance burden, code duplication

### 3. Plugin Architecture
- **Pros**: Flexible, modular approach
- **Cons**: Complex to implement, potential performance overhead

## Implementation Plan

### Phase 1: Open Source Authentication (Current)
1. Implement basic JWT authentication
2. Create User and Role entities
3. Add authentication middleware
4. Protect API endpoints
5. Integrate with admin dashboard

### Phase 2: SaaS Preparation (Future)
1. Add tenant abstraction layer
2. Implement tenant isolation
3. Add subscription management
4. Integrate cloud identity providers

## References
- [ADR-0001: Clean Architecture](../adr/ADR-0001-clean-architecture.md)
- [ADR-0002: ASP.NET Core](../adr/ADR-0002-aspnet-core.md)
- [GitHub Issue #8: Authentication System](../github-issues/templates/issue-8-authentication-system.md) 