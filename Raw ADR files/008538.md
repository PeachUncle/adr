# Decision to Implement Comprehensive Request Body Validation with Detailed Error Responses

## Status

**Proposed**

## Context

Validating request bodies is essential for ensuring the correctness, security, and integrity of the API. Providing comprehensive validation and returning detailed error responses helps clients understand and address all issues in their submissions at once. Without this approach, clients may encounter a frustrating trial-and-error process where only one validation error is reported per request, requiring multiple iterations to fix all issues.

For example, a `POST /customers` request body may have multiple validation errors such as:

- A malformed email address.
- A pre-existing email address already in use.
- An empty `fullName` field.
- A missing `preferredName` field.

Instead of returning a single error for each invalid submission, the API will validate the entire request body and return a list of all detected errors.

## Decision

The API will implement comprehensive request body validation for relevant endpoints and provide detailed error responses listing all validation errors. This approach will:

1. Ensure clients receive actionable feedback for all issues in a single response.
2. Enhance the developer experience by reducing trial-and-error cycles.
3. Maintain clarity and consistency in error reporting across the API.

### Example Error Response

#### Request Body:

```json
{
  "email": "invalid-email",
  "fullName": "",
  "preferredName": null
}
```

#### Response Body:

```json
{
  "errors": [
    {
      "field": "email",
      "message": "Email address is malformed."
    },
    {
      "field": "email",
      "message": "Email address already exists."
    },
    {
      "field": "fullName",
      "message": "Full name cannot be empty."
    },
    {
      "field": "preferredName",
      "message": "Preferred name is required."
    }
  ]
}
```

## Implementation Details

1. **Validation Framework**:
    - Use Spring Jakarta Validations for declarative field-level constraints.
    - Implement custom validators for domain-specific rules, such as checking for duplicate email addresses.

2. **Global Error Handling**:
    - Create a centralized exception handler using `@ControllerAdvice` to process validation errors and format responses.

3. **Error Response Schema**:
    - Standardize the error response structure to include:
        - `field`: The name of the field that failed validation.
        - `message`: A human-readable description of the validation error.
        - Optional metadata for advanced use cases (e.g., error codes).

4. **Endpoints**:
    - Apply this validation approach to all endpoints that accept structured request bodies.

5. **Testing**:
    - Write unit and integration tests to ensure:
        - All validation rules are correctly enforced.
        - Error responses include all validation errors with the correct format.

## Consequences

### Benefits

- **Improved Client Experience**: Clients can fix multiple errors in one iteration, reducing frustration.
- **Clear Feedback**: Comprehensive error responses provide clear and actionable information.
- **Consistency**: Standardized error responses improve the API’s usability and professionalism.
- **Scalability**: New validation rules can be added without changing the error reporting structure.

### Drawbacks

- **Increased Response Size**: Returning multiple errors may slightly increase response payload size.
- **Implementation Complexity**: Requires careful design of error handling and response formatting.
- **Validation Performance**: Validating all fields may slightly increase request processing time, but the impact is negligible for most use cases.

## Alternatives Considered

1. **Single Error Reporting**:
    - Rejected because it forces clients to fix one error at a time, increasing iteration cycles and reducing efficiency.

2. **Partial Validation**:
    - Rejected because it may allow some invalid fields to pass unnoticed, compromising data integrity.

3. **Ad Hoc Validation Responses**:
    - Rejected because it introduces inconsistency in error reporting across endpoints.

## Implementation Plan

1. **Validation Enhancements**:
    - Define comprehensive validation rules for all request objects.
    - Implement custom validators as needed for domain-specific requirements.

2. **Global Error Handler**:
    - Create a centralized handler to format validation errors into a consistent response structure.

3. **Testing**:
    - Write extensive tests to ensure all validation rules are enforced and error responses are formatted correctly.

4. **Documentation**:
    - Update API documentation with examples of validation error responses for each endpoint.

## Conclusion

Adopting comprehensive request body validation with detailed error responses enhances the client experience, improves data integrity, and aligns the API with best practices. While this approach introduces some implementation complexity, the long-term benefits of clarity, consistency, and efficiency outweigh the drawbacks.
