# ADR 0003: Database Architecture for User and Profile Management

## Status
Accepted

## Date
2025-12-18

## Context
The authentication system needs to store user accounts and profile data for personalization. We need to decide how to structure the data model for users and their background information (software and hardware experience levels). The system uses Neon Postgres as the database provider and must integrate with better-auth's user management.

Key considerations include:
- Better-auth manages core user authentication data
- Need to store additional profile information for personalization
- Need to maintain data consistency and relationships
- Performance requirements for user lookups and profile access

## Decision
We will use a hybrid approach where better-auth manages the core user table, and we maintain a separate user_profiles table linked by foreign key. The architecture will be:

- Users table: Managed by better-auth with email, password hash, and authentication metadata
- User profiles table: Custom table with software_experience, hardware_experience, and background_preference fields
- Foreign key relationship: user_profiles.user_id references users.id with cascade delete
- Separate but related tables allowing better-auth to handle authentication while custom code handles profiles

## Alternatives Considered
- Store profile data in better-auth's user metadata: Rejected due to potential size limitations and query complexity
- Separate NoSQL storage for profiles: Rejected due to complexity and consistency concerns with existing Postgres setup
- Single combined table: Rejected as it would require customizing better-auth's core functionality
- JSON fields in user table: Rejected as it would complicate validation and querying

## Consequences
### Positive
- Clean separation between authentication and profile data
- Leverages better-auth's proven authentication handling
- Maintains referential integrity with foreign keys
- Allows for independent evolution of profile schema
- Supports efficient querying for personalization

### Negative
- Requires joins for authentication + profile operations
- More complex queries than single-table approach
- Additional maintenance for related table operations
- Potential for orphaned profile records if user deletion fails

## References
- specs/4-auth-profiling-integration/plan.md
- specs/4-auth-profiling-integration/research.md
- specs/4-auth-profiling-integration/data-model.md