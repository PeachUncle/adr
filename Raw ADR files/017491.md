# ADR-003: MCP Tool Layer for Task Operations

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-19
- **Feature:** Phase 3 - Todo AI Chatbot
- **Context:** AI agents need to perform task CRUD operations on the backend. We must decide how agents interact with the data layer: direct service calls, REST API calls, GraphQL, or an abstraction layer like MCP (Model Context Protocol). The choice affects testability, security, and standardization.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ Yes - defines AI-to-backend contract
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ Yes - direct calls, REST, GraphQL, MCP
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ Yes - affects all agent-backend interactions
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We adopt **MCP (Model Context Protocol)** as the abstraction layer between AI agents and backend task operations:

| Component | Technology | Configuration |
|-----------|------------|---------------|
| **Protocol** | MCP | Anthropic's Model Context Protocol |
| **Server** | MCPServerAgent | Python implementation via `mcp` SDK |
| **Tools** | 5 task tools | Stateless, schema-validated, deterministic |
| **Validation** | Pydantic schemas | Strict input/output typing |
| **Execution** | 30-second timeout | Per constitution rules |

### MCP Tools Registry

| Tool | Operation | Input Schema | Output Schema |
|------|-----------|--------------|---------------|
| `list_tasks` | Read | `{ status?, limit?, offset? }` | `{ tasks[], total }` |
| `create_task` | Create | `{ title, description?, due_date? }` | `{ task }` |
| `update_task` | Update | `{ task_id, title?, description? }` | `{ task }` |
| `complete_task` | Update | `{ task_id, completed }` | `{ task }` |
| `delete_task` | Delete | `{ task_id, confirm }` | `{ deleted_task_id }` |

### Tool Design Principles

1. **Stateless**: No state persisted between invocations
2. **Deterministic**: Same input always produces same output
3. **Schema-validated**: Pydantic models for all I/O
4. **User-scoped**: All operations filtered by authenticated user_id
5. **Confirmation-gated**: Destructive actions require `confirm: true`

### Standard Result Format

```python
class MCPToolResult:
    success: bool
    data: dict | list | None
    error: str | None
    error_code: str | None  # TASK_NOT_FOUND, CONFIRMATION_REQUIRED, etc.
```

## Consequences

### Positive

- **Standardized interface**: All agents use the same tool contract
- **Inspectable**: Tool calls can be logged, audited, and replayed
- **Type safety**: Pydantic schemas catch malformed requests at invocation time
- **Testable**: Tools can be unit tested in isolation from agents
- **Extensible**: New tools can be added without modifying agent code
- **Security boundary**: Tools enforce user scoping; agents cannot bypass
- **Interoperability**: MCP is an emerging standard; future LLM integrations supported

### Negative

- **Abstraction overhead**: Extra layer between agents and services
- **Learning curve**: Team must understand MCP protocol and SDK
- **Limited ecosystem**: MCP is newer than alternatives (GraphQL, REST)
- **Python-specific**: Current MCP SDK is Python; limits language flexibility
- **Indirection**: Debugging requires tracing through tool layer

## Alternatives Considered

### Alternative A: Direct Service Calls

- **Approach**: Agents call `task_service.create_task()` directly
- **Pros**: Fastest, no abstraction overhead, full control
- **Cons**: No standardized interface, hard to audit, tight coupling, no schema validation
- **Why rejected**: Agents need a controlled, inspectable interface

### Alternative B: Internal REST API Calls

- **Approach**: Agents make HTTP requests to `/tasks` endpoints
- **Pros**: Reuses existing API, HTTP is universal, easy to debug
- **Cons**: Network overhead, authentication complexity, not designed for AI consumption
- **Why rejected**: Overhead of HTTP for internal calls; REST not optimized for tool semantics

### Alternative C: GraphQL Layer

- **Approach**: Expose task operations via GraphQL mutations/queries
- **Pros**: Flexible queries, strong typing, introspection
- **Cons**: Heavy for simple CRUD, learning curve, not AI-native
- **Why rejected**: GraphQL's flexibility is overkill; MCP is purpose-built for AI tools

### Alternative D: Custom Tool Interface

- **Approach**: Define our own tool protocol (JSON-RPC or similar)
- **Pros**: Full control over design, no external dependencies
- **Cons**: Reinventing the wheel, no ecosystem benefits, maintenance burden
- **Why rejected**: MCP provides a well-designed standard; no need to build our own

## References

- Feature Spec: `specs/phase3-ai-chatbot/spec.md` (Section 3: MCP Server Tools)
- MCP Skill Definition: `.claude/skills/mcp-server-tools/SKILL.md`
- MCP Agent Definition: `.claude/agents/mcp-server-implementer.md`
- Related ADRs: ADR-002 (MCPServerAgent is part of orchestration architecture)
- Constitution: `.specify/memory/constitution.md` (MCP tool timeout: 30s)
