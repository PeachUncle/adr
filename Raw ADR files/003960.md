# Instruction Parser

## Premise

The YnabCli application requires a robust way to parse user input from the terminal into structured command objects that can be processed by the application. Users need to enter commands with a familiar CLI syntax that includes command names, subcommands, and typed arguments.

For example, users should be able to enter commands like:
```bash
/spare-money --minus-savings true
/user create --user-name Joshua
/settings create --name YnabApiKey --value AJsokoaAoj_ajsiiAIejenias
```

The system needs to understand the command structure, extract different parts of the command, and convert string arguments into their appropriate types (int, bool, string, etc.).

## Problem

Parsing terminal input is complex because:

1. **Variable Command Structure** - Commands can have different structures:
   - Simple commands: `/database create`
   - Commands with subcommands: `/user create`
   - Commands with multiple arguments: `/settings create --name YnabApiKey --value xyz`
   - Commands with optional arguments: `/spare-money --minus-savings` (bool defaults to true)

2. **Type Conversion** - String input needs to be converted to strongly-typed arguments:
   - Numbers (int, decimal)
   - Booleans (with smart defaulting)
   - Dates (DateOnly)
   - GUIDs
   - Strings (with proper detection)

3. **Flexible Syntax** - The parser needs to handle:
   - Variable spacing between tokens
   - Optional argument values (like boolean flags)
   - Mixed argument types in a single command

4. **Maintainability** - Adding new argument types should be straightforward without modifying core parsing logic

5. **Error Handling** - Invalid commands need to be detected and reported clearly to users

## Solution

The Instruction Parser implements a three-stage pipeline architecture with a plugin-based type system:

### Architecture Overview

The parser is composed of three main stages:

1. **Indexing** (`ConsoleInstructionTokenIndexer`)
2. **Extraction** (`ConsoleInstructionTokenExtractor`)
3. **Building** (`ConsoleInstructionParser` with `IConsoleInstructionArgumentBuilder` implementations)

### 1. Token Indexing Stage

The `ConsoleInstructionTokenIndexer` analyzes the raw terminal input string and identifies the positions (start/end indexes) of each token type:

- **Prefix Token**: The command prefix (e.g., `/`)
- **Name Token**: The main command name (e.g., `spare-money`)
- **SubName Token**: Optional subcommand (e.g., `create` in `/user create`)
- **Argument Tokens**: All arguments and their values (e.g., `--name value`)

**Key Design Decision**: The indexer only identifies positions; it doesn't extract or parse content. This separation allows the indexer to be simpler and more focused.

**Example**:
```
Input: "/spare-money help --argumentOne hello world"
Output: ConsoleInstructionTokenIndexes {
    PrefixTokenIndexed = true,
    PrefixTokenStartIndex = 0,
    PrefixTokenEndIndex = 1,
    NameTokenStartIndex = 1,
    NameTokenEndIndex = 12,
    SubNameStartIndex = 13,
    SubNameEndIndex = 17,
    ArgumentTokensStartIndex = 18,
    ...
}
```

### 2. Token Extraction Stage

The `ConsoleInstructionTokenExtractor` uses the indexes from stage 1 to extract the actual string values:

- Extracts prefix, name, and subname strings
- Parses arguments into a `Dictionary<string, string?>` where:
  - Key = argument name (e.g., `"minus-savings"`)
  - Value = argument value or `null` if no value provided

**Key Design Decision**: Argument values can be `null` to support optional values (especially for boolean flags). This is documented in ADR01.

**Example**:
```
Input indexes + "/spare-money --minus-savings"
Output: ConsoleInstructionTokenExtraction {
    PrefixToken = "/",
    NameToken = "spare-money",
    SubNameToken = null,
    ArgumentTokens = { ["minus-savings"] = null }
}
```

### 3. Argument Building Stage

The `ConsoleInstructionParser` orchestrates the final parsing by:

1. Calling the indexer to get token positions
2. Calling the extractor to get token values
3. For each argument, using the builder pattern to convert string values to typed arguments

**Builder Pattern for Type Detection**:

The `IConsoleInstructionArgumentBuilder` interface defines two methods:
```csharp
public interface IConsoleInstructionArgumentBuilder
{
    bool For(string? argumentValue);  // Can this builder handle this value?
    ConsoleInstructionArgument Create(string argumentName, string? argumentValue);
}
```

**Builder Implementations**:
- `IntConsoleInstructionArgumentBuilder`: Handles integer values
- `DecimalConsoleInstructionArgumentBuilder`: Handles decimal values
- `BoolConsoleInstructionArgumentBuilder`: Handles boolean values (fallback)
- `StringConsoleInstructionArgumentBuilder`: Handles string values
- `DateOnlyConsoleInstructionArgumentBuilder`: Handles date values
- `GuidConsoleInstructionArgumentBuilder`: Handles GUID values

