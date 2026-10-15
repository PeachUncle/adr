# ADR 016 - ECMA-55 Compliance

### Status: Accepted

### Josh Holbrook

## Context

I discovered in my research that there is an actually an old (and largely obsolete) ECMA standard for a minimal BASIC implementation, which can be found here:

<https://ecma-international.org/publications-and-standards/standards/ecma-55/>

I also discovered two [fantasy console](https://github.com/paladin-t/fantasy) implementations which discuss adherence to ECMA-55:

- [M16BASIC](https://itch.io/t/966540/preliminary-manual), which describes specific deviations from the standard
- [bas55](https://jorgicor.niobe.org/bas55/bas55.html), which purports to be spec-compliant and not much else

Having read the specification - it's about 30 pages - I can say that, generally speaking, it's not worth trying to adhere to in any meaningful way.

One obvious deficit is that its treatment of variables and values is extremely limiting, and even 80s era BASIC implementations deviated from it significantly. In fact, ECMA-55 only supported strings and numbers, while many other dialects support distinct integers and floats.

It also, naturally, has specifications for error handling which would be considered odd by today's standards. It doesn't specify exceptions, of course. But, for instance, its _recommendation_ for integer overflows is to assign an "infinity" value and move forward.

It does, however, have a few areas worth referencing in the future.

### Number Literals

The standard includes a specification for how to parse number literals. It only supports decimal representations - no hex or binary - but it does include a specification.

Matanuska's current behavior isn't specified. The scanner converts strings into numbers with `parseInt`, and otherwise appears to follow a subset of a number formatting standard that's compatible with JavaScript. It would be worth considering a specification for numbers.

Of course, there are many other places to look than ECMA-55. JavaScript's numbers aren't particularly controversial - that specification, or Python's, would suffice. Alternately, VB.NET could be a good source of inspiration.

It's unlikely that ECMA-55 would play a _major_ role in informing such a number literal specification. But it could be a useful refrence, and may not be a stretch to support as a subset.

### Built-In Functions

ECMA-55 includes a very short list of implementation-supplied functions. Supporting these would likely not be difficult, and in fact they may make for a good start.

### GOTOs

In general, I don't like the semantics of BASIC's GOTOs, and have no interest in adhering to any given standard. That said: the ECMA-55 standard specifies _two_ keywords (`go to`) rather than one (`goto`). I don't actually know if that's common in 80s era BASICs. But supporting it wouldn't be difficult either.

### FOR/NEXT

The standard includes a tight specification for `FOR` and `NEXT`. The `FOR` statement in BASIC is relatively uncontroversial, and I _do_ intend to develop at least a variant that's more or less a straight cut. It could prove to be a useful reference.

### DATA, READ and RESTORE

A feature that I've seen in many BASIC implementations, but have had a hard time wrapping my head around, is built around the keywords `DATA`, `READ` and `RESTORE`. Lucky for us, ECMA-55 includes a straightforward explanation of how this works.

This is important, as BASIC doesn't have syntax for array literals - it uses these keywords to fill in the values of an array instead. While I'm heavily motivated to develop syntax for array literals, these keywords are the likely alternative.

### PRINT

As discussed in [ADR 15](./015-string-concat-operator.md), the ECMA-55 standard reveals that `PRINT`'s behavior is bizarre and strange. When deciding how to implement the `PRINT` statement, it will be an invaluable reference.

## Decision

Having read the standard, I do not feel the need to attempt to _adhere_ to it in any way. By extension, I also do not feel the need to _test_ for any particular behavior as informed by the specification.

That said, we _have_ identified some areas where the standard can operate as a useful _reference_. No decisions will be made currently in those identified avenues at this time, but the standard is there when I'm ready.
