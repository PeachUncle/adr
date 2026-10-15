# ADR-009: Choose DBGp Server Mode Architecture

**Status:** Accepted  
**Date:** 2025-11-09  
**Deciders:** YDebug Development Team

## Context

During Feature 009 (Variable Inspection Core) implementation, we discovered a fundamental architectural incompatibility with our original client-based approach:

### Original Architecture Problem
- YDebug was designed as a **secondary DBGp client** to connect to existing IDE debugging sessions
- Most IDEs (including PhpStorm) do not support multiple simultaneous DBGp connections despite having configuration options for it
- When a secondary DBGp client attempts to connect, the IDE immediately closes the connection
- This rendered the variable inspection functionality unusable in standard development environments

### Discovery Process
Testing revealed that:
1. **Connection Attempts Failed**: `ydebug connect` and `ydebug inspect` consistently failed with ECONNREFUSED errors
2. **IDE Connection Closure**: Protocol testing showed PhpStorm immediately closing secondary connections
3. **Multi-connection Limitations**: Despite "max simultaneous connections" settings, IDEs prioritize single-client connections
4. **Architectural Mismatch**: YDebug's design assumption that IDEs support multiple DBGp clients was incorrect

### Proof-of-Concept Success
A server mode implementation successfully demonstrated:
- Listening for Xdebug connections on port 9003
- Handling proper DBGp handshake protocol
- Setting breakpoints and controlling execution flow
- Retrieving and parsing variable data from paused PHP scripts
- Displaying formatted variable inspection results

## Decision

We will implement YDebug as a **DBGp server** that acts like an IDE debugger, rather than a secondary client connecting to existing debugging sessions.

## Rationale

### Technical Compatibility
- **Standard Protocol Compliance**: Xdebug connects to servers (debuggers), not clients
- **IDE Independence**: YDebug operates independently without requiring IDE cooperation
- **Full Protocol Control**: Complete control over debugging session lifecycle and commands
- **Breakpoint Management**: Ability to set breakpoints programmatically without IDE conflicts

### Proven Functionality
- **Working Implementation**: Proof-of-concept successfully retrieved PHP variables
- **Protocol Adherence**: Proper DBGp handshake, command execution, and response parsing
- **Execution Control**: Demonstrated breakpoint setting, script pause/resume, and variable inspection
- **Data Formatting**: Successfully integrated with existing VariableFormatter for consistent output

### Operational Benefits
- **No IDE Conflicts**: Eliminates dependency on IDE multi-connection support
- **Direct Control**: Full debugging session management without external dependencies
- **Session Isolation**: Each YDebug session operates independently
- **Configuration Flexibility**: Custom port configuration and debugging behavior

## Implementation Details

### Core Server Architecture
1. **DBGp Server**: TCP listener on configured port (default 9003)
2. **Session Manager**: Handle active debugging sessions and state
3. **Execution Controller**: Manage script flow (run, step, breakpoints)
4. **Breakpoint Controller**: Automatic breakpoint placement and management
5. **Variable Inspector**: Integration with existing VariableFormatter

### Protocol Flow
1. Server listens for Xdebug connections
2. Handles init handshake and feature negotiation
3. Sets breakpoints at target locations
4. Issues run command to continue execution
5. Receives break notification when script pauses
6. Requests variable contexts via context_get
7. Formats and displays variable data
8. Continues or terminates session as needed

### CLI Integration
- **Dual Mode Support**: Maintain existing client mode for specific use cases
- **Server Mode Commands**: `ydebug inspect --server` and `ydebug server`
- **Auto-detection**: Graceful fallback between modes based on environment
- **Configuration**: Server-specific settings in existing config system

## Consequences

### Positive
- **Reliable Operation**: Works independently of IDE debugging support
- **Complete Control**: Full debugging session management and customization
- **Proven Implementation**: Working proof-of-concept demonstrates viability
- **Existing Integration**: Reuses existing variable parsing and formatting code
- **AI Agent Compatibility**: Direct debugging control suitable for AI agent interaction

### Negative
- **Port Conflicts**: Cannot run simultaneously with IDE debuggers on same port
- **User Workflow Change**: Requires stopping IDE debugger to use YDebug server mode
- **Additional Complexity**: Dual-mode support increases codebase complexity
- **Security Considerations**: Listening server has different security profile than connecting client

### Neutral
- **Development Effort**: Similar complexity to client mode but different focus areas
- **Testing Requirements**: Need different testing approach for server vs client modes
- **Documentation**: Additional documentation for server mode usage and configuration

## Alternatives Considered

1. **Continue Client Mode Only**: Would leave variable inspection permanently broken with standard IDEs
2. **IDE Plugin Development**: Would require significant effort for each IDE and limit compatibility
3. **Proxy/Bridge Mode**: Complex middle-ground approach with unclear benefits
4. **Fork IDE Support**: Impractical approach requiring maintaining IDE forks

## Migration Path

### Backwards Compatibility
- Maintain existing client mode for specialized use cases
- Auto-detect appropriate mode based on connection scenarios
- Clear error messages directing users to appropriate mode
- Configuration options for mode selection and behavior

### Implementation Phases
1. **Core Server Implementation**: DBGp server with session management
2. **CLI Integration**: Server mode commands and configuration
3. **Testing and Validation**: Comprehensive server mode testing
4. **Documentation Updates**: Usage guides for server vs client modes
5. **Feature Completion**: Variable inspection functionality validation

## Related ADRs

- [ADR-001: Choose Xdebug with DBGp Protocol](001-choose-xdebug-dbgp-protocol.md) - Established DBGp as our debugging protocol
- [ADR-008: Choose Direct DBGp Implementation](008-choose-direct-dbgp-implementation.md) - Direct protocol implementation enables server mode

## Impact on Existing Features

### Feature 009: Variable Inspection Core
- **Resolution**: Server mode enables the variable inspection functionality that failed in client mode
- **Integration**: Existing VariableFormatter and parsing logic remain unchanged
- **Enhancement**: Proper execution control allows inspection at precise breakpoint locations

### Future Features
- **Execution Control**: Server mode provides foundation for step-through debugging
- **AI Agent Integration**: Direct debugging control enables sophisticated AI agent debugging workflows
- **Extensibility**: Server architecture supports advanced debugging features and customization

## Success Criteria

- [ ] Server mode successfully receives and handles Xdebug connections
- [ ] Variables are reliably inspected at proper execution points
- [ ] Integration with existing VariableFormatter works correctly
- [ ] CLI provides clear feedback about server state and operations
- [ ] Error handling covers common failure scenarios
- [ ] Documentation explains usage differences between client and server modes
- [ ] Backwards compatibility maintained for existing client mode functionality