**Key Design Decision**: The `BoolConsoleInstructionArgumentBuilder` always returns `true` for its `For()` method, making it a fallback/default builder. It must be registered last in the dependency injection container to ensure other builders are tried first. This is documented as a constraint in ADR01.

### 4. Result Model

The parser produces a `ConsoleInstruction` record:
```csharp
public record ConsoleInstruction(
    string? Prefix,
    string? Name,
    string? SubName,
    IEnumerable<ConsoleInstructionArgument> Arguments);
```

Arguments are represented as:
- Base class: `ConsoleInstructionArgument` (has ArgumentName)
- Typed class: `TypedConsoleInstructionArgument<TArgumentValue>` (has ArgumentName and strongly-typed ArgumentValue)

### Constants and Configuration

The `ConsoleInstructionConstants` class defines the parsing rules:
```csharp
public static class ConsoleInstructionConstants
{
    public const char DefaultCommandNameSeparator = '-';
    public const string DefaultNamePrefix = "/";
    public const string DefaultArgumentPrefix = "--";
    public const char DefaultSpaceCharacter = ' ';
}
```

These constants make the parser's behavior explicit and provide a single place to adjust syntax rules if needed.

## Constraints

### Builder Order Dependency
The `BoolConsoleInstructionArgumentBuilder` must be registered last in the DI container because it acts as a fallback (its `For()` method always returns true). This dependency on injection order is brittle and should be addressed in the future (see ADR01).

### Argument Value Nullability
Argument values can be `null` to support optional values. All `IConsoleInstructionArgumentBuilder` implementations must handle `null` appropriately:
- Return `false` from `For()` if they can't handle `null`
- Throw an exception from `Create()` if called with `null` when they require a value
- Or provide a sensible default (like `BoolConsoleInstructionArgumentBuilder` defaulting to `true`)

This is fully documented in ADR01.

### Single Argument Value Support
The current implementation assumes each argument name appears once in a command. Multiple values for the same argument name would need special handling (e.g., `--file doc1.txt --file doc2.txt`).

### Space-Based Tokenization
The parser relies on space characters to separate tokens. This means argument values with spaces (e.g., `--name John Smith`) are treated as a single value string, which works well for most cases but prevents using multiple separate values without additional escaping.

### Immutable After Parse
Once created, the `ConsoleInstruction` record and its arguments are immutable. Any modifications require creating new instances.

## Questions & Answers

### Why separate indexing from extraction?

Separating indexing from extraction follows the Single Responsibility Principle. The indexer focuses on identifying where tokens are located (complex logic with edge cases), while the extractor focuses on pulling out the string values (simpler logic). This makes each component easier to test, understand, and maintain.

### Why use a builder pattern instead of a factory?

The builder pattern with the `For()` method allows for dynamic type detection at runtime. Each builder inspects the argument value and decides if it can handle it. This makes adding new types straightforward—just implement `IConsoleInstructionArgumentBuilder` and register it in DI. A factory would require maintaining a mapping of types or patterns, which is less flexible.

### How does the parser handle malformed input?

The parser throws exceptions for critical issues (missing prefix, missing command name) but is lenient about optional elements (subcommands, arguments). This balance ensures core requirements are met while allowing flexible command structures.

### Could the parser support different command syntaxes (like `-` instead of `--`)?

Yes, by modifying `ConsoleInstructionConstants`. However, the current design assumes a fixed syntax. Supporting multiple syntaxes simultaneously would require more complex configuration or making the constants injectable/configurable.

### Why use records for ConsoleInstruction?

Records provide value-based equality, immutability, and concise syntax. Since `ConsoleInstruction` is a data container that shouldn't change after parsing, records are a natural fit. The immutability also makes the parser's output predictable and thread-safe.

### How are errors from builders handled?

Currently, builders can throw exceptions if they receive invalid input. The parser doesn't catch these, allowing them to bubble up to command handlers. For production use, consider adding a validation phase or more structured error handling.

### What about performance with many builders?

The parser iterates through builders using `First()` which short-circuits on the first match. For most commands with 2-5 arguments and 6-8 builders, performance is negligible. If needed, builders could be optimized with a pre-screening step or caching.

### How extensible is this design for future CLI needs?

Very extensible. Adding new argument types just requires implementing `IConsoleInstructionArgumentBuilder`. The three-stage pipeline is stable and unlikely to need changes. The main limitation is the assumption of space-delimited, flag-based syntax (which is standard for most CLIs).

### Why not use an existing CLI parsing library?

Building a custom parser provides full control over the syntax, error messages, and integration with the rest of the application. It also keeps dependencies minimal and ensures the parser matches the specific needs of YnabCli without the overhead of a generic library.
