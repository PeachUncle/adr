# 4. Rest API Resource Naming and HTTP Methods

## Status

Accepted

Date: 2025-06-19

## Context

As our API ecosystem grows, we need consistent conventions for resource naming and HTTP method usage to ensure:

- Predictable and intuitive API design across all services
- Proper application of REST principles
- Improved developer experience when working with multiple APIs
- Easier API discoverability
- Consistent behavior across all microservices

We need to establish guidelines that balance REST purity with practical considerations for our business domain.

## Decision

We will adopt the following conventions for API resource naming and HTTP method usage:

### Resource Naming

1. **Use Plural Nouns for Collections**
   - Use plural nouns for collection resources (e.g., `/customers`, not `/customer`)
   - Example: `/v1.0/customers` for the collection of all customers

2. **Resource Hierarchy and Relationships**
   - Distinguish between "first-level citizen" resources and dependent resources
   - First-level citizens are resources that have meaning independent of other resources and can be accessed directly
   - Dependent resources only make sense within the context of a parent resource
   - Express ownership with nested resources using URI paths only for dependent resources
   - Limit nesting to maximum 2–3 levels to avoid overly complex URIs
   - Example: `/v1.0/customers/{customer-id}/orders` for listing a customer's orders, but `/v1.0/orders/{order-id}` 
     for accessing a specific order

3. **Resource Identifiers**
   - Use kebab-case (hyphen-separated) for multi-word resource names
   - Use consistently formatted IDs (e.g., UUID, domain-specific IDs)
   - Example: `/v1.0/delivery-zones/{zone-id}`

4. **Action Resources**
   - For operations that do not map cleanly to CRUD, use action resources with verbs
   - Prefer to use them as sub-resources
   - Example: `/v1.0/customers/{customer-id}/password/reset`

### HTTP Methods

1. **GET**
   - Used for retrieving resources without side effects
   - Safe and idempotent
   - Must not change resource state
   - Examples:
     - `GET /v1.0/customers` - List customers
     - `GET /v1.0/customers/{id}` - Get a specific customer

2. **POST**
   - Used for creating new resources or submitting data for processing
   - Not idempotent (multiple identical requests may create multiple resources)
   - Examples:
     - `POST /v1.0/customers` - Create a new customer
     - `POST /v1.0/customers/{id}/verify` - Process a verification action

3. **PUT**
   - Used for complete replacement of a resource
   - Idempotent (multiple identical requests have the same effect)
   - Example: `PUT /v1.0/customers/{id}` - Replace the entire customer resource

4. **PATCH**
   - Used for partial updates to a resource
   - Must be implemented to be idempotent
   - Example: `PATCH /v1.0/customers/{id}` - Update specific fields of a customer

5. **DELETE**
   - Used for removing resources
   - Should be idempotent (repeated calls should not cause errors)
   - Example: `DELETE /v1.0/customers/{id}` - Remove a customer

6. **OPTIONS**
   - Used for describing the communication options for the target resource
   - Primarily for CORS preflight requests

## Consequences

### Positive

- Consistent, predictable API design improves developer experience
- Follows REST best practices for resource naming and HTTP methods
- Simplifies API documentation and reduces a cognitive load
- Enables more efficient API gateway configuration
- Facilitates API discovery and learning curve
- Supports better tooling and code generation

### Negative

- Some complex domain operations may not map cleanly to REST resources
- May require additional endpoints for complex actions
- Could lead to deeply nested URLs for complex resource relationships

### Neutral

- Need to balance REST purity with practical considerations
- Different resource modeling approaches may be needed for different domains
- Some legacy systems may require special accommodations

## Implementation Notes

### First-Level Citizen Resources

To determine if a resource should be a first-level citizen:

1. **Independent Existence**: Does the resource have meaning, and can it exist independently of other resources?
2. **Global ID**: Is the resource identifier globally unique and meaningful without parent context?
3. **Multiple Relationships**: Can the resource be related to multiple different parent resources?

Examples:
- **Orders** are first-level citizens because:
  - They have meaning on their own (an order exists independently)
  - They have globally unique IDs
  - They can be related to customers, restaurants, and couriers

- **Customer payment history entries** are dependent resources because:
  - They only make sense in the context of a specific customer
  - Their IDs might only be unique within a customer's history
  - They are fundamentally tied to a single parent resource

This approach provides several benefits:
- Cleaner URLs for commonly accessed resources
- Reduced duplication of endpoints
- More intuitive API structure
- Better reflects the domain model

### Resource Naming Examples

| Resource | URI Pattern | Description |
|----------|-------------|-------------|
| Collection | `/v1.0/customers` | List of all customers |
| Single Resource | `/v1.0/customers/{id}` | Specific customer |
| First-level Resource | `/v1.0/orders/{order-id}` | Specific order (first-level citizen) |
| Sub-resource Collection | `/v1.0/customers/{id}/orders` | Orders belonging to a customer |
| Dependent Sub-resource | `/v1.0/customers/{id}/payment-history/{payment-id}` | Specific payment in customer's history (dependent resource) |
| Filtering | `/v1.0/orders?status=delivered` | Filtered list of orders |
| Action | `/v1.0/customers/{id}/email/verify` | Action to verify email |

### HTTP Method and Status Code Mapping

| Operation | HTTP Method | Success Status | Resource URI |
|-----------|-------------|----------------|-------------|
| List | GET | 200 OK | `/v1.0/customers` |
| Retrieve | GET | 200 OK | `/v1.0/customers/{id}` |
| Create | POST | 201 Created | `/v1.0/customers` |
| Replace | PUT | 200 OK | `/v1.0/customers/{id}` |
| Update | PATCH | 200 OK | `/v1.0/customers/{id}` |
| Remove | DELETE | 204 No Content | `/v1.0/customers/{id}` |
| Action | POST | 200 OK | `/v1.0/customers/{id}/verify` |

## Related Documents

- [OpenAPI Specification 3.0.3](https://spec.openapis.org/oas/v3.0.3)
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)

## Contributors

- Àlex Grau Roca
