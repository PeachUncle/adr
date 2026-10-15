# `Sequence` construction

## Status

Accepted

## Context

We need consistent handling for `Sequence` constructors that will allow flexibility to end users but also avoid unnecessary complexity. This implies a consistent construction interface across all `Sequence`s.

There are generally two types of `Sequence` construction:
- Creating `Sequence`s afresh, typically implemented by an end-user.
 - These are likely to have a more free-format input (pitches, objects, Sequences and SeqenceMembers).
- Creating `Sequence`s from another `Sequence`, typically implemented within Palestrina.
 - These can always be created from a series of SeqMembers (and a `NumericValidator`).

Some notes:
- When creating `Sequence`s from afresh, an additional complexity arises with the `.to{NumSeq,NoteSeq,ChordSeq,Melody}()` methods. This requires the injection of references to creation methods for these types of `Sequence`--though this could perhaps be avoided with a `.to()` method that takes a `Sequence` constructor as an argument.
- Unlike in the case of `SeqMember`s, it should be comparatively rare that a `Sequence` is created from an identical `Sequence`. There simply aren't many use cases for this, since `Sequence`s are immutable (except for the control flow methods). Thus a `Sequence.from()` optimisation to ensure fewer new entities are created is of much lower value than for  `SeqMember`s.
- Many `Sequence` modifications involve either removing members or adding new members at specified locations within the `Sequence`. It is not performance-optimal to revalidate the unmodified members in these cases; instead the new members (if any) should be validated, and the new `Sequence` createed without performing validation.

This suggests that the `Sequence` constructor should *not* perform validation on entities, but for any situation where an end user is the one creating a `Sequence`, validation should be performed on its argument. Which argues for a non-constructor method for `Sequence` that requires a validator being the only creation method available to end users, and the constructor allowing the absence of validation as an optimisation.

## Decision

`Sequence` constructors should take only the following argument type as a first argument:
- an array of any the appropriate `SeqMembers` for the `Sequence`.

- `Sequence` constructors should take a `Metadata` object as its second argument. This will not be used to validate the `Sequence` contents but purely to identify the validator to be used on any subsequent operations involving the `Sequence`.

An alternative construction method should be available:

The first argument to it will be:
- an array containing any number of:
 - null
 - number
 - number[]
 - object representing the data in a `MelodyMember`
 - `SeqMember` of any type
or:
- a `Sequence` of any type

The second argument to it will be an optional numeric validator. If this is not passed, it will default to the default integer validator.

This method will convert and validate the first argument, create Metadata for the second argument (including the validator and references to the `Sequence` conversion methods), and then call the constructor function with these arguments.

## Consequences

- Constructor methods are simpler as they do not need to validate beyond that all members are `SeqMember`s.
- The alternative construction method will be used by all methods that allow `Sequence` creation not from other `Sequence`s.
- Methods that can be optimised so as to not require revalidating known good data should be so optimised.
- This decision should be re-evaluated after implementation to determine if it is working as well as intended.
