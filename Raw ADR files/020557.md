# ADR-010: Choose Native MCP Server Integration for Claude Code Connectivity

**Status:** Accepted  
**Date:** 2025-11-15  
**Deciders:** YDebug Development Team

## Context

With YDebug's proven debugging capabilities and AI analysis integration, the opportunity has emerged to connect YDebug directly with Claude Code through the Model Context Protocol (MCP). This would enable Claude Code to perform real-time debugging operations on PHP applications, extending beyond static code analysis to dynamic runtime inspection.

### Integration Requirements
- Enable Claude Code to control PHP debugging sessions through standardized protocol
- Provide real-time access to variable states, execution flow, and runtime context
- Maintain existing YDebug functionality while adding MCP capabilities
- Support collaborative debugging between developers and Claude Code
- Ensure clean architecture and minimal technical debt

### Available Integration Options
Three architectural approaches were evaluated:
1. **Native MCP Server**: YDebug as dedicated MCP server exposing debugging tools
2. **Bidirectional MCP Bridge**: Translation layer between YDebug API and MCP protocol  
3. **Hybrid Approach**: Mixed MCP debugging tools with Claude API analysis integration

### Architecture Evaluation
Software architecture analysis revealed:
- **Option A (Native MCP Server)**: Clean Architecture Score 9/10, Maintainability Score 9/10
- **Option B (Bidirectional Bridge)**: Clean Architecture Score 6/10, Maintainability Score 4/10
- **Option C (Hybrid Approach)**: Clean Architecture Score 5/10, Maintainability Score 3/10

## Decision

We will implement YDebug as a **Native MCP Server** that exposes debugging capabilities through standardized MCP tools, integrated directly into the existing ydebug package.

## Rationale

### Clean Architecture Principles
- **Perfect Separation of Concerns**: YDebug becomes a pure MCP server with debugging as its core responsibility
- **Dependency Inversion**: MCP protocol abstracts client interface, allowing any MCP-compliant client connection
- **Single Responsibility**: Each component maintains one clear purpose (DBGp communication, MCP protocol handling, session management)
- **Interface Segregation**: MCP tools provide focused, specific interfaces for different debugging operations

### Architectural Compatibility
- **Existing Command Pattern**: Current command registry in `CommandRegistry.js` directly supports MCP tool registration
- **Natural Protocol Mapping**: DBGp commands map cleanly to MCP tool definitions
- **Established Error Handling**: Existing error hierarchy in `/src/debugger/errors/` maps directly to MCP error responses
- **Transaction Management**: Current `TransactionManager.js` provides natural request/response correlation for JSON-RPC

### Development Efficiency
- **Minimal Implementation Effort**: 2-3 weeks development time, leveraging 80% of existing codebase
- **Standard Protocol Compliance**: MCP is well-documented with established patterns and SDK support
- **Proven Architecture**: Builds on YDebug's solid existing foundation without introducing complexity
- **Testing Leverage**: Can reuse existing 1800+ test cases as foundation for MCP functionality

### Package Integration Benefits
- **Shared Dependencies**: MCP tools directly use existing DBGp protocol, AnalysisService, and ConfigManager
- **Atomic Deployment**: Debugging and MCP integration are functionally coupled
- **Unified Configuration**: Single configuration system, logging, and error handling
- **User Experience**: Developers expect debugging and MCP as unified functionality

## Implementation Details

### MCP Server Architecture
```
/src/mcp/
├── MCPServer.js           # Main MCP server implementation
├── tools/                 # MCP tool implementations
│   ├── DebugStartSession.js
│   ├── DebugSetBreakpoint.js  
│   ├── DebugStepExecution.js
│   ├── DebugInspectVariables.js
│   ├── DebugEvaluateExpression.js
│   ├── DebugGetStackTrace.js
│   └── DebugAnalyzeContext.js
├── resources/             # MCP resource management
└── transport/             # STDIO and HTTP+SSE transport
```

### MCP Tool Mapping
- `debug_start_session` → DBGp connection establishment
- `debug_set_breakpoint` → Existing breakpoint management
- `debug_step_execution` → Current step/continue commands
- `debug_inspect_variables` → Variable inspection functionality
- `debug_analyze_context` → Integration with existing AnalysisService

### CLI Integration
- Add `ydebug mcp-server` command to existing CLI interface
- Optional MCP service mode that doesn't affect non-MCP users
- Leverage existing configuration, logging, and error handling systems
- Maintain backward compatibility with current debugging workflows

## Consequences

