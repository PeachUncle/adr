# 3. Tenant's Strategy

## Status

Accepted

Date: 2025-10-30

## Context

The system is multi-tenant where different organizations (restaurants, restaurant chains, delivery companies) 
operate independently within the same infrastructure. We need a strategy to:

- Isolate data and operations between different tenants
- Associate users (staff, couriers...) with their respective organizations
- Ensure proper authorization and data access control
- Support both single-tenant restaurants and multi-location chains
- Enable efficient querying and data filtering by tenant

Current challenges:

- Need for clear tenant identification across services
- Ensuring data isolation without performance degradation
- Supporting different tenant types (restaurants, delivery companies)
- Maintaining scalability as the number of tenants grows
- Preventing cross-tenant data access vulnerabilities

## Decision

We will implement a tenant identification strategy using a `tenant` field containing the tenant ID in the JWT:

1. **Tenant Identification**
    - Every tenant-scoped entity includes a `tenant` field with the tenant ID
    - Applied to tenant users, currently only applied to staff

2. **Token Claims**
    - Staff access tokens include tenant information:
      ```json
      {
        "sub": "user-id",
        "exp": 1234567890,
        "iat": 1234567890,
        "role": "staff",
        "tenant": "tenant-id"
      }
      ```
    - Non-tenant tokens do not include tenant field

3. **Data Access Patterns**
    - All queries for tenant-scoped resources must filter by tenant ID
    - Database indexes include tenant field for efficient querying
    - Tenant validation occurs at the authentication layer
    - API endpoints automatically scope requests to the authenticated user's tenant

4. **Staff Tenant Entity**. The tenant entity for staff users is the Restaurant entity. So, the tenant will contain 
   the Restaurant ID.

## Consequences

### Positive

- Clear data isolation between tenants
- Simple and explicit tenant identification
- Efficient database queries with proper indexing
- Protection against cross-tenant data access
- Easy to audit and trace data by tenant
- Supports multi-tenant architecture scalability

### Negative

- Additional field in some domain entities
- Need to remember to filter by tenant in all necessary queries
- Slightly increased token size for staff
- Requires careful testing to prevent tenant leakage

### Neutral

- Regular security audits for tenant isolation
- Monitoring required for cross-tenant access attempts
- Need for tenant management interfaces
- Documentation requirements for tenant boundaries

## Implementation Notes

1. **Entity Structure**
   ```go
   type Staff struct {
       ID           string `json:"id" bson:"_id"`
       RestaurantID string `json:"restaurant_id" bson:"restaurant_id"`
       Email        string `json:"email" bson:"email"`
       // other fields...
   }
   ```

2. **Query Pattern**
   ```go
   // Always include tenant filter for scoped resources
   filter := bson.M{
       "restaurant_id": restaurantID,
       "email": email,
   }
   ```

3. **Middleware Validation**
   ```
   1. Extract JWT from request
   2. Validate tenant claim exists (for staff)
   3. Inject tenant ID into request context
   ```

4. **Database Indexes**
   ```
   - Compound index: (restaurant_id, email) for user lookups
   - Compound index: (restaurant_id, created_at) for list queries
   - Tenant field included in all tenant-scoped queries
   ```

5. **Security Considerations**
    - Always validate tenant ownership before operations
    - Prevent tenant ID manipulation in requests
    - Log cross-tenant access attempts
    - Use middleware to enforce tenant scoping
    - Unit tests must verify tenant isolation

## Related Documents

- [ADR-1 Authentication Strategy](./0001-authentication-strategy.md)
- [ADR-4 User Types and Roles Structure](./../../global/0004-user-types-and-roles-structure.md)

## Contributors

- Àlex Grau Roca
