# ADR 003: Model Context Protocol (MCP) for Tool Integration

## Status
Accepted

## Context
We need a standardized approach for integrating external tools, data sources, and capabilities with our AI agents. The tool integration layer determines how agents interact with the outside world, affecting reliability, security, and maintainability.

### Problem Statement
- Agents need access to external tools (filesystem, databases, APIs, etc.)
- Tool definitions should be reusable across different LLMs and frameworks
- Security and sandboxing are critical for tool execution
- Tool discovery and documentation should be automated
- Local-first tools must work without network dependencies

### Requirements
- **Standardization**: Common protocol for tool definition and execution
- **Security**: Sandboxed execution with explicit permissions
- **Discoverability**: Tools self-describe their capabilities
- **Composability**: Tools can be combined and chained
- **Local-First**: Must work entirely offline
- **Extensibility**: Easy to add custom tools
- **Interoperability**: Work across LangChain, other frameworks

## Decision
We will adopt the **Model Context Protocol (MCP)** as the standard for tool integration, with the following approach:
1. MCP servers for all external tool integrations
2. Official MCP servers (filesystem, git, database) used where available
3. Custom MCP servers for project-specific capabilities
4. LangChain MCP integration layer for agent access
5. Explicit permission model for all tool access

## Rationale

### Why MCP

**Standardization Benefits:**
- Vendor-neutral protocol backed by Anthropic
- Clear specification for tool definition and execution
- Growing ecosystem of pre-built servers
- Consistent interface across different tools
- Future-proof as standard evolves

**Security Model:**
- Server-based architecture enables sandboxing
- Explicit capability declarations
- Permission-based access control
- Resource limits configurable per server
- Audit logging built-in

**Developer Experience:**
- JSON-RPC 2.0 based (familiar, well-specified)
- Auto-generated tool descriptions from schemas
- TypeScript/Python SDKs available
- Hot-reload support during development
- Comprehensive documentation

**Local-First Compatibility:**
- No cloud dependencies required
- Servers run as local processes
- IPC or stdio communication (no network needed)
- Works offline by design
- Fast (sub-millisecond) local communication

### MCP vs Alternatives

**Comparison Matrix:**

| Feature | MCP | OpenAI Functions | LangChain Tools | Direct Python |
|---------|-----|------------------|-----------------|---------------|
| Standardization | ✅ Protocol | ❌ Vendor-specific | ⚠️ Framework-specific | ❌ Ad-hoc |
| Security | ✅ Sandboxed | ❌ Same process | ❌ Same process | ❌ Full access |
| Reusability | ✅ Cross-framework | ❌ OpenAI only | ⚠️ LangChain only | ❌ Project-specific |
| Documentation | ✅ Auto-generated | ⚠️ Manual | ⚠️ Partial | ❌ Manual |
| Local-First | ✅ Native | ✅ Compatible | ✅ Compatible | ✅ Native |
| Ecosystem | ⚠️ Growing | ✅ Large | ✅ Large | N/A |

**Trade-off Analysis:**
- Accept smaller ecosystem today for future standardization
- Slight overhead (JSON-RPC) acceptable for security benefits
- Investment in MCP skills transfers across projects
- Can wrap existing tools in MCP servers

## Consequences

### Positive
- Future-proof tool integrations as MCP adoption grows
- Secure-by-default tool execution
- Reusable tools across different agents and projects
- Clear separation between agent logic and tool implementation
- Easier testing (mock MCP servers)
- Potential to share tools with broader community
- Better resource management (per-server limits)

### Negative
- Additional layer of abstraction (JSON-RPC overhead)
- Smaller ecosystem than direct LangChain tools
- Need to wrap some existing tools in MCP servers
- Learning curve for MCP protocol
- Debugging requires understanding client-server model
- Each server is a separate process (resource overhead)

### Mitigation Strategies
1. **Overhead**: Profile performance, optimize critical paths, acceptable for local models
2. **Ecosystem**: Contribute custom servers back, leverage LangChain tools as fallback
3. **Learning Curve**: Provide templates and examples for common server patterns
4. **Debugging**: Build development tools (server inspector, request logger)
5. **Resources**: Share servers between agents, lazy initialization

## Alternatives Considered

### Alternative 1: Direct LangChain Tools
**Pros:**
- Large existing ecosystem
- Zero overhead
- Simple Python functions
- Excellent documentation
- Native integration

