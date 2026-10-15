---
type: DRR
winner_id: embedded-flask-api-in-orchestrator-with-sqlite
created: 2025-12-24T11:52:22-08:00
content_hash: 720945b69156459ba902f1b0149a3e18
---

# Channel Registration REST API: Embedded Flask with SQLite

## Context
SpeedData v0.4 uses static YAML configuration (config/relay.yaml) for channel definitions, preventing runtime registration by remote devices. Need dynamic channel registration system with:
- REST API for CRUD operations (view, register, de-register channels)
- Port conflict prevention and availability queries
- Schema validation and compatibility checks
- Persistent storage across service restarts
- Integration with relay orchestrator for spawning/stopping relay processes
- Multi-client access (frontend for humans, API for remote agents)
- Platform range: Raspberry Pi to multi-core Xeon

## Decision
**Selected Option:** embedded-flask-api-in-orchestrator-with-sqlite

Embed Flask REST API in relay/orchestrator.py with SQLite backend (data/registry.db) for channel registration state management.

## Rationale
Selected based on highest R_eff (0.90 vs 0.72) and lowest risk profile:

**Evidence Quality:**
- Internal testing (CL3) in target environment with 3/3 tests passed
- SQLite ACID guarantees validated for concurrent access
- Port conflict detection via UNIQUE constraints confirmed
- Flask integration compatibility verified with test client

**Risk Analysis:**
- Deployment: LOW (single service, no new process management)
- Integration: LOW (direct function calls, atomic register→spawn operations)
- Operational: LOW (Flask + SQLite already in Python ecosystem)
- Performance: LOW (<1ms queries validated for <100 channels)
- Pi compatibility: LOW (no memory footprint increase)

**Rejection of Alternative (Standalone FastAPI):**
- Lower R_eff (0.72) due to CL2 penalty (external research, context mismatch)
- Medium operational risk (extra service, IPC complexity, +50-100MB RAM)
- Performance benefits (5-10x) wasted on non-hot-path (<1 req/s registration)
- Clean architecture doesn't justify deployment complexity for single-host use case

**Alignment with Constraints:**
- Maintains service-oriented architecture (orchestrator remains independent service)
- Preserves YAML baseline for git-tracked config
- Python-only (no compiled dependencies)
- Works across platform range (Pi to Xeon)

## Consequences
**Immediate Actions:**
1. Extend relay/orchestrator.py with Flask blueprint
2. Create SQLite schema: channels(name, port, schema_path, config_json, status, created_at, pid)
3. Implement REST endpoints:
   - GET/POST/DELETE /channels
   - GET /channels/{name}/schema
   - POST /channels/{name}/validate-schema
   - GET /ports/available
4. Add startup sequence: Load relay.yaml → Load registry.db → Merge (DB overrides) → Spawn fleet → Start Flask
5. Update requirements.txt with Flask dependency

**Trade-offs Accepted:**
- Tighter coupling (API + orchestrator in same process) - accepted because atomic operations beneficial
- Flask performance (2-3k req/s) vs FastAPI (15-20k req/s) - acceptable for <1 req/s registration traffic
- No OpenAPI auto-docs - can add flask-swagger if needed later

**Next Steps:**
1. Implement SQLite schema and migrations
2. Add Flask routes with request validation
3. Integrate with existing RelayFleet class
4. Write integration tests (API → DB → relay spawn)
5. Update documentation (API spec, usage examples)

**Future Considerations:**
- If multi-host orchestration needed: revisit standalone service option
- If registration traffic exceeds 100 req/s: benchmark Flask performance
- Consider adding /health and /metrics endpoints for monitoring

**Validity Period:**
Review this decision if:
- Multi-host orchestration becomes requirement
- Channel count exceeds 100 (SQLite scaling limit)
- Registration becomes hot path (>10 req/s sustained)
- Orchestrator process becomes too complex (>2000 LOC)
