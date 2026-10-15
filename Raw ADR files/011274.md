# ADR-004: SDK as Mandatory Integration Layer

**Status:** Accepted

**Date:** December 2024

**Context:**

The system architecture includes multiple layers:
- **Core**: Infrastructure (config, logging, errors)
- **MCP**: Server logic (tools, resources, prompts)
- **Transport**: Communication (STDIO, potentially HTTP/WebSocket)
- **UI**: User interface (CLI)

The question arises: **How should the UI layer communicate with the server?**

Several integration approaches are possible:

1. **Direct Transport Usage**: UI directly uses transport classes (STDIO, HTTP, etc.)
2. **Direct MCP Server Access**: UI directly calls MCP server methods
3. **SDK Layer**: Introduce client SDK that wraps transport communication

Considerations:
- **Architectural Clarity**: Is the integration pattern clear and maintainable?
- **Separation of Concerns**: Does each layer have a distinct responsibility?
- **Testability**: Can UI be tested without running actual server?
- **Replaceability**: Can transport be swapped without changing UI?
- **Educational Value**: Does this teach important software patterns?
- **Professional Practices**: What do real-world systems do?

Assignment context:
- **assignment8** explicitly defines **Stage 5: SDK + UI**, suggesting SDK is expected
- **Software submission guidelines** emphasize modularity and separation of concerns
- **MCP specification** typically includes client SDKs in production implementations

**Decision:**

We will introduce a **mandatory SDK (Software Development Kit) layer** between the UI and Transport layers:

```
┌─────────────────────────────────────────────┐
│              User Interface (CLI)            │
│                                              │
│  - Parses user commands                     │
│  - Displays results                         │
│  - Uses SDK only (no transport knowledge)   │
└──────────────────┬───────────────────────────┘
                   │ calls
                   ▼
┌─────────────────────────────────────────────┐
│            SDK Layer (MCP Client)            │
│                                              │
│  - Wraps transport communication            │
│  - Provides high-level methods              │
│  - Handles serialization/deserialization    │
│  - Manages request IDs                      │
│  - Exposes clean API                        │
└──────────────────┬───────────────────────────┘
                   │ uses
                   ▼
┌─────────────────────────────────────────────┐
│           Transport Layer (STDIO)            │
│                                              │
│  - Sends/receives raw messages              │
│  - Handles I/O mechanics                    │
└──────────────────────────────────────────────┘
```

**SDK provides high-level client API:**

```python
# src/sdk/mcp_client.py
class MCPClient:
    def __init__(self, transport: BaseTransport):
        self.transport = transport
        self._request_id = 0

    # High-level methods that UI uses
    def get_server_info(self) -> dict:
        """Get server information."""

    def list_tools(self) -> list[str]:
        """List available tools."""

    def execute_tool(self, name: str, parameters: dict = None) -> dict:
        """Execute a tool with parameters."""

    def list_resources(self) -> list[str]:
        """List available resources."""

    def read_resource(self, uri: str) -> dict:
        """Read a resource by URI."""

    def list_prompts(self) -> list[str]:
        """List available prompts."""

    def get_prompt_messages(self, name: str, arguments: dict = None) -> list[dict]:
        """Get prompt messages with arguments."""

    # Context manager support
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
```

**Alternatives Considered:**

### Alternative 1: UI Directly Uses Transport
- **Description**: CLI directly creates and uses `StdioTransport` to send/receive messages
- **Implementation Example**:
  ```python
  # src/cli/mcp_cli.py
  class MCPCli:
      def __init__(self):
          self.transport = StdioTransport()

      def list_tools(self):
          request = {
              "id": "req-1",
              "method": "tool.list",
              "params": {}
          }
          self.transport.send_message(request)
          response = self.transport.receive_message()
          return response["result"]["tools"]
  ```
- **Pros**:
  - Fewer layers (no SDK)
  - Direct, straightforward
  - Less code to maintain
- **Cons**:
  - **Violates Separation of Concerns**: UI knows about transport protocol details
  - **Code Duplication**: Every UI (CLI, web, desktop) would duplicate request/response logic
  - **Hard to Test**: UI tests require mocking transport I/O
  - **Tight Coupling**: Changing message format requires changing UI
  - **Request ID Management**: UI must manage request IDs manually
  - **Error Handling**: UI must parse transport-level errors
  - **Not Professional**: Real-world systems don't expose transport directly to UI
- **Rejected Because**: Creates tight coupling, violates SoC, leads to code duplication, poor testability

### Alternative 2: UI Directly Calls MCP Server
- **Description**: CLI creates `MCPServer` instance and calls methods directly (no transport)
- **Implementation Example**:
  ```python
  # src/cli/mcp_cli.py
  class MCPCli:
      def __init__(self):
          self.server = MCPServer()

      def list_tools(self):
          return self.server.list_tools()
  ```
