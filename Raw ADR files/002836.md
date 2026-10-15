# 7. Adopting the "JSend" Response Convention

Date: 2024-03-10

## Status

2024-03-10 accepted

## Context

In the development of web services and APIs, establishing a consistent format for responses is crucial for maintaining clarity and ease of integration for clients. A standardized response format ensures that clients can reliably parse and react to responses, regardless of the outcome of their requests.

## Decision

- **Standard JSON Response**: The most basic approach, where each endpoint may have its unique response structure. While flexible, it can lead to inconsistencies across different parts of the API, making it harder for clients to handle responses.
- **RESTful API Standards**: These standards suggest using HTTP status codes to indicate the success or failure of requests, with the response body containing the requested resource or error details. While widely adopted, the response body's structure can still vary significantly.
- **JSend**: A simple, easy-to-understand specification for JSON response objects. It standardizes the response format into three types: `success`, `fail`, and `error`. This convention simplifies client-side logic for handling responses by providing a consistent structure.

After evaluating the options, we have decided to adopt the **JSend** response convention for our project's web services and APIs. JSend's simplicity and clarity make it an excellent choice for ensuring consistent and predictable responses across our API. It strikes a balance between flexibility and standardization, providing a structured format that is easy for both API consumers and developers to understand. Additional to the response object we introduce 3 new properties (`statusCode`, `timestamp`, `path`) to fulfill the response information.

### Advantages of JSend:

- **Simplicity**: JSend's structure is straightforward, with clear distinctions between successful responses and various types of failures (`success`, `fail`, and `error`).
- **Predictability**: Clients can easily predict and handle the API's responses, as the structure remains consistent across different endpoints.
- **Ease of Implementation**: Implementing JSend requires minimal effort and changes to existing codebases, making it an attractive option for projects at any stage of development.
- **Improved Client-Side Handling**: The standardized response format simplifies error handling on the client side, as the type of response (`success`, `fail`, `error`) clearly indicates the action to be taken.

## Consequences

- **Consistency Across the API**: Adopting JSend will improve the consistency of response formats across our API, enhancing the developer experience and reducing potential confusion.
- **Client-Side Adjustments**: Clients of our API may need to adjust their handling of responses to align with the JSend format. This adjustment will be a one-time effort that results in simpler and more robust client-side code.
- **Documentation Clarity**: Our API documentation can now uniformly describe the response format, making it easier for new consumers to understand how to interact with our API.
- **Swagger Decoratirs**: new decorators need to be prepared to reflect response with the OpenAPI documentation