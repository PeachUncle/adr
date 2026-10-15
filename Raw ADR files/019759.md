---
description: "Centralized ADR hosting via MCP protocol enabling universal AI agent access without filesystem dependencies"
---

# Use MCP Protocol for ADR Distribution

## Status
**Proposed** | Date: 2025-09-03

## Context
- AI agents across multiple projects need access to organizational architectural decisions
- Traditional ADR storage in git repositories requires filesystem access that AI agents don't have
- Teams work on different projects but face similar architectural questions repeatedly
- Knowledge sharing across projects is hampered by ADR isolation in individual repositories
- AI-assisted development is becoming standard but lacks access to organizational wisdom
- Need to distribute architectural knowledge to any team or project on-demand
- Being able to connect any MCP client to data globally distributed.

## Decision
We will expose ADRs as MCP (Model Context Protocol) resources hosted on a remote server, enabling any MCP client to connect and consume architectural knowledge without filesystem dependencies.

**Architecture:**
```
Remote MCP Server (ADR Host)
    ↓ (MCP Protocol)
Any MCP Client (Claude, ChatGPT, etc.)
    ↓
AI Agent with Architectural Context
```

**Key Principles:**
- Centralized hosting on remote server for universal access
- Standard MCP protocol for client compatibility
- On-demand resource consumption without local storage
- Distribution controlled by MCP client configuration

## Consequences

### ✅ Positive
- **Universal Access** - Any MCP client can connect to the remote server from anywhere
- **Centralized Knowledge** - Single source of truth for architectural decisions across all projects
- **Selective Distribution** - Share ADRs with specific teams/projects by sharing server connection details
- **Zero Local Setup** - No git cloning, no filesystem access, no local maintenance for consumers
- **Protocol Standardization** - Works with any MCP-compatible AI tool (Claude Code, ChatGPT, custom clients)

### ❌ Negative
- **Infrastructure Dependency** - Requires maintaining remote server infrastructure
- **Network Requirement** - ADRs inaccessible during network outages
- **Additional Abstraction** - Extra layer between ADRs and consumers vs. direct file access
- **Operational Overhead** - Server monitoring, updates, and availability management

### ⚪ Neutral
- ADRs transition from static files to network-accessible resources
- Architectural knowledge becomes part of AI agent's available context
- Access patterns shift from pull (git clone) to connect (MCP client configuration)

## Alternatives Considered

| Alternative | Rejection Reason |
|-------------|------------------|
| **Git Repository Only** | AI agents lack filesystem access; requires manual copy-paste of context |
| **Wiki/Documentation Site** | No standardized protocol for AI consumption; requires web scraping |
| **Database with API** | Requires custom client implementation for each AI tool |
| **Embedded in Each Project** | Duplicates decisions across projects; maintenance nightmare |
| **SharePoint/Google Docs** | No programmatic access standard for AI agents; poor version control |

## Implementation Notes

**Reference:** [Model Context Protocol Specification](https://modelcontextprotocol.io)

The remote hosting enables the key value proposition: "connect once, access everywhere." Teams configure their MCP clients to connect to the ADR server and immediately gain access to organizational architectural wisdom.