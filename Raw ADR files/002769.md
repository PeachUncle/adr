# ADR-0001: Discovery Worker Pool for MCP Servers

## Status

**Accepted**

**Date**: 2024-11-01

**Deciders**: Core Team

## Context

Mut needs to automatically discover tools, prompts, and resources from connected MCP servers. The discovery process involves:
- Connecting to MCP servers via stdio or SSE protocols
- Querying available capabilities
- Storing discovered items in the database
- Detecting changes over time
- Maintaining health status for each server

Challenges:
- Multiple MCP servers need to be discovered periodically
- Discovery operations are I/O bound (process spawning, network calls)
- Need to avoid database thrashing on unchanged data
- Must handle server failures gracefully
- Newly created MCPs should be discovered immediately, not after waiting for scheduled interval

## Decision

We will implement an asynchronous worker pool architecture for MCP discovery with:

1. **Dual-Queue System**: Priority queue for immediate discovery + regular job queue for scheduled discovery
2. **Worker Pool**: Configurable number of concurrent workers processing discovery jobs
3. **Checksum-Based Updates**: SHA256 checksums to detect changes before updating database
4. **Scheduled Discovery**: Periodic refresh (every 10 minutes) for all active MCPs
5. **On-Demand Discovery**: Immediate priority discovery when MCPs are created or updated

## Architecture

```
       ┌─────────────────────┐         ┌─────────────────────┐
       │   Scheduler         │         │  API Create MCP     │
       │   (Every 10 min)    │         │  (On-Demand)        │
       └──────────┬──────────┘         └──────────┬──────────┘
                  │                               │
      Fetch Active MCPs from DB           Trigger Immediate
                  │                        Discovery (Priority)
                  │                               │
                  ▼                               ▼
       ┌─────────────────────┐         ┌─────────────────────┐
       │   Job Queue         │◄────────┤  Priority Queue     │
       │   (Buffered Chan)   │         │  (High Priority)    │
       └──────────┬──────────┘         └─────────────────────┘
                  │
  ┌───────────────┼───────────────────┐
  │               │                   │
  ▼               ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Worker 1    │ │  Worker 2    │ │  Worker N    │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │               │                 │
       │    Discover MCP (stdio/sse)     │
       │    Calculate Checksums          │
       │               │                 │
       └───────────────┼─────────────────┘
                       │
                       ▼
             ┌─────────────────────┐
             │  Result Handler     │
             │  - Compare checksums│
             │  - Update if changed│
             │  - Update health    │
             └─────────────────────┘
```

## Rationale

### Why Worker Pool?
- **Parallelism**: Multiple MCPs can be discovered concurrently
- **Resource Control**: Bounded concurrency prevents system overload
- **Isolation**: One failing MCP doesn't block others

### Why Checksums?
- **Efficiency**: Avoid unnecessary database writes when nothing changed
- **Performance**: SHA256 is fast and reliable for change detection
- **Audit Trail**: Track what changed and when

### Why Priority Queue?
- **User Experience**: Immediate feedback when creating new MCPs
- **Flexibility**: Allows manual refresh without waiting for schedule
- **Efficiency**: Separates time-sensitive from periodic tasks

### Why Scheduled Discovery?
- **Freshness**: Keep discovered items up-to-date
- **Reliability**: Catch changes even if manual refresh is forgotten
- **Automation**: No manual intervention required

## Implementation Notes

### Core Components

1. **Scheduler**: Ticker-based, runs every 10 minutes
2. **Priority Queue**: Buffered channel for high-priority jobs
3. **Job Queue**: Buffered channel for scheduled jobs
4. **Workers**: Goroutines that poll priority queue first, then job queue
5. **Result Handler**: Processes discovery results and updates database

### Key Features

**Checksum-Based Change Detection:**
- SHA256 checksums for tools, prompts, and resources
- Only updates database when changes detected
- Stores checksums in `mcps_meta` table

**Async Worker Pool:**
- Configurable number of concurrent workers
- Bounded job queue prevents memory issues
- Each worker processes jobs independently

**Fault Tolerance:**
- Automatic retries with exponential backoff
- Isolated worker failures
- Health status tracking per MCP

**Graceful Shutdown:**
- Clean shutdown without job loss
- Wait for in-flight jobs to complete
- Configurable grace period

**Observability:**
- Rich structured logging with zerolog
- Worker metrics (jobs processed, changes detected)
- Per-MCP error tracking

**Priority Discovery for New MCPs:**
- Newly created MCPs trigger immediate discovery
- Priority queue bypasses the scheduled interval
- High-priority jobs processed before scheduled discoveries
- Ensures fast feedback for newly added servers
- Admin sees discovered tools/prompts/resources within seconds
