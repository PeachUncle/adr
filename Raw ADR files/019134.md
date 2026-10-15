See the [technical decision index for all ADRs](../technical-decisions.md)

# ADR-004: Database Schema Design for Multi-Tenancy

**Date**: September 3, 2025  
**Status**: Accepted  
**Context**: Design database schema that supports individual users initially but can evolve to household sharing.

## Decision

**Strategy**: Single database with row-level security and foreign key relationships  
**User Model**: Individual users with optional household relationships  
**Data Isolation**: User ID and Household ID based access control  
**Future-Proofing**: Schema designed for multi-tenant evolution

## Schema Design

Authoritative schema definition (DDL, indexes, triggers, and RLS policies) is maintained in the [database schema spec](../implementation-specs/database-schema.md). Use that as the source of truth.

## Row Level Security

See the [database schema spec](../implementation-specs/database-schema.md) for RLS policies and implementation details.

## Rationale

### Single Database Benefits

- **Simplicity**: Easier to manage than multiple databases
- **Consistency**: ACID transactions across user data
- **Performance**: Efficient joins and queries
- **Cost**: Lower operational overhead

### Row Level Security

- **Data Isolation**: Automatic enforcement of access controls
- **Security**: Database-level protection against data leaks
- **Flexibility**: Policy-based access control
- **Audit**: Built-in access logging

### Evolution Strategy

- **Phase 1**: Individual users only (household_id NULL)
- **Phase 2**: Optional location sharing
- **Phase 3**: Full household collaboration

## Alternatives Considered

- **Database-per-User**: Rejected due to operational complexity and cost
- **Shared Schema**: Rejected due to data isolation concerns
- **Application-Level Filtering**: Rejected due to security risks

## Consequences

### Positive

- Clean evolution path from individual to household usage
- Strong data isolation with database-level enforcement
- Efficient queries with proper indexing
- Simplified backup and maintenance

### Negative

- PostgreSQL RLS learning curve
- Potential performance impact with complex policies
- Migration complexity for existing users

## Implementation Notes

- Implement proper indexing strategy for RLS policies
- Set up database migrations for schema evolution
- Test RLS policies thoroughly with different user scenarios
- Monitor query performance with RLS enabled
- Plan migration strategy for converting individual users to households
