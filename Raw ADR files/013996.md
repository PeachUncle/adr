# Use spring message validation for type mismatches when binding to forms

* Deciders: cwood
* Date: 2020-07-07

## Context and Problem Statement

When binding string values from a POST request to Integer or BigDecimal fields on a form object, the default error message
in the binding result for the field is an exception stacktrace informing that the value couldn't be converted to the required object type. 

We need to find a reusable, low-effort solution to this problem that provides user-readable error messages in these situations. 

## Considered Options

* handle in validator class using new validator utils method
* use String for all number-related form variables and convert them in the relevant services (after validating that they can be converted properly in the validator)
* override Spring default message for Integer/BigDecimal validation

## Decision Outcome

Chosen option: "override Spring default message...", because it is the lowest effort, lowest impact way of achieving the desired behaviour. Although
in its current form we can't refer to the specific field that is in error in the message (per GDS guidelines), it is hoped that users wouldn't often enter a
non-numeric value in a numeric field if the screen guidance/labels etc imply that a number is required.

## Pros and Cons of the Options

### handle in validator class using new validator utils method

* Bad, because the error is already present on the binding result by the time the validator is called, would mean manipulating the result
* Bad, because it has to be implemented in every existing validator and every future validator

### use String for all number-related form variables

* Good, because it prevents stack traces appearing as error messages
* Bad, because requires extra validation conditions for every integer or decimal field
* Bad, because requires extra conversion back and forth between form objects and entities
* Bad, because would need to be retrospectively applied to our reasonably-sized codebase

### override Spring default message

* Good, because it prevents stack traces appearing as error messages
* Good, because it can be applied everywhere with minimal effort
* Good, because it standardises messaging for type mismatch errors, no chance of inconsistency
* Bad, because we can't refer to the field prompt in the error message easily without implementing targeted custom messages for
each affected field, which could end with the custom message and the onscreen prompt getting out of sync
