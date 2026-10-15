# `SeqMember` construction

## Status

Accepted

## Context

We need consistent handling for `SeqMember` constructors that will allow flexibility to end users but also avoid unnecessary complexity. This implies a consistent construction interface across all `SeqMember`s.

Generally speaking `SeqMember`s will not be constructed by the end user, due to the ease with which this would allow inconsistent validation to creep into a project. Therefore `SeqMember`s can be expected to be primarily created by two entities:
- `Sequence`s (as part of the creation of a sequence)
- `SeqMember`s

Since `SeqMember`s are immutable, creating a copy of a `SeqMember` is not desirable if no changes are expected; this indicates the need for a `SeqMember`.from()` method which will trap any case where undesirable duplication of entities would be possible. Examples of these might include:
- Creation of a `SeqMember` from another `SeqMember` when the validator has not changed
- Mapping operations on a Sequence that only change some `SeqMember`s

In cases where this is not possible, we should use a constructor method rather than an unnecessary wrapping around one. Examples of this might include:
- Creation of a `SeqMember` from another `SeqMember` when the validator has changed
- Creation of a `SeqMember` from an argument containing values

## Decision

`SeqMember` constructors will take as their first argument one of:
- null
  - representing silence
- number
  - representing a single note
- number[]
  - representing a chord
- an object representing the data in a `MelodyMember`
  - representing a chord with duration, velocity and other metadata
- a `SeqMember`

`SeqMember` constructors will take an optional numeric validator as a second argument. If not passed, this will default to an integer validator.

`SeqMember`s will also implement a `.from()` method that wraps the constructor. This will take the same first argument, but the second argument's behaviour when not passed is slightly different:

If the first argument is a `SeqMember` or an object containing a `SeqMember` in its `pitch` property, the second argument will default to the validator extracted from the first argument, otherwise it will default to an integer validator. This is to ensure that `SeqMember`s created from other `SeqMember`s do not require special handling when the validator from the original `SeqMember` should be inherited.

In addition, the `.from()` method will attempt to avoid creating new `Sequence Member`s, by
- If creating a `SeqMember` from the same type of `SeqMember`, it will reuse the existing object unless the validator has changed.
- If creating a `SeqMember` from an object containing a `SeqMember` in its `pitch` property, that object will be reused unless the validator has changed.

## Consequences

- Constructor methods are somewhat more complex as they have to handle any of five input types
- It should be easier to create `Sequence`s from a varity of input data, with no need to create a numeric `Sequence` and then convert to a `Melody`.
- There should be no need for factory methods to create `SeqMember`s.
- It should be harder for end users to write faulty `SeqMember` manipulation that tries to convert non-integer validation to integer validation
- The library will need to choose between `new SeqMember()` and `SeqMember.from()` as appropriate.
