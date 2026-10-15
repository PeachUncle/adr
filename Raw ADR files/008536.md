# Decision to Implement Pagination and Sorting for "Get All Customers"

## Status

**Proposed**

## Context

The `GET /customers` endpoint is intended to retrieve a list of all customers. As the number of customers in the database grows, returning all records in a single response becomes inefficient and resource-intensive. Large responses can lead to:

1. **Performance Issues**: Increased server processing time and higher memory usage.
2. **Network Latency**: Large payloads slow down data transmission, especially for clients with limited bandwidth.
3. **Poor Client Experience**: Parsing large responses can overwhelm clients, particularly on resource-constrained devices.

Pagination and sorting provide a scalable solution to these challenges, allowing clients to fetch manageable subsets of data and specify the desired order of results.

## Decision

The `GET /customers` endpoint will support pagination and sorting by introducing query parameters. This will:

1. Limit the number of records returned per request.
2. Allow clients to navigate through the dataset using pagination controls (e.g., page number, page size).
3. Enable clients to sort results by specific fields (e.g., `fullName`, `createdAt`).

### Query Parameters

1. **Pagination Parameters**:
   - `page`: The page number to retrieve (default: `1`).
   - `size`: The number of records per page (default: `10`, maximum: `100`).

2. **Sorting Parameters**:
   - `sortBy`: The field to sort by (e.g., `fullName`, `email`, `createdAt`).
   - `sortOrder`: The sort direction (`asc` for ascending, `desc` for descending; default: `asc`).

### Example Requests

#### Default Pagination and Sorting:

```http
GET /customers?page=1&size=10&sortBy=fullName&sortOrder=asc HTTP/1.1
```

#### Custom Pagination and Sorting:

```http
GET /customers?page=3&size=20&sortBy=createdAt&sortOrder=desc HTTP/1.1
```

#### Response Example:

```json
{
  "customers": [
    { "id": "123", "fullName": "John Doe", "email": "john.doe@example.com", "createdAt": "2024-01-01T12:00:00Z" },
    { "id": "124", "fullName": "Jane Smith", "email": "jane.smith@example.com", "createdAt": "2024-01-02T12:00:00Z" }
  ],
  "pagination": {
    "currentPage": 1,
    "pageSize": 10,
    "totalPages": 5,
    "totalRecords": 50
  }
}
```

## Consequences

### Benefits

- **Improved Performance**: Reduces server and network load by limiting the size of responses.
- **Scalability**: Supports datasets of any size by enabling clients to request data in chunks.
- **Enhanced Usability**: Clients can retrieve data in a more structured and manageable way.
- **Flexibility**: Sorting options allow clients to organize data according to their needs.

### Drawbacks

- **Increased Complexity**: Requires additional implementation effort for pagination and sorting logic.
- **Client Adaptation**: Clients must handle pagination and sorting logic on their end.

## Alternatives Considered

1. **Limit Only**:
   - Rejected because it does not provide a mechanism for navigating through the dataset.

2. **No Pagination or Sorting**:
   - Rejected because it leads to inefficiency and poor user experience for large datasets.

3. **Cursor-Based Pagination**:
   - Considered for high-performance use cases but rejected in favor of page-based pagination for simplicity and ease of implementation.

## Implementation Plan

1. **Backend Updates**:
   - Update the database query logic to support `LIMIT` and `OFFSET` for pagination.
   - Add `ORDER BY` clauses for sorting based on the specified fields and directions.

2. **API Specification**:
   - Update the OpenAPI documentation to include pagination and sorting query parameters.

3. **Testing**:
   - Write unit and integration tests to validate pagination and sorting functionality.
   - Test edge cases, such as invalid parameters and large datasets.

4. **Client Communication**:
   - Notify API clients of the new pagination and sorting capabilities.
   - Provide examples and usage guidelines in the API documentation.

## Conclusion

Adding pagination and sorting to the `GET /customers` endpoint improves performance, scalability, and usability. While it introduces some complexity, the benefits significantly outweigh the drawbacks, ensuring the API can handle large datasets efficiently and flexibly.

