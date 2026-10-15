# ADR-001: Dashboard HTTP API Evaluation

**Status:** Accepted  
**Date:** 2025-11-27  
**Decision Maker:** Framework Architecture & Tooling Team  
**Issue:** #36  

## Context

The Loaded Vibes framework requires a dashboard interface for both the CLI (`loaded-vibes dashboard`) and potential VS Code extension integrations. The current requirements specify:

- **PRD §5.2**: Synthwave UI with DevCycle queue, live logs, metrics, and TODO/CHANGELOG feeds
- **TECH §5.2**: UI toolkit based on `ink`, `blessed-contrib`, and related CLI rendering libraries
- **TECH §5.4**: Dashboard log latency < 200 ms on modern hardware
- **TECH §11**: Open question regarding local HTTP API for dashboards/webviews

We evaluated whether a local HTTP API should back CLI dashboards or VS Code webviews, considering security, latency, portability, and implementation complexity.

## Use Cases Assessed

### CLI Dashboard Use Cases

| Use Case | Description | Data Flow |
|----------|-------------|-----------|
| DevCycle Queue | Display pending/active/completed DevCycles | Read from `devcycles.config.json` + state |
| Live Logs | Stream orchestrator events in real-time | Tail NDJSON logs, pipe to UI |
| Metrics Panel | CPU/memory usage, latency stats | Poll system APIs, render charts |
| TODO/CHANGELOG Feed | Display recent changes | Read/parse markdown files |
| Command Palette | Fuzzy search DevCycle actions | In-memory command registry |
| Notifications | Error toasts + remediation links | Event-driven from orchestrator |

### VS Code Webview Use Cases

| Use Case | Description | Integration Pattern |
|----------|-------------|---------------------|
| Embedded Dashboard | Mirror CLI dashboard in VS Code | Webview panel + message passing |
| DevCycle Launcher | Trigger DevCycles from sidebar | Extension command + terminal |
| Log Viewer | Rich log browsing/filtering | Webview with virtual scrolling |
| State Inspector | View `state.json` graphically | Tree view or webview |
| Doctor Results | Display diagnostics | Problem matcher + webview |

## Options Considered

### Option A: Pure CLI Streaming (Ink/React-Ink)

**Architecture:**
```
Orchestrator → NDJSON Logs → File Watcher → Ink Components → Terminal
```

**Pros:**
- Zero network surface—no ports to secure `[SPEC-SECURITY §1]`
- Native terminal integration, consistent with CLI-first philosophy
- Lower resource footprint (no HTTP server process)
- Simpler dependency graph (no Express/Fastify/Hono overhead)
- Ink's React model supports `< 200 ms` updates for log streaming
- Direct file/process communication avoids serialization overhead

**Cons:**
- VS Code webviews cannot consume Ink directly
- Potential code duplication if webview requires separate rendering
- Terminal-only: no browser-based dashboard fallback

### Option B: Local HTTP API Server

**Architecture:**
```
Orchestrator → HTTP Server (localhost:PORT) → REST/SSE/WebSocket → Dashboard UI
```

**Pros:**
- Single data source for CLI, VS Code webview, and browser dashboards
- WebSocket/SSE enables push-based real-time updates
- Decoupled frontend—could use any web technology
- Easier to test API endpoints in isolation

**Cons:**
- **Security risk**: Exposes localhost port; requires token-based auth or socket permissions `[SPEC-SECURITY §1]`
- **Port conflicts**: Must handle port-in-use scenarios gracefully
- **Latency overhead**: HTTP handshake + serialization adds ~10-50 ms per request
- **Dependency creep**: Requires HTTP framework, middleware, CORS handling
- **Process management**: Must spawn/manage server lifecycle alongside CLI
- **Firewall warnings**: May trigger OS-level firewall prompts on first run
- **Resource usage**: Persistent HTTP server consumes memory even when idle

### Option C: Hybrid Approach (Recommended)

**Architecture:**
```
Orchestrator → NDJSON Logs ← CLI (Ink) via file watcher
                          ← VS Code Extension via file watcher + message passing
                          ← Optional HTTP Server (future, opt-in)
```

**Pros:**
- CLI dashboard uses pure Ink streaming—no HTTP overhead
- VS Code extension uses native `fs.watch` + extension host messaging
- HTTP API remains optional for advanced users (browser dashboards, remote debugging)
- Preserves security posture by default `[SPEC-SECURITY §1]`
- Meets `< 200 ms` latency target via direct file tailing `[TECH §5.4]`

**Cons:**
- Two integration paths (file-based vs HTTP) to maintain if HTTP is enabled
- Slightly more complex extension code for message bridging

## Decision

**We recommend Option C: Hybrid Approach** with the following implementation strategy:

1. **Primary Path (CLI):** Use Ink-based React components with direct file watching for NDJSON logs and state. This is the default and only required implementation.

2. **VS Code Integration:** The VS Code extension SHALL use the Extension Host file system APIs (`vscode.workspace.fs`, `fs.watch`) to read state and logs, then forward data to webview panels via `postMessage`. No HTTP server required.

3. **Optional HTTP API (Future):** Reserve the option to add an opt-in HTTP API for advanced use cases (browser-based dashboards, remote access, third-party integrations). If implemented:
   - Bind to `127.0.0.1` only (no external access)
   - Require a per-session authentication token stored in `.loaded-vibes/session-token`
   - Support `loaded-vibes config set api.enabled true` to activate
   - Document security implications in SECURITY.md

## Consequences

### Immediate Actions
- Update TECH_REQUIREMENTS.md §11 to reflect the decision
- CLI dashboard implementation proceeds with Ink + file watchers
- VS Code extension (future) uses native file APIs + webview messaging

### Deferred Actions
- HTTP API implementation deferred until concrete browser dashboard or remote-access requirements emerge (tracked in TODO.md)

### Security Implications
- No additional attack surface introduced by default
- File-based communication stays within process/user boundaries
- Future HTTP API requires explicit opt-in with documented risks

### Performance Implications
- File watching is efficient (~1 ms latency on modern SSDs)
- Ink's virtual DOM minimizes terminal redraws
- Expected dashboard latency: 50-150 ms (well under 200 ms target)

## References

- `[PRD §5.2]` Retro Console Experience
- `[PRD §5.4]` Observability & Reporting
- `[TECH §5.2]` Console UX & Modules
- `[TECH §5.4]` Security & Performance
- `[TECH §11]` Roadmap & Open Questions
- `[SPEC-CLI §2]` Interaction & UX Model
- `[SPEC-SECURITY §1]` Policies
- `[SPEC-OBS §3]` Implementation Guidance
