# ADR-0006: MCP Server Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "MCP Server Architecture" includes server framework, transport protocol, tool design, and deployment topology).

- **Status:** Accepted
- **Date:** 2025-12-17
- **Feature:** 002-ai-chatbot
- **Context:** Phase 3 requires exposing task operations (add, list, complete, delete, update) as tools that the AI agent can invoke. The Model Context Protocol (MCP) is the standard protocol for tool invocation between AI agents and external services. The MCP server must enforce user isolation (tools only operate on the authenticated user's tasks), integrate with existing Phase 2 task services, and run separately from the main FastAPI application for future scalability.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines microservice boundary and tool integration pattern
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Embedded vs separate, Python vs Node.js evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects AI agent integration, task operations, and deployment architecture
-->

## Decision

We will adopt the following integrated MCP server architecture:

- **Framework:** FastMCP Python SDK
- **Transport:** HTTP transport on port 8001
- **Deployment:** Separate Python process from main FastAPI app (port 8000)
- **Tool Pattern:** @mcp.tool() decorator with user_id parameter
- **Database Access:** Direct SQLModel/SQLAlchemy using shared database connection
- **User Isolation:** user_id parameter enforced in every tool; filtered in all database queries

### Tool Definitions

| Tool | Parameters | Returns |
|------|------------|---------|
| `add_task` | user_id, title, description? | {task_id, status, title} |
| `list_tasks` | user_id, status? | [{id, title, completed}] |
| `complete_task` | user_id, task_id | {task_id, status} |
| `delete_task` | user_id, task_id | {task_id, status} |
| `update_task` | user_id, task_id, title?, description? | {task_id, status} |

### Server Configuration Pattern

```python
from fastmcp import FastMCP
from src.services.task_service import TaskService

mcp = FastMCP("Todo MCP Server")

@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Create a new task for the user."""
    task = await task_service.create_task(user_id, title, description)
    return {"task_id": task.id, "status": "created", "title": task.title}

@mcp.tool()
async def list_tasks(user_id: str, status: str = "all") -> list:
    """List user's tasks, optionally filtered by status."""
    tasks = await task_service.list_tasks(user_id, status)
    return [{"id": t.id, "title": t.title, "completed": t.completed} for t in tasks]

# Run server
if __name__ == "__main__":
    mcp.run(host="0.0.0.0", port=8001)
```

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Client (Browser)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ SSE/HTTP
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Main App (Port 8000)                    │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ /api/chat/*     │  │ /api/tasks/*    │                   │
│  │ (Agent Runner)  │  │ (REST CRUD)     │                   │
│  └────────┬────────┘  └─────────────────┘                   │
└───────────┼─────────────────────────────────────────────────┘
            │ MCP HTTP
            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastMCP Server (Port 8001)                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  @mcp.tool() add_task, list_tasks, complete_task, ... │  │
│  └────────────────────────┬──────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────┘
                            │ SQLModel
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Neon PostgreSQL (Shared Database)               │
└─────────────────────────────────────────────────────────────┘
```

### Rationale

FastMCP provides a simple decorator-based approach to defining MCP tools. Running the MCP server as a separate process creates a clean microservice boundary that can scale independently. This architecture is Kubernetes-ready - the MCP server can be deployed as a separate container with its own scaling rules. User isolation is enforced at the tool level by requiring user_id in every tool call, which is injected by the agent runner from the authenticated JWT.

## Consequences

### Positive

- **Clean Separation:** MCP server has single responsibility; doesn't bloat main API
- **Independent Scaling:** Can scale MCP server separately based on tool execution load
- **Kubernetes Ready:** Separate processes map directly to separate containers/pods
- **Simple Tool Definition:** @mcp.tool() decorator is intuitive and generates schema automatically
- **HTTP Transport:** Standard HTTP protocol, easy to debug and monitor
- **Shared Database:** Reuses existing Neon PostgreSQL; no data synchronization needed
- **User Isolation Enforced:** user_id parameter ensures tools only access user's data
- **Async First:** FastMCP supports async, matching FastAPI patterns

### Negative

- **Process Overhead:** Running separate Python process adds memory overhead (~50-100MB)
  - *Mitigation:* Acceptable for Phase 3; containerization will optimize in Phase 4
- **Network Hop:** Tool calls go over HTTP (localhost:8001) instead of in-process
  - *Mitigation:* Localhost latency is <1ms; well within 500ms MCP tool execution target
- **Configuration Complexity:** Must manage two server processes in development and deployment
  - *Mitigation:* Document startup scripts; consider process manager (PM2/supervisord)
- **Database Connection Duplication:** Both servers maintain connection pools
  - *Mitigation:* Neon connection pooling handles this; total connections within limits
- **Cold Start:** MCP server may have cold start if scaled to zero
  - *Mitigation:* Keep minimum 1 replica in production; acceptable for Phase 3

## Alternatives Considered

### Alternative A: Embedded MCP in FastAPI
- **Pros:** Single process, no network hop, simpler deployment, shared database connection pool
- **Cons:** Tight coupling, harder to scale independently, complicates FastAPI middleware
- **Why Rejected:** Embedding MCP in FastAPI would require custom middleware integration and prevent independent scaling. Separate process provides cleaner architecture and is Kubernetes-ready for Phase 4.

### Alternative B: Node.js MCP Server
- **Pros:** Mature MCP SDK support, good async performance, separate language boundary
- **Cons:** Different language from backend, requires Node.js runtime, separate dependency management
- **Why Rejected:** Team expertise is Python; adding Node.js increases operational complexity. FastMCP provides equivalent functionality in Python.

### Alternative C: Raw MCP Protocol Implementation
- **Pros:** No dependency on FastMCP, full control over protocol handling
- **Cons:** Must implement MCP spec from scratch, more boilerplate, higher bug risk
- **Why Rejected:** Reimplementing MCP protocol is unnecessary work; FastMCP handles protocol correctly. Violates "don't reinvent the wheel" principle.

### Alternative D: gRPC Transport Instead of HTTP
- **Pros:** Binary protocol (faster), strong typing via protobuf, streaming support
- **Cons:** More complex setup, requires protobuf compilation, harder to debug
- **Why Rejected:** HTTP is sufficient for our latency requirements (<500ms); gRPC complexity not justified. HTTP is easier to debug and monitor in development.

## References

- Feature Spec: [specs/002-ai-chatbot/spec.md](../../specs/002-ai-chatbot/spec.md)
- Implementation Plan: [specs/002-ai-chatbot/plan.md](../../specs/002-ai-chatbot/plan.md) §Phase 2
- Research Notes: [specs/002-ai-chatbot/research.md](../../specs/002-ai-chatbot/research.md) §2
- Related ADRs: ADR-0002 (Backend Stack - SQLModel/PostgreSQL), ADR-0005 (AI Agent Stack - tool integration)
- FastMCP GitHub: https://github.com/jlowin/fastmcp
- MCP Specification: https://modelcontextprotocol.io/
