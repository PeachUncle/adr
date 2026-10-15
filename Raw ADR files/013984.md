# ADR-003: Message Format

## Status

Accepted (Revised)

## Context

We needed a message format that:

- Is human-readable and human-writable
- Supports structured metadata for machines
- Allows flexible body content
- Works well with LLMs (AI readability)
- Avoids the complexity of email's MIME format

### Previous Decision

Originally chose YAML front matter (`---` delimiters). This worked but had limitations:

- YAML is indentation-sensitive (problematic for LLMs)
- JSON brackets are hard for LLMs to match
- No clear type hints for body format

## Decision

Use XML-style envelope with `<meta>` block and flexible body.

## Format Specification

```
<meta type="yaml">
...yaml key-value pairs...
</meta>

...body content (markdown by default)...
```

### Rules

1. `<meta>` block is required
2. `type` attribute is optional (defaults to `yaml`)
3. Everything after `</meta>` is the body
4. Body is markdown by default
5. Use `<body type="...">` for non-markdown body content

## Examples

### Simple Message

```
<meta>
id: msg123
from: @alice/acme.ping
to: @bob/other.ping
timestamp: 2024-01-03T10:00:00Z
signature: ed25519:a1b2c3...
type: messaging.message.v1
</meta>

Hey Bob,

This is **markdown** by default.
```

### Explicit Meta Type

```
<meta type="yaml">
id: msg123
from: @alice/acme.ping
</meta>

Body here.
```

### Non-Markdown Body

```
<meta>
from: @acme.ping
in-reply-to: req123
</meta>

<body type="yaml">
keys:
  - kty: OKP
    crv: Ed25519
    kid: laptop
    x: a1b2c3...
</body>
```

### RPC Request (No Body)

```
<meta>
id: req123
from: @bob/other.ping
method: keys
params:
  address: @alice
</meta>
```

## Rationale

### Why XML-Style Tags?

| Advantage | Details |
|-----------|---------|
| LLM-friendly | Self-describing tags, no bracket matching |
| Clear boundaries | `<meta>` and `</meta>` are unambiguous |
| Type hints | `type` attribute declares format |
| Flexible | Works with any content in body |

### Why Not Pure YAML Front Matter?

| Issue | Details |
|-------|---------|
| Indentation | YAML spaces are significant, easy to mess up |
| LLM errors | AI models struggle with consistent indentation |
| No type hints | `---` doesn't indicate format |

### Why Not JSON?

| Issue | Details |
|-------|---------|
| Bracket matching | LLMs often miss closing `}` or `]` |
| Escaping | Quotes in content need escaping |
| Human readability | Less natural to write |

### Defaults

| Element | Default |
|---------|---------|
| `<meta type="...">` | yaml |
| Body (no `<body>` tag) | markdown |

## Consequences

- Messages use `<meta>` blocks for metadata
- Any text editor can create valid messages
- LLMs can generate messages reliably
- Body defaults to markdown (human-friendly)
- Structured data uses `<body type="yaml">` or similar
