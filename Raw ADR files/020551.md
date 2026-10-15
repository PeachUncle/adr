# ADR-003: Choose API Gateway Pattern for AI Agent Integration

**Date:** 2025-11-08  
**Status:** Accepted  
**Deciders:** Development Team  
**Technical Story:** Define architecture for AI agent integration with debugging sessions

## Context

Building on previous architectural decisions:
- **ADR-001:** Selected Xdebug/DBGp protocol for PHP debugging capabilities
- **ADR-002:** Chose Node.js runtime for rapid prototype development

We need to define how AI agents connect to and control debugging sessions. The architecture must support:

- **Prototype Phase:** Single breakpoint variable inspection with basic AI analysis
- **MVP Phase:** Full debugging session control with multiple AI agent support
- **Future Scalability:** Multi-user, multi-session debugging environments

### Key Requirements

- Clean separation between DBGp protocol complexity and AI reasoning logic
- Platform-agnostic AI agent integration (supports various AI frameworks)
- Testable and debuggable architecture during development
- Real-time communication capabilities for interactive debugging
- Scalable design that grows from prototype to production

## Decision

We will implement an **API Gateway Pattern** with a dedicated debugging service that exposes REST and WebSocket APIs for AI agent integration.

### Architecture Flow
```
AI Agent → HTTP/WebSocket API → YDebug Service → DBGp Client → Xdebug → PHP Application
```

### Core Components

1. **YDebug API Service** (Node.js/Express.js)
   - REST endpoints for debugging operations
   - WebSocket server for real-time events
   - DBGp protocol client integration
   - Session management and state handling

2. **API Layer**
   - RESTful debugging operations (start/stop, breakpoints, variable inspection)
   - WebSocket streams for real-time debugging events
   - Authentication and session management
   - Request/response validation and transformation

3. **AI Agent Interface**
   - HTTP client for debugging commands
   - WebSocket client for real-time updates
   - Abstract debugging operations (no DBGp knowledge required)
   - Focus on AI reasoning and decision-making logic

## Alternatives Considered

### Option 1: Direct DBGp Client Integration
**Description:** AI agent runs DBGp client directly, communicating with Xdebug without intermediary service.

**Pros:**
- Minimal architecture complexity
- Direct protocol control and customization
- Lowest possible latency for debugging operations
- No additional service dependencies

**Cons:**
- AI agent requires deep DBGp protocol knowledge
- Tight coupling between AI logic and debugging protocol
- Complex error handling and protocol edge cases for AI to manage
- Difficult to unit test AI reasoning separately from protocol handling

### Option 2: Event-Driven Architecture
**Description:** AI agent subscribes to debugging events via message queue system (Redis/RabbitMQ).

**Pros:**
- Highly scalable and decoupled design
- Natural support for multiple concurrent AI agents
- Built-in audit trail and event replay capabilities
- Flexible event processing patterns

**Cons:**
- Over-engineered complexity for prototype requirements
- Additional infrastructure setup and maintenance overhead
- Potential latency issues with message queue processing
- Complex debugging of distributed event flows

### Option 3: Plugin/Extension Architecture
**Description:** AI agent implemented as plugin/extension to existing IDE debugging tools.

**Pros:**
- Leverages existing mature debugging infrastructure
- Familiar integration patterns for developers
- Inherits IDE debugging features and UI components

**Cons:**
- IDE-specific implementation constraints and limitations
- Complex integration with various IDE plugin architectures
- Reduces AI agent flexibility and deployment options
- Dependent on IDE debugging capabilities and update cycles

## Decision Rationale

### Primary Factors

1. **Clean Separation of Concerns**
   - DBGp protocol complexity isolated in dedicated service
   - AI agents focus on reasoning without protocol implementation details
   - Clear boundaries enable independent testing and development

2. **Development Velocity**
   - RESTful endpoints provide familiar, easily testable interfaces
   - Standard HTTP tools for debugging and monitoring during development
   - Rapid iteration on API design without affecting AI agent implementation

3. **Scalability Foundation**
   - Architecture naturally supports multiple concurrent AI agents
   - Session management built into API layer from the start
   - WebSocket capabilities enable real-time features for MVP phase

4. **Platform Agnostic**
   - AI agents can be implemented in any language/framework
   - Standard HTTP/WebSocket protocols ensure broad compatibility
   - Future integration with various AI platforms and services

## Implementation Details

### API Design Examples

