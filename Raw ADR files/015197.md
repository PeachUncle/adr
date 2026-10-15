# ADR-012: Mission Control UI Overhaul

**Status:** Accepted  
**Date:** 2025-12-30  
**Accepted:** 2025-12-30  
**Decision Makers:** TechTrend Federal - Digital Twin Team  
**Category:** UI/UX Architecture & Geospatial Infrastructure  
**Related ADRs:** ADR-005 (Skills-First), ADR-006 (Google-Only LLM)

---

## Visual Reference

![Mission Control UI Mockup](../designs/mockups/ranger-cc-ui-mockup.png)

*Expert-provided mockup showing BriefingStrip, PhaseFilterChips, LayersPanel, cluster tooltip, and IncidentRail with jurisdiction rows.*

---

## Context

### The "8-Minute Reality"

Regional Forester Maria has 8 minutes before her 6:40 AM briefing call with Washington. She needs to answer:

1. **"What's going sideways?"** — Which fires need escalation in the next 72 hours?
2. **"Where's the resource pressure?"** — Are any districts getting overwhelmed?
3. **"What do I tell Washington?"** — A 30-second summary of regional recovery posture

The current Mission Control interface, while functional, requires too many cognitive hops to answer these questions. Users cannot determine jurisdiction at a glance, phase filters are ambiguous, and there's no persistent briefing summary.

### Identified Gaps

| Gap | Current State | User Impact |
|-----|--------------|-------------|
| **Jurisdiction opacity** | No boundary overlays; jurisdiction unknown until drill-down | Cannot triage by administrative unit |
| **Phase filter ambiguity** | "Phase" label without context | Users unsure what phases mean operationally |
| **No briefing summary** | Metrics scattered across interface | Cannot generate quick status report |
| **Information density** | Competing panels with redundant chrome | Map view constrained; cognitive overload |
| **Field usability** | Glassmorphism optimized for demos, not sunlight | Low contrast in operational environments |

### Expert Panel Consultation

External geospatial and UX specialists reviewed the current interface and provided recommendations converging on:

1. **Vector tiles for jurisdictional boundaries** — GeoJSON will not scale for national extent
2. **Hover for instant jurisdiction answers** — Click-to-discover is too slow for briefings
3. **Progressive disclosure** — Start simple, reveal complexity on demand
4. **PMTiles on Cloud Storage** — No tile server required for prototype
5. **Field mode toggle** — High-contrast option for outdoor use

---

## Decision

### Implement a comprehensive Mission Control UI overhaul comprising:

1. **Jurisdictional Boundary Layers** via PMTiles vector tiles
2. **Redesigned Phase Filter** with chip-based UI and counts
3. **Briefing Strip** for persistent portfolio metrics
4. **Layers Panel** for boundary overlay control
5. **Hover Tooltips** for instant jurisdiction identification
6. **Field Mode Toggle** for high-contrast operational use
7. **Responsive Breakpoints** for tablet/mobile field deployment

This is a unified implementation, not phased rollout. All components ship together to avoid inconsistent user experience during transition.

---

## Architecture

### Component Structure

```
MissionControlView.tsx
├── BriefingStrip (absolute top-0, w-full)
│   ├── MetricChip: Active Hotspots
│   ├── MetricChip: Fires by Phase
│   ├── MetricChip: Acres (NFS vs BLM)
│   ├── MetricChip: Last FIRMS Update
│   └── CopyBriefingButton
│
├── MapContainer (flex: 1, relative)
│   ├── NationalMap (MapLibre GL, full viewport)
│   │   ├── Source: hotspots-source (GeoJSON, clustered)
│   │   ├── Source: federal-boundaries (PMTiles)
│   │   │   ├── Layer: usfs-fill (15% opacity)
│   │   │   ├── Layer: usfs-outline
│   │   │   ├── Layer: blm-fill
│   │   │   ├── Layer: blm-outline
│   │   │   ├── Layer: tribal-fill
│   │   │   └── Layer: ranger-districts-outline
│   │   ├── Layer: hotspots-layer
│   │   ├── Layer: fires-layer
│   │   └── Layer: fires-selected-layer
│   │
│   ├── LeftRail (absolute left-0, collapsible)
│   │   ├── NavTabs: National | Watchlist
│   │   └── PhaseFilterChips
│   │       ├── Active (count)
│   │       ├── BAER Assessment (count)
│   │       ├── BAER Implementation (count)
│   │       └── Restoration (count)
│   │
│   ├── LayersPanel (absolute bottom-4 right-[336px])
│   │   ├── LayerGroup: Ownership
│   │   │   ├── LayerToggle: USFS
│   │   │   ├── LayerToggle: BLM
│   │   │   └── LayerToggle: Tribal
│   │   └── LayerGroup: Operations
│   │       ├── LayerToggle: Ranger Districts
│   │       └── LayerToggle: Wilderness
│   │
│   ├── JurisdictionTooltip (MapLibre Popup, hover-triggered)
│   │
│   └── FieldModeToggle (top-right)
│
└── IncidentRail (absolute right-0, w-80)
    └── IncidentCard[] (with jurisdiction row)
```