**Cons:**
- No sandboxing
- Tools tied to LangChain
- Security concerns
- No standardized protocol
- Manual documentation

**Why Rejected:** Security and standardization concerns outweigh convenience. We use LangChain tools as fallback for simple, trusted operations.

### Alternative 2: OpenAI Function Calling
**Pros:**
- Well-documented
- Large ecosystem
- Direct LLM support
- JSON Schema based

**Cons:**
- Vendor lock-in
- No sandboxing
- Requires OpenAI-compatible API
- Not a true protocol (just format)
- Execution in same process

**Why Rejected:** Vendor-specific, no security benefits, doesn't align with local-first philosophy.

### Alternative 3: Custom Plugin System
**Pros:**
- Full control
- Optimized for our use case
- No external dependencies
- Simple implementation

**Cons:**
- Reinventing wheel
- No community ecosystem
- Maintenance burden
- Non-standard
- No interoperability

**Why Rejected:** MCP provides everything we need without maintenance burden. Better to contribute to ecosystem than build custom system.

### Alternative 4: Docker-Based Sandboxing
**Pros:**
- Strong security
- Resource isolation
- Proven technology
- Language-agnostic

**Cons:**
- Heavyweight (>100MB per container)
- Slow startup (seconds)
- Requires Docker daemon
- Complex setup
- Not local-first friendly

**Why Rejected:** Too heavyweight for tool execution. MCP provides sufficient sandboxing with lower overhead.

### Alternative 5: WASM Plugins
**Pros:**
- True sandboxing
- Near-native performance
- Cross-platform
- Small size

**Cons:**
- Immature ecosystem
- Limited language support
- Complex build pipeline
- Debugging challenges
- No existing AI tool ecosystem

**Why Rejected:** Too experimental for production use. Interesting future direction, but MCP serves needs today.

## Implementation

### MCP Server Categories

**1. Official MCP Servers** (use as-is):
```bash
# Filesystem access
npm install -g @anthropic/mcp-server-filesystem

# Git operations
npm install -g @anthropic/mcp-server-git

# Database access
npm install -g @anthropic/mcp-server-postgres
```

**2. Custom MCP Servers** (build for project):
```
mcp-servers/
├── custom/
│   ├── ollama-manager/          # Manage local models
│   ├── langgraph-inspector/     # Debug agent state
│   ├── transformer-lens/        # Interpretability tools
│   └── apple-shortcuts/         # macOS automation
└── README.md
```

**3. LangChain MCP Integration**:
```python
from langchain_mcp import MCPToolkit

# Initialize MCP client
toolkit = MCPToolkit(
    server_path="npx",
    server_args=["-y", "@anthropic/mcp-server-filesystem", "/Users/user"],
    timeout=30
)

# Convert to LangChain tools
tools = toolkit.get_tools()

# Use with agent
agent = create_react_agent(llm, tools)
```

### Custom Server Example
```python
# mcp-servers/custom/ollama-manager/server.py
from mcp import Server, Tool
import ollama

server = Server("ollama-manager")

@server.tool()
async def list_models() -> dict:
    """List all available Ollama models"""
    result = ollama.list()
    return {"models": [m["name"] for m in result["models"]]}

@server.tool()
async def pull_model(name: str) -> dict:
    """Pull a model from Ollama registry"""
    ollama.pull(name)
    return {"status": "success", "model": name}

@server.tool()
async def get_model_info(name: str) -> dict:
    """Get detailed information about a model"""
    info = ollama.show(name)
    return info

if __name__ == "__main__":
    server.run()
```

### Server Configuration
```json
// config/mcp-servers.json
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-filesystem", "/Users/user"],
      "enabled": true
    },
    "git": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-git"],
      "enabled": true
    },
    "ollama": {
      "command": "python",
      "args": ["mcp-servers/custom/ollama-manager/server.py"],
      "enabled": true
    }
  }
}
```

