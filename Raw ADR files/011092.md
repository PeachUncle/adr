# ADR 013 - If, Then and Else Syntax

### Status: Accepted

### Josh Holbrook

## Context

In order to implement conditional branching, we need to specify a syntax for if, then and else. We would like this syntax to match the expectations of a period-appropriate BASIC, but we would also like it to support modern idioms, particularly multi-line branches.

MSX BASIC supports the following forms:

- `IF <condition> THEN <lineNo | instructions>`
- `IF <condition> THEN <lineNo | instructions> ELSE <lineNo | instructions>`
- `IF <condition> GOTO <lineNo>`
- `IF <condition> GOTO <lineNo> ELSE <lineNo | instructions>`

When supplied a lineNo, BASIC will jump to that line. Otherwise, it will run the listed instructions.

Notable is that MSX BASIC does _not_ support multi-line if statements. For an example of a BASIC which _does_ support them, we can look to BBC BASIC. BBC BASIC supports the following:

```
IF <condition> THEN
  ...
ELSE
  ...
ENDIF
```

Also notable is that neither MSX BASIC nor BBC BASIC has an `else if` - though, MSX BASIC likely parses `if <cond> then <ins> else if <cond> then <ins> else <ins>` as `If(cond, ins, If(cond, ins, ins))`, where the second `if` is simply another instruction.

## Decision

We will support two kinds of "if"s: single-line instructions (called `ShortIf` in the AST) and multi-line collections of instructions (made up of the instructions `If`, `ElseIf`, `Else` and `EndIf`. Single-line if instructions may be evaluated as commands.

Single-line if statements will initially support the following forms:

- `if <condition> then <instructions> endif`
- `if <condition> then <instructions> else <instructions> endif`

In these forms, `instructions` may not contain if/else/endif instructions used in a multi-line context. They may, however, support nested short ifs - that is, `if` and `else` are allowed if they're closed with an `endif` on the same line.

Multi-line if blocks will support forms such as the following:

```
<line_no> if <condition> then
  <lines>
<line_now> else if <condition> then
  <lines>
<line_no> else
  <lines>
<line_no> endif
```

`else if` will be treated the same as in JavaScript, or like `elif` in Python.

### What's Not Supported

#### GOTOs

These forms don't support line numbers for `goto`. That decision will be made in the future, when `goto` is existing functionality.

#### Else If in Short If

As noted, "long if" supports `else if`. However, "short if" currently parses `if <cond_a> then <then_a> else if <cond_b> then <then_b> endif endif` as containing a nested "short if" within an "else" block, and `if <cond_a> then <then_a> else if <cond_b> then <then_b> endif` is considered unterminated. This is because the whitespace in a "long if" is significant!

This issue reveals a wart in Matanuska BASIC's syntax - and, in fact, BBC BASIC does not support an analogous construction.

One way to address this may be to introduce a new keyword, `elif`, that operates like the corresponding keyword in Python. In fact, if that were the case, we would likely deprecate `else if` in long ifs in favor of `elif`.

There's an argument to be made for not supporting "else if" in Matanuska BASIC at this time, in order to avoid such a deprecation. That would be consistent with other decisions made in this ADR. However, unlike those decisions, this one doesn't significantly complicate the parser. Moreover, there isn't a strong motivation to use `else if` on its own line to represent a discrete `if` inside a `else` block, therefore deprecation is anticipation of such a deprecation. That would not expected to be painful.

#### Unterminated "Short If" and Multi-Line with Then on Same Line

Also not supported are an unterminated short if, as in MSX BASIC and BBC BASIC:

```basic
if <condition> then <instructions>
```

and a long if supporting "then" instructions on the first line, which is not supported by MSX BASIC nor BBC BASIC:

```basic
<line_no> if <condition> then <instructions>
<line_no>   else <instructions> endif
```

Allowing one of these forms doesn't strictly rule out the other. But supporting both requires a more complicated grammar. For instance, an implementation supporting both may require lookahead in the compiler, or possibly backtracking in the parser.

Allowing either form exclusively, on the other hand, is relatively straightforward. This means that, while implementing one of them would be easy, it would make it much more difficult to implement the other.

By implementing neither, we leave the door open on this issue.

#### Then on Following Line

Finally, a feature for which support was considered but dropped is starting `then` on the following line, like so:

```
<line_no> if <condition>
<line_no>   then <instructions>
  <lines>
<line_now> else if <condition>
<line_no>    then <instructions>
  <lines>
<line_no> else
  <lines>
<line_no> endif
```

There are aesthetic reasons to support this form. However, allowing it also complicates the parser by introducing a new form for lines:

```
line_with_then := <line_no> then <instructions>
```

with this form only being valid if the _previous_ line contains an `if` statement ending before the `then`. Practically speaking, parsing this form requires maintaining an extra piece of state in the parser - "should we expect a `then`" - and matching it prior to parsing other instructions in those cases. This isn't a heavy lift, but it's _enough_ of a complication that BBC BASIC did not implement it. In our case, we're deciding to leave it out _for now_, so as to not immediately commit to the additional complexity in our parser. It may, however, be introduced in the future.
