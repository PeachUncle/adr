# 9. Aggregate creation convention

Date: 2024-02-11

## Status

2024-02-11 accepted

## Context

Having the DDD approach taken, the project stands before the decision covering creating business objects (value objects, aggregate roots) strategy. However, few issues arose instantly during the discussion.

First one: the business layer. We don't want to use constructors. Instead, we should use a method that initializes the instance. That method should be aware of value objects and entities and perform full validation on the input according to the given business rules.

Second one: the repository layer. On the contrary, it shouldn't know anything other than the basic structures and types needed to save the series of events into the database and restore the entire object from the DB's snapshot. Also, the validation shouldn't be triggered in this case, as the database is the ultimate source of truth.

Third one: validation itself. To avoid confusion, we shouldn't duplicate the logic. As much as it's possible, it should be reused for events and initialization.

Several approaches have been thought and considered:
- private constructor that repository would cast to any and execute (a bit hacky, but would work just fine)
- public static method that takes basic types as input and constructs the object using them ("createFromSnapshot"), no validation
- same as above, but extracted into the factory class

## Decision

We'll introduce two public static methods on aggregate roots: `create` and `restoreFromSnapshot`.

`create` understands the business layer types and initializes the object with the input data, triggering the validation upon then beforehand. It also commits the creation event to the aggregate root (with the same data, of course).  `create` follows the result object pattern.

`restoreFromSnapshot` populates the aggregate root object using the basic types (in its declaration, it isn't aware of any business types). It doesn't create any event, and thus - no validation is triggered. It's creating the object while having data from the source of truth.

## Consequences

The solution satisfies all initial conditions:
- Business layer can create aggregate roots using a method that validates input and understands business types.
- Business layer can utilize the same validation logic for initialization and applying changes.
- Repository layer can create aggregate roots without both knowing the business types and validation.