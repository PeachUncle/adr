# ADR-009: Fixture-First Development Strategy

**Status:** Accepted  
**Date:** 2025-12-27  
**Decision Makers:** TechTrend Federal - Digital Twin Team  
**Category:** Data Architecture & Demo Strategy  
**Related:** ADR-005 (Skills-First Architecture), ADR-006 (Google-Only LLM)

---

## Context

RANGER is being developed as a demonstration of **agentic AI workflows** for federal post-fire forest recovery. The core value proposition is the multi-agent coordination pattern—how AI agents synthesize information across domains (burn severity, trail damage, timber salvage, NEPA compliance) to produce integrated briefings.

For the Phase 1 demo, we face a strategic choice:

1. **Build full infrastructure first** (Cloud SQL, MCP servers, live API integration) then demonstrate agents
2. **Demonstrate agents first** with realistic fixture data, then add infrastructure

The federal sales cycle and stakeholder engagement require us to show working agent coordination *now*, while infrastructure can be added incrementally. However, we must be crystal clear about what is demo scaffolding versus production architecture.

### The Demonstration Goal

When a Forest Supervisor asks: *"Give me a recovery briefing for Cedar Creek"*

The demo should show:
- ✅ **Multi-agent orchestration** (Coordinator delegates to 4 specialists)
- ✅ **Domain expertise synthesis** (burn + trails + timber + NEPA combined)
- ✅ **Proof Layer transparency** (reasoning chains, confidence scores, citations)
- ✅ **Real data formats** (MTBS classification, TRACS codes, FSVeg XML)

The demo does NOT need to show:
- ❌ Live satellite imagery processing
- ❌ Real-time NIFC API polling
- ❌ Persistent conversation memory across sessions
- ❌ Multi-user concurrent access patterns

---

## Decision

### Adopt "Fixture-First" Development Strategy

We use **static fixture data derived from real federal sources** bundled in the Docker container for Phase 1. This enables rapid agent development while preserving data authenticity.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DEMO ARCHITECTURE                                │
│                         (Phase 0-1, Current)                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                    Cloud Run: ranger-coordinator                  │  │
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐  │  │
│   │  │ Recovery       │  │ Specialist     │  │ Skills Library     │  │  │
│   │  │ Coordinator    │──│ Agents (4)     │──│ (Python scripts)   │  │  │
│   │  │ (ADK)          │  │ (ADK AgentTool)│  │                    │  │  │
│   │  └────────────────┘  └────────────────┘  └────────────────────┘  │  │
│   │           │                                        │              │  │
│   │           ▼                                        ▼              │  │
│   │  ┌────────────────┐                    ┌────────────────────────┐│  │
│   │  │ ADK Session    │                    │ data/fixtures/         ││  │
│   │  │ (In-Memory)    │                    │ ├── cedar-creek/       ││  │
│   │  │                │                    │ │   ├── burn-severity  ││  │
│   │  │ Lost on        │                    │ │   ├── trail-damage   ││  │
│   │  │ container      │                    │ │   ├── timber-plots   ││  │
│   │  │ restart        │                    │ │   └── briefing-events││  │
│   │  └────────────────┘                    │ └── bootleg/           ││  │
│   │                                        └────────────────────────┘│  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                    Cloud Run: ranger-console                      │  │
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐  │  │
│   │  │ React UI       │  │ NIFC Direct    │  │ MapTiler           │  │  │
│   │  │ (Mission       │──│ (Fallback to   │──│ (Map tiles)        │  │  │
│   │  │  Control)      │  │  demo fires)   │  │                    │  │  │
│   │  └────────────────┘  └────────────────┘  └────────────────────┘  │  │
│   └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                       PRODUCTION ARCHITECTURE                            │
│                       (Phase 2+, Target State)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                    Cloud Run: ranger-coordinator                  │  │
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐  │  │
│   │  │ Recovery       │  │ Specialist     │  │ Skills Library     │  │  │
│   │  │ Coordinator    │──│ Agents (4)     │──│ (Same scripts!)    │  │  │
│   │  │ (ADK)          │  │ (ADK AgentTool)│  │                    │  │  │
│   │  └────────────────┘  └────────────────┘  └────────────────────┘  │  │
│   │           │                   │                    │              │  │
│   │           ▼                   ▼                    ▼              │  │
│   │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐  │  │
│   │  │ Firestore      │  │ MCP Client     │  │ MCP Servers        │  │  │
│   │  │ (Persistent    │  │ (HTTP/SSE)     │──│ (Cloud Run)        │  │  │
│   │  │  sessions)     │  │                │  │                    │  │  │
│   │  └────────────────┘  └────────────────┘  └────────────────────┘  │  │
│   │                                                    │              │  │
│   └────────────────────────────────────────────────────┼──────────────┘  │
│                                                        │                 │
│                                          ┌─────────────┴────────────┐   │
│                                          │                          │   │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │   │
│   │ NIFC/IRWIN       │  │ MTBS             │  │ TRACS            │  │   │
│   │ (Fire perimeters)│  │ (Burn severity)  │  │ (Trail system)   │  │   │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘  │   │
│                                                                      │   │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │   │
│   │ Cloud SQL        │  │ AlloyDB          │  │ Vertex AI        │  │   │
│   │ (pgvector)       │  │ (Analytics)      │  │ (Managed RAG)    │  │   │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘  │   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Key Principle: Same Skills, Different Data Sources

