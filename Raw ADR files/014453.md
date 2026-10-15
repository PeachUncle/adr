# 4. User Types and Roles Structure

## Status

Accepted

Date: 2025-06-18

## Context

The food delivery platform requires different types of users with distinct responsibilities and access levels. We need to:

- Define clear user types and their associated roles
- Establish consistent access control across all services
- Support different authentication flows for each user type
- Enable future extensibility for new roles or user types
- Ensure security is appropriate to each user type's responsibilities

## Decision

We will implement three primary user types, each with specific roles and permissions:

1. **Customers**
    - Primary end-users of the platform
    - Role: `customer`
    - Capabilities:
        - Browse restaurants and menus
        - Place and track orders
        - Manage delivery addresses
        - Handle payment methods
    - Authentication: Email/password

2. **Restaurant Staff**
    - Restaurant management personnel
    - Role: `staff`
    - Capabilities:
        - Manage restaurant profile
        - Update menus and prices
        - Handle incoming orders
        - View order history
    - Authentication: Email/password (future: MFA)
    - Additional security considerations:
        - Restaurant-specific access control
        - Audit logging of critical operations

3. **Couriers**
    - Delivery personnel
    - Role: `courier`
    - Capabilities:
        - View assigned deliveries
        - Update delivery status
        - Access delivery route information
        - Mark orders as delivered
    - Authentication: Email/password
    - Additional considerations:
        - Location tracking permissions
        - Real-time status updates

## Consequences

### Positive

- Clear separation of user responsibilities
- Simplified permission management per user type
- Enhanced security through role isolation
- Easy to extend for new user types
- Consistent access control across services

### Negative

- More complex authentication flows
- Additional testing requirements per user type
- Need for role-specific API endpoints
- Increased complexity in token management

### Neutral

- Each service must implement role-based access control
- Need for comprehensive user management interfaces
- Regular security audits per user type

## Implementation Notes

**API Endpoints Structure Example**

- `/v1.0/customers/*` for customer operations
- `/v1.0/staff/*` for restaurant staff
- `/v1.0/couriers/*` for delivery personnel

## Related Documents

- [ADR-3 Authentication and Authorization](./0003-authentication-and-authorization.md)
- Restaurant Service Design Document (to be created)
- Delivery Service Design Document (to be created)
- Security Standards Document (to be created)

## Contributors

- Àlex Grau Roca