# ADR 008 - Sigils

### Status: Accepted

### Josh Holbrook

## Context

`Writing Interactive Compilers & Interpreters` introduces the concept of _manifest data types_. This means that the type of a variable is known at compile time.

BASIC has manifest data types, insofar as the language distinguishes between numbers and string variables. Syntactically, it does this by _postfixing_ identifiers with a [sigil](https://www.perl.com/article/on-sigils/). By doing this, and by using distinct syntax for defining other types, the compiler is able to track and enforce the type of a variable throughout execution.

From a compiler perspective, this allows for the interpreter to use opcodes which can _assume_ the type of a value. For instance, suppose you want to add two values. Without manifest types, you would need a `ADD` operation which inspects the types of the values, and decides what to do accordingly. With manifest types, however, you could implement an `ADD` operation which only works for numbers, a separate `CONCAT` operation for strings, and a `NUM_TO_STR` operation to convert numbers to strings. For example, the bytecode for `one + $two` may look like:

```
# stack: []
GET_GLOBAL_INT &one
# stack: [1]
NUM_TO_STR
# stack: ["1"]
GET_GLOBAL_STR &two
# stack: ["1", "2"]
CONCAT
# stack: ["12"]
```

In other words, manifest types can help avoid `typeof` and `instanceof` checks at runtime.

### The Decisions of MSX BASIC

Between `Modern MSX Game Development` and the [MSX2 Technical Handbook](https://konamiman.github.io/MSX2-Technical-Handbook/md/Chapter2.html), we can discover these rules:

1. Integers in MSX BASIC have a `%` sigil.
2. Singles in MSX BASIC have a `!` sigil.
3. Doubles in MSX BASIC have a `#` sigil.
4. Strings in MSX BASIC have a `$` sigil.
5. Variables defined without a sigil have a _configurable_ default type. For
   MSX this is initially configured to doubles, though it's common practice to
   change it to integers. This is widely considered to be a footgun.
6. Arrays and functions _by convention_ have the same postfix sigils as their
   _return values_ - but not always! While the syntax doesn't show their type
   in context, they are defined within the program using unambiguous syntax.
7. Arrays and functions in call signatures, however, _are_ ambiguous, since
   the relevant definition doesn't exist in the function. Within functions,
   types are _not_ completely manifest.
8. Channels aren't variables, but are _prefixed_ with `#` when specified.
9. MSX BASIC doesn't have a dedicated boolean type. Instead, the integer `0`
   is treated as `false` and the integer `-1` is treated as `true`. This is
   most apparent in the return values of comparison operators.
10. Variables of different types can reuse the same names. The correct variable
    is fetched based on the compiler's knowledge of the type.

A few aspects of this are worth diving into in more detail.

### Types in Call Signatures

In the context of a program, the type of an array or function is unambiguous. However, in the context of a call signature, they typically _are_ ambiguous. Arrays and functions don't have sigils, aside from a convention of including a sigil for the inner type. In effect, call signatures appear to be untyped in many implementations of BASIC.

In addition, a callable may return a void type. There is, of course, no sigil for identifying a void type.

Were we to stick to the syntax of a typical BASIC, we would need to support untyped call signatures and return values. This is the most straightforward to implement, as it doesn't require inventing new syntax - simply check the types of values where used.

There are, however, a few options for syntax extensions:

1. Implement prefix sigils for functions and arrays. There is already an
   example of prefix sigils for channels, and this would allow reuse of sigils
   already used in a postfix context.
2. Use sigils within a call syntax: `foo$(%)`. Combined with a prefix sigil,
   this may look like `@foo$(%)` or `&foo!($)`.
3. Require that functions without a sigil return `void`

### Untyped and Union Identifiers

Variables and function arguments in MSX BASIC don't support unions. In other words, a variable can't be either an integer _or_ a string. However, as mentioned, function arguments are effectively dynamically typed - and many _native_ functions in BASIC _can_ accept union or `any` types as arguments.

One option for a syntax extension to support these use cases is to list multiple sigils for union types. For instance, `ident%!` could be a union of integers and reals. In this case, ordering may be a linting rule.

Another option is to allow completely untyped identifiers. These are two major options:

1. Use a dedicated sigil. Unfortunately, many of the natural sigils - such as
   `?` - are taken. `_` may work, if identifiers are modified to disallow that
   character at the end.
2. Use no sigil at all. Given the behavior of traditional BASICs of
   auto-assigning a type, this may be a natural choice. However, it's less
   explicit, and may discourage users from using types.

## Decision

For primary types, Matanuska BASIC will begin by broadly implementing the same decisions as MSX BASIC, with the following differences:

1. Since we only support Reals, use the `!` sigil exclusively.
2. Do not implement default default types for identifiers without a sigil.
3. Booleans will use a `?` sigil.
4. In call signatures, no sigil will mean the value is untyped.

That is:

| sigil    | type |
| -------- | ---- |
| `%`      | int  |
| `!`      | real |
| `?`      | bool |
| `$`      | str  |
| `<none>` | any  |

For now, we will assume that sigils in dims reflect their inner type, and that sigils in functions reflect their return type. When functions have no sigil, they will be expected to only use bare or implicit returns - ie, have a `void` return type.

However, we will also assume that call signatures of functions are untyped. While functions are likely going to remain unimplemented for some time, further decisions in the compiler and runtime will be made under this assumption. When functions are to be implemented, these decisions _may_ be revisited.

All syntax extensions aside from those already mentioned will be deferred until a later date. For instance, identifiers - for now - will only be allowed to support one type.

These decisions are being made with the following goals:

1. Avoiding novel syntax extensions. Syntax is really hard to get right, and
   BASIC's syntax limits our ability to extend it in a comfortable manner.
2. Keep implementation scope sensible. If we don't commit to building full
   typing, we're not committed to building the features in the interpreter.
