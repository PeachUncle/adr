# ADR-0001: Custom Jinja2 Delimiters for LaTeX

## status

Accepted

## date

2024-10-18

## context

LaTeX heavily uses curly braces `{}`, which conflicts with default Jinja2 delimiters (`{{`, `{%`, `{#`). This makes it impossible to use standard Jinja2 syntax in LaTeX templates without extensive escaping.

Example conflict:

```latex
% LaTeX code with Jinja2 would be ambiguous
\textbf{Hello, {{ name }}}  % Is {{ part of LaTeX or Jinja2?
```

## Options Considered

### Option 1: Backslash-based delimiters

Use `\VAR{}`, `\BLOCK{}`, `\COMMENT{}`.

**Pros:**

- Looks like LaTeX commands
- Clear visual distinction

**Cons:**

- Verbose (more typing)
- Backslash conflicts with LaTeX escaping
- Harder to read in templates

### Option 2: Parenthesis-based delimiters

Use `(((`, `((*`, `((#`.

**Pros:**

- Short and easy to type
- No conflict with LaTeX (triple parentheses not used)
- Easy to read
- Familiar to Python developers

**Cons:**

- Non-standard (requires documentation)

### Option 3: XML-style delimiters

Use `<!--VAR-->`, `<!--BLOCK-->`.

**Pros:**

- Clear boundaries

**Cons:**

- Very verbose
- Conflicts with potential HTML output

## Decision

Use parenthesis-based custom delimiters:

- Variables: `((( variable )))`
- Blocks: `((* if condition *))`
- Comments: `((# comment #))`

Validated against all `.tex` files in Awesome-CV repository. No conflicts found.

## Consequences

### Positive

- Clean, readable templates
- No escaping needed for LaTeX braces
- Short syntax reduces typing
- Compatible with all tested Awesome-CV files

### Negative

- Non-standard syntax requires documentation
- IDE support may be limited (no syntax highlighting)
- New contributors must learn custom delimiters

## Implementation

```python
def create_latex_environment():
    env = Environment(
        loader=PackageLoader('awesomecv_jinja', 'templates'),
        block_start_string='((*',
        block_end_string='*))',
        variable_start_string='(((',
        variable_end_string=')))',
        comment_start_string='((#',
        comment_end_string='#))',
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    return env
```

## References

- [Jinja2 Custom Delimiters](https://jinja.palletsprojects.com/en/3.1.x/api/#jinja2.Environment)
- [LaTeX Special Characters](https://en.wikibooks.org/wiki/LaTeX/Special_Characters)
