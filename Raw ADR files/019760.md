---
description: "Direct GitHub repository access eliminating local storage and synchronization complexity"
---

# Use GitHub as Stateless ADR Backend

## Status
**Proposed** | Date: 2025-09-03

## Context
- MCP server needs a storage backend for ADRs that's simple to implement and maintain
- FastMCP doesn't support native git:// URI scheme despite MCP specification listing it
- Need version control for tracking ADR evolution and decision history
- Want to avoid operational complexity of synchronization mechanisms
- ADRs must be editable through standard git workflows
- Multiple deployment environments should serve identical content without configuration drift

## Decision
We will fetch ADRs directly from GitHub repository via raw URLs (raw.githubusercontent.com) without any local storage, caching, or synchronization.

**Architecture:**
```
GitHub Repository (Source of Truth)
    ↓ (HTTPS - raw.githubusercontent.com)
MCP Server (Stateless)
    ↓ (On-demand fetch)
MCP Client
```

**Implementation Approach:**
- Use `requests.get()` to fetch from raw GitHub URLs
- No local file storage or git operations
- Each request fetches fresh content from GitHub
- Parse YAML frontmatter on-demand

## Consequences

### ✅ Positive
- **Zero State Management** - No local storage, no cache invalidation, no sync scripts
- **Single Source of Truth** - GitHub repository is the only authoritative source
- **Version Control Built-in** - Full git history, branching, and collaboration features
- **Operational Simplicity** - No cron jobs, webhooks, or sync monitoring required
- **Deployment Simplicity** - Server can run anywhere with internet, no persistent storage needed
- **Immediate Updates** - Push to GitHub → immediately available (after CDN cache refresh)

### ❌ Negative
- **Network Dependency** - Every ADR access requires internet connectivity
- **No Native git:// Support** - Must use HTTP instead of git protocol as intended by MCP spec
- **GitHub API Rate Limits** - 60 requests/hour for unauthenticated access
- **Latency** - Network round-trip for every ADR fetch (~100-200ms)

### ⚪ Neutral
- Uses raw.githubusercontent.com instead of git protocol
- GitHub CDN caching can cause brief delays in update propagation
- Performance acceptable for ADR use case (infrequent reads)

## Alternatives Considered

| Alternative | Rejection Reason |
|-------------|------------------|
| **VPS with Local Files + Sync** | Operational complexity: cron jobs, sync failures, monitoring overhead |
| **Git Clone on Startup** | State management complexity; requires pulls for updates |
| **Local Cache Layer** | Cache invalidation complexity; "two hard problems in CS" |
| **Database Storage** | Loses version control benefits; additional infrastructure |
| **Git Submodules** | Complex for consumers; requires local filesystem |

## Implementation Notes

The key insight: **operational simplicity > code simplicity**. While fetching from GitHub on every request seems inefficient, it eliminates entire categories of operational problems (sync failures, cache inconsistencies, storage management).

**Trade-off:** We accept network latency (100-200ms) to eliminate operational complexity. For ADR access patterns (infrequent reads), this is optimal.