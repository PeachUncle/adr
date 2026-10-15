# 5. Rest API Request Formatting

## Status

Accepted

Date: 2025-06-20

## Context

As our API ecosystem expands, we need to establish clear guidelines for request formatting to ensure:

- Consistent data exchange patterns across all services
- Predictable request structures for API consumers
- Efficient request processing
- Clear validation error feedback
- Interoperability with various client platforms

Without standardized request formatting, we risk inconsistent implementations across services, increased 
client-side complexity, and poor developer experience.

## Decision

We will adopt the following conventions for API request formatting:

### Content Types

1. **Primary Content Type**
   - Use `application/json` as the primary content type for request bodies
   - All services must accept and process JSON-formatted requests
   - Set appropriate `Content-Type` request header: `Content-Type: application/json`

2. **Secondary Content Types**
   - For file uploads, use `multipart/form-data`

### JSON Structure

1. **Property Naming**
   - Use `sanke_case` for all property names
   - Use meaningful and descriptive names

2. **Nested Objects**
   - Limit nesting to 3 levels maximum for readability
   - Use flattening techniques for deeply nested structures
   - Only nest objects when they represent a logical hierarchy or ownership

3. **Arrays**
   - Use arrays for lists of similar objects
   - Keep array items homogeneous (same structure for all items)
   - Consider pagination for large arrays

4. **Data Types**
   - Use appropriate JSON data types (string, number, boolean, object, array, null)
   - For dates and times, use ISO 8601 format (e.g., `2025-06-20T14:30:00Z`)
   - For currency values, use integer numbers with explicit currency code and considering the number of decimals for 
     that currency (e.g. `1.00€` will be exposed as `{"amount": 100, "currency": "EUR"}`)

### Query Parameters

1. **Parameter Naming**
   - Use `kebab-case` for parameter names to maintain consistency with JSON property naming
   - Use meaningful and descriptive names
   - Prefix parameters with their context when necessary (e.g., `user-id` instead of just `id`)

2. **Pagination**
   - Standard pagination parameters:
     - `page`: Current page number ([1-based indexing](https://rosalind.info/glossary/1-based-numbering/))
     - `page-size`: Number of items per page
   - Default values:
     - `page-size`: 10 items
     - `page`: 1
   - Maximum allowed page size: 100 items

3. **Sorting**
   - Use the `sort` parameter for all sorting operations
   - Prefix field with `-` for descending order, no prefix means ascending order
   - Multiple sort criteria should be comma-separated
   - Examples:
       - Single field ascending: `?sort=created-at`
       - Single field descending: `?sort=-created-at`
       - Multiple fields: `?sort=-created-at,name,-status`
   - Default sorting must be documented per endpoint
   - Important considerations:
       - Field names in sort parameters should use `kebab-case`
       - Only allow sorting by documented sortable fields
       - Document the default sort order in API specifications
       - Consider performance implications when allowing sorting on non-indexed fields

4. **Filtering**
   - Basic filtering:
     - Use the field name as the parameter: `?status=active`
     - Multiple values: `?status[]=active&status[]=pending`
   - Advanced filtering:
     - Operators in parameter names:
       - `field-gt`: Greater than
       - `field-gte`: Greater than or equal
       - `field-lt`: Less than
       - `field-lte`: Less than or equal
       - `field-like`: Pattern matching
       - `field-between`: Range (comma-separated values)
     - Examples:
       - `?created-at-gte=2025-01-01`
       - `?price-between=10,20`
       - `?name-like=john`

### Request Validation

1. **Required Fields**
   - Document required fields in API specifications
   - Return validation errors when required fields are missing

2. **Field Constraints**
   - Define and document constraints (min/max values, regex patterns, enum values)
   - Provide clear error messages when constraints are violated

3. **Input Sanitization**
   - Validate and sanitize all user inputs
   - Guard against common security threats (injection attacks, XSS)

## Consequences

### Positive

- Consistent request format improves developer experience
- Standardized validation reduces duplicate code across services
- JSON structure guidelines improve readability and maintainability
- Clear property naming reduces ambiguity
- Better interoperability with client applications

### Negative

- Some complex domain models might be challenging to express with limited nesting
- Strict validation requirements may initially slow development

### Neutral

- Different domains may require specialized validation rules
- Some clients may need to adjust to standardized formats

## Implementation Notes

### Example Request with Query Parameters

```json
{
  "customer_id": "cust-123",
  "order_details": {
    "items": [
      {
        "product_id": "prod-456",
        "quantity": 2,
        "unit_price": 1099,
        "currency": "EUR"
      },
      {
        "product_id": "prod-789",
        "quantity": 1,
        "unit_price": 2999,
        "currency": "EUR"
      }
    ],
    "shipping_address": {
      "street": "123 Main St",
      "city": "Anytown",
      "postal_code": "12345",
      "country": "US"
    }
  },
  "payment_method": "credit_card",
  "currency": "USD",
  "notes": null
}
```

### Pagination and Filtering Example (Gin Framework)

```go
// OrderRequest represents the structure for an order creation request
type OrderRequest struct {
    CustomerID    string      `json:"customer_id" binding:"required"`
    OrderDetails  OrderDetails `json:"order_details" binding:"required"`
    PaymentMethod string      `json:"payment_method" binding:"required,oneof=credit_card paypal bank_transfer"`
    Currency      string      `json:"currency" binding:"required,len=3"`
    Notes         *string     `json:"notes"`
}

// Handler function with validation
func (h *Handler) CreateOrder(c *gin.Context) {
    var req OrderRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        // Handle validation error using standard error format
        c.JSON(http.StatusBadRequest, gin.H{
            "code": "VALIDATION_ERROR",
            "message": "validation failed",
            "details": extractValidationErrors(err),
        })
        return
    }

    // Process valid request...
}
```

### Flattening Deep Structures

When dealing with deeply nested structures, consider flattening:

Instead of:
```json
{
  "user": {
    "address": {
      "home": {
        "street": "123 Main St",
        "city": "Anytown"
      }
    }
  }
}
```

Consider:
```json
{
  "user": {
    "home_street": "123 Main St",
    "home_city": "Anytown"
  }
}
```

## Related Documents

- [REST API Resource Naming and HTTP Methods](./0004-rest-api-resource-naming-and-http-methods.md)
- [REST API Error Response Format](./0002-rest-api-error-response-format.md)
- [OpenAPI Specification 3.0.3](https://spec.openapis.org/oas/v3.0.3)
- [JSON Schema](https://json-schema.org/)
- [1-based indexing](https://rosalind.info/glossary/1-based-numbering/)

## Contributors

- Àlex Grau Roca
