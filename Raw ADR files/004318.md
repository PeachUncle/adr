# ADR-008: Model Context Protocol Integration

## Status
Accepted

## Context
ToolVault's bundle-based architecture provides rich metadata about analysis tools that AI systems could leverage for intelligent assistance. Users would benefit from AI-powered tool discovery, automated pipeline creation, and natural language interfaces for complex analytical workflows. The Model Context Protocol (MCP) provides a standardized way to expose ToolVault's capabilities to AI systems while maintaining appropriate security boundaries and human oversight.

## Decision
We will implement native MCP server integration with the following characteristics:

### MCP Implementation Architecture
- **Native MCP server**: ToolVault directly implements MCP protocol for optimal performance
- **Full tool exposure**: All tools available to human users are accessible via MCP
- **Rich metadata exposure**: Complete tool schemas including input/output types, parameters, and usage examples
- **Bundle-aware discovery**: AI can explore tools across all loaded bundles

### AI Integration Capabilities
- **Tool discovery and recommendation**: AI suggests relevant tools based on user data and objectives
- **Automated pipeline creation**: AI chains tools together into complete analytical workflows
- **Natural language interface**: Users can describe analytical needs in plain language
- **Parameter assistance**: AI helps configure complex tool parameters when requested

### Security and Oversight Model
- **Sandboxed execution**: AI can execute tools but outputs remain quarantined until human approval
- **Pipeline approval workflow**: AI proposes complete analysis pipelines, human approves before execution
- **Human gate for persistence**: Results only saved/exported after explicit human confirmation
- **Full audit trail**: All AI-driven actions logged with provenance information

### Context Management Evolution
- **Phase 1 - Stateless**: Each AI interaction independent, simple tool discovery and execution
- **Phase 2 - Project-based**: AI maintains context across sessions for coherent project workflows  
- **Phase 3 - Persistent learning**: AI builds knowledge about user preferences and workflow patterns

## Rationale

### Native Integration Benefits
Direct MCP implementation provides optimal performance and tightest integration with ToolVault's metadata-driven architecture, enabling sophisticated AI assistance without external dependencies.

### Full Tool Exposure with Sandboxing
Exposing all tools via MCP maximizes AI capability for pipeline creation while sandboxed execution ensures safety through human approval gates.

### Rich Metadata Exposure
Complete tool schemas enable AI to make intelligent recommendations and create valid tool chains without needing execution history or documentation complexity.

### Phased Context Evolution
Starting stateless and evolving toward persistent learning allows incremental capability development while maintaining system simplicity initially.

### Human-Centered Approval Workflow
Pipeline approval with save/export gates maintains human control over final outputs while allowing AI to demonstrate full analytical workflows.

## Consequences

### Positive
- **Enhanced productivity**: AI assistance for tool discovery and pipeline creation
- **Lower barrier to entry**: Natural language interface reduces learning curve
- **Intelligent recommendations**: AI suggests relevant tools based on data characteristics
- **Workflow automation**: Automated pipeline creation for common analytical patterns
- **Standards compliance**: MCP integration enables compatibility with multiple AI systems

### Negative
- **Implementation complexity**: Native MCP server requires protocol implementation
- **Security considerations**: AI access to all tools requires careful sandboxing
- **Performance overhead**: AI interactions add processing load
- **Context management**: Persistent learning phases increase system complexity

### Mitigation Strategies
- **Incremental rollout**: Start with stateless implementation and evolve capabilities
- **Robust sandboxing**: Ensure AI outputs cannot affect persistent storage without approval
- **Performance monitoring**: Track AI interaction overhead and optimize as needed
- **Clear boundaries**: Maintain explicit human approval gates for all persistent actions

## MCP Protocol Compliance Requirements

### Core Capabilities Declaration
ToolVault must declare support for the following MCP capabilities during initialization:
- **Tools capability**: With `listChanged` notification support for dynamic tool availability
- **Resources capability**: For exposing bundle metadata and tool documentation  
- **Prompts capability**: For providing analytical workflow templates

### Required Protocol Methods

#### Tools Interface
- **`tools/list`**: Discover available tools across all loaded bundles
  - Support pagination for large tool collections
  - Include tool name, description, input/output schemas
- **`tools/call`**: Execute specific tools with parameter validation
  - Validate inputs against tool schemas
  - Return structured results with provenance metadata
- **`notifications/tools/list_changed`**: Notify when bundles are loaded/unloaded

#### Resources Interface  
- **`resources/list`**: Expose bundle metadata and tool documentation
- **`resources/read`**: Provide access to tool schemas and example data
- **`resources/subscribe`**: Notify on bundle or tool metadata changes

#### Prompts Interface
- **`prompts/list`**: Expose analytical workflow templates
- **`prompts/get`**: Retrieve parameterized workflow templates
- **Arguments support**: Allow customization of workflow prompts

### Message Transport
- **JSON-RPC 2.0**: All MCP communication via JSON-RPC protocol
- **HTTP with SSE**: Server-Sent Events for real-time notifications
- **Version negotiation**: Support MCP version "2025-06-18" format

### Security and Validation
- **Input validation**: All tool parameters validated against schemas
- **Access controls**: Human approval gates for tool execution
- **Rate limiting**: Prevent excessive AI tool invocations
- **Output sanitization**: Clean tool outputs before returning to AI

## Implementation Notes
- MCP server will be integrated into ToolVault's backend architecture
- Tool metadata exposure will leverage existing bundle `index.json` schemas
- Sandboxed execution environment will isolate AI-driven tool runs
- Audit logging will capture all AI interactions for provenance and debugging
- Human approval interface will clearly show proposed pipelines before execution
- Context management will evolve through defined phases with clear upgrade paths
- MCP version negotiation will occur during client initialization
- Tool schemas will be automatically generated from bundle metadata
- Resource endpoints will expose bundle contents and documentation
- Prompt templates will be created for common analytical workflows