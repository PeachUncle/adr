# Role Type Classification System

## Status

Accepted

## Context

PalletCloud requires a flexible role-based access control (RBAC) system that can efficiently manage permissions across different categories of users. The platform serves multiple distinct user groups (customers, partners, system administrators) with vastly different permission requirements and operational contexts.

Previously, we included `organizationId` in the `Roles` table to allow organization-scoped role definitions. However, since every **customer** and **partner** belongs to a distinct organization, this design created unnecessary duplication and complexity. Instead, we removed the `organizationId` field from `Roles` and introduced a **`type` field** to classify roles as `CUSTOMER`, `PARTNER`, or `SYSTEM`.

## Problem Statement

Without clear role categorization, we face several challenges:

* **Role Explosion**: Hundreds of granular roles without organization
* **Assignment Complexity**: Difficulty mapping roles to specific user groups
* **Maintenance Burden**: Roles tied to organizations would need to be duplicated for each org
* **Security Risks**: Risk of partners/customers creating or assigning privileged roles
* **Query Performance**: Inefficient lookups across all roles without filtering

## Decision

### Role Type Classification

**Decision**: Introduce a `type` field in the Roles table to categorize roles into distinct types: `CUSTOMER`, `PARTNER`, and `SYSTEM`.

### Role Type Definitions

#### 1. CUSTOMER Type Roles

* **Purpose**: Roles for end-users who consume storage services.
* **Characteristics**:

  * Limited to booking and account management.
  * Self-service permissions only.
  * No administrative authority.

#### 2. PARTNER Type Roles

* **Purpose**: Roles for business partners who provide logistics/storage services.
* **Characteristics**:

  * Business-focused permissions.
  * Multi-user organizational support.
  * Facility and revenue management capabilities.

#### 3. SYSTEM Type Roles

* **Purpose**: Roles for platform-level administration.
* **Characteristics**:

  * Cross-organizational access.
  * System monitoring and configuration.
  * Super admin only.

### Predefined Roles & Governance

* **Roles are predefined** by the **Super Admin**.
* **Partners and Customers cannot create or modify roles**.
* Roles must be **used as-is** based on their type (`CUSTOMER`, `PARTNER`, `SYSTEM`).
* This ensures **consistency and security** across organizations.

### Assignment Rules

* **CUSTOMER users** → can only be assigned `CUSTOMER` roles.
* **PARTNER users** → can only be assigned `PARTNER` roles.
* **Super Admin (SYSTEM)** → manages and assigns `SYSTEM` roles.

## Benefits

### 1. Efficient Role Management

**Query Optimization**:

```sql
-- Fast role lookup by type
SELECT * FROM roles WHERE type = 'CUSTOMER';

-- Assignment validation
SELECT * FROM roles 
WHERE type = (SELECT type FROM users WHERE userId = 'abc-123');
```

### 2. Security Boundaries

* Prevents assigning **system roles** to partners/customers.
* Guarantees **clear separation** of business and system roles.
* Enforces **centralized control** over roles by Super Admin.

### 3. Scalability & Maintainability

* Roles grow within their categories instead of being organization-scoped.
* Cleaner, reusable role definitions across multiple tenants/partners.
* Easier to manage lifecycle of roles without duplication.

### 4. Developer & Ops Experience

* Clear intent from role type.
* Easier to test in isolation (`CUSTOMER` vs `PARTNER`).
* Self-documenting structure.

## Consequences

### Positive

* Stronger **security guarantees** with type-based restrictions.
* No role duplication per organization.
* Simplified role assignment model.
* Improved query performance with indexed `type`.
* Easier to scale as platform grows.

### Negative

* Migration effort to classify existing roles into types.
* One more dimension (role type) to consider during development.
* Teams must adapt to type-based role management.

---