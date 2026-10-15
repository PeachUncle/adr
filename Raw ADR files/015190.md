# ADR-004: Site Analysis Feature and OpenRouter Migration

**Status:** Superseded (see ADR-006)
**Date:** 2025-12-24
**Superseded:** 2025-12-26
**Decision Makers:** TechTrend Federal - Digital Twin Team
**Category:** Feature Architecture & API Infrastructure

---

> **⚠️ Superseded Notice**
>
> This ADR has been superseded by **ADR-006: Google-Only LLM Strategy**.
> **Supersedes:** Partially superseded by ADR-006
>
> **Reason:** OpenRouter was introduced to address Google API rate limits during development. However, since ADK agents require the Google Gemini API anyway (for the runtime), and Managed RAG/File Search is Google-only, maintaining a second LLM provider added complexity without clear Phase 1 value.
>
> **Current Strategy:** All LLM calls (agents, frontend, RAG) use Google Gemini API directly.
>
> The Site Analysis feature described in this ADR remains valid—only the OpenRouter integration has been removed.

---

## Context

RANGER's Command Console needed a way for field rangers to get AI-powered analysis of specific map features (trail damage points, timber plots, burn severity zones) without leaving the map interface. Additionally, we encountered rate limiting issues with the direct Gemini API that required a more robust solution.

### Problem Statement

1. **Feature-Level Analysis Gap** — Rangers can view map features but lack contextual AI analysis for individual sites
2. **UX Friction** — Current chat panel requires context-switching; rangers want analysis triggered directly from map features
3. **API Rate Limiting** — Direct Google Generative AI API free tier limits (10 RPM, 100 RPD) proved insufficient during development and would fail at scale
4. **Results Persistence** — Analysis results disappear when closing the modal; no way to save or compare analyses

### Requirements

| Requirement | Priority | Rationale |
|-------------|----------|-----------|
| Feature-triggered analysis | Must have | Natural UX for field rangers |
| Quick query chips | Must have | Standardized queries reduce typing on gloves/mobile |
| Real LLM integration | Must have | Meaningful AI responses, not just mock data |
| Save/download results | Should have | Preserve analysis for reports and handoff |
| Reliable API access | Must have | Rate limits cannot block field operations |
| USFS-aligned terminology | Must have | Cultural fit with Forest Service workflows |

---

## Decision

### 1. Implement Site Analysis Feature

We implemented a **feature-triggered analysis workflow** accessible directly from map popups:

- Click any map feature → "Analyze Site" button in popup
- Quick Query Chips provide pre-built, context-aware queries
- Results displayed inline with markdown rendering
- Save to localStorage and download as markdown files

### 2. Migrate from Direct Gemini to OpenRouter

We will migrate from **Google Generative AI API** (`generativelanguage.googleapis.com`) to **OpenRouter** (`openrouter.ai`) as our LLM gateway.

### 3. Analysis History with Local Persistence

We implemented a **Zustand store with localStorage persistence** for saving analyses, enabling:
- Cross-session persistence
- View/download/delete saved analyses
- Future: sync to backend when available

---

## Rationale

### Why Site Analysis Feature

| Factor | Before | After |
|--------|--------|-------|
| **Analysis trigger** | Open chat → type context → ask question | Click feature → select chips → run |
| **Context transfer** | Manual copy/paste of coordinates, IDs | Automatic feature metadata injection |
| **Query consistency** | Free-form text, variable quality | Pre-built chips ensure complete queries |
| **Mobile/glove UX** | Difficult keyboard input | Touch-friendly 44px chip targets |
| **Workflow alignment** | Generic chat interface | USFS-aligned terminology and patterns |

### Why OpenRouter over Direct Google Generative AI API

| Factor | Direct Google Generative AI API | OpenRouter |
|--------|-------------------|------------|
| **Free tier rate limits** | 10 RPM, 100 RPD (severely constrained) | 50 RPD free, unlimited with $10 credit |
| **Gemini access via OpenRouter** | N/A | 20 RPM, 200 RPD for Gemini models |
| **Fallback options** | None - rate limit = failure | Multi-provider routing possible |
| **API format** | Google-specific | OpenAI-compatible (industry standard) |
| **Model flexibility** | Gemini only | 100+ models via single API |
| **Cost overhead** | Direct token pricing | 5% platform fee |
| **Provider stability** | Subject to Google's rate limit changes | Abstracts provider instability |

**Key finding:** During development testing, we hit the Google Generative AI API 429 rate limits within minutes, causing silent fallback to simulation mode. OpenRouter's rate limits are 2-10x more generous for the same models.

### Why localStorage for Analysis History

| Factor | Backend Storage | localStorage |
|--------|-----------------|--------------|
| **Implementation time** | Requires bucket setup, API routes | Immediate, frontend-only |
| **Offline capability** | Requires connection | Works offline |
| **Phase 1 scope** | Backend not yet implemented | Aligns with fixture-based approach |
| **Migration path** | N/A | Easy sync to backend when ready |

---

## Implementation

### Site Analysis Components

```
apps/command-console/src/
├── config/
│   └── siteAnalysisChips.ts         # [NEW] Quick Query Chip definitions
├── stores/
│   ├── visualAuditStore.ts          # [MODIFIED] Added feature mode, chips
│   └── analysisHistoryStore.ts      # [NEW] Zustand + localStorage persistence
├── components/
│   └── map/
│       ├── QuickQueryChips.tsx      # [NEW] 2-column chip selector
│       ├── VisualAuditOverlay.tsx   # [MODIFIED] Feature analysis flow
│       └── AnalysisHistoryPanel.tsx # [NEW] History viewer modal
└── App.tsx                          # [MODIFIED] History panel integration
```