### State Management

```typescript
// New state additions to missionStore.ts
interface MissionState {
  // Existing...
  
  // New: Layer visibility
  layersVisible: {
    usfs: boolean;
    blm: boolean;
    tribal: boolean;
    rangerDistricts: boolean;
    wilderness: boolean;
  };
  
  // New: Field mode
  fieldMode: boolean;
  
  // New: Hovered jurisdiction (from queryRenderedFeatures)
  hoveredJurisdiction: {
    owner: string;      // "USFS" | "BLM" | "Tribal" | "State" | "Private"
    unit: string;       // "Deschutes NF"
    subunit?: string;   // "Bend RD"
  } | null;
}

// Actions
toggleLayer: (layerId: keyof LayersVisible) => void;
setFieldMode: (enabled: boolean) => void;
setHoveredJurisdiction: (jurisdiction: HoveredJurisdiction | null) => void;
```

### Vector Tile Pipeline

**Source Data:**
- PAD-US 4.1 (Protected Areas Database of the United States)
- USGS Gap Analysis Project: https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download

**Processing Pipeline:**
```bash
# 1. Extract BAER-relevant federal boundaries from PAD-US geodatabase
# NOTE: Filtering by Mang_Agency (not Mang_Type) to get USFS/BLM/BIA only
# Excludes military, NPS, USFWS which are not BAER-relevant
ogr2ogr -f GeoJSON \
  -where "Own_Type='FED' AND Mang_Agency IN ('USFS', 'BLM', 'BIA')" \
  -sql "SELECT Mang_Name, Mang_Type, Own_Type, Mang_Agency, Unit_Nm, GIS_Acres, SHAPE FROM PADUS4_1Fee" \
  pad-us-federal.geojson \
  PADUS4_1_Geodatabase.gdb

# 2. Generate PMTiles with zoom-dependent simplification
tippecanoe -o federal-boundaries.pmtiles \
  --name="Federal Land Boundaries" \
  --layer=boundaries \
  --drop-densest-as-needed \
  --extend-zooms-if-still-dropping \
  --simplify-only-low-zooms \
  --minimum-zoom=3 \
  --maximum-zoom=12 \
  --force \
  pad-us-federal.geojson

# 3. Upload to Cloud Storage
gsutil cp federal-boundaries.pmtiles gs://ranger-twin-tiles/
gsutil iam ch allUsers:objectViewer gs://ranger-twin-tiles
```

**Output Characteristics:**
- File size: ~150-250MB for continental US federal boundaries
- Processing time: ~15-30 minutes on 16GB RAM machine
- Zoom levels: 3-12 with automatic simplification

**MapLibre Integration:**
```typescript
// PMTiles protocol handler (maplibre-gl v4+)
// npm install pmtiles
import maplibregl from 'maplibre-gl';
import { Protocol } from 'pmtiles';

// Register protocol ONCE before any map initialization
const protocol = new Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);

// Add source with tiles array (NOT url property)
map.addSource('federal-boundaries', {
  type: 'vector',
  tiles: ['pmtiles://https://storage.googleapis.com/ranger-twin-tiles/federal-boundaries.pmtiles/{z}/{x}/{y}'],
});

// Alternative: Use @protomaps/react-maplibre for React integration
// npm install @protomaps/react-maplibre
import { Protomaps } from '@protomaps/react-maplibre';
// <Protomaps.Map url="https://..." />
```

### Hover Jurisdiction Lookup

