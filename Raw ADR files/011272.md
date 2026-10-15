# ADR-002: Transport Abstraction via Handler

**Status:** Accepted

**Date:** December 2024

**Context:**

The MCP (Model Context Protocol) architecture needs to support communication between clients and servers. However, the communication mechanism should not be tightly coupled to the MCP server implementation for several reasons:

1. **Multiple Transport Protocols**: Different use cases may require different transport mechanisms:
   - STDIO (standard input/output) for CLI tools
   - HTTP/REST for web services
   - WebSocket for real-time communication
   - Named pipes for inter-process communication
   - TCP sockets for network communication

2. **Testability**: The MCP server should be testable without requiring actual I/O operations (using mock transports)

3. **Replaceability**: Per assignment8 requirements, components should be replaceable without modifying other layers

4. **Separation of Concerns**:
   - **MCP Server** should focus on business logic (executing tools, managing resources, handling prompts)
   - **Transport Layer** should focus on communication mechanics (serialization, I/O, protocol details)

5. **Educational Value**: Students should learn to separate protocol logic from business logic

**Decision:**

We will implement a **three-component transport abstraction**:

```
┌─────────────────────────────────────────────┐
│           Transport Handler                  │
│  (Orchestrates server + transport)          │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│ MCP Server  │  │  Transport  │
│             │  │  (STDIO)    │
└─────────────┘  └─────────────┘
```

**Components:**

1. **Abstract Transport Interface** (`src/transport/base_transport.py`):
   ```python
   class BaseTransport(ABC):
       @abstractmethod
       def start(self) -> None:
           """Initialize and start the transport."""

       @abstractmethod
       def stop(self) -> None:
           """Stop the transport and clean up resources."""

       @abstractmethod
       def send_message(self, message: dict) -> None:
           """Send a message through the transport."""

       @abstractmethod
       def receive_message(self) -> Optional[dict]:
           """Receive a message from the transport."""
   ```

2. **Concrete Transport Implementation** (`src/transport/stdio_transport.py`):
   - Implements `BaseTransport` for STDIO communication
   - Handles JSON serialization/deserialization
   - Manages stdin/stdout reading/writing
   - Provides error handling for I/O operations

3. **Transport Handler** (`src/transport/transport_handler.py`):
   - **Orchestrates** MCP server and transport
   - Receives messages via transport
   - Routes messages to appropriate MCP server methods
   - Sends responses back via transport
   - Handles the request/response lifecycle

**Alternatives Considered:**

### Alternative 1: Direct STDIO in MCP Server
- **Description**: Implement STDIO read/write directly in `MCPServer` class
- **Implementation Example**:
  ```python
  class MCPServer:
      def run(self):
          while True:
              line = sys.stdin.readline()
              message = json.loads(line)
              response = self.handle_message(message)
              sys.stdout.write(json.dumps(response) + "\n")
  ```
- **Pros**:
  - Simpler initial implementation
  - Fewer classes to maintain
  - Direct, obvious flow
- **Cons**:
  - **Violates Single Responsibility**: Server handles both MCP logic AND I/O
  - **Untestable**: Cannot test server without actual stdin/stdout
  - **Not Replaceable**: Changing transport requires modifying MCP server
  - **Tight Coupling**: MCP logic coupled to STDIO specifics
  - **Hard-Coded Protocol**: JSON serialization baked into server
- **Rejected Because**: Violates SOLID principles, fails testability requirement, makes layer replacement impossible

### Alternative 2: Callback-Based Transport
- **Description**: Transport calls callbacks on MCP server when messages arrive
- **Implementation Example**:
  ```python
  class MCPServer:
      def on_message_received(self, message: dict):
          # Handle message

  class Transport:
      def __init__(self, callback: Callable):
          self.callback = callback

      def run(self):
          message = self.receive_message()
          self.callback(message)
  ```
- **Pros**:
  - Decouples transport from server
  - Server doesn't know about transport details
- **Cons**:
  - **Inverted Control Flow**: Server becomes passive, transport drives execution
  - **Complex Error Handling**: Errors in callbacks hard to propagate
  - **Testing Complexity**: Need to mock callbacks, manage async behavior
  - **Unclear Ownership**: Who owns the request/response lifecycle?
- **Rejected Because**: Makes control flow confusing, complicates error handling, unclear architectural boundaries

### Alternative 3: Message Queue with Broker
- **Description**: Use message queue (like RabbitMQ pattern) between transport and server
- **Implementation Example**:
  ```python
  class MessageBroker:
      def __init__(self):
          self.request_queue = Queue()
          self.response_queue = Queue()

  # Transport puts in request_queue
  # Server reads from request_queue, writes to response_queue
  # Transport reads from response_queue
  ```
- **Pros**:
  - Complete decoupling via queues
  - Natural async handling
  - Could support multiple transports simultaneously
- **Cons**:
  - **Over-Engineering**: Too complex for synchronous request/response pattern
  - **Performance Overhead**: Queue operations add latency
  - **Complexity**: Requires queue management, threading/async
  - **Not Required**: Assignment doesn't require multi-transport or async handling
