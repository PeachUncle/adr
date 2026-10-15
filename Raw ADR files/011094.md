# ADR 015 - String Concatenation Operator

### Status: Accepted

### Josh Holbrook

## Context

### Atto

While researching [fantasy consoles](https://github.com/paladin-t/fantasy), I learned about a BASIC implementation called [Atto](https://atto.devicefuture.org/). In its ["from BASIC" doc](https://github.com/devicefuture/atto/blob/main/docs/frombasic.md), it mentions that it uses `;` as its string concatenation operator.

This seems like an odd decision. But it makes sense when you remember that `print` in traditional BASIC use `;` to separate expressions. As I understand it, this is ad-hoc syntax in those commands. What Atto does here is take this syntax and _generalizes_ it. That makes it a _very_ interesting and clever design choice.

### Matanuska BASIC's Current Behavior

Currently, Matanuska BASIC treats `+` as a concatenation operator. This isn't an unusual choice - BASIC8 goes this route, for example. It's also consistent with many modern languages, such as Python.

### Traditional BASIC Behavior

The [ECMA-55 Standard](https://ecma-international.org/publications-and-standards/standards/ecma-55/) describes `;` as _solely_ a mechanic within `print` statements. Other statements which similarly take multiple arguments use `,` to separate them. In fact, `print` will allow expressions to be separated by `,` as well, but treats `,` and `;` differently - put a pin in that.

The specification for `PRINT` is... interesting. It specifies fixed-width "zones" for print output within a fixed-width "margin". The specification ensures that numbers can be formatted in a way where they'll always fit within one of these zones. It then specifies that, while `;` is treated as a concatenation operator, `,` generates enough space to align the following value to the next zone. `TAB(<n>)` is treated as _special syntax_ which "tabs over" `n` number of zones. If a print statement _ends_ in a `;` or `,`, a newline is _not_ generated and the _following_ print statement appends to the end of that line. Finally, if a print statement has enough values that it overflows the margin (or outputs a string which is long enough to do the same), it inserts newlines as-needed to avoid clipping.

## Decision

Matanuska will continue to use the `+` operator for general purpose string concatenation.

First, `+` is common and well-understood in many modern languages, while `;` would be considered strange and unusual. Honestly, that's enough.

But second, `;` isn't treated as a concatenation operator in traditional print statements, as much as it is treated as special syntax for formatting print output - and it's odd syntax at that. Rather than implement `;` as a general purpose string concatenation operator, I'd rather leave print statements as a potential odd duck - or possibly avoid traditional semantics altogether, in favor of either `echo`-like behavior or shell-like string "templating".