```typescript
// Query topmost visible jurisdiction layer (sub-10ms latency)
const JURISDICTION_LAYERS = ['usfs-fill', 'blm-fill', 'tribal-fill'];

map.on('mousemove', (e) => {
  const visibleLayers = JURISDICTION_LAYERS.filter(
    id => map.getLayoutProperty(id, 'visibility') === 'visible'
  );
  
  const features = map.queryRenderedFeatures(e.point, { layers: visibleLayers });
  const topFeature = features[0];
  
  if (topFeature) {
    setHoveredJurisdiction({
      owner: topFeature.properties.Mang_Type,
      unit: topFeature.properties.Unit_Nm,
      subunit: topFeature.properties.Dist_Nm,
    });
  } else {
    setHoveredJurisdiction(null);
  }
});
```

### Cluster Jurisdiction Aggregation

When hotspots are clustered at national zoom, hover shows dominant jurisdiction.

**Preferred: Server-side pre-aggregation** (non-blocking)

The FIRMS processor adds jurisdiction data during ingest via PostGIS `ST_Intersects`:

```typescript
// FIRMS API response includes pre-computed jurisdictions:
interface ClusterProperties {
  cluster_id: number;
  hotspot_count: number;
  jurisdictions: {
    USFS?: number;   // e.g., 38 (81%)
    BLM?: number;    // e.g., 6 (13%)
    Private?: number; // e.g., 3 (6%)
  };
  dominant_owner: string; // "USFS"
}

// Client hover (instant, non-blocking):
map.on('mouseenter', 'hotspot-clusters', (e) => {
  const props = e.features[0].properties as ClusterProperties;
  showClusterTooltip(e.lngLat, {
    count: props.hotspot_count,
    dominant: props.dominant_owner,
    jurisdictions: props.jurisdictions,
  });
});
```

**Fallback: Client-side aggregation** (use sparingly)

```typescript
// Only if server pre-aggregation unavailable
// WARNING: Blocks UI for large clusters
map.on('mouseenter', 'hotspot-clusters', async (e) => {
  const clusterId = e.features[0].properties.cluster_id;
  const leaves = await map.getClusterLeaves(
    'hotspots-source',
    clusterId,
    50 // Limit to avoid UI blocking
  );
  
  const jurisdictionCounts = leaves.reduce((acc, leaf) => {
    const j = leaf.properties.jurisdiction || 'Unknown';
    acc[j] = (acc[j] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  
  const sorted = Object.entries(jurisdictionCounts)
    .sort(([,a], [,b]) => b - a);
  
  showClusterTooltip(e.lngLat, {
    count: leaves.length,
    dominant: `${sorted[0][0]} (${Math.round(sorted[0][1]/leaves.length*100)}%)`,
    others: sorted.slice(1, 3),
  });
});
```

### Field Mode Styling

```css
/* Field Mode: High-contrast dark theme */
.field-mode {
  /* Text: 21:1 contrast ratio */
  --text-primary: #FFFFFF;
  --text-secondary: #E5E7EB;
  
  /* Backgrounds: Full opacity */
  --panel-bg: rgba(0, 0, 0, 0.95);
  --panel-border: rgba(255, 255, 255, 0.25);
  
  /* Touch targets: 48px minimum */
  --touch-target-min: 48px;
}

.field-mode .glass-panel {
  backdrop-filter: none;
  background: var(--panel-bg);
  border: 2px solid var(--panel-border);
}

.field-mode .filter-chip {
  min-height: var(--touch-target-min);
  min-width: var(--touch-target-min);
  font-weight: 700;
  font-size: 1.1em;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
}

/* Target canvas only - targeting #map breaks MapLibre picking */
.field-mode .maplibregl-canvas {
  filter: contrast(1.2) brightness(1.1);
}
```

### Responsive Breakpoints

```typescript
// Tailwind breakpoints for field devices
const breakpoints = {
  mobile: 'max-w-767px',    // Bottom sheet panels
  tablet: '768px-1024px',   // Collapsible side panels
  desktop: 'min-w-1024px',  // Full layout
};

// Mobile: Panels become bottom sheets
@media (max-width: 767px) {
  .left-rail {
    @apply fixed bottom-0 left-0 w-full h-1/3;
    @apply transform translate-y-full;
    @apply transition-transform duration-300;
  }
  .left-rail.expanded {
    @apply translate-y-0;
  }
  .incident-rail {
    @apply hidden; /* Replaced by bottom sheet */
  }
}

// Tablet: Collapsible panels
@media (min-width: 768px) and (max-width: 1024px) {
  .left-rail {
    @apply w-16 hover:w-48 transition-all duration-200;
  }
}
```

---

## Implementation Plan

### Files to Create

