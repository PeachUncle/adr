# Decision to Restrict Domain Object Instantiation to Valid States

## Status

**Proposed**

## Context

Domain objects are central to encapsulating the rules and behaviors of the domain they represent. Allowing domain objects to exist in states that are impossible or invalid in the domain introduces risks such as:

1. **Unexpected Behavior**: Operations on invalid objects can lead to runtime errors or unintended side effects.
2. **Complex Validation**: Repeated checks across the application increase complexity and reduce maintainability.
3. **Eroded Domain Integrity**: Violations of the domain rules reduce the reliability of the system.

By ensuring that domain objects cannot be instantiated in invalid states, these risks are mitigated. This approach aligns with the principles presented in **[Richard Feldman’s Elm Europe Conference talk](https://www.youtube.com/watch?v=IcgmSRJHu_8)** on leveraging the type system to enforce correctness at compile-time.

Feldman highlights how the Elm language prevents invalid states through types, and this concept can be translated into object-oriented design by enforcing strict validation during instantiation. Adopting this principle for the API’s domain objects ensures the system’s integrity and robustness.

## Decision

Domain objects will enforce validation rules during instantiation, ensuring that only valid objects can exist in the system. This will be achieved through:

1. **Constructors with Validation**:
    - Constructors will include validation logic that throws exceptions or prevents instantiation when rules are violated.
    - Example:
      ```kotlin
      class CustomerName(val fullName: String, val preferredName: String) {
          init {
              require(fullName.isNotBlank()) { "Full name cannot be blank." }
              require(preferredName.isNotBlank()) { "Preferred name cannot be blank." }
          }
      }
      ```

2. **Factory Methods**:
    - Factory methods will provide additional flexibility while ensuring that only valid objects are created.
    - Example:
      ```kotlin
      companion object {
          fun create(fullName: String, preferredName: String): CustomerName? {
              return if (fullName.isNotBlank() && preferredName.isNotBlank()) {
                  CustomerName(fullName, preferredName)
              } else {
                  null
              }
          }
      }
      ```

3. **Value Objects for Validation**:
    - Encapsulate specific fields (e.g., email addresses, phone numbers) in value objects with built-in validation.

## Consequences

### Benefits

- **Domain Integrity**: Ensures that all objects adhere to domain rules from their creation.
- **Simplified Validation**: Reduces the need for repeated validation logic throughout the application.
- **Improved Reliability**: Prevents runtime errors caused by invalid states.
- **Enhanced Readability**: Clear instantiation rules make the domain model easier to understand and maintain.

### Drawbacks

- **Initial Complexity**: Requires additional effort to implement validation logic in constructors or factory methods.
- **Developer Overhead**: Teams must adhere to these design principles consistently across the codebase.
- **Edge Cases**: Uncommon scenarios may require special handling, increasing development time.

## Alternatives Considered

1. **Post-Instantiation Validation**:
    - Rejected because it allows invalid objects to exist temporarily, increasing the risk of misuse.

2. **External Validation**:
    - Rejected because it disperses validation logic, reducing maintainability and cohesion.

3. **Optional Instantiation Enforcement**:
    - Considered allowing some objects to bypass validation for testing or performance, but rejected to maintain consistency and reliability.

## Implementation Plan

1. **Define Rules**:
    - Identify and document the validity rules for each domain object.

2. **Update Constructors**:
    - Add validation logic to constructors and factory methods for all domain objects.

3. **Test Validation**:
    - Write unit tests to ensure that invalid inputs are rejected and valid ones are accepted.

4. **Refactor Existing Code**:
    - Replace ad hoc validation logic with constructor-based or factory-based validation.

5. **Documentation**:
    - Update developer guidelines to emphasize the importance of creating only valid domain objects.

## Conclusion

Restricting domain object instantiation to valid states strengthens the system’s integrity, aligns with domain-driven design principles, and reduces runtime errors. While this approach introduces some complexity during implementation, the long-term benefits of maintainability, reliability, and correctness outweigh the drawbacks. This decision ensures the domain model accurately represents the business rules and logic, as inspired by Richard Feldman’s insights on preventing invalid states.
