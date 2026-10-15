# ADR-003: Use Attribute-Based Tool Discovery

**Status**: Accepted

**Date**: 2025-10-29

## Context

We need to establish a pattern for defining and discovering MCP tools within our .NET server implementation. Tools are the primary way that AI clients interact with the server to perform specific actions.

The key requirements are:
- Clear definition of which methods are MCP tools
- Automatic discovery and registration of tools
- Rich metadata for AI assistants to understand tool capabilities
- Type-safe parameter binding and return value handling
- Easy to understand and maintain for developers

## Decision

We will use **attribute-based tool discovery** using the `[McpServerTool]` attribute provided by the Microsoft MCP SDK, combined with `[Description]` attributes for metadata.

### Options Considered

1. **Attribute-Based Discovery with [McpServerTool]** ✅
   - Pros: Declarative, clear intent, automatic discovery, rich metadata support, type-safe
   - Cons: Requires reflection, attributes can be overlooked

2. **Interface-Based Approach**
   - Pros: Compile-time checking, clear contracts, testable
   - Cons: More boilerplate, less flexible, harder tool discovery

3. **Convention-Based Discovery**
   - Pros: Minimal code, no attributes needed
   - Cons: Implicit behavior, harder to understand, fragile naming dependencies

4. **Manual Registration**
   - Pros: Explicit control, no reflection, predictable
   - Cons: Verbose, error-prone, harder to maintain

## Decision Rationale

- **SDK Alignment**: Uses the official Microsoft MCP SDK pattern and infrastructure
- **Declarative Intent**: `[McpServerTool]` clearly marks methods as MCP tools
- **Rich Metadata**: `[Description]` attributes provide AI-readable documentation
- **Type Safety**: Automatic parameter binding leverages .NET's type system
- **Developer Experience**: IntelliSense and tooling support for attributes
- **Automatic Discovery**: No manual registration needed, reduces boilerplate

## Consequences

### Positive
- **Clear Intention**: Attributes make tool methods obvious and searchable
- **Rich Documentation**: Description attributes serve as both code documentation and AI guidance
- **Type Safety**: Automatic parameter validation and conversion
- **Reduced Boilerplate**: No manual registration or configuration files needed
- **IDE Support**: Visual Studio/VS Code provide excellent attribute support
- **Maintainable**: Easy to add, remove, or modify tools

### Negative
- **Runtime Discovery**: Tools discovered via reflection at startup (minimal performance impact)
- **Attribute Dependency**: Developers must remember to add attributes
- **Less Compile-Time Checking**: Tool existence not verified until runtime

### Neutral
- **Learning Curve**: Developers need to understand attribute patterns
- **Debugging**: Need to understand reflection-based tool discovery

## Implementation Pattern

### Basic Tool Structure
```csharp
internal class MyTools
{
    [McpServerTool]
    [Description("Clear description of what this tool does")]
    public ReturnType MethodName(
        [Description("Parameter description")] ParameterType param1,
        [Description("Optional parameter")] ParameterType param2 = defaultValue)
    {
        // Implementation
        return result;
    }
}
```

### Registration
```csharp
builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithTools<MyTools>();
```

### Naming Convention
- Method names converted to snake_case for MCP (e.g., `GetRandomNumber` → `get_random_number`)
- Use descriptive method names that clearly indicate the tool's purpose
- Avoid generic names like `Execute` or `Process`

## Guidelines

### Required Attributes
- **[McpServerTool]**: Must be present on all tool methods
- **[Description]**: Strongly recommended on methods and parameters for AI discoverability

### Method Signature Requirements
- Must be public methods in registered tool classes
- Return types must be JSON-serializable
- Parameters must be JSON-deserializable
- Async methods supported (`Task<T>` return types)

### Best Practices
- Provide meaningful default values for optional parameters
- Use specific, descriptive parameter names
- Include comprehensive descriptions for complex parameters
- Handle errors gracefully with appropriate exceptions

## Related ADRs

- [ADR-001: Use .NET 9.0 for MCP Server Implementation](001-dotnet-9-mcp-server.md)
- [ADR-002: Choose stdio Transport for MCP Communication](002-stdio-transport.md)
- [ADR-004: Self-Contained Single-File Distribution](004-self-contained-distribution.md)

## References

- [Microsoft MCP SDK Tool Documentation](https://aka.ms/nuget/mcp/guide)
- [MCP Tools Specification](https://spec.modelcontextprotocol.io/specification/basic/tools/)