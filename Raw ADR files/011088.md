# ADR 007 - Type Semantics for Primary Types

### Status: Accepted

### Josh Holbrook

## Context

Matanuska is currently aware of the following types:

- integers
- reals
- booleans
- strings
- nil

It also supports a number of binary and unary operations, including math operators (+, -, \*, /), logical operators (`and`, `or`, `not`), and various comparison operators (==, <>, >, <, >=, <=).

In some cases, the behavior is easy and obvious. For example, adding two integers together does the right thing by default. However, many other cases are _not_ obvious. For example, what should happen if you add an integer and a string? Python will throw a `TypeError`, but JavaScript will cast the integer to a string and concat the results.

In addition, cast to booleans (ie, "truthiness" and "falsiness") differs significantly between languages.

This ADR attempts to iron out the expected semantics.

### Concepts

This ADR invokes a number of concepts - it's worth going over them now.

**Casting** is, for the purposes of this ADR, the action of implicitly converting a value into a value of another type, in order to facilitate an operation. For example, when adding a boolean and a real, the boolean will be cast to a real and then added to the other argument. In general, values are cast before an operation so they're the same type.

In theory, these casting rules could be bespoke to every combination of types. However, in practice, one type is cast to the other type, based on what I'm calling **type precedence**. Consider the previous example - the boolean was converted to a real, because the type of real has a "higher precedence" than the boolean. I'm not sure if this concept is widely accepted. However, at least one language, [T-SQL](https://learn.microsoft.com/en-us/sql/t-sql/data-types/data-type-precedence-transact-sql?view=sql-server-ver16), implements something similar.

**Conversion** is similar to casting, but is always explicit and more relaxed. Conversion is not used in operators, but will come into play in the future if and when Matanuska BASIC implements keywords for doing explicit conversions.

**Truthiness** and **Falsiness** have to do with whether a value "counts" as true or false, respectively, when executing logic operations. This is similar to the result of converting a value into a boolean, but is distinct from a definition standpoint.

### Behavior of Other Languages

#### Python

Python generally allows implicitly casting booleans to integers and integers to floats. Its booleans cast to `0` for False and `1` for True. However, it will not cast non-string values to strings.

Strings support `+` for concatenation, and comparison operators through lexicographical sort order.

Python treats non-zero integer and float values as truthy. It treats empty strings as falsey, and non-empty strings as truthy.

While arrays are out of scope of this discussion, Python also allows lists to be concatenated with the `+` operator. It also seems to allow comparisons through element-wise comparison similar to lexicographical sorts, and similarly treats non-empty lists as truthy.

#### JavaScript

JavaScript's behavior is subtly different from Python. The biggest difference is that it will gleefully cast values to strings in order to make an operation succeed. But its behavior in edge cases is tough to predict - often, you have to try it to find out.

In terms of truthiness and boolean casts, JavaScript treats booleans and numbers similarly to Python - though, note, it only has a `number` type, with oddball semantics of its own. However, its philosophy for truthiness of string and Array values differs significantly, in that any defined Object is truthy.

The trade-off is that Python allows you to check for empty strings/lists with an `if value:` check, but requires `if value is not None` when definition is important - JavaScript flips this, with `if (value.length) {` and `if (value) {` respectively.

#### MSX BASIC

Experimenting in an MSX emulator, MSX BASIC appears to cast ints to floats, but does not cast values to string. Given its rudimentary capabilities, it's not believed to have any interesting behavior in terms of its strings and dims - typically, operations are achieved through piecewise iteration and built-in functions.

It's worth noting that MSX BASIC treats non-zero integers and floats as truthy, the same as Python and JavaScript, but defines FALSE and TRUE as 0 and -1, respectively. This is presumably because of some two's compiliment behavior in signed values.

## Decision

Matanuska BASIC will implement behavior very similar to Python.

Note that array behavior is considered out of scope for this ADR, though their behavior will likely be consistent with strings.

### Casting

Casts between booleans, integers and floats will behave the same way as Python. This behavior is consistent across all three languages discussed, and is non-controversial.

Numerical values will not be implicitly cast to strings. This behavior causes a lot of confusion in JavaScript, and not allowing it is also consistent with MSX BASIC.

### Conversion

Conversions will implement the same internal API as casts, but the specific rules are out of scope for this ADR.

### Truthiness and Falsiness

Non-zero number-like values and non-empty strings will be treated as truthy. Zero number-like values, empty strings and `nil` will be treated as falsey. In other words, truthiness and falsiness will follow rules similar to Python.

### Casting Rules in Binary Operations

Binary arithmetic operations will implement type precedence in the following order, from least to greatest:

1. Booleans
2. Integers
3. Reals
4. Strings
5. All other types

Binary operations will find the type with the highest precedence, cast the lower precedence operand to that type, and then execute the operation against similar types.

This has less flexibility than a full matrix between types and casts, but it should be much easier to reason about without causing too many edge cases.

### Allowed Binary Operations

Most binary arithmetic operations are allowed for booleans, integers and reals. Addition (`+`) is allowed for string as a concatenation operator, but other operations are (for now) invalid.

### Dissimmilar Types in Comparison Operations

For `==` and `<>`, dissimilar types will be considered unequal. For all other comparison operators, comparisons between dissimilar types will be considered invalid.

### Comparison Sort Order

Strings will support lexicographical sorting. This is consistent with Python and JavaScript.
