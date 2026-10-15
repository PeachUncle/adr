# ADR-002: MCP Integration Architecture

**Status**: Accepted
**Date**: 2025-12-02 (Retroactive - Phase 7)
**Decision Makers**: Development Team
**Supersedes**: N/A

---

## Context

The NFL SIM needed to integrate external data sources and AI capabilities for:

- Historical NFL player statistics (for draft comparisons)
- Real-time weather data (for game conditions)
- Sports news generation (for narrative immersion)
- Future AI agent capabilities (scouting, coaching, etc.)

**Requirements**:

1. Standardized way to connect to external tools/APIs
2. Support for both local and remote services
3. Security (API key management, request sanitization)
4. Performance (caching, rate limiting)
5. Extensibility (easy to add new tools)
6. Testability (mock external services)

**Constraints**:

- Backend is Python/FastAPI
- Some tools may be external APIs, others internal services
- Need to support different transport protocols
- Must work in Docker environment

---

## Decision

**We adopted the Model Context Protocol (MCP) as our integration architecture.**

**Implementation**:

- **Registry Pattern**: `MCPRegistry` manages all MCP server connections
- **Client Abstraction**: `MCPHostClient` handles individual server communication
- **Transport Support**: stdio (local processes) and SSE (HTTP remote servers)
- **Configuration**: JSON-based config file (`mcp_config.json`) with environment variable support
- **Security**: Request/response sanitization, network isolation via Docker
- **Performance**: In-memory caching layer (`MCPCache`)

---

## Rationale

1. **Standardization**: MCP provides a well-defined protocol for tool integration, avoiding bespoke integration code for each service.

2. **Flexibility**: Supports multiple transports (stdio for local, SSE for remote), allowing mix of local Python scripts and remote APIs.

3. **Security by Design**:

   - Process isolation (stdio servers run in separate processes)
   - Network isolation (Docker)
   - Automatic request sanitization to prevent API key leaks

4. **Developer Experience**:

   - `fastmcp` library makes creating new servers trivial
   - Clear separation of concerns (MCP server vs application logic)
   - Easy to mock for testing

5. **Ecosystem**: MCP is gaining traction in AI tooling space, with growing library of compatible tools.

6. **Future-Proof**: Can easily add more sophisticated features like:
   - Dynamic server discovery
   - Load balancing across instances
   - Circuit breakers for failing services

---

## Consequences

### Positive Consequences

- ✅ Clean separation between application and external integrations
- ✅ Easy to add new data sources (create MCP server, register in config)
- ✅ Testable (mock MCP servers in tests)
- ✅ Secure (process/network isolation, sanitization)
- ✅ Observable (audit logging for all tool calls)
- ✅ Cacheable (reduce external API costs)

### Negative Consequences

- ⚠️ Additional complexity (registry, clients, servers)
- ⚠️ Learning curve (team must understand MCP protocol)
- ⚠️ Debugging complexity (multi-process architecture)
- ⚠️ Startup time increased (MCP server initialization)
- ⚠️ MCP protocol is still evolving (potential breaking changes)

### Neutral Consequences

- Each external integration requires a separate MCP server
- Configuration managed via JSON file (not database)
- MCP servers are Python scripts (must deploy with application)

---

## Alternatives Considered

### Alternative 1: Direct API Integration

- **Description**: Call external APIs directly from service layer
- **Pros**:
  - Simpler (no abstraction layer)
  - Fewer components
  - Easier debugging
- **Cons**:
  - Tightly coupled to specific APIs
  - Difficult to mock for testing
  - Security concerns (API keys in service code)
  - No standardization across integrations
- **Reason for rejection**: Would create maintenance burden as more integrations added

### Alternative 2: Message Queue (RabbitMQ/Kafka)

- **Description**: Use message broker for async external requests
- **Pros**:
  - Decoupled architecture
  - Async by default
  - Scalable
- **Cons**:
  - Overkill for synchronous requests
  - Infrastructure overhead (broker deployment)
  - Complexity for simple use cases
  - Higher latency
- **Reason for rejection**: Too heavyweight for current needs; MCP simpler

### Alternative 3: GraphQL Federation

- **Description**: Use GraphQL to federate external data sources
- **Pros**:
  - Standardized query language
  - Client can request exactly what it needs
  - Good for data aggregation
- **Cons**:
  - Requires GraphQL expertise
  - Overkill for action-oriented tools (not just data)
  - Performance overhead (query parsing)
- **Reason for rejection**: MCP better suited for action/tool paradigm

### Alternative 4: Custom Plugin System

- **Description**: Build our own plugin architecture
- **Pros**:
  - Full control over design
  - Tailored to our exact needs
- **Cons**:
  - Reinventing the wheel
  - Maintenance burden
  - No ecosystem benefits
- **Reason for rejection**: MCP achieves the same goals with existing protocol

---

## Implementation Notes

**Key Components:**

1. **MCP Registry** (`backend/app/core/mcp_registry.py`)

   - Singleton that manages all MCP server connections
   - Loads configuration from `backend/mcp_config.json`
   - Resolves environment variables for secrets
   - Handles startup/shutdown lifecycle

2. **MCP Host Client** (`backend/app/core/mcp_client.py`)

   - Represents connection to a single MCP server
   - Supports stdio and SSE transports
   - Implements request/response sanitization
   - Audit logging for all tool calls

3. **MCP Servers** (`backend/mcp_servers/`)

   - `nfl_stats_server/` - Historical player data
   - `weather_server/` - Game weather conditions
   - `sports_news_server/` - News generation
   - Built with `fastmcp` library

4. **Configuration** (`backend/mcp_config.json`)

   ```json
   {
     "servers": [
       {
         "name": "nfl_stats",
         "transport": "stdio",
         "command": "python",
         "args": ["mcp_servers/nfl_stats_server/server.py"],
         "env": { "API_KEY": "${NFL_STATS_API_KEY}" }
       }
     ]
   }
   ```

5. **Integration Points**:
   - `DraftAssistant` service uses `nfl_stats` MCP
   - `GMAgent` service uses multiple MCPs for trade evaluation
   - Future: Game simulation can use `weather` MCP

**Deployment**:

- MCP servers run as child processes in Docker container
- Environment variables injected via Docker Compose
- Network isolation via `app-network` in Docker

---

## Validation Criteria

**Success Metrics:**

1. **Performance**: MCP tool calls <500ms (p95) with caching
2. **Reliability**: 99.9% uptime for MCP registry
3. **Security**: Zero API key leaks in logs (audited)
4. **Extensibility**: New MCP server added in <1 hour
5. **Test Coverage**: >80% coverage for MCP components

**Current Status** (Phase 7 Complete):

- ✅ All metrics achieved
- ✅ 3 MCP servers operational
- ✅ Security audit passed
- ✅ Performance benchmarks met

**Review Timeline**: Reassess after adding 5+ more MCP servers or if performance degrades.

---

## References

- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [`fastmcp` Library](https://github.com/jlowin/fastmcp)
- Internal Documentation:
  - `docs/mcp_architecture.md` - Architecture overview
  - `docs/mcp_tools.md` - Available tools reference
  - `docs/guides/adding_mcp_servers.md` - Developer guide
  - `docs/SECURITY.md` - Security best practices
- Phase 7 Completion Report: `PHASE_7_COMPLETION.md`
