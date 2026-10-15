# Design: Paperless-NGX MCP Server

## Context
Paperless-NGX is a document management system with a REST API. We need to expose its functionality through MCP (Model Context Protocol) to enable AI assistants to search and interact with documents. This is a new project, starting from a minimal Python scaffold.

## Goals / Non-Goals

### Goals
- Provide MCP-compliant server for Paperless-NGX integration
- Support OpenWebUI as primary client via HTTP streaming
- Implement document search as the first capability
- Enable local testing through VS Code MCP support
- Use modern Python tooling (uv, fastmcp, ruff)
- Keep configuration simple (environment variables)

### Non-Goals
- Not implementing all Paperless-NGX API endpoints in this change
- Not building a web UI or standalone client
- Not handling document uploads/modifications (read-only for now)
- Not implementing user authentication (uses single API token)

## Decisions

### Decision 1: Use fastmcp Framework
**Rationale**: fastmcp provides a simple, Pythonic way to build MCP servers with minimal boilerplate. It handles protocol details and tool registration automatically.

**Alternatives considered**:
- `mcp` official Python SDK - More verbose, requires manual protocol handling
- Custom implementation - Unnecessary complexity for this use case

### Decision 2: .env File for Configuration
**Rationale**: 
- API URL and token should not be hardcoded
- .env files are standard for local development secrets
- Easy to change without code modifications
- python-dotenv automatically loads .env at startup
- .env file is gitignored for security

**Configuration**:
- `.env` file in project root with:
  - `PAPERLESS_API_URL` - Base URL (default: http://localhost:8000)
  - `PAPERLESS_API_TOKEN` - Authentication token (required)
- `.env.example` provided as template

### Decision 3: httpx for HTTP Client
**Rationale**: Modern async-capable HTTP client, better than requests for MCP server context.

### Decision 4: Support Both stdio and Streamable HTTP Transports
**Rationale**:
- stdio for VS Code and Claude Desktop (local MCP clients)
- Streamable HTTP for OpenWebUI (MCP's official HTTP transport protocol)
- fastmcp supports both transports natively

**Implementation**:
- Default to stdio when no port specified
- Enable Streamable HTTP with --port flag
- OpenWebUI requires "MCP (Streamable HTTP)" type in configuration

### Decision 5: Start with Single Tool (search_documents)
**Rationale**: 
- Validate the architecture with one working tool
- Avoid over-engineering before proving the approach
- Easy to add more tools incrementally

**Tool Signature**:
```python
@mcp.tool()
def search_documents(query: str, page: int = 1, page_size: int = 25) -> str:
    """Search Paperless-NGX documents by query string"""
```

Returns formatted JSON string with:
- Document ID, title, content preview
- Correspondent, document type, tags
- Created date, file information
- Total count and pagination info

## Architecture

### Module Structure
```
paperless-ngx-mcp/
├── src/
│   └── paperless_ngx_mcp/
│       ├── __init__.py
│       ├── server.py      # MCP server setup
│       ├── api.py         # Paperless API client
│       └── tools.py       # MCP tools (search_documents)
├── main.py               # Entry point
├── pyproject.toml        # Dependencies
└── .vscode/
    └── mcp-server.json   # VS Code MCP config
```

### Data Flow

**stdio mode** (VS Code, Claude Desktop):
1. MCP client calls server via stdin/stdout
2. MCP server receives tool invocation (search_documents)
3. API client makes HTTP request to Paperless-NGX
4. Response is formatted and returned through MCP protocol via stdout

**Streamable HTTP mode** (OpenWebUI):
1. OpenWebUI connects to server via HTTP endpoint
2. Uses MCP's Streamable HTTP protocol for bidirectional communication
3. MCP protocol messages exchanged over HTTP streams
4. API client makes HTTP request to Paperless-NGX
5. Response is formatted and streamed back through Streamable HTTP

## Risks / Trade-offs

### Risk: API Token Security
**Mitigation**: 
- Document that token should never be committed
- Use environment variables
- Add .env to .gitignore
- Future: Support token file or keychain integration

### Risk: API Changes in Paperless-NGX
**Mitigation**: 
- Pin to tested API version in documentation
- Handle API errors gracefully
- Log API responses for debugging

### Trade-off: Sync vs Async
**Decision**: Use synchronous httpx calls initially
**Rationale**: 
- Simpler to implement and debug
- MCP protocol handles concurrency
- Can migrate to async later if needed

## Migration Plan

This is a new implementation, no migration needed.

**Rollout**:
1. Implement and test locally
2. Document setup process
3. Validate with VS Code MCP integration
4. Add to project README

**Validation**:
- Verify search returns correct results
- Test with empty results, large result sets
- Confirm VS Code can invoke the tool
- Test with invalid API credentials (should fail gracefully)

## Open Questions

None at this time. Implementation is straightforward with established patterns.
