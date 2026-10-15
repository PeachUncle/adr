# ADR-0011: Access Control

## Status

Accepted

Date of decision: 2024-08-23

## Context and Problem Statement

The Private Rented Sector Database has several different user groups, each with different permissions. Authentication of
users has already been covered in ADR-0007 - User Authentication, Registration, and ID Verification; this ADR addresses
the authorisation mechanism.

The web application will be built with Spring Boot (see ADR-0005 - Server-side Language & Framework), so using
role-based access control (RBAC) with Spring Security is the natural choice – but how should we determine which role(s)
a given user holds?

## Considered Options

* Roles Determined Via Database
* Roles Determined Via OIDC Claims
* Roles Determined Via Authorisation Service

## Decision Outcome

Roles Determined Via Database, because it is by far the simplest option.

## Pros and Cons of the Options

### Roles Determined Via Database

User details are stored in the application database, including the identifier used for that user in the authentication
provider (e.g. subject identifier as used by One Login). These details can be used to determine the user’s role(s) (e.g.
their identifier is stored in certain tables for different user types, or a user type column associated with the
identifier).

* Good, because there is minimal extra effort needed to associate an external user ID with user data that will otherwise
  be needed in the database.
* Good, because it is a simple, well-established pattern.
* Bad, because either the database must be queried on every request, or the user’s role(s) must be cached in session
  storage and this cache must be destroyed before a role change is picked up.

### Roles Determined Via OIDC Claims

Some OIDC providers (e.g. full-featured platforms like Auth0) allow users to be associated with custom claims. This can
be used to include a “roles” claim in returned tokens, with specified values for each user.

* Bad, because only Entra ID, not One Login, supports providing such role information in the tokens it issues.
* Good, because it is simple to determine roles at point of login.
* Bad, because role changes are not picked up without the user reauthenticating.

### Roles Determined Via Authorisation Service

Dedicated services, such as Keycloak, can be used to store role information for users, and can provide a UI for
management of this information.

* Bad, because this involves significant extra complexity (a whole extra application) to manage this simple data.
* Bad, because the service must be queried on every request, or the roles cached, the same as when using a database.
* Neutral, because some super-admin facing UI would be provided by the product – but user facing admin UI (e.g. an LA
  admin managing their users) would still need to be bespoke.

## More Information

* [One Login Claims technical documentation](https://docs.sign-in.service.gov.uk/before-integrating/choose-which-user-attributes-your-service-can-request/#choose-which-claims-your-service-can-request)
* [Keycloak authorisation services](https://www.keycloak.org/docs/latest/authorization_services/index.html) 