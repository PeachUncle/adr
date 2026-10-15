# Configurable Root Command Formats

## Status

Accepted

## Context

CLI applications often have hierarchical command structures like:
- `example` (root command showing help)
- `example one` (subcommand)
- `example two` (subcommand)

Different projects use different conventions for organizing root command documentation:
- **Hugo-style**: `_index.md` (convention from static site generators)
- **Next.js-style**: `index.md` or `<dir>.md` (web routing patterns)
- **Directory-based**: `example/example.md` (self-documenting)

Making this configurable allows integration with existing documentation workflows and tools.

## Decision

Implement configurable root command formats through `root_command_format` setting:

1. **`"directory"`** (default): `example/example.md` with `example/index.md` fallback
2. **`"index"`**: `example/index.md` only  
3. **`"_index"`**: `example/_index.md` only (Hugo-style)
4. **`"hugo"`**: Alias for `_index`

Benefits:
- **Documentation integration**: Same files can drive CLI and docs
- **Team consistency**: Match existing project conventions
- **Migration friendly**: Support multiple formats during transition

## Consequences

### Positive
- Flexible integration with documentation generators (Hugo, Docusaurus, etc.)
- Teams can use familiar conventions from web development
- Easy migration between formats
- Self-documenting directory structure with `directory` format

### Negative
- Additional configuration complexity
- Need to document different formats
- Potential confusion about which format to use

### Implementation

**Configuration**:
```yaml
# .adder.yaml
root_command_format: directory  # directory, index, _index, or hugo
```

**File organization examples**:

Directory format (default):
```
docs/commands/
├── generate.md          # adder generate
├── example/
│   ├── example.md       # adder example (root)
│   ├── one.md          # adder example one
│   └── two.md          # adder example two
```

Index format:
```
docs/commands/
├── generate.md          # adder generate  
├── example/
│   ├── index.md        # adder example (root)
│   ├── one.md          # adder example one
│   └── two.md          # adder example two
```

Hugo format:
```
docs/commands/
├── generate.md          # adder generate
├── example/
│   ├── _index.md       # adder example (root)
│   ├── one.md          # adder example one  
│   └── two.md          # adder example two
```

**Root command behavior**:
- Shows help text from markdown content
- Lists available subcommands
- Can have its own flags and arguments (for shared behavior)

## Migration Path

Projects can migrate between formats by:
1. Moving/renaming root command files
2. Updating `root_command_format` in config
3. Regenerating commands

Example migration from Hugo to directory format:
```bash
# Move files
mv docs/commands/example/_index.md docs/commands/example/example.md

# Update config
# root_command_format: hugo -> root_command_format: directory

# Regenerate
adder generate
```