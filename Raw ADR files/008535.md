# Decision to Obfuscate 409 Responses on Customer Endpoints

## Status

**Proposed**

## Context

The `409 Conflict` HTTP status code is used to indicate that a request could not be completed due to a conflict with the current state of the resource. For example, if a client attempts to create or update a customer with an email address that already exists, a `409` response is returned.

While this behavior is correct from a technical perspective, it exposes sensitive information, such as whether an email address is already registered in the system. This creates a potential security risk, as malicious actors could use these responses to fish for valid email addresses.

To address this, the API should obfuscate `409` responses to prevent the disclosure of sensitive information while maintaining usability for legitimate clients.

## Decision

The API will obfuscate `409 Conflict` responses on customer creation and update endpoints. Instead of explicitly stating the reason for the conflict, the API will:

1. Replace `409 Conflict` responses with `400 Bad Request` responses.
2. Return a generic error message, such as: `"The request could not be completed due to a conflict."`
3. Avoid revealing whether the conflict is due to an existing email address or any other specific field.
4. Log the detailed conflict reason internally for debugging and auditing purposes.

### Example

#### Current Behavior:

Request:
```http
POST /customers HTTP/1.1
Content-Type: application/json

{
  "email": "existing@example.com",
  "fullName": "John Doe",
  "preferredName": "John"
}
```

Response:
```json
{
  "error": "Email address already exists."
}
```

#### Proposed Behavior:

Request:
```http
POST /customers HTTP/1.1
Content-Type: application/json

{
  "email": "existing@example.com",
  "fullName": "John Doe",
  "preferredName": "John"
}
```

Response:
```json
{
  "error": "The request could not be completed due to a conflict."
}
```

Status Code: `400 Bad Request`

## Consequences

### Benefits

- **Improved Security**: Prevents malicious actors from fishing for valid email addresses.
- **Privacy Compliance**: Aligns with best practices for protecting user data.
- **Internal Visibility**: Logs detailed conflict reasons for debugging and auditing without exposing them to clients.
- **Simplified Error Handling**: Aligns with existing use of `400 Bad Request` for other validation errors, creating consistency.

### Drawbacks

- **Reduced Client Feedback**: Legitimate clients may find it harder to diagnose the cause of the conflict without detailed error messages.
- **Increased Support Load**: Obfuscated error messages may lead to more support requests for clarification.
- **Semantic Change**: Replacing `409` with `400` changes the HTTP semantics slightly, which may require client updates.

## Alternatives Considered

1. **Detailed Error Responses with Rate Limiting**:
    - Provide detailed error messages but limit the rate of requests to prevent abuse.
    - Rejected because it does not fully address the risk of information disclosure.

2. **Error Codes with Documentation**:
    - Return a generic error message along with a code (e.g., `ERR_CONFLICT`) that is documented for clients.
    - Considered as a potential enhancement to the obfuscated approach.

3. **No Change**:
    - Rejected because it exposes sensitive information and does not align with security best practices.

## Implementation Plan

1. **Modify Error Handling**:
    - Update the customer creation and update endpoints to replace `409` responses with obfuscated `400` responses.

2. **Internal Logging**:
    - Ensure detailed conflict reasons are logged internally for debugging and auditing purposes.

3. **Documentation**:
    - Update API documentation to reflect the obfuscated `400` error responses.

4. **Testing**:
    - Write tests to verify that `400` responses are correctly returned and obfuscated.
    - Validate that internal logs capture detailed conflict reasons.

## Conclusion

Replacing `409 Conflict` responses with obfuscated `400 Bad Request` responses on customer creation and update endpoints enhances security by preventing information disclosure while maintaining internal visibility for debugging. This approach aligns with best practices for protecting sensitive user data and mitigates the risk of abuse by malicious actors.