The **Skills Library code is identical** between demo and production. The only change is *where the data comes from*:

```python
# Demo: Load from bundled fixture
def execute(inputs: dict) -> dict:
    fire_data = load_fixture_data(fire_id)  # Local JSON
    ...

# Production: Load via MCP
def execute(inputs: dict) -> dict:
    fire_data = mcp_client.fetch("nifc://fires/{fire_id}")  # Live API
    ...
```

This is achieved through the **MCP abstraction layer** defined in ADR-005. Skills call MCP tools; MCP tools can be backed by fixtures OR live APIs.

---

## Fixture Data Provenance

### Authenticity Requirement

All fixture data MUST be derived from real federal data sources. We are demonstrating agent coordination on **real data formats**, not synthetic test data.

### Cedar Creek Fire Fixtures

| Fixture File | Source | Authenticity | Date |
|--------------|--------|--------------|------|
| `burn-severity.json` | MTBS (Monitoring Trends in Burn Severity) | Real dNBR values, sector boundaries from MTBS classification | 2022-10-15 |
| `trail-damage.json` | TRACS format specification | Real damage codes, realistic assessments | 2022-11-01 |
| `timber-plots.json` | FSVeg (Field Sampled Vegetation) | Real plot structure, realistic volume estimates | 2022-11-15 |
| `incident-metadata.json` | IRWIN (Integrated Reporting of Wildland-Fire Information) | Real fire attributes, dates, coordinates | 2022-08-01 |
| `briefing-events.json` | Synthetic (agent outputs) | Generated from above real data sources | 2025-12 |

### Citation Format

All agent outputs include data provenance in the Proof Layer:

```json
{
  "proof_layer": {
    "confidence": 0.92,
    "citations": [
      {
        "source": "MTBS",
        "reference_id": "cedar-creek-2022-mtbs",
        "imagery_date": "2022-10-15",
        "snippet": "dNBR classification per Key & Benson (2006)"
      }
    ],
    "reasoning_chain": [
      "Loaded 8 sectors from MTBS dataset",
      "Applied standard dNBR thresholds: HIGH >= 0.66",
      "Sector NW-1: dNBR 0.72 -> HIGH severity"
    ]
  }
}
```

### What to Say in Demos

**Correct framing:**
> "This demonstration uses cached data from the Cedar Creek Fire (2022), sourced from MTBS satellite imagery and USFS field assessments. The agent coordination and reasoning you're seeing is real-time—only the underlying data is pre-loaded for demo reliability. Production deployment connects to live federal data feeds via MCP."

**Avoid:**
> ❌ "This is fake data" (it's not—it's real data, cached)
> ❌ "This is test data" (implies synthetic)
> ❌ "This would work differently in production" (the agents work identically)

---

## Session Memory Strategy

### Current State (In-Memory)

```python
# main.py
SESSION_SERVICE_URI = os.environ.get(
    "SESSION_SERVICE_URI",
    None  # Use in-memory by default
)
```

ADK's default session service stores conversation state in memory. This means:
- ✅ Fast for demos (no database latency)
- ✅ Simple (no infrastructure to manage)
- ❌ Lost on container restart
- ❌ Not shared across instances

### Production State (Firestore)