- **Pros**:
  - Very simple
  - No network/transport overhead
  - Fast
- **Cons**:
  - **Violates Layered Architecture**: Skips transport layer entirely
  - **Not Representative**: Doesn't demonstrate client/server communication patterns
  - **Defeats Stage 4 Purpose**: Transport abstraction (Stage 4) becomes unused
  - **Not Extensible**: Can't later add remote server capability
  - **Not Realistic**: Real MCP servers run as separate processes (STDIO communication)
  - **Poor Educational Value**: Doesn't teach client/server patterns
- **Rejected Because**: Defeats the purpose of layered architecture, violates assignment's staged architecture approach, doesn't reflect real-world MCP usage

### Alternative 3: Thin Wrapper Functions (Not a Class)
- **Description**: Provide module-level helper functions instead of SDK class
- **Implementation Example**:
  ```python
  # src/sdk/mcp_helpers.py
  def execute_tool(transport, name: str, parameters: dict):
      request = {"method": "tool.execute", "params": {"name": name, "parameters": parameters}}
      transport.send_message(request)
      return transport.receive_message()

  # CLI uses
  from src.sdk.mcp_helpers import execute_tool
  result = execute_tool(transport, "calculator", {"operation": "add", "a": 1, "b": 2})
  ```
- **Pros**:
  - Simpler than full SDK class
  - Still provides abstraction
  - Easy to use
- **Cons**:
  - **No State Management**: Can't track request IDs, connection state
  - **No Context Manager**: Can't use `with` statement for resource management
  - **No Encapsulation**: Transport passed around everywhere
  - **Limited Extensibility**: Hard to add features (caching, retry logic, etc.)
  - **Not OOP**: Assignment emphasizes object-oriented principles
  - **Poor API Design**: Functions less discoverable than class methods
- **Rejected Because**: Doesn't encapsulate state, violates OOP emphasis, harder to extend

**Consequences:**

### Positive Consequences:

1. **Clean Separation of Concerns**:
   - **UI Layer**: User interaction, command parsing, display formatting
   - **SDK Layer**: Client-side protocol handling, request/response management
   - **Transport Layer**: I/O mechanics, serialization

2. **Simplified UI Code**:
   ```python
   # Without SDK (Alternative 1)
   request = {
       "id": f"req-{self.request_counter}",
       "method": "tool.execute",
       "params": {
           "name": tool_name,
           "parameters": tool_params
       }
   }
   self.transport.send_message(request)
   response = self.transport.receive_message()
   if not response["success"]:
       raise Exception(response["error"]["message"])
   result = response["result"]

   # With SDK (Current approach)
   result = client.execute_tool(tool_name, tool_params)
   ```

3. **Improved Testability**:
   ```python
   # Test UI without real transport
   def test_cli_tool_execution():
       mock_transport = MockTransport()
       mock_transport.set_response({"success": True, "result": {"output": 42}})

       client = MCPClient(mock_transport)
       cli = MCPCli(client)

       result = cli.handle_command("tool execute calculator --a 1 --b 2")
       assert "42" in result
   ```

4. **Reusability Across UI Types**:
   - Same SDK can be used by CLI, web UI, desktop UI, etc.
   - No code duplication of protocol logic
   - Consistent behavior across UIs

5. **Request ID Management**:
   ```python
   def _next_request_id(self) -> str:
       self._request_id += 1
       return f"req-{self._request_id}"
   ```
   - SDK handles request ID generation automatically
   - UI doesn't need to track this

6. **Error Handling Abstraction**:
   ```python
   def _send_request(self, method: str, params: dict = None) -> dict:
       # Send request
       self.transport.send_message(request)

       # Receive and validate response
       response = self.transport.receive_message()
       if response is None:
           raise Exception("No response received from server")
       if not response.get("success"):
           error = response.get("error", {})
           raise Exception(f"Server error: {error.get('message', 'Unknown error')}")

       return response["result"]
   ```
   - UI gets clean exceptions, doesn't parse error responses

7. **Context Manager Support**:
   ```python
   with MCPClient(transport) as client:
       tools = client.list_tools()
       result = client.execute_tool("calculator", {"operation": "add", "a": 1, "b": 2})
   # Transport automatically cleaned up
   ```

8. **Professional Practice**:
   - Mirrors real-world client SDK patterns (AWS SDK, Stripe SDK, etc.)
   - Teaches students industry-standard approach
   - Demonstrates library design principles

9. **Future Extensibility**:
   - Easy to add features to SDK:
     - Response caching
     - Retry logic
     - Request timeout
     - Batch requests
     - Async support
   - UI remains unchanged when SDK adds features

