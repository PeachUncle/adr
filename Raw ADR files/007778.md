# ADR: Artist Creation Process for Copper Print Gallery

## Date
2024-07-26

## Status
Proposed

## Context
The Copper Print Gallery system requires a secure method for creating artist accounts. Initially, the system is intended for use by a single artist, but we want to maintain flexibility for potential future expansion. We need to ensure that artist creation is a controlled process while avoiding unnecessary restrictions on the system's scalability.

## Decision
We will implement a manual, admin-controlled process for artist creation with the following key features:

1. A secure admin interface or script for creating artist accounts.
2. Integration with Keycloak for authentication and role-based access control.
3. A database schema that supports multiple artists without enforcing a strict single-artist policy.
4. A standardized process for artist account creation, including both database and Keycloak entries.

The artist creation process will involve:
- Admin-only access to the creation interface
- Creation of an artist record in the database
- Creation of a corresponding user in Keycloak with a specific 'gallery_artist' role
- Generation of a temporary password and forced password change on first login
- Requirement for the artist to complete their profile on first system access

## Consequences

### Positive
- Maintains security by restricting artist creation to authorized administrators
- Provides flexibility to add multiple artists in the future if needed
- Ensures consistency between the database and Keycloak for artist accounts
- Establishes a clear, repeatable process for artist onboarding
- Simplifies the data model by avoiding unnecessary constraints

### Negative
- Requires manual intervention for artist creation, which may be less convenient than self-registration
- Necessitates careful management of admin access to prevent unauthorized artist creation

### Risks
- If admin credentials are compromised, unauthorized artists could potentially be added to the system

## Implementation Notes
- The admin interface for artist creation should be separate from the main application and secured behind strong authentication.
- Regular audits of artist accounts should be conducted to ensure system integrity.
- The process should be documented clearly for system administrators.

## Related Decisions
- Choice of Keycloak as the authentication and authorization system
- Database schema design for the ARTIST table

## References
- Keycloak documentation: [link to Keycloak docs]
- System security requirements specification: [link to relevant document]