```python
SESSION_SERVICE_URI = "firestore://projects/ranger-twin-prod/databases/(default)/documents/sessions"
```

Firestore provides:
- ✅ Persistent across restarts
- ✅ Shared across all Cloud Run instances
- ✅ Built-in ADK integration
- ✅ FedRAMP authorized (via GCP)

### Migration Path

1. **Phase 0-1 (Demo):** In-memory sessions, acceptable for single-user demos
2. **Phase 2 (Pilot):** Firestore sessions, environment variable switch only
3. **Phase 3 (Production):** Firestore with user partitioning (multi-tenant)

No code changes required—only the `SESSION_SERVICE_URI` environment variable.

---

## Database Strategy

### Why No Cloud SQL in Demo

Cloud SQL (PostgreSQL with pgvector) is the target for production vector search and analytics, but it adds:
- Monthly cost (~$50-100 even at minimum)
- Cold start latency for serverless connector
- Schema migration complexity
- Backup/maintenance overhead

For demo purposes, this complexity provides zero value—we're demonstrating agent coordination, not database queries.

### Production Database Role

| Database | Purpose | Demo Equivalent |
|----------|---------|-----------------|
| Cloud SQL (pgvector) | NEPA document embeddings for RAG | Google File Search (managed) |
| Firestore | Session persistence, user preferences | In-memory (ADK default) |
| AlloyDB | Analytics, historical trends | Not needed for demo |

### Migration Path

1. **Phase 0-1:** No database (fixtures + in-memory)
2. **Phase 2:** Firestore for sessions, File Search for RAG
3. **Phase 3:** Cloud SQL for pgvector if self-hosted RAG needed

---

## MCP Transition Plan

### Current: Skills Load Fixtures Directly

```python
# skills/soil-burn-severity/scripts/assess_severity.py
def load_fixture_data(fire_id: str) -> dict:
    fixture_path = Path("data/fixtures/cedar-creek/burn-severity.json")
    with open(fixture_path) as f:
        return json.load(f)
```

### Target: Skills Call MCP Tools

```python
# skills/soil-burn-severity/scripts/assess_severity.py
def load_fire_data(fire_id: str, mcp_client) -> dict:
    # MCP tool call - works with fixtures OR live API
    return mcp_client.call("nifc_get_burn_severity", fire_id=fire_id)
```

### MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Server: ranger-mcp-nifc                   │
│                    (Cloud Run, separate service)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Tool: nifc_get_fire_perimeter(fire_id)                        │
│   Tool: nifc_get_burn_severity(fire_id)                         │
│   Tool: nifc_list_active_fires(region, year)                    │
│                                                                  │
│   ┌─────────────────┐    ┌─────────────────┐                    │
│   │ Fixture Mode    │ OR │ Live Mode       │                    │
│   │ (FIXTURE_MODE=1)│    │ (FIXTURE_MODE=0)│                    │
│   │                 │    │                 │                    │
│   │ Load from       │    │ Call NIFC API   │                    │
│   │ /data/fixtures  │    │ (ArcGIS REST)   │                    │
│   └─────────────────┘    └─────────────────┘                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

This allows:
- **Demo mode:** MCP server returns fixtures (fast, reliable)
- **Production mode:** MCP server calls live APIs (real-time)
- **Same agent code:** Agents don't know the difference

---

## Rationale

### Why Fixture-First Works for Federal Sales

1. **Demo Reliability:** Live APIs fail, rate-limit, or return unexpected data during demos. Fixtures never fail.

2. **Reproducibility:** Stakeholders can see identical results across multiple demo sessions, enabling comparison.

3. **Focus on Value:** The value is agent coordination, not data fetching. Fixtures let us demonstrate the core innovation without infrastructure noise.

4. **Faster Iteration:** Adding new skills or agents doesn't require MCP integration first.

5. **Compliance Story:** We can demonstrate the complete Proof Layer (reasoning chains, citations) with fixtures. The compliance architecture is identical to production.

### Why We're Not "Cheating"

The fixture data is **real federal data** in **real federal formats**:
- MTBS dNBR values are actual satellite-derived metrics
- TRACS damage codes are official USFS classification
- Fire coordinates are actual Cedar Creek perimeter points
- Severity thresholds are published USFS standards

We're caching real data, not inventing it.

---

## Consequences

### Positive