### Positive
- **Architectural Excellence**: Maintains clean separation of concerns and SOLID principles
- **Minimal Technical Debt**: Builds naturally on existing well-designed architecture
- **Standard Protocol**: MCP compliance ensures future interoperability and extensibility
- **Development Efficiency**: Optimal reuse of existing codebase with minimal new complexity
- **Future-Proof**: Easy extension with additional MCP tools as requirements evolve
- **Performance**: Direct protocol implementation without unnecessary abstraction layers

### Negative
- **Protocol Learning**: Team needs to understand MCP protocol specifications and JSON-RPC 2.0
- **Additional Complexity**: New MCP server mode adds to existing functionality scope
- **Testing Requirements**: Need comprehensive MCP protocol compliance testing
- **Documentation**: Additional usage documentation for MCP integration scenarios

### Neutral
- **Package Size**: Moderate increase in package complexity, but within manageable bounds
- **Deployment**: Single package deployment remains straightforward
- **Versioning**: Unified version management for debugging and MCP capabilities

## Alternatives Rejected

### Option B: Bidirectional MCP Bridge
**Rejected because:**
- Introduces unnecessary abstraction layer without architectural benefit
- Creates protocol translation overhead and potential impedance mismatch
- Violates YAGNI principle by supporting multiple protocols without clear justification
- Higher maintenance burden with multiple interface contracts
- Risk of creating complex "god object" bridge handling too many responsibilities

### Option C: Hybrid Approach
**Rejected because:**
- Mixes MCP and Claude API creating unclear protocol boundaries
- Complex dual dependency management and coordination logic
- Violates Single Responsibility Principle for debugging components
- Exponentially more complex integration testing requirements
- Creates tight coupling between debugging operations and AI analysis protocols

### Separate ydebug-mcp Package
**Rejected because:**
- Unnecessary complexity for functionality that shares core dependencies
- Would require complex peer dependency management
- Integration testing across packages more difficult
- No clear business boundary justifying package separation
- MCP tools are debugging tools, not separate business functionality

## Migration Path

### Implementation Phases
1. **MCP Server Framework** (4-5 days): JSON-RPC 2.0 server, capability negotiation, lifecycle management
2. **Tool Implementation** (5-7 days): Seven MCP tools mapping to existing YDebug functionality
3. **Resource Management** (2-3 days): Session state and context data exposure through MCP resources
4. **CLI Integration** (2-3 days): `ydebug mcp-server` command and configuration options
5. **Integration Testing** (3-4 days): End-to-end MCP protocol compliance and functionality validation

### Compatibility Approach
- MCP functionality remains completely optional
- Existing debugging workflows unchanged
- MCP server mode available through new CLI command
- Shared configuration, logging, and error handling systems
- No breaking changes to current API or functionality

## Success Criteria

### Technical Requirements
- [ ] Full JSON-RPC 2.0 message format compliance
- [ ] Proper MCP capability negotiation during client-server handshake
- [ ] Robust lifecycle management (initialization, operation, cleanup)
- [ ] Support for both STDIO and HTTP+SSE transport methods
- [ ] MCP tool response times under 2 seconds for standard operations

### Functional Validation
- [ ] Claude Code can establish debugging connections to Xdebug-enabled PHP applications
- [ ] Breakpoint management works reliably through MCP tools
- [ ] Step-by-step execution control functions properly
- [ ] Variable inspection returns accurate data structures
- [ ] Expression evaluation works in current debugging context
- [ ] AI analysis integration provides contextualized insights through MCP

### Integration Success
- [ ] Seamless integration within Claude Code interface
- [ ] Clear visibility into debugging actions and observations
- [ ] Meaningful AI insights providing actionable debugging assistance
- [ ] No disruption to existing YDebug functionality
- [ ] Comprehensive test coverage for MCP functionality

## Related ADRs

- [ADR-008: Choose Direct DBGp Implementation](008-choose-direct-dbgp-implementation.md) - Direct protocol implementation enables MCP tool development
- [ADR-009: Choose DBGp Server Mode Architecture](009-choose-dbgp-server-mode.md) - Server architecture provides foundation for MCP debugging tools

## Impact on Existing Features

### Current Functionality
- **No Breaking Changes**: All existing CLI commands, API, and workflows remain unchanged
- **Additive Integration**: MCP server mode adds functionality without modifying existing features
- **Shared Components**: Leverages existing AnalysisService, ConfigManager, and error handling

### Future Extensibility
- **Multi-Language Support**: MCP architecture provides foundation for extending to other programming languages
- **IDE Integration**: MCP's standardized approach enables integration with other development environments
- **Enhanced AI Capabilities**: Structured MCP interface supports future AI models without protocol changes
- **Distributed Debugging**: HTTP+SSE transport enables remote debugging scenarios