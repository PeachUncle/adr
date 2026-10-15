# ADR 001: Frontmatter Validation Architecture

## Status

Accepted

## Context

MDBook documents often use YAML frontmatter to store metadata about chapters. This metadata can include:
- Title and description
- Tags and categories
- Status (draft, published, etc.)
- Author information
- Related documents

Without validation, frontmatter can become inconsistent across a book, leading to:
- Missing required fields
- Incorrect data types
- Inconsistent naming conventions
- Broken integrations with downstream tools

## Decision

We will implement an MDBook preprocessor that:

1. **Validates frontmatter against a JSON Schema** - Using the `jsonschema` crate for schema validation
2. **Supports two modes**:
   - `validate`: Report errors without modifying content
   - `fix`: Attempt to fix issues automatically
3. **Loads schemas from flexible sources**:
   - HTTP/HTTPS URLs for remote schemas
   - `file://` URLs for local schemas
4. **Configures behavior via `book.toml`**:
   - Schema location
   - Processing mode
   - Fail-on-error toggle

### Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   MDBook    │────▶│ Preprocessor │────▶│ Schema Loader   │
│             │     │              │     │ (HTTP/File)     │
└─────────────┘     └──────────────┘     └─────────────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │ Chapter      │     │ Compiled Schema │
                    │ Processing   │◀────│ (jsonschema)    │
                    └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Validate or  │
                    │ Fix Mode     │
                    └──────────────┘
```

### Data Flow

1. MDBook invokes preprocessor via stdin/stdout JSON protocol
2. Preprocessor loads configuration from `book.toml`
3. Schema is fetched and compiled once
4. Each chapter is processed:
   - Extract YAML frontmatter
   - Parse as JSON value
   - Validate against schema
   - In fix mode: apply corrections
   - In validate mode: collect errors
5. Return modified book or fail with errors

## Consequences

### Positive

- Consistent frontmatter across all chapters
- Early detection of metadata issues
- Self-documenting schema defines expected structure
- Compatible with existing JSON Schema tooling

### Negative

- Additional build dependency
- Network requests for remote schemas (mitigated with caching)
- Limited fix capabilities for complex schemas

### Neutral

- Authors must learn JSON Schema format
- Schema must be maintained alongside book