- **Rejected Because**: Excessive complexity for current requirements, over-engineered solution

**Consequences:**

### Positive Consequences:

1. **Replaceability Achieved**:
   - Can swap STDIO transport for HTTP transport without touching MCP server
   - Example: Create `HTTPTransport(BaseTransport)` and inject into handler
   - Handler orchestration logic remains unchanged

2. **Testability Improved**:
   ```python
   # Test MCP server in isolation
   def test_tool_execution():
       server = MCPServer()
       result = server.execute_tool("calculator", {"operation": "add", "a": 1, "b": 2})
       assert result["result"] == 3

   # Test transport in isolation
   def test_stdio_transport():
       transport = StdioTransport()
       mock_stdin = io.StringIO('{"method": "test"}\n')
       # Test transport I/O without MCP logic
   ```

3. **Clear Separation of Concerns**:
   - **MCP Server**: Tools, resources, prompts, business logic (Stages 2-3)
   - **Transport**: I/O, serialization, protocol (Stage 4)
   - **Handler**: Request lifecycle orchestration (Stage 4)

4. **Single Responsibility Principle**:
   - Each component has ONE reason to change:
     - Transport changes if I/O mechanism changes
     - Server changes if MCP logic changes
     - Handler changes if routing logic changes

5. **Educational Clarity**:
   - Students clearly see separation of protocol (transport) from logic (server)
   - Abstract base class demonstrates interface design
   - Dependency injection pattern demonstrated in handler

6. **Future Extensibility**:
   - Easy to add new transports (HTTP, WebSocket, etc.)
   - Could support multiple simultaneous transports
   - Could add middleware (logging, authentication) in handler

### Negative Consequences:

1. **Additional Classes**:
   - More files to maintain (BaseTransport, StdioTransport, TransportHandler)
   - **Mitigation**: Each class is small (<150 lines), focused, well-tested

2. **Indirection**:
   - Message flow goes through handler layer
   - Slightly more complex to trace request flow
   - **Mitigation**: Clear documentation in architecture.md, well-named methods

3. **Initial Learning Curve**:
   - Students need to understand abstraction pattern
   - Must understand dependency injection
   - **Mitigation**: This is pedagogically valuable, teaches professional patterns

**Implementation Details:**

**Transport Handler Request Flow:**
```python
class TransportHandler:
    def __init__(self, server: MCPServer, transport: BaseTransport):
        self.server = server
        self.transport = transport

    def handle_request(self, message: dict) -> dict:
        method = message.get("method", "")
        params = message.get("params", {})

        # Route to appropriate server method
        if method == "tool.execute":
            result = self.server.execute_tool(
                params["name"],
                params.get("parameters", {})
            )
        # ... other routes

        return {"success": True, "result": result}
```

**Dependency Injection in CLI:**
```python
# src/cli/mcp_cli.py
def main():
    server = MCPServer()
    transport = StdioTransport()  # Could swap for HTTPTransport
    handler = TransportHandler(server, transport)
    handler.run()
```

**Testing Strategy:**

1. **Unit Tests for Transport** (test I/O without MCP logic):
   ```python
   def test_stdio_send_message():
       transport = StdioTransport()
       message = {"method": "test"}
       # Mock stdout, verify JSON written correctly
   ```

2. **Unit Tests for Server** (test MCP logic without I/O):
   ```python
   def test_server_tool_execution():
       server = MCPServer()
       # Direct method calls, no transport needed
   ```

3. **Integration Tests for Handler** (test orchestration):
   ```python
   def test_handler_request_lifecycle():
       server = MCPServer()
       mock_transport = MockTransport()  # Test double
       handler = TransportHandler(server, mock_transport)
       # Verify full request/response cycle
   ```

**Metrics for Success:**

- **Transport Replaceability**: Can create new transport in <50 lines ✓
- **Zero MCP Server Changes**: Adding HTTP transport requires 0 changes to MCP server ✓
- **Test Independence**: Server tests run without transport, transport tests run without server ✓
- **Code Size**: Each component <150 lines ✓

**Alignment with Principles:**

- **SOLID**:
  - **S**ingle Responsibility: Each class has one job
  - **O**pen/Closed: Open for extension (new transports), closed for modification
  - **L**iskov Substitution: Any `BaseTransport` subclass works
  - **I**nterface Segregation: Minimal interface (4 methods)
  - **D**ependency Inversion: Handler depends on `BaseTransport` abstraction, not `StdioTransport` concrete class

- **Separation of Concerns**: Protocol vs logic fully separated
- **Dependency Injection**: Handler receives dependencies, doesn't create them
- **Interface-Based Design**: `BaseTransport` defines contract

**Related ADRs:**

- ADR-001: Five-Stage Architecture (this implements Stage 4)
- ADR-004: SDK as Mandatory Integration Layer (SDK uses transport abstraction)

**References:**

- assignment8.pdf: Stage 4 requirements for transport abstraction
- docs/architecture.md: Section 2.3 describes transport layer
- src/transport/base_transport.py: Abstract interface definition
- src/transport/stdio_transport.py: Concrete STDIO implementation
- src/transport/transport_handler.py: Handler orchestration logic
