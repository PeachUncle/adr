# 6. Rest API Response Formatting

## Status

Accepted

Date: 2025-06-20

## Context

As our API ecosystem continues to grow, we need to establish consistent patterns for response formatting to ensure:

- Predictable and consistent response structures across all services
- Clear separation between successful and error responses
- Efficient client-side parsing and handling of responses
- The appropriate use of HTTP status codes

Inconsistent response formats lead to increased client complexity, poor developer experience, and brittle integrations.

## Decision

We will adopt the following conventions for API response formatting:

### Content Types

1. **Primary Content Type**
   - Return `application/json` as the primary content type for responses
   - Set appropriate `Content-Type` response header: `Content-Type: application/json`

2. **Secondary Content Types**
   - For file downloads, use appropriate MIME types (e.g., `application/pdf`)
   - For binary data, use `application/octet-stream`

### HTTP Status Codes

1. **Success Codes**
   - `200 OK`: Standard success response
   - `201 Created`: Resource creation successful
   - `204 No Content`: Successful operation with no response body

2. **Error Codes**
    - Error codes follow the format defined in [REST API Error Response Format](./0002-rest-api-error-response-format.md)
    - Refer to that ADR for specific implementation details

### Response Structure

1. **Success Response Format**
   - For single resource responses, return the resource directly as a JSON object
   - For collection responses, use a standard wrapper with pagination metadata

   Single Resource Example:
   ```json
   {
     "id": "cust-123",
     "name": "John Doe",
     "email": "john@example.com",
     "created_at": "2025-06-15T10:30:00Z"
   }
   ```

   Collection Example:
   ```json
   {
     "items": [
       {
         "id": "order-123",
         "status": "delivered"
       },
       {
         "id": "order-456",
         "status": "processing"
       }
     ],
     "pagination": {
       "total_items": 42,
       "total_pages": 5,
       "current_page": 1,
       "page_size": 10
     }
   }
   ```

2. **Error Response Format**
   - Error responses follow the format defined in [REST API Error Response Format](./0002-rest-api-error-response-format.md)
   - Refer to that ADR for specific implementation details

3. **JSON Structure**
   - Use `snake_case` for all property names (e.g., `created_at` not `createdAt`)
   - Use appropriate data types (string, number, boolean, object, array, null)
   - For dates and times, use ISO 8601 format (e.g., `2025-06-20T14:30:00Z`)

4. **Null Handling**
   - Do not include null properties in responses unless necessary
   - Use empty arrays `[]` instead of null for empty collections
   - Use empty strings `""` only when semantically appropriate

### Pagination Metadata

- For paginated collections, include standard pagination metadata
- Use consistent parameter names: `page`, `page_size`, `total_items`, `total_pages`

## Consequences

### Positive

- Consistent response format improves developer experience
- Standardized error responses simplify client-side error handling
- Clear separation between success and error cases
- Improved API documentation and discoverability
- Reduced client-side parsing complexity

### Negative

- Some complex domain models might require specialized response structures

### Neutral

- Different domains may need additional metadata
- Some clients may need to adjust to standardized formats

## Implementation Notes

### Response Examples

For error responses, refer to [REST API Error Response Format](./0002-rest-api-error-response-format.md) for 
implementation details.

### Pagination Implementation

```go
// PaginatedResponse represents a standard paginated response
type PaginatedResponse struct {
    Items      interface{} `json:"items"`
    Pagination Pagination  `json:"pagination"`
}

// Pagination contains standard pagination metadata
type Pagination struct {
    TotalItems  int `json:"total_items"`
    TotalPages  int `json:"total_pages"`
    CurrentPage int `json:"current_page"`
    PageSize    int `json:"page_size"`
}

// Handler function with pagination
func (h *Handler) ListOrders(c *gin.Context) {
    page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
    pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))

    // Get results from service
    orders, total, err := h.service.ListOrders(c.Request.Context(), page, pageSize)
    if err != nil {
        // Handle error based on ADR-0002
        return
    }

    // Calculate pagination metadata
    totalPages := (total + pageSize - 1) / pageSize

    // Return paginated response
    c.JSON(http.StatusOK, PaginatedResponse{
        Items: orders,
        Pagination: Pagination{
            TotalItems:  total,
            TotalPages:  totalPages,
            CurrentPage: page,
            PageSize:    pageSize,
        },
    })
}
```

### Successful Response Example (Login Customer)

```go
// TokenResponse represents a successful login or token refresh response
type TokenResponse struct {
    AccessToken  string `json:"access_token"`
    RefreshToken string `json:"refresh_token"`
    ExpiresIn    int    `json:"expires_in"`
    TokenType    string `json:"token_type"`
}

// Handler function for login
func (h *Handler) LoginCustomer(c *gin.Context) {
    // ... validation and service call ...

    // Return successful response
    c.JSON(http.StatusOK, TokenResponse{
        AccessToken:  tokenPair.AccessToken,
        RefreshToken: tokenPair.RefreshToken,
        ExpiresIn:    tokenPair.ExpiresIn,
        TokenType:    tokenPair.TokenType,
    })
}
```

## Related Documents

- [REST API Resource Naming and HTTP Methods](./0004-rest-api-resource-naming-and-http-methods.md)
- [REST API Request Formatting](./0005-rest-api-request-formatting.md)
- [REST API Error Response Format](./0002-rest-api-error-response-format.md)
- [OpenAPI Specification 3.0.3](https://spec.openapis.org/oas/v3.0.3)
- [JSON:API Specification](https://jsonapi.org/)

## Contributors

- Àlex Grau Roca