### Quick Query Chip System

Chips are organized by feature type and category:

| Feature Type | Categories | Example Chips |
|--------------|------------|---------------|
| Trail Damage | Safety, History, Compliance, Logistics | "Check NFS database", "BAER history", "Hazard trees" |
| Timber Plots | Volume, Access, Compliance | "Volume estimate", "Haul routes", "Salvage window" |
| Burn Zones | Severity, Ecology, Restoration | "dNBR values", "Seed bank", "Erosion risk" |

Chips use `{placeholder}` syntax for feature property injection:
```typescript
query: "Check NFS trail database for {trail_name}. What is the official trail classification?"
// Becomes: "Check NFS trail database for Hills Creek Trail #3510. What is..."
```

### OpenRouter Integration

**API endpoint change:**
```typescript
// Before (Direct Google Generative AI API)
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

// After (OpenRouter)
const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions';
```

**Headers:**
```typescript
headers: {
  'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
  'HTTP-Referer': 'https://ranger-demo.vercel.app',
  'X-Title': 'RANGER Recovery Coordinator',
  'Content-Type': 'application/json'
}
```

**Model selection:**
```typescript
model: 'google/gemini-2.0-flash-exp:free' // Or paid variant
```

### Environment Variables

```bash
# .env.local (remove old, add new)
# VITE_GEMINI_API_KEY=xxx  # Deprecated - was for Direct Google Generative AI API
VITE_OPENROUTER_API_KEY=sk-or-v1-xxxxxxx
```

---

## Consequences

### Positive

1. **Natural field UX** — Analysis triggered from context, not abstract chat
2. **Reliable AI access** — OpenRouter's rate limits support real usage
3. **Model flexibility** — Can hot-swap models without code changes
4. **Preserved work** — Save/download ensures analysis isn't lost
5. **Standardized queries** — Chips ensure complete, well-formed prompts
6. **Mobile-ready** — 44px touch targets, minimal typing

### Negative

1. **Additional dependency** — OpenRouter adds a service dependency
2. **5% cost overhead** — Platform fee on top of model costs
3. **localStorage limits** — ~5MB per origin; heavy users may hit limits
4. **Simulation fallback** — If OpenRouter fails, still falls back to mock data

### Mitigations

| Risk | Mitigation |
|------|------------|
| OpenRouter dependency | Service has 99.9% uptime; fallback to simulation exists |
| 5% cost overhead | Negligible at development scale; justified by reliability |
| localStorage limits | Implement cleanup of old analyses; future: backend sync |
| Simulation fallback | Clear user messaging when in simulation mode |

---

## Alternatives Considered

### Analysis Feature Alternatives

| Approach | Verdict | Rationale |
|----------|---------|-----------|
| Chat panel only | Rejected | Context-switching, poor mobile UX |
| Dedicated analysis page | Rejected | Breaks map-centric workflow |
| Right-click context menu | Rejected | Not discoverable, no mobile equivalent |
| **Popup-triggered modal** | **Accepted** | Natural, discoverable, touch-friendly |

### API Gateway Alternatives

| Approach | Verdict | Rationale |
|----------|---------|-----------|
| Direct Google Generative AI API | Rejected | Severe rate limits, no fallback |
| Direct OpenAI API | Rejected | No Gemini access, different ecosystem |
| Self-hosted proxy | Rejected | Infrastructure overhead for Phase 1 |
| Multiple direct APIs | Rejected | Complex client code, no unified fallback |
| **OpenRouter** | **Accepted** | Unified API, generous limits, Gemini access |

### Persistence Alternatives

| Approach | Verdict | Rationale |
|----------|---------|-----------|
| No persistence | Rejected | Analysis is lost on modal close |
| Session storage | Rejected | Lost on browser close |
| Backend bucket | Deferred | Backend not implemented yet |
| **localStorage** | **Accepted** | Immediate, offline-capable, easy migration |

---

## References

- [Site Analysis Feature Spec](../features/FORENSIC-POPUP-TRIGGER.md)
- [UX Review Summary](../features/UX-REVIEW-SUMMARY.md)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter Models](https://openrouter.ai/models) — Gemini availability
- [ADR-003: Gemini 3 Flash](./ADR-003-gemini-3-flash-file-search.md) — Previous model decision

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-24 | Site Analysis feature accepted | Natural UX for field rangers, USFS-aligned terminology |
| 2025-12-24 | OpenRouter migration accepted | Google Generative AI API rate limits insufficient; OpenRouter provides reliable access with fallback options |
| 2025-12-24 | localStorage persistence accepted | Immediate implementation; backend sync deferred to Phase 2 |

---

## Appendix: Quick Query Chip Reference

### Trail Damage Chips
- **NFS Database** — Official trail classification, maintenance schedule
- **Maintenance History** — Work records, last inspection date
- **BAER History** — Prior Burned Area Emergency Response actions
- **Hazard Trees** — Documented hazard tree assessments
- **Access Status** — Current closure status, bypass routes
- **Wilderness Boundary** — Wilderness designation, equipment restrictions

### Timber Plot Chips
- **Volume Estimate** — Board feet estimate, species composition
- **Haul Routes** — Viable access roads, weight restrictions
- **Salvage Window** — Beetle infestation risk timeline
- **Prior Cruises** — Historical cruise data comparison
- **Contract Status** — Active timber contracts, overlaps

### Burn Zone Chips
- **dNBR Analysis** — Precise severity values for zone
- **Seed Bank** — Native seed survival assessment
- **Erosion Risk** — Soil stability, revegetation urgency
- **Recovery Timeline** — Expected natural recovery timeframe
- **BAER Priority** — Suggested BAER treatment priority
