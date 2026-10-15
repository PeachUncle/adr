# ADR-002: Choose stdio Transport for MCP Communication

**Status**: Accepted

**Date**: 2025-10-29

## Context

The MCP (Model Context Protocol) specification supports multiple transport mechanisms for communication between clients (AI assistants) and servers. We need to choose the primary transport method for our .NET MCP server implementation.

The main transport options available are:
- stdio (JSON-RPC over stdin/stdout)
- Server-Sent Events (SSE) over HTTP
- WebSocket connections

## Decision

We will use **stdio transport** as the primary and initially sole transport mechanism for the MCP server.

### Options Considered

1. **stdio (JSON-RPC over stdin/stdout)** ✅
   - Pros: Simple, standard MCP approach, no network configuration, works with all IDEs, secure by default
   - Cons: Single client limitation, debugging complexity (mixed output streams)

2. **Server-Sent Events (SSE)**
   - Pros: Web-native, supports multiple clients, easy debugging with browser tools
   - Cons: More complex setup, requires HTTP server, port management, security considerations

3. **WebSocket**
   - Pros: Bidirectional, real-time, supports multiple clients, good performance
   - Cons: Most complex setup, requires WebSocket server infrastructure, port management

4. **Multi-transport support**
   - Pros: Maximum flexibility, supports different client needs
   - Cons: Significant complexity increase, testing overhead, maintenance burden

## Decision Rationale

- **MCP Standard**: stdio is the most common and recommended transport for MCP servers
- **IDE Integration**: VS Code and Visual Studio both expect stdio-based MCP servers by default
- **Simplicity**: No network configuration, port management, or firewall considerations
- **Security**: Process-level isolation, no network exposure, inherent security
- **Official Support**: Microsoft's MCP SDK provides first-class stdio support via `WithStdioServerTransport()`
- **Distribution Model**: Aligns well with our self-contained executable distribution strategy

## Consequences

### Positive
- **Zero Configuration**: No ports, URLs, or network setup required
- **IDE Ready**: Works out-of-the-box with VS Code and Visual Studio MCP integration
- **Secure by Default**: No network exposure, process-level security boundary
- **Simple Testing**: Can test with command-line JSON input/output
- **Standard Compliance**: Follows MCP best practices and common patterns
- **Debugging Support**: Standard input/output streams are well-supported by debugging tools

### Negative
- **Single Client**: Only one AI assistant can connect at a time
- **Output Mixing**: Need careful separation of logs (stderr) vs protocol (stdout)
- **Process Lifecycle**: Client controls server lifetime completely
- **No Web Integration**: Cannot be accessed via web browsers or HTTP clients
- **Limited Observability**: No built-in metrics or monitoring endpoints

### Neutral
- **Performance**: Adequate for typical MCP workloads, not optimized for high-throughput
- **Scalability**: Sufficient for single-user scenarios, would need different approach for multi-user

## Implementation Notes

- Configure logging to stderr only (`LogToStandardErrorThreshold = LogLevel.Trace`)
- Use stdout exclusively for MCP protocol JSON messages
- Implement graceful shutdown handling for process termination
- Document stdio configuration patterns for different IDEs

## Future Considerations

If multi-client support becomes necessary, we could:
- Add SSE transport as an additional option
- Implement WebSocket transport for real-time scenarios
- Create a hybrid approach with stdio as default and HTTP as optional

## Related ADRs

- [ADR-001: Use .NET 9.0 for MCP Server Implementation](001-dotnet-9-mcp-server.md)
- [ADR-003: Use Attribute-Based Tool Discovery](003-attribute-based-tools.md)

## References

- [MCP Transport Specification](https://spec.modelcontextprotocol.io/specification/basic/transports/)
- [Microsoft MCP SDK Documentation](https://aka.ms/nuget/mcp/guide)