| File | Purpose |
|------|---------|
| `components/mission/BriefingStrip.tsx` | Top bar with portfolio metrics |
| `components/mission/PhaseFilterChips.tsx` | Chip-based phase filter |
| `components/mission/LayersPanel.tsx` | Boundary layer toggle panel |
| `components/mission/LayerToggle.tsx` | Individual layer checkbox with swatch |
| `components/mission/JurisdictionTooltip.tsx` | Hover popup content |
| `components/mission/FieldModeToggle.tsx` | High-contrast mode switch |
| `hooks/useJurisdictionQuery.ts` | `queryRenderedFeatures` wrapper |
| `hooks/usePMTiles.ts` | PMTiles protocol setup |
| `styles/field-mode.css` | Field mode CSS overrides |
| `scripts/process-pad-us.sh` | Vector tile generation script |

### Files to Modify

| File | Changes |
|------|---------|
| `stores/missionStore.ts` | Add layer visibility, field mode, jurisdiction state |
| `components/mission/NationalMap.tsx` | Add boundary sources/layers, hover handlers |
| `components/mission/IncidentCard.tsx` | Add jurisdiction row |
| `components/mission/MissionControlLayout.tsx` | Integrate BriefingStrip, FieldModeToggle |
| `components/mission/IncidentRail.tsx` | Responsive breakpoint handling |
| `index.css` | Import field-mode.css |

### Data Pipeline Setup

1. **Download PAD-US 4.1** from USGS
2. **Process with ogr2ogr** → Extract federal boundaries
3. **Generate PMTiles with tippecanoe**
4. **Upload to Cloud Storage** → `gs://ranger-twin-tiles/`
5. **Configure CORS** for public read access

### Testing Strategy

| Test Type | Coverage |
|-----------|----------|
| **Unit** | PhaseFilterChips state management, LayerToggle visibility |
| **Integration** | PMTiles loading, `queryRenderedFeatures` accuracy |
| **Visual** | Field mode contrast ratios (WCAG AA 7:1) |
| **Performance** | Map render with 6 boundary layers + 1000 hotspots |
| **Responsive** | Mobile bottom sheet, tablet collapse, desktop full |
| **Accessibility** | Touch targets 48px, keyboard navigation |

---

## Rationale

### Why PMTiles over GeoJSON?

| Factor | GeoJSON | PMTiles |
|--------|---------|---------|
| **File size** | 500MB+ for PAD-US | 150-250MB (tiled) |
| **Initial load** | Entire dataset | Only visible tiles |
| **Zoom performance** | Re-render entire dataset | Zoom-specific simplification |
| **Memory** | All features in memory | Tiles cached on demand |
| **Hosting** | Any static host | Cloud Storage (no tile server) |

### Why PMTiles over ArcGIS REST Services?

| Factor | ArcGIS REST | PMTiles |
|--------|-------------|---------|
| **CORS** | Requires proxy or workarounds | Native browser fetch |
| **Dependency** | External service availability | Self-hosted, controlled |
| **Cost** | Potential API limits | Cloud Storage egress only |
| **Offline** | Not supported | Cache-able |

### Why Hover over Click for Jurisdiction?

The "8-minute reality" demands answers in 1 second, not 3. Click-to-discover adds cognitive overhead:

1. See hotspot → 2. Wonder "whose land?" → 3. Click → 4. Wait for panel → 5. Read

With hover: 1. See hotspot → 2. Hover → 3. Answer visible (300ms)

### Why Single Implementation vs. Phased?

Partial UI states create user confusion:
- Phase chips without briefing strip → "Where are my totals?"
- Layers panel without boundary data → "Toggle does nothing?"
- Hover tooltips without jurisdiction layers → "Shows 'Unknown'"

A unified release ensures consistent, coherent experience from day one.

---

## Consequences

### Positive

1. **Instant jurisdiction answers** — Hover reveals ownership in <500ms
2. **Briefing-ready interface** — Copy summary button for quick status reports
3. **Field deployment ready** — High-contrast mode for outdoor use
4. **Scalable architecture** — PMTiles handles national extent efficiently
5. **Progressive disclosure** — Simple default, complexity on demand
6. **Mobile/tablet support** — Responsive breakpoints for field devices

### Negative

1. **Implementation scope** — Multiple coordinated changes required
2. **Data pipeline dependency** — Requires PAD-US processing before deployment
3. **Storage costs** — ~250MB PMTiles file on Cloud Storage
4. **Learning curve** — New layer control paradigm for existing users

### Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| PAD-US data quality issues | 30% | Medium | Validate against known boundaries (Deschutes, Rogue River-Siskiyou); fallback to ArcGIS REST |
| PMTiles mobile support (iOS Safari) | 40% | High | iOS Safari has inconsistent `fetch` for large PMTiles. **Fallback:** Serve `/federal-low-zoom.geojson` (10MB) for mobile + zoom < 6; ArcGIS REST tiles on PMTiles 404 |
| User confusion with new UI | 40% | Low | Provide guided tour; document changes in release notes |
| tippecanoe processing failures | 20% | Medium | Pre-process and cache; provide fallback GeoJSON for dev |
| Client-side jurisdiction lookup failure | 30% | Medium | Fails on: clustered hotspots (no geometry), private land gaps, multi-jurisdiction points. **Phase 2:** Server-side PostGIS `ST_Intersects` on FIRMS ingest |

---

## Alternatives Considered

### Alternative 1: ArcGIS REST Services Direct

**Description:** Consume BLM/USFS ArcGIS MapServer tiles directly.

| Factor | Assessment |
|--------|------------|
| Setup complexity | Low — no processing pipeline |
| CORS | Problematic — requires proxy |
| Reliability | External dependency |
| Offline support | None |
| **Verdict** | **Rejected** — CORS issues and external dependency |

### Alternative 2: GeoJSON with Simplification

**Description:** Serve simplified GeoJSON boundaries per zoom level.

| Factor | Assessment |
|--------|------------|
| Implementation | Multiple GeoJSON files per zoom |
| Performance | Poor at national extent |
| Memory | High — entire dataset in browser |
| **Verdict** | **Rejected** — Does not scale |

### Alternative 3: Phased Implementation

**Description:** Ship components incrementally (Phase filter → Layers → Hover → Field mode).

| Factor | Assessment |
|--------|------------|
| Risk | Lower per release |
| User experience | Inconsistent during rollout |
| Testing | More integration points |
| **Verdict** | **Rejected** — Coherent UX more important |

### Alternative 4: Server-Side Jurisdiction Lookup

**Description:** Pre-compute jurisdiction for each hotspot on the backend via PostGIS `ST_Intersects` on FIRMS ingest.

| Factor | Assessment |
|--------|------------|
| Hover latency | Eliminated (data pre-joined) |
| Data freshness | Stale until re-processed |
| Backend complexity | Additional spatial join service |
| Handles clustered hotspots | Yes (client query fails on clusters) |
| Handles private land gaps | Yes (PAD-US has gaps) |
| Handles multi-jurisdiction | Yes (can return percentages) |
| **Verdict** | **PROMOTED to Phase 2 Must-Have** — Client-side lookup insufficient for production reliability |

---

## Resources

### Data Sources

| Resource | URL | Purpose |
|----------|-----|---------|
| PAD-US 4.1 | https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download | Federal boundary source |
| USFS Ranger Districts | https://data-usfs.hub.arcgis.com/datasets/668753ac078342b286f79fd8529d9e80 | Operational units |
| BLM SMA | https://gbp-blm-egis.hub.arcgis.com/datasets/6bf2e737c59d4111be92420ee5ab0b46 | Surface management |

### Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| tippecanoe | Vector tile generation | `brew install tippecanoe` |
| ogr2ogr | Geodata conversion | `brew install gdal` |
| pmtiles (npm) | Protocol handler | `npm install pmtiles` |

### Reference Dashboards

| Dashboard | Patterns to Study |
|-----------|-------------------|
| NIFC EGP | https://egp.wildfire.gov/maps/ — Layer controls, incident focus |
| FEMA Wildfires | https://gis-fema.hub.arcgis.com/pages/wildfires — National overview |
| NASA FIRMS | https://firms.modaps.eosdis.nasa.gov/usfs/ — Hotspot visualization |
| Esri Wildfire | https://www.esri.com/en-us/disaster-response/disasters/wildfires — Situational awareness |

### Documentation

| Resource | URL |
|----------|-----|
| MapLibre GL JS | https://maplibre.org/maplibre-gl-js/docs/ |
| PMTiles Spec | https://github.com/protomaps/PMTiles |
| PAD-US Web Services | https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-web-services |

---

## Success Metrics

