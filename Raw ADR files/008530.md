# Decision to Use Domain-Driven Endpoints for Updates

## Status

**Proposed**

## Context

Traditional RESTful APIs often use a single `update` endpoint to modify multiple fields of a resource. For example, a `PUT /customers/{id}` endpoint may accept a payload with all updatable fields, even if only one or a few fields are being changed. While this approach simplifies endpoint design, it introduces the following challenges:

1. **Complexity in Validation**: The server must handle partial updates, validate multiple fields, and ensure consistency.
2. **Audit and Telemetry**: It becomes harder to track and log which specific fields were updated, reducing the granularity of telemetry.
3. **Conflict Resolution**: Updating unrelated fields in a single payload increases the risk of concurrency issues.
4. **Coupling of Responsibilities**: Overloading a single endpoint with the responsibility of handling diverse update operations violates the principle of single responsibility.

This proposal aligns closely with principles of **Domain-Driven Design (DDD)**, as introduced by **Eric Evans** in his seminal book *Domain-Driven Design: Tackling Complexity in the Heart of Software*. DDD emphasizes creating models and interfaces that closely reflect the domain concepts, ensuring that technical implementations remain aligned with the business problem space. In this case, separating update operations into domain-driven endpoints enhances clarity and directly maps API operations to distinct aspects of the customer domain.

## Decision

The API will use separate, domain-driven endpoints for updating logical groupings of fields instead of a single generic update endpoint. Examples include:

1. **`PATCH /customers/{id}/name`**: Updates the `full_name` and `preferred_name` fields.
2. **`PATCH /customers/{id}/email`**: Updates the `email_address` field.
3. **`PATCH /customers/{id}/phone-number`**: Updates the `phone_number` field.

Each endpoint will handle updates to fields within its domain grouping, ensuring clarity, validation, and auditability.

### Implementation Details

1. **Endpoint Design**:
   - Each domain-driven endpoint will have a clear, specific purpose and accept minimal payloads.
   - Example payloads:
      - `PATCH /customers/{id}/name`
        ```json
        {
          "full_name": "John Doe",
          "preferred_name": "Johnny"
        }
        ```
      - `PATCH /customers/{id}/email`
        ```json
        {
          "email_address": "john.doe@example.com"
        }
        ```
      - `PATCH /customers/{id}/phone-number`
        ```json
        {
          "phone_number": "+1234567890"
        }
        ```

2. **Validation**:
   - Each endpoint will perform targeted validation for its fields, reducing the complexity of validation logic.

3. **Telemetry and Auditing**:
   - Log each update operation with detailed information about the updated fields, enabling granular telemetry and auditing.

4. **Reduced Coupling**:
   - Each endpoint will be decoupled from other update operations, ensuring clear separation of concerns.

## Consequences

### Benefits

- **Improved Validation**: Focused endpoints reduce validation complexity and improve maintainability.
- **Granular Telemetry**: Easier to track which fields are being updated, providing better insights into usage patterns and debugging.
- **Conflict Resolution**: Limits the scope of updates to specific fields, reducing the likelihood of concurrent update conflicts.
- **Clear Responsibility**: Aligns with domain-driven design principles, ensuring each endpoint has a single, well-defined purpose.
- **Domain Modeling**: Reflects the DDD principle of aligning APIs with the domain model, enhancing both technical and business clarity.

### Drawbacks

- **Increased Endpoint Count**: The number of endpoints increases, potentially making the API appear more complex to clients.
- **Client Changes**: Clients must adapt to the new endpoint structure, potentially requiring updates to existing integrations.
- **Additional Documentation**: Requires more detailed API documentation to describe the purpose and usage of each endpoint.

## Alternatives Considered

1. **Single `PUT` or `PATCH` Endpoint**:
   - Rejected due to the complexity of handling partial updates and the lack of granularity in telemetry and auditing.

2. **GraphQL API**:
   - Considered for its flexibility in querying and updating fields but rejected as it adds significant complexity and may not align with RESTful principles preferred in this project.

3. **Hybrid Approach**:
   - Use a single `PATCH` endpoint but include optional parameters for specifying fields to update. Rejected because it does not fully address validation and telemetry challenges.

## Implementation Plan

1. **Endpoint Development**:
   - Define and implement domain-driven update endpoints in the controller layer.
   - Add validation logic specific to each endpoint.

2. **Logging and Telemetry**:
   - Update the logging system to capture detailed information for each update operation.

3. **Client Communication**:
   - Notify clients of the new endpoint structure and provide migration guidelines.

4. **Documentation**:
   - Update API documentation with detailed descriptions, payload examples, and use cases for each endpoint.

## Conclusion

Adopting domain-driven endpoints for updates ensures clarity, maintainability, and better telemetry for the API. While it introduces additional endpoints and requires client updates, the benefits of improved validation, auditing, and reduced complexity outweigh the drawbacks. This approach aligns with modern API design principles and the foundational concepts of Domain-Driven Design by Eric Evans, enhancing the overall quality of the application.
