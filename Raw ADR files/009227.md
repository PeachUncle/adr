# ADR 004: Migration from Gradio to FastMCP + FastAPI Architecture

**Status:** Proposed  
**Date:** 2025-10-12  
**Authors:** Development Team  
**Decision:** Migrate from Gradio-based MCP server to FastMCP + FastAPI architecture deployed on Fly.io

---

## Context

The current `expo-smooth-mcp` prototype uses Gradio v5.x with built-in MCP support, deployed on Hugging Face Spaces (free tier). While this setup enabled rapid prototyping and provides a functional demo, it has critical limitations that prevent production deployment:

### Identified Performance Issues

1. **600ms Tool Call Overhead**
   - Gradio's queuing system adds ~600ms latency to every MCP tool invocation
   - This overhead is architectural - it cannot be eliminated through code optimization
   - Source: GitHub Issue [#11961](https://github.com/gradio-app/gradio/issues/11961)

2. **2-Minute Cold Start Penalty**
   - Hugging Face Spaces requires ~120 seconds to provision and start a paused container
   - This makes the service non-viable for on-demand, interactive use
   - Source: [HF Forums Discussion](https://discuss.huggingface.co/t/slow-space-cold-boot/72154)

3. **Transport Limitations**
   - Gradio MCP only supports SSE (Server-Sent Events) transport
   - No native stdio support for local integrations (Claude Desktop, Cursor, VS Code)
   - Requires workarounds like `mcp-remote` proxy

4. **Framework Mismatch**
   - Gradio is optimized for ML demo UIs, not production API services
   - The queuing system is designed to prevent GPU OOM errors, not minimize API latency
   - Coupling UI framework to API layer violates separation of concerns

### Business Impact

- **User Experience:** Multi-second delays are unacceptable for a lightweight forecasting model
- **Market Reach:** Cannot integrate with local MCP clients (Claude Desktop users)
- **Scalability:** Single-worker-per-function model limits concurrency
- **Maintainability:** Tight coupling between UI and business logic

---

## Decision

We will migrate to a modern, decoupled architecture consisting of:

1. **FastMCP 2.0** - Production-grade MCP server framework
2. **FastAPI** - High-performance ASGI web framework
3. **Fly.io** - Container-as-a-Service platform with <1s cold starts
4. **Mounted Gradio** - Preserved as backward-compatible UI at `/gradio`

### Target Architecture

```
FastAPI (ASGI)
├── FastMCP Server (/mcp)          # Primary MCP endpoint
├── Gradio UI (/gradio)            # Backward compatibility
├── REST API Endpoints             # Standard HTTP API
└── Core Business Logic (logic.py) # Framework-agnostic
```

### Local Deployment Strategy: Docker MCP Toolkit

For local development and testing, we will leverage the **Docker MCP Toolkit** (integrated into Docker Desktop) rather than classic Docker containers:

**Key Benefits:**
- ✅ **One-Click Client Setup:** Automatic configuration for Claude Desktop via Docker Desktop UI
- ✅ **Built-in Security Sandboxing:** Resource limits (1 CPU, 2GB RAM max), filesystem isolation, secret scanning
- ✅ **Centralized Management:** Single UI for all MCP servers (catalog + custom)
- ✅ **Automatic Discovery:** Clients discover tools through secure gateway
- ✅ **No Manual JSON Editing:** Eliminates error-prone `mcp.json` configuration

**Implementation:**
```bash
# Build Docker image
docker build -t expo-smooth-mcp:latest .

# Enable in MCP Toolkit
docker mcp server enable expo-smooth-mcp:latest

# Connect clients via Docker Desktop UI (Clients tab → Claude Desktop → Connect)
```

**Reference:** See [docker-vs-docker-mcp.md](../docs/docker-vs-docker-mcp.md) for detailed analysis.

---

## Rationale

### Why FastMCP over Gradio MCP?

| Factor | Gradio MCP | FastMCP | Winner |
|--------|------------|---------|--------|
| **Tool Overhead** | ~600ms (queuing) | <10ms (direct) | FastMCP (60x faster) |
| **Transport Support** | SSE only | stdio + SSE + HTTP | FastMCP (native dual) |
| **Development Time** | Very low (minutes) | Low (1-2 hours) | Gradio (for prototypes) |
| **Production Features** | Limited | Enterprise auth, composition, proxying | FastMCP |
| **Primary Use Case** | ML demos | Production APIs | FastMCP (for our needs) |
| **Concurrency Model** | Queued workers | Async event loop | FastMCP (1000+ concurrent) |

**Conclusion:** FastMCP is purpose-built for production MCP servers, while Gradio MCP is a convenience feature for demos.

### Why Fly.io over Hugging Face Spaces?

| Factor | HF Spaces | Fly.io | Winner |
|--------|-----------|--------|--------|
| **Cold Start** | ~120s (container provisioning) | <1s (Firecracker VMs) | Fly.io (120x faster) |
| **Always-On Option** | No (free tier auto-pauses) | Yes (`min_machines_running=1`) | Fly.io |
| **Global Distribution** | Single region | 30+ regions | Fly.io |
| **Cost (512MB)** | $0 (free tier) | $0-5/month | HF Spaces (cheaper) |
| **Memory Requirements** | N/A (managed) | 256MB min, 512MB recommended | Fly.io (right-sized) |
| **Primary Purpose** | ML demos | Production apps | Fly.io (for our needs) |
| **Deployment Model** | Git push | Docker + CLI | Tie |

**Conclusion:** For production workloads requiring low latency, Fly.io's architecture is superior despite marginal cost.

### Why FastAPI as Foundation?

1. **Performance:** One of the fastest Python frameworks (comparable to NodeJS/Go)
2. **ASGI Native:** Built for high-concurrency async workloads
3. **Type Safety:** Automatic validation via Pydantic and type hints
4. **FastMCP Integration:** First-class support for mounting FastMCP servers
5. **OpenAPI:** Automatic, interactive API documentation
6. **Ecosystem:** Mature libraries for auth, rate limiting, monitoring

### Why Preserve Gradio UI?

**Backward Compatibility Strategy:**
- Many users may rely on the existing web UI
- Mounting Gradio at `/gradio` provides zero-downtime migration
- UI can be deprecated gradually after user base transitions
- Demonstrates feasibility of hybrid architectures

---

## Quantified Expected Improvements

### Performance Metrics

| Metric | Current (Gradio/HF) | Target (FastMCP/Fly.io) | Improvement |
|--------|---------------------|-------------------------|-------------|
| Tool call latency (p50) | 650ms | 50ms | **13x faster** |
| Tool call latency (p95) | 850ms | 100ms | **8.5x faster** |
| Cold start time | 120s | 1s | **120x faster** |
| Max concurrent requests | ~40 | 1000+ | **25x increase** |

### Architectural Benefits

1. **Dual Transport:** Native support for stdio (local) and HTTP/SSE (remote)
2. **Separation of Concerns:** UI, API, and business logic cleanly decoupled
3. **Scalability:** Global deployment with autoscaling
4. **Production-Ready:** OAuth2, rate limiting, structured logging out-of-box
5. **Maintainability:** Framework-agnostic core logic, easily testable

### Resource Requirements Analysis

**Exponential Smoothing is Exceptionally Lightweight:**

Our application has minimal memory footprint due to its stateless, statistical nature:

| Component | Memory Footprint |
|-----------|-----------------|
| Python 3.12 runtime | ~30-50MB |
| pandas (small FMCG dataset) | ~20-40MB |
| statsmodels (Holt-Winters) | ~30-50MB |
| FastMCP + FastAPI + Uvicorn | ~20-30MB |
| Application code + model state | ~10-20MB |
| **Baseline Total** | ~**110-190MB** |
| **Peak (during forecasting)** | ~**200-300MB** |
| **+ Plotly figure generation** | ~**+50-100MB** |
| **+ Gradio UI (if mounted)** | ~**+50-100MB** |

**Recommended Container Configurations:**

1. **Minimal (FastMCP only):** 256MB RAM
   - Sufficient for core forecasting without UI
   - Suitable for stdio transport (local clients)
   
2. **Standard (FastMCP + REST API):** 512MB RAM ✅ **RECOMMENDED**
   - Comfortable headroom for HTTP/SSE transport
   - Supports concurrent requests
   - Allows Plotly visualization generation
   
3. **Full (with Gradio UI):** 1GB RAM
   - Required if mounting Gradio at `/gradio`
   - Supports full backward compatibility

**Docker MCP Toolkit Default:** 2GB RAM limit (conservative, significantly oversized for this app)

**Why 512MB is Optimal:**
- ✅ 2-3x safety margin over peak usage
- ✅ Supports burst traffic without OOM errors
- ✅ Enables concurrent forecast requests
- ✅ Accommodates Plotly/visualization overhead
- ✅ Fits Fly.io free tier comfortably
- ✅ Cost-effective ($0-5/month on Fly.io)

**Validation:** This matches the baseline profile: "suitable for 128-512 MB containers" confirmed by dependency analysis.

---

## Alternatives Considered

### Alternative 1: Optimize Current Gradio Setup

**Approach:** Tune Gradio performance parameters (`concurrency_limit`, `max_threads`)

**Rejected Because:**
- Cannot eliminate 600ms overhead (inherent to queuing architecture)
- Cannot solve HF Spaces cold start (platform limitation)
- Cannot add stdio transport (Gradio doesn't support it)
- Does not address tight coupling of UI and logic

### Alternative 2: Raw MCP Python SDK

**Approach:** Use low-level MCP SDK without FastMCP abstraction

**Rejected Because:**
- 8-12 hours development time (vs. 1-2 hours for FastMCP)
- Manual implementation of auth, error handling, transport switching
- Requires deep MCP protocol expertise
- Higher maintenance burden

### Alternative 3: Keep Gradio, Move to Modal or Railway

**Approach:** Deploy Gradio app on a better platform to solve cold starts

**Rejected Because:**
- Solves cold start but not 600ms overhead
- Doesn't add stdio transport
- Doesn't address architectural coupling
- Still limited by Gradio's queuing model

### Alternative 4: Microservices Architecture

**Approach:** Separate forecasting service + UI service + API gateway

**Rejected Because:**
- Adds complexity (network hops, orchestration)
- Increases latency (inter-service communication)
- Overkill for single-purpose forecasting model
- Higher operational burden

---

## Migration Strategy

### Phased Approach (Zero-Downtime)

**Phase 1: Decouple (2-3 days)**
- Extract business logic to `logic.py`
- Refactor `app.py` to use logic functions
- Validate existing functionality preserved

**Phase 2: Build FastMCP Backend (3-4 days)**
- Create `main.py` with FastAPI + FastMCP
- Expose forecasting tools via `@mcp.tool`
- Implement dual-transport entrypoint
- Add REST endpoints for non-MCP clients

**Phase 3: Mount Gradio (1-2 days)**
- Use `gr.mount_gradio_app()` to integrate UI
- Update Gradio to call FastAPI backend
- Test both interfaces simultaneously

**Phase 4: Deploy to Fly.io (2-3 days)**
- Create optimized Dockerfile
- Configure `fly.toml` with `min_machines_running=1`
- Deploy and validate cold start performance

**Phase 5: Production Hardening (3-4 days)**
- Implement OAuth2 + JWT authentication
- Add Redis-backed rate limiting
- Configure structured logging and metrics
- Create comprehensive test suite

**Total Timeline:** 11-16 days

### Risk Mitigation

1. **Breaking Changes:** Gradio UI preserved at `/gradio` for continuity
2. **Performance Regression:** Benchmark before/after, rollback plan ready
3. **Deployment Issues:** Test on Fly.io staging first
4. **Cost Overruns:** Start with free tier, monitor usage

---

## Consequences

### Positive

1. ✅ **60-120x performance improvement** in critical metrics
2. ✅ **Native local integration** via stdio (Claude Desktop, etc.)
3. ✅ **Production-grade reliability** (auth, rate limiting, monitoring)
4. ✅ **Clean architecture** with separated concerns
5. ✅ **Backward compatibility** maintained during transition
6. ✅ **Future-proof** foundation for feature expansion

### Negative

1. ❌ **Marginal cost increase:** $0-5/month (vs. free HF Spaces)
2. ❌ **Development time:** 11-16 days for full migration
3. ❌ **Complexity:** More components (FastAPI + FastMCP + Gradio)
4. ❌ **Learning curve:** Team needs to learn FastMCP patterns

### Neutral

1. 🔄 **Deployment model change:** From Git push (HF) to CLI deploy (Fly.io)
2. 🔄 **Infrastructure management:** Need to manage Fly.io resources
3. 🔄 **Testing requirements:** More integration tests needed

---

## Implementation Status

- [ ] ADR approved
- [ ] Phase 1: Decouple business logic
- [ ] Phase 2: Build FastMCP backend
- [ ] Phase 3: Mount Gradio UI
- [ ] Phase 4: Deploy to Fly.io
- [ ] Phase 5: Production hardening
- [ ] Documentation updated
- [ ] Migration complete

---

## Success Criteria

### Must Have (Go/No-Go)
- ✅ Tool call latency < 100ms (p95)
- ✅ Cold start time < 5s
- ✅ Both stdio and HTTP/SSE transports functional
- ✅ Gradio UI working at `/gradio`
- ✅ Zero data loss during migration

### Should Have (Quality)
- ✅ JWT authentication implemented
- ✅ Rate limiting active
- ✅ Structured logging operational
- ✅ Health checks passing
- ✅ OpenAPI documentation complete

### Nice to Have (Future)
- ⏸️ Prometheus metrics exported
- ⏸️ Custom frontend to replace Gradio
- ⏸️ Multi-region deployment
- ⏸️ CI/CD pipeline for auto-deployment

---

## References

1. [research-Lightweight-MCP-Server.md](../docs/research-Lightweight-MCP-Server.md) - Framework analysis
2. [research-Gradio-FastMCP-Migration.md](../docs/research-Gradio-FastMCP-Migration.md) - Migration strategy
3. [docker-vs-docker-mcp.md](../docs/docker-vs-docker-mcp.md) - Docker deployment options analysis
4. [MIGRATION_ROADMAP.md](../docs/MIGRATION_ROADMAP.md) - Detailed implementation plan
5. [FastMCP Documentation](https://gofastmcp.com/)
6. [Fly.io Documentation](https://fly.io/docs/)
7. [Docker MCP Toolkit Documentation](https://docs.docker.com/desktop/mcp/)
8. [Gradio Issue #11961](https://github.com/gradio-app/gradio/issues/11961) - 600ms overhead report

---

## Approval

**Proposed by:** Development Team  
**Date:** 2025-10-12  
**Status:** Awaiting approval

**Sign-off Required:**
- [ ] Technical Lead
- [ ] Product Owner
- [ ] Architecture Review Board

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-12 | Dev Team | Initial proposal |
| 1.1 | 2025-10-13 | Dev Team | Added Docker MCP Toolkit local deployment strategy; Added detailed resource requirements analysis (512MB RAM recommendation); Updated memory requirements in comparison table |