### User Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to jurisdiction answer | <1 second | Hover to tooltip visible |
| Time to generate briefing | <30 seconds | Click "Copy Briefing" to clipboard |
| Phase filter clarity | >80% comprehension | User testing |
| Field mode readability | WCAG AA (7:1) | Contrast ratio audit |

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Map initial load | <3 seconds | Time to interactive (TTI) |
| Boundary layer render | <500ms | Layer toggle to visible |
| Hover tooltip latency | <300ms | Mouse enter to popup |
| Mobile touch target | 48px minimum | CSS audit |
| PMTiles cache hit rate | >80% | Browser DevTools |
| **Jurisdiction accuracy** | >95% match | Test 100 known hotspots against ground truth (critical for trust) |

### Business Metrics

| Metric | Target | Timeline |
|--------|--------|----------|
| Pilot user satisfaction | >4/5 rating | Post-demo survey |
| Briefing time reduction | 50% | User observation |
| Field deployment feasibility | Yes/No | Device testing |

---

## References

- [ADR-005: Skills-First Architecture](./ADR-005-skills-first-architecture.md) — Agent architecture context
- [ADR-006: Google-Only LLM Strategy](./ADR-006-google-only-llm-strategy.md) — Backend integration
- [PRODUCT-SUMMARY-COMPACT.md](../PRODUCT-SUMMARY-COMPACT.md) — "8-minute reality" user story
- [MapLibre GL JS Documentation](https://maplibre.org/maplibre-gl-js/docs/)
- [PMTiles Specification](https://github.com/protomaps/PMTiles)
- [PAD-US Web Services](https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-web-services)
- [NASA FIRMS Documentation](https://firms.modaps.eosdis.nasa.gov/usfs/)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-30 | Unified implementation (no phased rollout) | Coherent UX more important than incremental risk reduction |
| 2025-12-30 | PMTiles over ArcGIS REST | Self-hosted, CORS-free, offline-capable |
| 2025-12-30 | Hover for jurisdiction (not click) | "8-minute reality" demands 1-second answers |
| 2025-12-30 | Field mode as toggle (not separate theme) | Single codebase, user-controlled context switch |
| 2025-12-30 | PAD-US as boundary source | Authoritative federal dataset; includes all agencies |
| 2025-12-30 | **ADR ACCEPTED** | Expert panel review passed with required fixes applied |
| 2025-12-30 | PMTiles protocol fix | Use `tiles` array with `{z}/{x}/{y}` pattern, not `url` property |
| 2025-12-30 | ogr2ogr filter refined | Filter `Mang_Agency IN ('USFS', 'BLM', 'BIA')` excludes non-BAER agencies |
| 2025-12-30 | Server-side jurisdiction promoted | Phase 2 Must-Have due to client-side limitations on clusters/gaps |
| 2025-12-30 | iOS Safari fallback added | Simplified GeoJSON for mobile + zoom < 6 |
| 2025-12-30 | Jurisdiction accuracy metric | 95% ground truth match required for trust |

---

## Appendix A: PhaseFilterChips Component Spec

```typescript
interface PhaseFilterChipsProps {
  phases: {
    id: 'active' | 'baer_assessment' | 'baer_implementation' | 'in_restoration';
    label: string;
    count: number;
    color: string;
  }[];
  selected: string[];
  onToggle: (phaseId: string) => void;
  collapsed?: boolean;
}

// Collapsed state (48px wide):
// Shows colored dots with count badges
// Single tap → filter
// Expand on hover

// Expanded state (200px wide):
// Full labels with checkboxes
// Multi-select support
// Helper text: "Filter by post-fire phase"
```

## Appendix B: LayersPanel Component Spec

```typescript
interface LayersPanelProps {
  layers: {
    id: string;
    label: string;
    color: string;
    group: 'ownership' | 'operations';
    visible: boolean;
  }[];
  onToggle: (layerId: string) => void;
  activeCount: number;
}

// Floating panel (300x200px)
// Grouped checkboxes with color swatches
// Header shows "Layers (N active)"
// Hover preview flashes layer 500ms
// Collapse to icon when closed
```

## Appendix C: BriefingStrip Component Spec

```typescript
interface BriefingStripProps {
  metrics: {
    activeHotspots: number;
    firesByPhase: Record<string, number>;
    acresByJurisdiction: { nfs: number; blm: number; other: number };
    lastFirmsUpdate: Date;
  };
  onCopyBriefing: () => void;
}

// Fixed position top bar
// 4 metric chips + copy button
// Compact: hide labels on mobile
// Copy generates text summary:
//   "National Status (12/30 0640): 2,143 active hotspots across 47 incidents.
//    BAER: 32 assessments, 11 implementations. 1.2M acres NFS, 340K BLM.
//    Last FIRMS update: 0615 UTC."
```