#### REST Endpoints
```javascript
// Session Management
POST   /api/v1/debug/sessions          // Start debugging session
GET    /api/v1/debug/sessions/:id      // Get session status
DELETE /api/v1/debug/sessions/:id      // End debugging session

// Breakpoint Management
POST   /api/v1/debug/sessions/:id/breakpoints    // Set breakpoint
GET    /api/v1/debug/sessions/:id/breakpoints    // List breakpoints
DELETE /api/v1/debug/sessions/:id/breakpoints/:bp // Remove breakpoint

// Execution Control
POST   /api/v1/debug/sessions/:id/continue       // Continue execution
POST   /api/v1/debug/sessions/:id/step          // Step execution
POST   /api/v1/debug/sessions/:id/step-over     // Step over

// Variable Inspection
GET    /api/v1/debug/sessions/:id/variables     // Get current variables
GET    /api/v1/debug/sessions/:id/stack         // Get call stack
POST   /api/v1/debug/sessions/:id/eval          // Evaluate expression
```

#### WebSocket Events
```javascript
// Real-time debugging events
{
  "type": "breakpoint_hit",
  "session_id": "sess_123",
  "breakpoint": { "file": "/app/index.php", "line": 42 },
  "variables": { /* current scope variables */ },
  "stack_trace": [ /* call stack */ ]
}

{
  "type": "execution_complete",
  "session_id": "sess_123",
  "exit_code": 0,
  "execution_time": 1.234
}

{
  "type": "error",
  "session_id": "sess_123",
  "error": { "message": "Connection lost", "code": "DBG_CONNECTION_LOST" }
}
```

### Technical Implementation

```javascript
// YDebug Service Core Structure
class YDebugService {
  constructor() {
    this.dbgpClient = new DBGpClient();
    this.sessionManager = new SessionManager();
    this.apiServer = new APIServer();
    this.websocketServer = new WebSocketServer();
  }
  
  // Abstract debugging operations for API layer
  async startDebuggingSession(config) {
    const session = await this.sessionManager.create(config);
    await this.dbgpClient.connect(session);
    return session;
  }
  
  async setBreakpoint(sessionId, file, line) {
    const session = this.sessionManager.get(sessionId);
    return await this.dbgpClient.setBreakpoint(session, file, line);
  }
  
  async inspectVariables(sessionId) {
    const session = this.sessionManager.get(sessionId);
    return await this.dbgpClient.getVariables(session);
  }
}
```

### AI Agent Integration Example

```javascript
// AI Agent Implementation
class AIDebugAgent {
  constructor(apiUrl) {
    this.apiClient = new YDebugAPIClient(apiUrl);
    this.websocket = new WebSocket(`${apiUrl}/ws`);
  }
  
  async analyzeBreakpoint(sessionId) {
    // Get current program state
    const variables = await this.apiClient.getVariables(sessionId);
    const stack = await this.apiClient.getStack(sessionId);
    
    // AI reasoning logic (no DBGp protocol knowledge required)
    const analysis = await this.performAIAnalysis(variables, stack);
    
    // Take debugging action based on analysis
    if (analysis.shouldContinue) {
      await this.apiClient.continue(sessionId);
    } else {
      await this.apiClient.stepOver(sessionId);
    }
  }
  
  performAIAnalysis(variables, stack) {
    // Pure AI logic separated from debugging protocol concerns
    // Focus on code analysis, bug detection, optimization suggestions
  }
}
```

## Consequences

### Positive Outcomes

- **Clean Architecture:** Clear separation enables focused development on AI reasoning vs debugging infrastructure
- **Testability:** REST APIs easily tested with standard HTTP tools; AI logic testable independently
- **Scalability:** Architecture foundation supports MVP requirements for multiple AI agents
- **Platform Agnostic:** AI agents can be built with any technology stack or AI framework
- **Development Velocity:** Familiar REST/WebSocket patterns accelerate prototype development

### Negative Consequences

- **Service Complexity:** Additional service layer adds deployment and maintenance overhead
- **Performance Overhead:** Extra network hop between AI agent and debugging protocol vs direct integration
- **Infrastructure Requirements:** Requires additional service deployment and monitoring

### Risk Mitigation Strategies

- **Performance Concerns:** Use WebSocket connections for performance-critical real-time operations
- **Service Complexity:** Start with minimal API surface for prototype, expand incrementally
- **Infrastructure Overhead:** Leverage containerization for simple deployment and scaling

## Implementation Phases

### Phase 1: Prototype (Current)
- Basic REST API for single breakpoint variable inspection
- Simple session management for single AI agent
- Core DBGp integration for Xdebug communication

### Phase 2: MVP Development
- WebSocket real-time event streaming
- Multi-session support for concurrent debugging
- Enhanced API endpoints for full debugging control
- Authentication and session security

### Phase 3: Production Scaling
- Multi-tenant session isolation
- Performance optimization and caching
- Comprehensive monitoring and logging
- API versioning and backward compatibility

## References

- **ADR-001:** Choose Xdebug and DBGp Protocol for PHP Debugging
- **ADR-002:** Choose Node.js for Rapid Prototype Development
- **DBGp Protocol Specification:** https://xdebug.org/docs/dbgp
- **REST API Design Best Practices:** RESTful service design patterns
- **WebSocket Protocol:** Real-time bidirectional communication standards