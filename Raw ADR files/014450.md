# 1. Restaurant Users Management: Staff

## Status

Accepted

Date: 2025-11-02

## Context

Restaurants are tenant-scoped domains that require controlled access by staff. Each restaurant must have a 
guaranteed account that:

- Can perform privileged administrative operations for that specific restaurant
- Cannot be accidentally deleted, leaving the restaurant without access
- Is created as part of the restaurant onboarding flow

Beyond the primary administrative account, restaurants need additional staff accounts with narrower privileges that 
can be added and removed over time.

Without a clear model:

- Services risk inconsistent authorization and orphaned restaurants (no staff able to manage them)
- Deletion of critical users could interrupt operations
- Staff lifecycle (creation, deletion, role assignment) may diverge across services

## Decision

We will manage restaurant staff with two categories:

1) Staff Owner
   - One per restaurant, created atomically with the restaurant registration request.
   - Non-deletable via standard staff-management flows.
   - Holds the highest tenant-scoped privilege for that restaurant (e.g., role "staff-owner").
   - May update its own credentials and profile data.
   - May manage other staff within the same tenant (create, update, deactivate/reactivate, delete...).
   - Deletion or ownership transfer is only possible through a controlled, audited platform-admin process.

2) Secondary Staff User
   - Created by the Staff Owner.
   - Always scoped to the same tenant (restaurant) as the Staff Owner performing the action.
   - Can be updated and deleted by the Staff Owner.
   - Intended for operational roles (e.g., manager, cashier, chef) with least-privilege access.

Authorization and scoping principles:
- All staff access tokens include the tenant claim to enforce tenant isolation.
- Role checks are always combined with tenant checks.
- Only Staff Owner can create/delete other staff within the same tenant.
- Staff Owner cannot be deleted or demoted by tenant-local flows.

Atomic onboarding:
- Restaurant registration and Staff Owner creation occur in a single request and should be processed atomically 
  (all succeed or all fail).
- If the user-creation step fails after the restaurant is created, a compensating action must roll back the 
  restaurant record or disable it until the Staff Owner is successfully created.

Note on ADR scope:
> This ADR intentionally bundles staff categorization, lifecycle, and restaurant onboarding coupling for coherence. 
  If the process becomes more complex (e.g., ownership transfer workflows, invitation/acceptance flows, or 
  cross-tenant operations), separate ADRs can be added later to deepen those topics without changing this 
  high-level policy.

## Consequences

### Positive

- Guarantees each restaurant always has an administrative account.
- Clear tenant-scoped roles and lifecycle responsibilities.
- Reduced risk of cross-tenant access due to mandatory tenant claim.
- Consistent staff management flows across services.
- Simpler support and recovery processes with a well-defined Staff Owner.

### Negative

- Additional complexity in onboarding (atomic creation and compensation).
- Non-deletable Staff Owner increases the need for a dedicated ownership transfer process.
- Data model and APIs must enforce constraints (single Staff Owner per tenant, tenant match, role restrictions).

### Neutral

- Slight increase in token and payload size due to tenant and role data.
- Does not enforce hard isolation (separate databases); focuses on logical isolation and lifecycle rules.

## Implementation Notes

1) Roles and Claims
   - Staff tokens include:
     - sub: user identifier (subject)
     - tenant: restaurant identifier
     - role: staff role, including "staff-owner" for the Staff Owner and other roles for extra staff
   - Services must enforce:
     - RequireRole("staff-owner") (or equivalent) for staff administration endpoints
     - RequireTenantMatch() for all tenant-scoped operations

2) Onboarding Flow (Restaurant + Staff Owner)
   - Single API call to register a restaurant including the Staff Owner credentials/profile.
   - Transactional behavior:
     - Reserve/insert restaurant with pending status
     - Create Staff Owner in authentication/user store
     - On success, mark the restaurant active; on failure, roll back or mark a restaurant disabled and emit an alert
   - Idempotency key is required to avoid duplicate creation on retries.

3) Staff Lifecycle Endpoints (Tenant-Scoped)
   - Create Extra Staff: only Staff Owner can create; tenant set from caller’s token.
   - Update Staff: role changes restricted; cannot demote/delete Staff Owner; validate tenant match.
   - Delete Staff: allowed for extra staff only; tenant match required.

4) Data Model and Constraints
   - Staff record fields (indicative):
     - id, tenant, email, role, main (bool), active (bool), created_at, updated_at
   - Constraints/Indexes:
     - Unique (tenant, main=true) ensuring exactly one Staff Owner per tenant
     - Unique (tenant, email) for staff within a tenant
     - Index on (tenant, role) for admin queries
   - Staff Owner guardrails:
     - Reject delete for main=true
     - Reject role changes that remove owner privileges from Staff Owner without an explicit ownership-transfer process

5) Ownership Transfer (Out of Scope Workflow)
   - Future ADR may define a secure, audited transfer from Staff Owner to another staff user.
   - Until then, only platform admins can perform transfer using a privileged, audited path.

6) Deactivation and Restaurant Lifecycle
   - Deleting a restaurant:
     - Soft-delete a restaurant and automatically soft-delete all staff accounts including Staff Owner.
   - Restoring a restaurant is not supported.

7) Observability and Auditing
   - Log actor sub, tenant, target staff id, and action.
   - Emit audit events for staff creation, role change, deletion, and Staff Owner-related operations.
   - Avoid logging PII beyond opaque identifiers.

8) Error Handling
   - 403 Forbidden for tenant mismatches or insufficient role.
   - 409 Conflict for attempts to create a second Staff Owner or delete the Staff Owner.
   - 422 Unprocessable Entity for invalid role transitions or payloads.

## Related Documents

- [ADR-3 Authentication and Authorization](./../../global/0003-authentication-and-authorization.md)
- [ADR-4 User Types and Roles Structure](./../../global/0004-user-types-and-roles-structure.md)
- [ADR-3 Tenant’s Strategy](./../authentication/0003-tenants-strategy.md)
- [ADR-7 Domain-Centric User Management](./../../global/0007-domain-centric-user-management.md)

## Contributors

- Àlex Grau Roca
