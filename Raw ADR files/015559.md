# 📋 ADR-005: Multi-tenant Architecture

## Status

Accepted

## Context

As Reportly evolved, we needed to support multiple organizations and teams using the platform, each with their own isolated data and user management. We needed to design a multi-tenant architecture that would:

1. Provide data isolation between different organizations
2. Allow users to belong to multiple workspaces
3. Support efficient access control and permissions
4. Scale with growing numbers of organizations and workspaces
5. Maintain performance as data volumes increase

## Decision

We decided to implement a multi-tenant architecture with Organizations and Workspaces as the primary organizational units.

## Rationale

The Organization and Workspace model provides several advantages:

1. **Hierarchical Structure**: Organizations contain Workspaces, providing a natural hierarchy for data organization.
2. **Data Isolation**: Each Workspace contains its own reports, comments, and other data, ensuring isolation between tenants.
3. **User Membership**: Users can belong to multiple Workspaces within an Organization, supporting flexible team structures.
4. **Access Control**: Permissions can be managed at both Organization and Workspace levels.
5. **Scalability**: The model scales horizontally as new Organizations and Workspaces are added.
6. **Familiar Model**: The concept of Organizations and Workspaces is familiar to users from other SaaS applications.

## Consequences

### Positive

- Clear separation of data between different organizations
- Flexible user membership across workspaces
- Granular access control at multiple levels
- Ability to implement workspace-specific features and settings
- Scalable architecture for growing user base

### Negative

- Increased complexity in data models and queries
- Need for additional access control checks in all operations
- More complex user interface to manage workspace switching
- Potential performance impact from additional filtering
- Migration challenges for existing data

## Implementation Details

1. **Data Models**:
   - Organization model with name, owner, and settings
   - Workspace model with name, organization reference, and member list
   - User model with references to organizations and workspaces
   - All content models (reports, comments) include workspace and organization references

2. **Access Control**:
   - Workspace-level access checks for all data operations
   - Organization-level settings and permissions
   - Active workspace selection and persistence

3. **User Experience**:
   - Workspace switcher in the UI
   - Organization and workspace management interfaces
   - Clear indication of current workspace context

## Alternatives Considered

### Single-tenant Architecture

A single-tenant architecture would be simpler but wouldn't provide the isolation and scalability needed for multiple organizations.

### Organization-only Model

Using only Organizations without Workspaces would be simpler but wouldn't provide the flexibility for teams within an organization to have separate spaces.

### Group-based Model

A flat group structure would be simpler but wouldn't provide the hierarchical organization needed for larger teams.

## References

- [Multi-tenant Data Architecture](https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant/considerations/data-considerations)
- [SaaS Multi-tenancy Models](https://www.mongodb.com/blog/post/building-with-patterns-the-document-versioning-pattern)
- [Workspace Model in Popular SaaS Applications](https://slack.engineering/building-hybrid-applications-with-slack/)
