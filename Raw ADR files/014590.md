# Architectural Decision Record: Using String IDs in API Contracts

## Status

Accepted (unanymously, i'm the only dev)

## Date

2025-06-14

## Context

When designing the API contracts for the Proletariat Budget application, we needed to decide on the data type for entity identifiers (IDs) that would be exposed through our APIs. While our current implementation uses MySQL with `BIGINT` as the primary key type, we wanted to ensure our API design would be flexible enough to accommodate potential future changes in database technology or ID generation strategies.

Key considerations included:
- Our default database (MySQL) uses numeric `BIGINT` IDs
- Different databases might use different ID formats (numeric, UUID, etc.)
- Frontend applications need to handle these IDs consistently
- JSON doesn't have a specific type for 64-bit integers, which can lead to precision issues

## Decision

We have decided to use string representations for all IDs in our API contracts, even though they are stored as numeric types in our current database implementation.

## Consequences

### Positive

1. **Database Agnosticism**: Using string IDs in the API contracts decouples the API from the underlying database implementation. This allows us to change database technologies (e.g., from MySQL to MongoDB or another NoSQL database that might use non-numeric IDs) without breaking API compatibility.

2. **Avoiding JavaScript Integer Limitations**: JavaScript, commonly used in frontend applications, has limitations with large integers (safe integers are limited to 53 bits). By using strings, we avoid potential precision loss when handling large numeric IDs in frontend applications.

3. **Support for Various ID Formats**: String IDs can accommodate various formats including:
   - Numeric IDs (e.g., "123456789")
   - UUIDs (e.g., "550e8400-e29b-41d4-a716-446655440000")
   - Custom formats (e.g., "user_123", "order-abc-xyz")

4. **Future-Proofing**: If we decide to change our ID generation strategy (e.g., moving to UUIDs or other non-numeric formats), the API contract remains unchanged.

5. **Consistency**: Having a uniform approach to IDs across all entities simplifies frontend development and reduces the chance of type-related bugs.

### Negative

1. **Type Conversion Overhead**: The backend must convert between numeric database IDs and string API IDs, which adds a small processing overhead.

2. **Potential for Confusion**: Developers might be confused about why IDs are strings when they know the underlying storage is numeric.

3. **Input Validation**: Additional validation is needed to ensure that string IDs can be properly converted to the appropriate database type when they represent numeric values.

## Implementation Details

1. **Backend Handling**:
   - When retrieving data from the database, numeric IDs will be converted to strings before being sent in API responses.
   - When receiving IDs from API requests, string IDs will be parsed to the appropriate numeric type for database operations.

2. **Frontend Handling**:
   - Frontend applications should always treat IDs as strings, regardless of their apparent numeric content.
   - Frontend validation should ensure IDs conform to expected patterns but should not assume they are numeric.

3. **Documentation**:
   - API documentation will clearly specify that all IDs are strings, even if they appear to be numeric.
   - Internal documentation will explain this decision to help onboard new developers.

## Alternatives Considered

1. **Using Numeric Types in API**: We considered using numeric types for IDs in the API to match our current database implementation, but this would limit our flexibility to change database technologies and could cause issues with large IDs in JavaScript.

2. **Using Different ID Types for Different Entities**: We considered using different ID types based on the entity type, but this would lead to inconsistency and potentially confuse developers.

3. **Using Objects with Type and Value Properties**: We considered using objects like `{"type": "numeric", "value": "123456789"}` to explicitly indicate the ID type, but this would significantly complicate the API without providing substantial benefits.

## References

- [JSON and JavaScript's Number Limitations](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER)
- [Database ID Strategies](https://www.mongodb.com/blog/post/generating-globally-unique-identifiers-for-use-with-mongodb)
- [RESTful API Design Best Practices](https://restfulapi.net/resource-naming/)