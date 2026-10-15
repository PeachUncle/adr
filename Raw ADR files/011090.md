# ADR 009 - Type Awareness in The Compiler and Runtime

### Status: Accepted

### Josh Holbrook

## Context

In [ADR 007](./007-type-semantics.md), we specified the type semantics for operations on dissimilar types. The takeaway from this ADR is that there are many such operations which are invalid, and the ones which _are_ valid require implicit type casting. In other words, the types of values matter.

In [ADR 008](./008-sigils.md), we decided to implement a standard BASIC model for manifest data types. To review, primary variables are typed using a postfix sigil, but those sigils don't distinguish them from arrays and functions. That means that we _sometimes_ have compile time type information.

When available, the advantages of manifest data types are two-fold.

First, the compiler can implement type checks - in other words, this introduces type safety. This can be accomplished by maintaining a stack of types in the compiler and comparing them at compile time. When the compiler detects an operation is being executed on incompatible types, it can throw an error prior to runtime execution. This is generally considered a better user experience.

Second, the runtime can assume data types and use type-specific bytecode instructions. In a fully typed language like Java, the runtime can implement type-specific instructions. For example, suppose we are executing `1 + true` and that our language casts boolean arguments to integers. In a dynamic typing regime, we would implement a generic `ADD` instruction that checks the types of the two values and casts `true` to `1` on the spot. But if we know a priori that `1` is an integer and `true` is a boolean, we could instead execute `CAST_INT_TO_BOOL, ADD_INTS`, and these instructions can assume that their arguments are a bool and two ints respectively. In contrast, a dynamically typed language _must_ use a generic `ADD` instruction.

The trade-off here is that typed instructions require _more_ instructions, but each instruction requires less work. Unfortunately, a partially typed runtime would mean that we'd need to implement _both_ typed and dynamic instructions - in other words, we would need to implement `CAST_BOOL_TO_INT` and `ADD_INT` for when types are known, and generic `ADD` for when types are unknown. This may still allow for optimized execution in cases where types are known, assuming that switch statements are cheap, but the runtime becomes undenably more complex.

The alternative is to implement a dynamic runtime, and only check types in the compiler. This would mean instructions would still need to check types and do implicit casting, but it would also mean a simpler instruction set - and remember, this doesn't preclude the compiler implementing partial type safety. Note also that a fully dynamic runtime can be an incremental step. If we implement a fully dynamic runtime, we can always add type-specific instructions later.

## Decision

First, we will implement type checks in the compiler by simulating a stack. These types will initially support primary types and an `Any` type. This will allow the compiler to detect and throw type errors, giving an improved user experience.

However, this work may be deferred until an unspecified date. It's more important that runtime behavior is correct than it is that type errors are caught in the compiler, and implementing it is relatively challenging - and low priority.

Second, we will _not_ initially support typed operations in the runtime. This will likely manifest in a slower runtime as compared to one that _can_ assume types. But will also keep the scope of the initial implementation smaller, as well as leaving the door open for typed operations in the future.
