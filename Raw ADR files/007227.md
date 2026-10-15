# ADR-008: Replace `cac` with `commander` for CLI

## Status

**Accepted** - October 22, 2025

## Context

The project used `cac` (Command And Conquer) as its CLI framework. While `cac` is lightweight, it had significant issues with TypeScript support and type safety.

### The Problem

**Issues with `cac`:**

1. **Poor TypeScript support**: 52 type errors in CLI code
2. **Weak typing**: Options typed as `any`
3. **No IntelliSense**: IDE couldn't provide autocomplete
4. **Maintenance**: Less actively maintained
5. **Documentation**: Sparse, TypeScript examples lacking

**Example type issues:**

```typescript
// ❌ With cac: No type safety
cli
  .command('generate <input>')
  .option('--output <path>', 'Output path')
  .action((input, options) => {
    // options is 'any' - no type safety!
    const outputPath = options.output; // Could be anything
  });
```

### Alternatives Considered

1. **`cac`** (Current)
   - ❌ Poor TypeScript support
   - ✅ Very lightweight (3.8kb)
   - ❌ Weak community

2. **`commander`**
   - ✅ Excellent TypeScript support
   - ✅ Strong typing with generics
   - ✅ Widely used (30M+ weekly downloads)
   - ✅ Active maintenance
   - ⚠️ Slightly larger (7kb)

3. **`yargs`**
   - ✅ Good TypeScript support
   - ⚠️ More complex API
   - ⚠️ Larger bundle size
   - ⚠️ Overkill for our needs

4. **`clipanion`**
   - ✅ Modern, TypeScript-first
   - ⚠️ Different paradigm (class-based)
   - ⚠️ Less familiar to team

## Decision

**We will use `commander` for CLI functionality.**

### Rationale

1. **Industry standard**: 30M+ weekly downloads, battle-tested
2. **TypeScript-first**: Excellent type inference
3. **Type safety**: Proper option types with generics
4. **Familiar API**: Similar to `cac`, easy migration
5. **Active maintenance**: Regular updates, responsive maintainers
6. **Documentation**: Comprehensive, including TypeScript examples

### Implementation

```typescript
import { Command } from 'commander';

const program = new Command();

// ✅ Type-safe option parsing
program
  .name('@engraph/castr')
  .description('Generate Zod schemas from OpenAPI specs')
  .version(version);

program
  .command('generate')
  .description('Generate Zod client from OpenAPI spec')
  .argument('<input>', "Path to OpenAPI spec (file, URL, or 'stdin')")
  .option('-o, --output <path>', 'Output path')
  .option('--api-client <name>', 'API client name', 'api')
  .option('--export-schemas', 'Export schemas separately')
  .action(async (input, options) => {
    // options is properly typed!
    const config: Config = {
      input,
      output: options.output,
      apiClientName: options.apiClient,
      exportSchemas: options.exportSchemas,
    };
    await generateClient(config);
  });

program.parse();
```

## Consequences

### Positive

✅ **Type safety**: Full TypeScript support with inference  
✅ **Zero type errors**: Eliminated all 52 CLI-related type errors  
✅ **Better DX**: IDE autocomplete and error detection  
✅ **Maintainability**: Well-documented, stable API  
✅ **Future-proof**: Active development, large community  
✅ **Familiar**: Similar API to many popular CLI tools

### Negative

⚠️ **Bundle size**: +3.2kb compared to `cac` (7kb vs 3.8kb)  
⚠️ **Migration effort**: Required rewriting CLI setup (minimal, ~1 hour)

### Mitigation

- **Bundle size**: Not a concern for CLI tool (users install, don't bundle)
- **Migration**: Straightforward, similar API patterns

## Migration Guide

### Before (`cac`)

```typescript
import cac from 'cac';

const cli = cac('@engraph/castr');

cli
  .command('<input>', 'Generate client')
  .option('--output <path>', 'Output path')
  .action((input, options) => {
    // options: any ❌
    generate(input, options.output);
  });

cli.help();
cli.version(version);
cli.parse();
```

### After (`commander`)

```typescript
import { Command } from 'commander';

const program = new Command();

program
  .name('@engraph/castr')
  .version(version)
  .description('Generate Zod schemas from OpenAPI specs');

program
  .command('generate')
  .argument('<input>', 'Path to OpenAPI spec')
  .option('-o, --output <path>', 'Output path')
  .action((input, options) => {
    // options: { output?: string } ✅
    generate(input, options.output);
  });

program.parse();
```

## Type Safety Examples

### Options with Types

```typescript
// ✅ Type-safe options
interface GenerateOptions {
  output?: string;
  apiClient?: string;
  exportSchemas?: boolean;
}

program
  .command('generate')
  .argument('<input>', 'Input spec')
  .option('-o, --output <path>', 'Output path')
  .option('--api-client <name>', 'Client name', 'api')
  .option('--export-schemas', 'Export schemas')
  .action((input: string, options: GenerateOptions) => {
    // Full type safety throughout!
  });
```

### Validation

```typescript
program
  .command('generate')
  .argument('<input>', 'Input spec')
  .addOption(
    new Option('-f, --format <type>', 'Output format')
      .choices(['typescript', 'javascript'])
      .default('typescript'),
  )
  .action((input, options) => {
    // options.format is "typescript" | "javascript"
  });
```

## Quality Impact

**Before (with `cac`):**

- 52 TypeScript errors in CLI code
- `options: any` throughout
- No IDE support

**After (with `commander`):**

- 0 TypeScript errors in CLI code ✅
- Fully typed options
- Full IDE IntelliSense ✅

## Related Decisions

- [ADR-007: ESM with NodeNext Module Resolution](./ADR-007-esm-with-nodenext-resolution.md) - CLI is ESM-compatible

## References

- `commander` documentation: <https://github.com/tj/commander.js>
- Implementation: `lib/src/cli.ts`
- Tests: CLI functionality tested via integration tests

## Commits

- Phase 1a: CLI modernization commit
