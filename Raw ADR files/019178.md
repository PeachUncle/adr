## Title
Separate REST objects from internal objects

## Status
Draft

## Context
We use rest APIs to expose endpoints to use the application.
We use a UseCase with an execute method which takes a Command.

We were considering annotating the use case directly with rest annotations
and using the Command as request body.

There were some drawbacks when attempting this approach.

1. Must not forget to put @Valid and @Validated annotations (though this could be tackled with ArchUnit)
    - at least when using created objects as input for other class methods
    - bean validations don't help when creating records inside a method and using them immediately without going through a validation proxy...
      - alternative could be to inject the validator and validate specifically but then we are just trying to cram the framework in the code?
2. Forced to use bean validations deeper in the code because the rest entrypoint depends on it to 
throw BadRequest when a constraint validation occurs
   - The rest endpoint would return a 500 internal error instead if we would not use 
     a bean validation deeper in the code (using Object.requireNonNull and such)
   Example: 
   ```java
    record HireEmployeeCommand(EmployeeId id, FullName fullName) {}
    record FullName(String firstName, String lastName) {
        public FullName {
            requireNonNull(firstName); //<-- 500 internal error if null
        }
    }
    ```
   - If we would handle requireNonNull and such exceptions to not return a 500 but a BadRequest instead
   then the other uses of requireNonNull (not linked to request validation) would also return BadRequest.
     Example:
   ```java
    record HireEmployeeCommand(EmployeeId id, FullName fullName) {}
    record FullName(String firstName, String lastName) {
        public FullName {
            requireNonNull(firstName); //<-- could handle Require exceptions in ControllerAdvice to return 400 instead
                                       // but not ok because it would not discriminate when validating the request vs just using a FullName deeper in the code 
    
        }
    }
    ```
   - If we would use request validation specific checks, then it still leads to problems because ValueObjects
   used in the command which may be used elsewhere (not in a request). At which point they should not cause BadRequest anymore.

Conclusion is valid annotations are great on request body etc., but must be separated from the rest of the internal code.

## Decision

We will use separate objects and map to separate the "BadRequest" concern from invalid objects created within the normal flow of the code.
The internal objects will use requirements to validate instead of annotation based validations
This will give a maximum response to the user regarding bad requests and maximum security for correct object construction in the code.

## Compliance
ArchUnit check to not use validation annotations in the domain.

## Notes
- Author: Gert Wijns
- Changelog:
    - 0.1 initial proposed version on 2024-12-21