10. **Alignment with Assignment**:
    - **Stage 5** explicitly mentions "SDK + UI"
    - Demonstrates progression: Core → MCP → Transport → SDK → UI
    - Each stage adds clear value

### Negative Consequences:

1. **Additional Layer**:
   - One more layer in the stack
   - Slightly more code to maintain
   - **Mitigation**: SDK is small (<200 lines), well-tested, provides significant value

2. **Initial Indirection**:
   - UI → SDK → Transport adds one extra hop
   - **Mitigation**: Negligible performance impact, clarity benefit far outweighs cost

3. **Learning Curve**:
   - Students must understand client SDK pattern
   - **Mitigation**: Common pattern in industry, valuable to learn, well-documented in ADR

**Implementation Details:**

**SDK Structure:**

```python
class MCPClient:
    def __init__(self, transport: BaseTransport):
        """Initialize client with a transport."""
        self.transport = transport
        self._request_id = 0

    def connect(self) -> None:
        """Connect to the server."""
        self.transport.start()

    def disconnect(self) -> None:
        """Disconnect from the server."""
        self.transport.stop()

    def _next_request_id(self) -> str:
        """Generate next request ID."""
        self._request_id += 1
        return f"req-{self._request_id}"

    def _send_request(self, method: str, params: dict = None) -> dict:
        """Send a request and return the result."""
        request = {
            "id": self._next_request_id(),
            "method": method,
            "params": params or {}
        }

        self.transport.send_message(request)
        response = self.transport.receive_message()

        if response is None:
            raise Exception("No response received from server")
        if not response.get("success"):
            error = response.get("error", {})
            raise Exception(f"Server error: {error.get('message', 'Unknown error')}")

        return response["result"]

    # High-level methods
    def list_tools(self) -> list[str]:
        result = self._send_request("tool.list")
        return result.get("tools", [])

    def execute_tool(self, name: str, parameters: dict = None) -> dict:
        params = {"name": name, "parameters": parameters or {}}
        return self._send_request("tool.execute", params)
```

**CLI Usage:**

```python
# src/cli/mcp_cli.py
class MCPCli:
    def __init__(self):
        transport = StdioTransport()
        self.client = MCPClient(transport)

    def run(self):
        with self.client:  # Auto-connect/disconnect
            while True:
                command = input("> ")
                self.handle_command(command)

    def handle_command(self, command: str):
        if command == "list tools":
            tools = self.client.list_tools()
            print(f"Available tools: {tools}")
        elif command.startswith("execute"):
            # Parse command
            result = self.client.execute_tool(tool_name, params)
            print(f"Result: {result}")
```

**Testing Strategy:**

```python
# tests/sdk/test_mcp_client.py
def test_client_execute_tool():
    # Create mock transport
    mock_transport = Mock()
    mock_transport.receive_message.return_value = {
        "success": True,
        "result": {"success": True, "result": {"output": 42}}
    }

    # Test SDK
    client = MCPClient(mock_transport)
    result = client.execute_tool("calculator", {"operation": "add", "a": 1, "b": 2})

    # Verify
    assert result["result"]["output"] == 42
    assert mock_transport.send_message.called
```

**Metrics for Success:**

- **UI Code Reduction**: UI code focuses on presentation, not protocol (measured by separation of concerns) ✓
- **Reusability**: Same SDK used by all UI types ✓
- **Test Coverage**: SDK has >80% unit test coverage ✓
- **API Simplicity**: All methods have clear, concise signatures ✓
- **Zero Transport Knowledge in UI**: UI doesn't import transport classes ✓

**Alignment with Principles:**

- **Separation of Concerns**: UI, SDK, Transport have distinct responsibilities
- **Single Responsibility**: SDK handles client protocol only
- **Dependency Inversion**: UI depends on SDK abstraction, not transport details
- **Open/Closed**: Can add SDK features without changing UI
- **DRY**: Protocol logic written once in SDK, used by all UIs
- **Client SDK Pattern**: Industry-standard approach for API libraries

**Related ADRs:**

- ADR-001: Five-Stage Architecture (SDK is Stage 5)
- ADR-002: Transport Abstraction (SDK uses transport abstraction)

**References:**

- assignment8.pdf: Stage 5 explicitly defines "SDK + UI"
- docs/architecture.md: Section 2.4 describes SDK layer
- docs/PRD.md: FR-5.1 and FR-5.2 define SDK requirements
- src/sdk/mcp_client.py: SDK implementation
- src/cli/mcp_cli.py: CLI using SDK
- tests/sdk/test_mcp_client.py: SDK unit tests demonstrating mock transport usage
