# Decision to Use Hypermedia in HTTP Response Bodies

## Status

**Proposed**

## Context

RESTful APIs often return structured data without guidance on how clients should interact with the system beyond the initial request. This lack of interaction context requires developers to rely on external documentation or hardcoded logic to navigate the API. By adopting **Hypermedia as the Engine of Application State (HATEOAS)** principles, the API can include actionable links in response bodies, enabling dynamic, self-describable interactions for clients.

For example, rather than returning only customer data, a hypermedia-enabled response would include links to related actions such as updating customer details, fetching related orders, or deleting the customer. This design ensures:

1. **Self-Descriptive APIs**: Clients can navigate and interact with the API dynamically based on links and actions provided in responses.
2. **Reduced Documentation Dependence**: Clients can rely on hypermedia responses instead of external documentation to discover available operations.
3. **Flexibility**: Changes to the API’s structure or workflows require fewer updates to client-side code.
4. **Entry Point Navigation**: A central "start" endpoint provides an entry point for clients to begin interacting with the API.

## Decision

The API will use hypermedia in its HTTP response bodies to provide actionable links and improve client usability. These links will adhere to common standards such as HAL (Hypertext Application Language) or JSON:API for consistent formatting.

### Example

#### Without Hypermedia:

```json
{
  "customer_id": "1234",
  "full_name": "John Doe",
  "email": "john.doe@example.com"
}
```

#### With Hypermedia:

```json
{
  "customer_id": "1234",
  "full_name": "John Doe",
  "email": "john.doe@example.com",
  "_links": {
    "self": { "href": "/customers/1234" },
    "update_name": { "href": "/customers/1234/name", "method": "PATCH" },
    "update_email": { "href": "/customers/1234/email", "method": "PATCH" },
    "update_phone_number": { "href": "/customers/1234/phone-number", "method": "PATCH" },
    "delete": { "href": "/customers/1234", "method": "DELETE" },
    "orders": { "href": "/customers/1234/orders" }
  }
}
```

### Start Endpoint Example:

```json
{
  "_links": {
    "self": { "href": "/start" },
    "customers": { "href": "/customers", "method": "GET" },
    "create_customer": { "href": "/customers", "method": "POST" },
    "documentation": { "href": "/docs" }
  }
}
```

### Implementation Details

1. **Response Format**:
    - Use HAL or a similar hypermedia format to define the `_links` object.
    - Include the HTTP methods supported for each link to guide client interactions.

2. **Link Generation**:
    - Dynamically generate hypermedia links based on the resource state and user permissions.

3. **Consistency**:
    - Ensure all response types consistently include hypermedia links where applicable.

4. **Documentation**:
    - Update API documentation to reflect the inclusion of hypermedia links and their structure.

## Consequences

### Benefits

- **Discoverability**: Clients can dynamically explore the API, reducing the need for hardcoded client logic.
- **Flexibility**: Future changes to API workflows are easier to manage as links and actions are provided dynamically.
- **Improved Developer Experience**: Clients have clear guidance on available operations for a given resource.
- **Hypermedia Clients**: Clients that are hypermedia-aware could immediately navigate and interact with the API without additional custom logic.
- **Alignment with REST Principles**: Embraces HATEOAS, a core tenet of RESTful API design.

### Drawbacks

- **Increased Response Size**: Adding links to responses slightly increases payload size.
- **Implementation Overhead**: Requires additional logic to generate and include hypermedia links dynamically.
- **Client Updates**: Clients must adapt to consume and act on hypermedia links effectively.

## Alternatives Considered

1. **Static API Responses**:
    - Rejected because they require external documentation and hardcoded client logic, reducing flexibility and discoverability.

2. **GraphQL**:
    - Considered for its flexibility in fetching related resources but rejected as it does not inherently provide actionable links for workflows.

3. **Partial Hypermedia Adoption**:
    - Considered including links only in specific endpoints but rejected for lack of consistency and diminished client usability.

## Implementation Plan

1. **Middleware for Link Injection**:
    - Develop middleware or utility functions to add `_links` objects to response bodies dynamically.

2. **Standardization**:
    - Adopt a hypermedia standard such as HAL or JSON:API for consistent implementation.

3. **Testing**:
    - Write tests to ensure links are correctly generated and included in responses.

4. **Client Communication**:
    - Notify clients of the new hypermedia-enabled responses and provide examples for integration.

5. **Documentation**:
    - Update API documentation with examples and explanations of hypermedia links and their usage.

## Conclusion

Adopting hypermedia in HTTP response bodies enhances the discoverability, flexibility, and usability of the API. While it introduces some implementation overhead, the benefits to client interaction and API evolution outweigh the drawbacks. This decision aligns the API with RESTful principles, ensuring a more intuitive and future-proof design.
