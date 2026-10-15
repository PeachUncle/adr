# ADR-008: Simple Message Error Response Format

**Date:** 2025-01-10
**Status:** Accepted
**Deciders:** Craig Banach
**Technical Story:** Standardising API error responses for single web app consumer

## Context

Need a consistent error response format for the API with considerations:
- Single web app consumer that we control
- No third-party API consumers
- No multi-language support needed
- Error messages should be user-friendly and displayable
- Simple implementation and parsing

## Decision

Use a simple, flat error response format:

```json
{
    "message": "A category named 'Groceries' already exists",
    "errors": {
        "amount": ["Amount must be greater than zero"],
        "description": ["Description is required", "Description cannot exceed 200 characters"]
    }
}
```

Implementation:
- **Single message** for general errors (404, 409, 500)
- **Field-specific errors** for validation failures (400)
- **User-friendly messages** suitable for direct display
- **No error codes** - HTTP status codes are sufficient
- **No stack traces** in production

## Consequences

**Positive:**
- **Simple to implement**: No complex error hierarchies
- **Easy to parse**: Flat structure, predictable format
- **User-friendly**: Messages can be displayed directly
- **Minimal overhead**: Small response size
- **Quick development**: No translation keys or error catalogues

**Negative:**
- **No machine-readable codes**: Can't programmatically handle specific errors
- **English only**: Would need refactoring for internationalisation
- **Limited debugging info**: No trace IDs or detailed context
- **Not standards-compliant**: Not following RFC 7807 (Problem Details)

**Neutral:**
- Tightly coupled to single consumer assumption
- Error messages become part of API contract
- Different from industry standards but fit for purpose

## Implementation Examples

```csharp
// Validation errors (400)
{
    "message": "Validation failed",
    "errors": {
        "amount": ["Amount must be greater than zero"],
        "categoryId": ["Category not found"]
    }
}

// Business rule violation (409)
{
    "message": "Cannot delete category 'Rent' as it has transactions"
}

// Not found (404)
{
    "message": "Transaction not found"
}

// Server error (500)
{
    "message": "An error occurred while processing your request"
}
```

## Error Response Helper

```csharp
public static class ErrorResponses
{
    public static object Validation(string message, Dictionary<string, string[]> errors) =>
        new { message, errors };
        
    public static object Simple(string message) =>
        new { message };
}
```

## Alternatives Considered

1. **RFC 7807 Problem Details**
   - Pros: Industry standard, rich error info
   - Cons: Overkill for simple app, more complex
   - Rejected: Over-engineered for our needs

2. **Custom error codes**
   - Pros: Machine-readable, language independent
   - Cons: Requires error catalogue, mapping layer
   - Rejected: Single language app doesn't need this

3. **GraphQL-style errors**
   - Pros: Consistent with GraphQL if we add it later
   - Cons: More complex structure
   - Rejected: Not using GraphQL, unnecessary complexity

## References

- [REST API Error Handling Best Practices](https://blog.restcase.com/rest-api-error-handling-best-practices/)
- [RFC 7807 - Problem Details](https://datatracker.ietf.org/doc/html/rfc7807) (considered but not adopted)