### Permission Model
```python
# config/mcp-permissions.py
from enum import Enum

class Permission(Enum):
    READ_FILESYSTEM = "fs:read"
    WRITE_FILESYSTEM = "fs:write"
    EXECUTE_COMMAND = "exec:run"
    NETWORK_ACCESS = "net:access"
    GIT_OPERATIONS = "git:*"

# Server permissions
SERVER_PERMISSIONS = {
    "filesystem": [Permission.READ_FILESYSTEM, Permission.WRITE_FILESYSTEM],
    "git": [Permission.GIT_OPERATIONS, Permission.READ_FILESYSTEM],
    "ollama": [Permission.NETWORK_ACCESS],  # localhost only
}

# User approval required for
REQUIRE_APPROVAL = [
    Permission.WRITE_FILESYSTEM,
    Permission.EXECUTE_COMMAND,
    Permission.NETWORK_ACCESS,
]
```

### Integration Pattern
```python
# utils/mcp_manager.py
from typing import List
from langchain_mcp import MCPToolkit
from config.mcp_servers import load_server_config

class MCPManager:
    def __init__(self, config_path: str = "config/mcp-servers.json"):
        self.config = load_server_config(config_path)
        self.toolkits = {}

    def initialize_server(self, server_name: str) -> MCPToolkit:
        """Initialize an MCP server and return toolkit"""
        if server_name in self.toolkits:
            return self.toolkits[server_name]

        server_config = self.config["servers"][server_name]
        if not server_config["enabled"]:
            raise ValueError(f"Server {server_name} is disabled")

        toolkit = MCPToolkit(
            server_path=server_config["command"],
            server_args=server_config["args"],
            timeout=30
        )

        self.toolkits[server_name] = toolkit
        return toolkit

    def get_all_tools(self, server_names: List[str] = None) -> List:
        """Get tools from specified servers"""
        if server_names is None:
            server_names = [
                name for name, config in self.config["servers"].items()
                if config["enabled"]
            ]

        tools = []
        for name in server_names:
            toolkit = self.initialize_server(name)
            tools.extend(toolkit.get_tools())

        return tools
```

## Verification

### Success Criteria
- [ ] All external tool access via MCP servers
- [ ] Filesystem, git, and Ollama servers implemented
- [ ] Permission model enforced
- [ ] Tool documentation auto-generated
- [ ] Examples demonstrate 5+ MCP servers
- [ ] Performance overhead <10ms per tool call

### Testing Strategy
```python
# tests/test_mcp_integration.py
def test_mcp_server_initialization():
    """Verify MCP servers start correctly"""

def test_tool_discovery():
    """Verify tools are discovered from servers"""

def test_permission_enforcement():
    """Verify permission model blocks unauthorized access"""

def test_tool_execution():
    """Verify tools execute correctly via MCP"""

def test_error_handling():
    """Verify graceful handling of server failures"""

# tests/test_custom_servers.py
def test_ollama_server():
    """Test custom Ollama MCP server"""

def test_transformer_lens_server():
    """Test custom TransformerLens MCP server"""
```

### Monitoring
- Track tool execution times
- Monitor server startup/shutdown
- Log tool usage patterns
- Measure overhead vs direct calls

## Migration Path

### Phase 1: Core MCP Servers (Current)
- Filesystem, git, database servers
- Basic integration examples
- Permission model implementation

### Phase 2: Custom Servers
- Ollama management server
- TransformerLens server
- macOS automation server

### Phase 3: Advanced Features
- Hot-reload for development
- Tool chaining and composition
- Cross-server transactions
- Performance optimization

### From Direct LangChain Tools
```python
# Before: Direct LangChain tool
from langchain.tools import tool

@tool
def read_file(path: str) -> str:
    """Read file contents"""
    with open(path) as f:
        return f.read()

# After: Via MCP filesystem server
from langchain_mcp import MCPToolkit

toolkit = MCPToolkit(
    server_path="npx",
    server_args=["-y", "@anthropic/mcp-server-filesystem", "/Users/user"]
)
tools = toolkit.get_tools()  # Includes read_file, write_file, etc.
```

## References
- [MCP Specification](https://github.com/modelcontextprotocol/specification)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Official MCP Servers](https://github.com/modelcontextprotocol/servers)
- [LangChain MCP Integration](https://python.langchain.com/docs/integrations/tools/mcp)
- [MCP Server Implementation Guide](https://modelcontextprotocol.io/docs/server)

## Related ADRs
- ADR-001: Local-First Architecture (compatibility requirement)
- ADR-002: LangGraph Choice (tool integration layer)
- Future: ADR on tool security and sandboxing

## Changelog
- 2025-10-26: Initial version - MCP as standard tool protocol
