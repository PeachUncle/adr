# 3. Tenant's Strategy

## Status

Accepted

Date: 2025-10-30

## Context

The platform is multi-tenant by nature: most entities (e.g., restaurants, menus, dishes, orders) are owned by a restaurant, and staff users are strictly associated with one restaurant. We must ensure that:
- Authorization decisions are scoped to the tenant that owns the resource.
- Cross-tenant access is prevented consistently across all services.
- Auditing, logging, and data storage preserve tenant isolation.

Without a uniform tenant strategy, each service would implement ad-hoc checks, increasing the risk of data leakage, confused-deputy problems, and authorization inconsistencies. We also need a generic, future-proof naming aligned with existing standard claims (e.g., sub).

## Decision

We will adopt a tenant claim named tenant in access tokens and enforce tenant scoping consistently across services and data stores.

1. Token Claim
   - Access tokens will include a tenant claim for tenant-scoped users (e.g., staff).
   - Claim semantics:
     - tenant: immutable tenant identifier at token-issuance time (e.g., the restaurant ID).
     - sub: user identifier (subject), as defined in the authentication strategy.
     - role: user role(s) used in authorization checks.
   - Example access token claims:
     ```json
     {
       "sub": "user-123",
       "tenant": "restaurant-456",
       "role": "staff:manager",
       "iss": "auth-service",
       "aud": "food-delivery-platform",
       "iat": 1730220000,
       "exp": 1730223600
     }
     ```

2. Authorization Invariants
   - Services must validate both:
     - Role authorization for the action being performed.
     - Tenant authorization: the caller’s tenant must match the target resource’s tenant.
   - When the request explicitly provides a restaurant or tenant identifier (e.g., path parameter), services must compare it to the token’s tenant.
   - When the request refers to a resource that implies a tenant (e.g., dish ID belongs to a restaurant), services must look up the resource’s tenant and compare it to the token’s tenant.

3. Claim Presence
   - Required for tenant-scoped users (e.g., staff).
   - Optional/omitted for non-tenant-scoped users (e.g., platform admins or global automation accounts). In those cases, services must explicitly allow cross-tenant actions only for authorized roles.

4. Data Model and Queries
   - Tenant-owned collections/tables must include a tenant field and all read/write queries must filter by tenant.
   - Unique constraints and indexes should be per-tenant (e.g., composite indexes with tenant as the leading key).
   - Background jobs operating on tenant data must require an explicit tenant value.

5. Token Freshness and Reassignment
   - If a user’s tenant assignment changes, new access tokens are required. To bound staleness, keep access-token TTL short for staff.
   - For immediate revocation or reassignment, support token invalidation (e.g., blacklist or assignment versioning) at the authentication layer.

6. Propagation
   - The tenant claim is extracted once at the edge (gateway/service middleware) and propagated via request context to downstream services.
   - No service may change the tenant in transit; only the authentication service may issue tokens with a tenant claim.

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive

- Uniform, explicit tenant scoping across all services.
- Reduced risk of cross-tenant data leakage and confused-deputy issues.
- Clear auditing and observability with tenant-correlated logs and traces.
- Predictable data-modeling patterns (per-tenant indexes, constraints).
- Easier to extend to other tenant-like domains due to generic claim naming.

### Negative

- Additional complexity in authorization (role + tenant checks).
- Need to update schemas and queries to include tenant filters and indexes.
- Potential token staleness when assignments change (mitigated with short TTL and revocation).
- Migration effort for existing data and APIs.

### Neutral

- No changes to refresh-token storage semantics; they continue to be stateful.
- Does not, by itself, provide hard isolation (e.g., separate databases per tenant); it standardizes logical isolation.
- Minor increase in token size.

## Implementation Notes

1. Token Issuance
   - On staff login/refresh, the authentication service includes tenant in the access token.
   - Access-token TTL for staff should be short (e.g., 5–15 minutes) to limit staleness.
   - Consider assignment versioning (e.g., a server-side version tied to the user-tenant relationship) to enable immediate revocation when necessary.

2. Service Enforcement
   - Introduce utilities/middleware to:
     - Extract sub, role, tenant from the token and attach them to the request context.
     - Provide helpers like RequireTenantMatch(ctx, targetTenant) and RequireRole(ctx, allowedRoles).
   - All write operations must either:
     - Receive the target tenant/restaurant explicitly and verify match; or
     - Derive the tenant from the referenced resource and verify match.
   - Read operations for tenant-owned data must always include tenant filters.

3. Data Modeling and Indexing
   - Add tenant field to tenant-owned entities.
   - Create composite indexes with tenant as the leading key (e.g., tenant + resource_id, tenant + slug).
   - Scope uniqueness to tenant where applicable.

4. Observability and Auditing
   - Include tenant in structured logs, traces, and audit records.
   - Avoid logging PII; log opaque identifiers only.

5. Backwards Compatibility and Migration
   - Rolling rollout:
     - Phase 1: Services accept tokens with or without tenant; if missing, derive tenant from the resource or reject non-derivable requests.
     - Phase 2: Enforce tenant presence for staff; fail requests lacking tenant when required.
   - Data backfill:
     - Populate tenant field on existing records based on known relationships.
     - Rebuild indexes to include tenant.
   - Update API contracts and client validations to include tenant-aware rules where the tenant is provided explicitly.

6. Service-to-Service Calls
   - Downstream calls must carry the original caller’s context, including tenant.
   - Internal services must not widen tenant scope; privilege elevation requires explicit, audited mechanisms.

7. Error Handling
   - Use clear errors for tenant mismatches (e.g., 403 Forbidden) and invalid/missing tenant claims (e.g., 401/403 depending on context).

## Related Documents

- [ADR-1 Authentication Strategy](./0001-authentication-strategy.md)
- [ADR-2 Password Security](./0002-password-security.md)
- [ADR-4 User Types and Roles Structure](./../../global/0004-user-types-and-roles-structure.md)
- API Security Standards (to be created)
- Data Partitioning and Indexing Guidelines (to be created)
- Multi-tenant Logging and Auditing Guidelines (to be created)

## Contributors

- Àlex Grau Roca
