---
type: DRR
winner_id: vanilla-js-frontend-thin-python-wrapper
created: 2025-12-24T16:07:24-08:00
content_hash: d29cbdfd7511e361242d384e7f8e5775
---

# Registration Frontend: Vanilla JS + Thin Python Wrapper

## Context
SpeedData v0.5 provides REST API for channel registration but lacks:
- Human-friendly web UI for operators to view/manage channels
- Python library for JupyterLab/scripting use cases
- Live data preview to verify channel activity
- Large schema handling (schemas can exceed UDP MTU but REST is fine)

User requirements:
- "Simplicity is a plus so react will have to prove itself"
- "This doesn't need awesome real-time - just ok"
- Match existing stripchart frontend style (monospace, simple HTML/CSS)
- Python library for Jupyter users to script registration (large schemas, DataSet integration possible)
- Subscribe to multicast for live data preview (demonstrate multicast benefit)

Platform range: Modern browsers to Raspberry Pi deployments

## Decision
**Selected Option:** vanilla-js-frontend-thin-python-wrapper

Implement vanilla JavaScript frontend (single HTML page) with thin Python wrapper library for REST API access.

## Rationale
Selected based on highest R_eff (0.90 vs 0.77) and best alignment with project constraints:

**Evidence Quality:**
- Internal testing (CL3) with 4/4 prototype tests passed
- Python wrapper pattern validated (~50 lines)
- Large schema handling empirically confirmed (1.02 MB via HTTP POST, no UDP MTU issues)
- Fetch API integration verified
- Pattern matches existing stripchart (proven in production)

**Risk Analysis:**
- Implementation: LOW (simple pattern, well-understood technologies)
- Browser compatibility: LOW (Fetch API + ES6 universally supported)
- Maintenance: LOW (~200 lines total, no build tools, no framework churn)
- Integration: LOW (matches existing stripchart pattern)
- Schema size: LOW (HTTP POST validated for large schemas)

**Alignment with Constraints:**
- Perfect match for "simplicity is a plus" preference
- Matches existing monospace/simple stripchart style
- No build tools (user preference for simplicity)
- Single-file approach minimizes complexity
- "Ok" real-time sufficient (WebSocket to existing stripchart server)
- Works across platform range (Pi to Xeon)

**Rejection of Alternative (Web Components + Schema Validation):**
- Lower R_eff (0.77) due to CL2 penalty (external research)
- Higher complexity (~400 lines vs ~200 lines)
- Learning curve for Web Components + Lit
- Schema validation valuable but not critical (server validates anyway)
- Jupyter magic nice-to-have but not essential
- Benefits don't justify 2x complexity increase given simplicity preference

**Cost-Benefit Analysis:**
Vanilla JS saves ~200 lines of code, eliminates learning curve, and achieves same core functionality (registration CRUD + live data) with 17% higher confidence and lower risk.

## Consequences
**Immediate Actions:**
1. Create frontend: `registration/frontend/index.html`
   - Channel list with status/port/schema display
   - Registration form (name, port, schema file upload)
   - De-registration controls
   - WebSocket connection to stripchart server for live data preview
   - Fetch API calls to orchestrator:8080/api/v1
2. Create Python library: `lib/python/speeddata_client.py`
   - SpeedDataClient class wrapping requests
   - Methods: list_channels(), register_channel(), deregister_channel(), get_channel(), upload_schema()
   - Schema file handling (read from .avsc files)
   - Error handling with descriptive messages
3. Serve static HTML via orchestrator or separate static file server
4. Update documentation (usage examples, API integration)

**Trade-offs Accepted:**
- No schema validation before upload (server-side only) - acceptable because REST API validates
- Basic UI without rich components - acceptable for "ok" real-time requirement
- No Jupyter magic commands - users can write simple Python scripts instead
- Single-file Python library - less modular but simpler (can refactor later if needed)
- Manual schema upload - no auto-extraction from DataSet (can add later if demand)

**Features Delivered:**
- Web UI: View all channels, register/de-register, live data preview via WebSocket
- Python library: Programmatic channel management from JupyterLab
- Large schema support: HTTP POST handles schemas >1MB (validated)
- Multicast integration: Live data preview demonstrates multicast benefit

**Next Steps:**
1. Implement HTML frontend (~100 lines HTML/CSS/JS)
2. Implement Python client library (~100 lines)
3. Write usage examples for both UI and library
4. Test with real schemas from existing DataSets
5. Document deployment (serve static HTML)

**Future Enhancements (if needed):**
- Add schema validation library (fastavro) if users request client-side validation
- Batch registration API for multiple channels
- DataSet schema auto-extraction helper function
- Richer UI components (if simplicity no longer priority)

**Validity Period:**
Review this decision if:
- User feedback requests schema validation before upload
- Team wants richer UI (drag-drop, wizards, etc.)
- Jupyter magic commands become high-demand feature
- Frontend exceeds 300 lines (consider modular approach)
- Build tools become acceptable (requirements change)