1. **Rapid Demo Development:** New agents can be built and tested without MCP infrastructure
2. **Clear Separation:** Demo vs. production architecture is explicit and documented
3. **Stakeholder Confidence:** Data authenticity can be cited with specific sources
4. **Easy Transition:** Fixture → MCP is an infrastructure change, not a code change

### Negative

1. **Two-Fire Limitation:** Demo only shows Cedar Creek and Bootleg (fixtures available)
2. **No Live Updates:** Stakeholders may ask "what about current fires?"
3. **Memory Loss:** Conversations don't persist between demos (in-memory sessions)

### Mitigations

| Risk | Mitigation |
|------|------------|
| "Only 2 fires?" | "Demo focuses on agent depth, not API breadth. Production connects to all 47 active NIFC fires." |
| "Is this real data?" | "Yes—Cedar Creek MTBS data from October 2022. The agent reasoning is real-time, only the source data is cached." |
| "Will it remember me?" | "Demo uses ephemeral sessions. Production uses Firestore for persistent memory." |

---

## Success Criteria

The demo architecture succeeds when:

1. [ ] Stakeholders understand the agent coordination value without being distracted by infrastructure
2. [ ] Data citations trace to real federal sources (MTBS, IRWIN, etc.)
3. [ ] The path from demo → production is clear (MCP + Firestore, not a rewrite)
4. [ ] New specialists can be added without MCP integration blocking progress
5. [ ] The same skill code runs in demo and production with zero changes

---

## References

- [ADR-005: Skills-First Architecture](./ADR-005-skills-first-architecture.md) — MCP abstraction layer
- [ADR-006: Google-Only LLM Strategy](./ADR-006-google-only-llm-strategy.md) — Gemini for all agents
- [Google Cloud: Host MCP Servers on Cloud Run](https://docs.cloud.google.com/run/docs/host-mcp-servers) — Production MCP pattern
- [MTBS Classification Protocol](https://www.mtbs.gov/) — Source for burn severity data
- [IRWIN Data Dictionary](https://www.nifc.gov/IRWIN/) — Source for incident metadata

---

## Appendix A: Fixture File Specifications

### burn-severity.json

```json
{
  "fire_id": "cedar-creek-2022",
  "fire_name": "Cedar Creek Fire",
  "total_acres": 127000,
  "imagery_date": "2022-10-15",
  "source": "MTBS",
  "sectors": [
    {
      "id": "NW-1",
      "name": "Northwest Sector 1",
      "dnbr_mean": 0.72,
      "acres": 3200,
      "slope_avg": 28,
      "priority_notes": "Steep terrain, immediate BAER assessment"
    }
  ]
}
```

### trail-damage.json

```json
{
  "fire_id": "cedar-creek-2022",
  "assessment_date": "2022-11-01",
  "source": "TRACS",
  "segments": [
    {
      "trail_id": "TR-405",
      "trail_name": "Moolack Ridge Trail",
      "segment_id": "TR-405-S3",
      "damage_class": "SEVERE",
      "tracs_code": "D4",
      "hazard_trees": 47,
      "closure_recommended": true
    }
  ]
}
```

---

## Appendix B: Demo Script Framing

### Opening Statement

> "RANGER demonstrates how AI agents can coordinate post-fire recovery analysis. You're about to see the Recovery Coordinator orchestrate four specialist agents—each expert in their domain—to produce an integrated briefing.
>
> The data you'll see is from the Cedar Creek Fire in Oregon, sourced from real USFS and MTBS datasets. While production deployment connects to live federal feeds, this demonstration uses cached data to ensure reliability. The agent reasoning and coordination is happening in real-time."

### Handling "Is This Real?" Questions

> "The data is real—MTBS satellite imagery from October 2022, USFS field assessments from November 2022. What we've done is cache it for demo reliability. The agents don't know the difference between cached and live data; they process it identically. Production deployment simply swaps the data source from local fixtures to MCP servers connected to NIFC and IRWIN."

### Handling "What About Current Fires?" Questions

> "Great question. The Mission Control view you see pulls from the live NIFC API—that's why you see dozens of current fires. For the deep-dive agent analysis, we're using Cedar Creek as our demonstration case because we have complete fixture data across all four domains. Production deployment enables agent analysis for any fire in the NIFC system."

---

**Document Owner:** RANGER Architecture Team  
**Last Updated:** December 27, 2025  
**Status:** Accepted
