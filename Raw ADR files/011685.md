# 6. Use the Delius Authorisation Model for Client Users

Date: 2021-02-26

## Status

Accepted

## Context

- National Delius uses a domain-specific, granular authorisation model for
  granting access to data.
- This model relies on the existence of an nDelius user record.
- Not all end-users of the Delius API will have nDelius user records.
- There are classes of user that will never have nDelius user records, such as
  users from intervention providers external to the MOJ.

### Virtual Private Database (VPD)

- nDelius users can only view details of Service Users within the datasets
  (Providers) they have been granted access to.
- This mechanism relies partially on setting the nDelius username in the VPD
  Context on the Oracle Database connection.

### Limited Access Offenders (LAO)

- Service Users can be marked as 'Restricted' in nDelius, so that only a subset of
  users can access their details. For example in high profile cases.
- nDelius users can be marked as 'Excluded' from accessing specific Service Users.
  For example if the user is a relative or victim of the Service User.
- Restriction/Exclusion records link a Service User record to the nDelius user
  record in the Delius database.

### Role-Based Access Control (RBAC)

- Each nDelius user has a set of roles containing specific business interactions
  they can perform, and at what level.
- Authorisation and auditing is performed using these business interaction codes.
- The role level defines when users are allowed to perform the associated
  interactions based on their engagement with the Service User:
    - Level 0 = Allowed regardless of offender or component
    - Level 1 = Allowed if the user is the Current Offender Manager
    - Level 2 = Allowed if the user is a Previous Offender Manager
    - Level 3 = Allowed if the user is the sub-component manager (e.g. NSI
      Manager, Event Manager etc)
- Roles are assigned to the nDelius user record in the Delius LDAP directory.

## Decision

- We will create a Delius user record for any client that does not act on behalf
  of an nDelius user.
- This "client user" will be linked to the authenticated client with a custom
  claim in HMPPS Auth.
- The Delius API will honor VPD restrictions by setting the client user ID on the
  Delius database connection.
- The Delius API will implement RBAC by allowing the usual Delius roles to be
  assigned to this client user, and using them to authorise requests.
- The Delius API will not implement LAO processing initially, with the intention
  being that this will be moved to an external service in the future. See 

## Consequences

- The Delius API can apply a consistent set of authorisation rules to both clients
  and nDelius users.
- Any client audit records will be linked to the client user, indicating to an
  auditor that they may need to check additional audit records in the calling
  service.
- We may need to come up with an automated process for creating client users in
  Delius.
- For any clients that represent non-nDelius users (e.g. the interventions
  service), roles and dataset restrictions can only be applied to the entire
  client, not to individual users.
- It will not be possible to perform LAO exclusions or restrictions for individual
  users.