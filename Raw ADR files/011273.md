# ADR-003: Registry Pattern for MCP Primitives

**Status:** Accepted

**Date:** December 2024

**Context:**

The Model Context Protocol (MCP) defines three types of primitives that servers expose to clients:

1. **Tools**: Executable functions that perform actions (e.g., calculator, file operations)
2. **Resources**: Data sources that can be read (e.g., configuration files, system status)
3. **Prompts**: Pre-defined prompt templates for LLM interactions (e.g., code review, summarization)

The system needs a mechanism to:
- **Register** primitives dynamically (add new tools/resources/prompts)
- **List** available primitives (clients need to discover what's available)
- **Retrieve** specific primitives by name for execution/reading
- **Validate** primitive schemas and configurations
- **Manage** primitive lifecycle (ensure no duplicates, validate before registration)

Architectural constraints:
- Must support registration from multiple modules
- Should enforce schema validation
- Must be accessible globally within the MCP layer
- Should not create tight coupling between primitive implementations
- Must be testable in isolation

**Decision:**

We will use the **Singleton Registry Pattern** with separate registries for each primitive type:

```
┌─────────────────────────────────────────────┐
│            MCP Server                        │
│  (Uses registries to execute/read)          │
└──────────┬──────────────┬──────────────┬────┘
           │              │              │
           ▼              ▼              ▼
    ┌────────────┐ ┌────────────┐ ┌────────────┐
    │   Tool     │ │  Resource  │ │   Prompt   │
    │  Registry  │ │  Registry  │ │  Registry  │
    │ (Singleton)│ │ (Singleton)│ │ (Singleton)│
    └────────────┘ └────────────┘ └────────────┘
```

**Implementation Structure:**

```python
# src/mcp/tool_registry.py
class ToolRegistry:
    _instance: Optional['ToolRegistry'] = None
    _tools: dict[str, Tool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'ToolRegistry':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_tool(self, tool: Tool) -> None:
        """Register a tool with schema validation."""

    def get_tool(self, name: str) -> Optional[Tool]:
        """Retrieve a tool by name."""

    def list_tools(self) -> list[dict]:
        """List all registered tools."""

    def clear(self) -> None:
        """Clear all tools (for testing)."""
```

**Similar implementations for `ResourceRegistry` and `PromptRegistry`.**

**Alternatives Considered:**

### Alternative 1: Dependency Injection with Service Container
- **Description**: Use a service container that holds all primitives, inject into server
- **Implementation Example**:
  ```python
  class ServiceContainer:
      def __init__(self):
          self.tools = []
          self.resources = []
          self.prompts = []

  class MCPServer:
      def __init__(self, container: ServiceContainer):
          self.container = container

      def execute_tool(self, name: str):
          tool = next(t for t in self.container.tools if t.name == name)
  ```
- **Pros**:
  - More explicit dependencies
  - Easier to test (inject mock container)
  - No global state
- **Cons**:
  - **Container Passing**: Need to pass container through many layers
  - **Registration Complexity**: Tools/resources/prompts defined in different modules need container reference
  - **Boilerplate**: More setup code needed in every module
  - **Not Necessary**: For this architecture, primitives are naturally global within MCP layer
- **Rejected Because**: Adds unnecessary complexity for managing what are essentially global catalogs, makes registration more difficult across modules

### Alternative 2: Simple Lists in MCPServer
- **Description**: Store primitives as lists directly in the `MCPServer` class
- **Implementation Example**:
  ```python
  class MCPServer:
      def __init__(self):
          self.tools = []
          self.resources = []
          self.prompts = []

      def register_tool(self, tool: Tool):
          self.tools.append(tool)

      def execute_tool(self, name: str):
          tool = next(t for t in self.tools if t.name == name)
  ```
- **Pros**:
  - Simplest possible implementation
  - No additional classes needed
  - Easy to understand
- **Cons**:
  - **Violates Single Responsibility**: Server both manages primitives AND executes them
  - **No Validation Layer**: No centralized place for schema validation
  - **Difficult to Extend**: Adding features (e.g., primitive metadata, versioning) requires modifying server
  - **Testing Complexity**: Must create full server instance to test registration
  - **No Separation**: Registration logic mixed with execution logic
- **Rejected Because**: Violates SRP, poor separation of concerns, hard to test registration independently

### Alternative 3: Factory Pattern with Builder
- **Description**: Use factory to create and manage primitives
- **Implementation Example**:
  ```python
  class ToolFactory:
      @staticmethod
      def create_tool(config: dict) -> Tool:
          # Validate and create tool

  class ToolManager:
      def __init__(self):
          self.factory = ToolFactory()
          self.tools = {}

      def register_from_config(self, config: dict):
          tool = self.factory.create_tool(config)
          self.tools[tool.name] = tool
  ```
- **Pros**:
  - Clear creation logic
  - Separation of construction from storage
- **Cons**:
  - **Over-Engineering**: Adds factory layer that's not needed (tools already self-contained objects)
  - **More Classes**: Factory + Manager + Tool (3 classes per primitive type)
  - **Complexity**: Students must understand factory pattern in addition to registry
  - **Overkill**: Tool construction is simple (usually just passing schema)
- **Rejected Because**: Unnecessary complexity for simple registration use case

### Alternative 4: Module-Level Dictionaries
- **Description**: Use simple module-level dictionaries
- **Implementation Example**:
  ```python
  # src/mcp/tool_registry.py
  _tools = {}

  def register_tool(tool: Tool):
      _tools[tool.name] = tool

  def get_tool(name: str):
      return _tools.get(name)
  ```
- **Pros**:
  - Very simple
  - No classes needed
  - Easy to import and use
- **Cons**:
  - **No Encapsulation**: Module-level variables can be modified anywhere
  - **No Instance Control**: Can't ensure single registry instance
  - **Testing Difficulties**: Hard to reset state between tests
  - **No Clear API**: Functions scattered rather than cohesive class interface
  - **No Validation**: No place to enforce invariants
- **Rejected Because**: Poor encapsulation, difficult to test, violates OOP principles that assignment emphasizes

**Consequences:**

### Positive Consequences:

1. **Centralized Management**:
   - All tools/resources/prompts registered in one place per type
   - Easy to list, validate, and manage primitives
   - Single source of truth for what's available

2. **Global Accessibility**:
   ```python
   # Any module can access registry
   from src.mcp.tool_registry import ToolRegistry

   registry = ToolRegistry.get_instance()
   registry.register_tool(my_tool)
   ```

3. **Schema Validation at Registration**:
   ```python
   def register_tool(self, tool: Tool) -> None:
       # Validate tool has required fields
       if not tool.name:
           raise ValueError("Tool must have a name")
       if not tool.schema:
           raise ValueError("Tool must have a schema")
       if tool.name in self._tools:
           raise ValueError(f"Tool {tool.name} already registered")

       self._tools[tool.name] = tool
   ```

4. **Testability**:
   ```python
   def test_tool_execution():
       # Clear registry before test
       ToolRegistry.get_instance().clear()

       # Register test tool
       test_tool = Tool(name="test", schema={}, handler=lambda x: x)
       ToolRegistry.get_instance().register_tool(test_tool)

       # Test execution
       result = server.execute_tool("test", {})

       # Clean up
       ToolRegistry.get_instance().clear()
   ```

5. **Separation of Concerns**:
   - **Registry**: Manages storage, validation, retrieval
   - **MCPServer**: Handles execution logic, uses registry as data source
   - **Tools/Resources/Prompts**: Define behavior, register themselves

6. **Clean API**:
   ```python
   # List all tools
   tools = ToolRegistry.get_instance().list_tools()

   # Get specific tool
   tool = ToolRegistry.get_instance().get_tool("calculator")

   # Register new tool
   ToolRegistry.get_instance().register_tool(new_tool)
   ```

7. **Prevents Duplication**:
   - Registry enforces unique names
   - Attempting to register duplicate raises error
   - Ensures consistency

8. **Educational Value**:
   - Demonstrates singleton pattern (classic design pattern)
   - Shows separation of data management from business logic
   - Illustrates encapsulation and information hiding

### Negative Consequences:

1. **Global State**:
   - Singleton introduces global state (shared across application)
   - Can make reasoning about state harder
   - **Mitigation**:
     - Clear API for state management
     - `clear()` method for testing
     - Documented lifecycle in architecture.md

2. **Testing Requires Cleanup**:
   - Must call `clear()` between tests to avoid state leakage
   - **Mitigation**:
     ```python
     @pytest.fixture(autouse=True)
     def reset_registries():
         ToolRegistry.get_instance().clear()
         ResourceRegistry.get_instance().clear()
         PromptRegistry.get_instance().clear()
         yield
     ```

3. **Not Obvious for Beginners**:
   - Students unfamiliar with singleton pattern may be confused initially
   - **Mitigation**:
     - ADR documents pattern and rationale
     - README includes usage examples
     - Architecture documentation explains pattern

4. **Harder to Mock**:
   - Singleton harder to replace with test double compared to injected dependency
   - **Mitigation**: `clear()` method allows resetting to known state

**Implementation Details:**

**Registration Flow:**
```python
# Stage 2: Tool registration during module initialization
from src.mcp.tool_registry import ToolRegistry
from src.mcp.primitives.tools.calculator import CalculatorTool

# Create tool instance
calculator = CalculatorTool()

# Register with registry
ToolRegistry.get_instance().register_tool(calculator)
```

**Execution Flow:**
```python
# MCPServer uses registry to execute tools
class MCPServer:
    def execute_tool(self, name: str, parameters: dict) -> dict:
        # Retrieve from registry
        tool = ToolRegistry.get_instance().get_tool(name)

        if tool is None:
            raise ValueError(f"Tool '{name}' not found")

        # Execute tool
        return tool.execute(parameters)
```

**Listing Flow:**
```python
# Client can list available tools
class MCPServer:
    def list_tools(self) -> list[dict]:
        return ToolRegistry.get_instance().list_tools()

# Returns:
# [
#   {"name": "calculator", "description": "...", "schema": {...}},
#   {"name": "echo", "description": "...", "schema": {...}},
#   ...
# ]
```

**Schema Validation Example:**
```python
def register_tool(self, tool: Tool) -> None:
    # Validate required attributes
    if not hasattr(tool, 'name') or not tool.name:
        raise ValueError("Tool must have a non-empty name")

    if not hasattr(tool, 'schema') or not tool.schema:
        raise ValueError("Tool must have a schema")

    if not callable(getattr(tool, 'execute', None)):
        raise ValueError("Tool must have an execute method")

    # Check for duplicates
    if tool.name in self._tools:
        raise ValueError(f"Tool '{tool.name}' is already registered")

    # Validate schema structure
    if "type" not in tool.schema or tool.schema["type"] != "object":
        raise ValueError("Tool schema must be a JSON Schema object")

    # Register
    self._tools[tool.name] = tool
```

**Metrics for Success:**

- **Centralization**: All tools/resources/prompts registered in one place ✓
- **Validation**: Schema validated at registration time ✓
- **Testability**: Tests can clear and reset registries ✓
- **No Duplication**: Duplicate names rejected ✓
- **Clean API**: Simple methods (register, get, list, clear) ✓
- **Code Size**: Each registry <100 lines ✓

**Alignment with Principles:**

- **Single Responsibility**: Registry only manages primitive storage/retrieval
- **Open/Closed**: Can add new primitives without modifying registry
- **Liskov Substitution**: All primitives implement same interface
- **Separation of Concerns**: Data management separate from execution logic
- **Singleton Pattern**: Ensures single instance per registry type

**Related ADRs:**

- ADR-001: Five-Stage Architecture (registries implemented in Stages 2-3)
- ADR-002: Transport Abstraction (handler uses registries to route requests to server, which queries registries)

**References:**

- assignment8.pdf: Stages 2-3 require implementing MCP primitives with registry pattern
- docs/architecture.md: Section 2.2 describes MCP layer with registries
- src/mcp/tool_registry.py: Tool registry implementation
- src/mcp/resource_registry.py: Resource registry implementation
- src/mcp/prompt_registry.py: Prompt registry implementation
- tests/mcp/test_tool_registry.py: Registry test examples with `clear()` usage
