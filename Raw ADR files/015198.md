# ADR-013: Geospatial Intelligence Layer

**Status:** Accepted  
**Date:** 2024-12-31  
**Decision Makers:** TechTrend Federal - Digital Twin Team  
**Category:** Architecture | Infrastructure  
**Depends On:** ADR-012 (Mission Control UI)

---

## Context

ADR-012 establishes the Mission Control UI architecture with three-column layout: IncidentRail (left), NationalMap (center), and AgentChat (right). The 4-week implementation plan focuses on incident filtering, agent communication, and proof layer transparency—but **does not address geospatial data overlays**.

Our mockups and stakeholder expectations include rich geospatial visualization:

| Layer Type | Data Source | Current State | Priority |
|------------|-------------|---------------|----------|
| Fire perimeters | NIFC GeoJSON | ✅ Implemented | Keep |
| FIRMS hotspots | NASA CSV/GeoJSON | ✅ Implemented | Keep |
| **Burn severity** | MTBS COG rasters | ❌ Not implemented | 🔴 Critical |
| **Trail damage** | Field assessment points | ❌ Not implemented | 🟡 High |
| **Treatment units** | BAER planning polygons | ❌ Not implemented | 🟢 Medium |
| **Layer control** | UI component | Partial | Full panel |

The Burn Analyst agent skill requires burn severity data for analysis, creating a dependency between the AI layer and the geospatial layer.

### Technical Landscape (2024-2025)

Modern geospatial web visualization has evolved significantly:

1. **Cloud Optimized GeoTIFF (COG)**: OGC standard (2023) enabling HTTP range requests for efficient raster streaming
2. **maplibre-cog-protocol**: Client-side COG rendering in MapLibre without server infrastructure (Geomatico, 2024)
3. **PMTiles**: Single-file archive format for serverless vector tile hosting
4. **TiTiler**: Server-side dynamic tile generation from COGs (Development Seed)
5. **deck.gl**: GPU-accelerated WebGL visualization for high-density vector data (vis.gl)

---

## Decision

Implement a **progressive geospatial layer architecture** with four tiers:

### Tier 1: Native MapLibre (Vectors)
- Fire perimeters (existing NIFC integration)
- Trail damage point markers (new)
- Phase-aware styling (colors match PhaseFilterChips)

### Tier 2: maplibre-cog-protocol (Rasters)
- MTBS burn severity COGs hosted on Google Cloud Storage
- Client-side rendering with dNBR colormaps
- No additional backend infrastructure required
- **Critical:** COGs must be preprocessed to EPSG:3857

### Tier 3: PMTiles (Static Vectors)
- Treatment unit polygons (BAER planning areas)
- Historical fire perimeters (archive data)
- PAD-US boundaries (protected areas)
- Single-file hosting on GCS with HTTP range requests

### Tier 4: deck.gl (Performance - Opt-in)
- High-density FIRMS hotspots when MapLibre struggles (>10K points)
- `MapboxOverlay` integration pattern
- Activate only if performance testing reveals need

### Deferred: TiTiler
- Reserved for dynamic band math requirements
- **Pivot triggers:** Dynamic styling requests, multi-band analysis (RdNBR vs dNBR), cross-fire mosaics (>10 fires)
- Not in initial implementation

---

## Rationale

### Why maplibre-cog-protocol over TiTiler?

| Factor | maplibre-cog-protocol | TiTiler |
|--------|----------------------|---------|
| Infrastructure | Zero (static GCS hosting) | Cloud Run service |
| Cost | Storage + CDN only | Compute + storage |
| Cold start | None | 5-15s on Cloud Run |
| Complexity | `npm install` | Docker + GDAL + FastAPI |
| Our data | Static (annual MTBS) | Dynamic band math |
| Maturity | 2024, in MapLibre docs | Battle-tested |

MTBS burn severity data is **static** (annual releases). We don't need dynamic band math or runtime reprojection. Client-side COG rendering matches our cost and simplicity constraints.

**Key validation:** Geomatico successfully tested maplibre-cog-protocol with a 12GB DEM. Our MTBS COGs (500MB-2GB) are well within proven limits.

### Why Add PMTiles?

PMTiles provides single-file vector tiles optimized for HTTP range requests—perfect for static polygon datasets:

- Treatment units change infrequently (BAER planning cycle)
- Historical perimeters are immutable
- Zero tile server required (same pattern as COG)
- Reduces GeoJSON payload size by 10-100x for complex polygons

### Why Not deck.gl First?

deck.gl adds complexity (dual render systems) and is overkill for current data volumes:

| Data Type | Expected Volume | MapLibre Handles? |
|-----------|-----------------|-------------------|
| FIRMS hotspots | 1-5K points/fire | ✅ Yes |
| Trail damage | 50-200 points/fire | ✅ Yes |
| Treatment units | 10-50 polygons/fire | ✅ Yes |

We'll add deck.gl **only if** MapLibre performance degrades below 30fps with real data.

### Why Separate from ADR-012?

1. **Different expertise**: UI/UX vs. geospatial/GIS
2. **Different dependencies**: ADR-012 needs ADK; ADR-013 needs GDAL/COG tooling
3. **Parallel execution**: Can run concurrently with ADR-012 Weeks 3-4
4. **Isolated risk**: Geospatial failures don't block agent chat development

---

## Architecture Integration

### Updated RANGER Stack Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           RANGER ARCHITECTURE                           │
├──────────────────────┬──────────────────────┬──────────────────────────┤
│     YOUR BROWSER     │     CLOUD RUN        │   PERSISTENT SERVICES    │
│  (React/Zustand/     │  (FedRAMP Moderate)  │                          │
│     MapLibre)        │                      │                          │
│                      │ • Frontend (static)  │ • Cloud SQL (PostGIS)    │
│ • COG Protocol       │ • API Orchestrator   │ • Vertex AI (Gemini)     │
│ • PMTiles Reader     │ • Agent Services     │ • Vertex AI RAG Engine   │
│ • Layer Controls     │ • Geospatial Query   │                          │
│                      │   API (lightweight)  │                          │
├──────────────────────┴──────────────────────┴──────────────────────────┤
│                     CLOUD STORAGE (GCS + Cloud CDN)                     │
│  • React bundle (~2MB)                                                  │
│  • MTBS COG rasters (burn severity, EPSG:3857)                         │
│  • PMTiles (treatment units, historical perimeters)                    │
│  • CDN caching (max-age=31536000 for immutable data)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                        EXTERNAL APIs (MCP Connected)                    │
│  • NIFC (fire perimeters)  • FIRMS (hotspots)  • MTBS Catalog          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Geospatial Data Flow

```
USER CLICKS INCIDENT IN IncidentRail
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: NationalMap centers on fire, loads layers              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │ Fire         │   │ Burn         │   │ Treatment    │        │
│  │ Perimeter    │   │ Severity     │   │ Units        │        │
│  │ (NIFC API)   │   │ (COG/GCS)    │   │ (PMTiles)    │        │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘        │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │           MapLibre GL JS (unified rendering)         │       │
│  │  • GeoJSON source (perimeter)                        │       │
│  │  • Raster source via cog:// protocol (severity)      │       │
│  │  • Vector source via pmtiles:// protocol (units)     │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

STEP 2: User enables "Burn Severity" layer toggle
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│ maplibre-cog-protocol                                           │
│  1. Reads COG header (HTTP range: bytes=0-16384)               │
│  2. Determines visible tiles for viewport                       │
│  3. Fetches only needed tiles (HTTP range requests)            │
│  4. Renders with dNBR colormap                                 │
│  5. Updates on pan/zoom (lazy tile loading)                    │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Integration Architecture

**For Burn Analyst geospatial queries, use lightweight HTTP API (not MCP):**

```
BURN ANALYST SKILL
    │
    │  "What's the severity distribution for Cedar Creek?"
    ▼
┌─────────────────────────────────────────────────────────────────┐
│ CLOUD RUN: Geospatial Query API (FedRAMP Moderate)              │
│                                                                 │
│  POST /api/v1/burn-severity/statistics                         │
│  {                                                              │
│    "fire_id": "cedar_creek_2024",                              │
│    "bbox": [-121.5, 44.1, -121.2, 44.4]                        │
│  }                                                              │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Rasterio reads COG from GCS (HTTP range)                │   │
│  │ Computes: mean, max, histogram, area by class           │   │
│  │ Returns JSON statistics                                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Response (200ms):                                              │
│  {                                                              │
│    "severity_distribution": {                                   │
│      "unburned": 0.12, "low": 0.28, "moderate": 0.35,          │
│      "high": 0.25                                               │
│    },                                                           │
│    "total_acres": 15420,                                        │
│    "high_severity_acres": 3855                                  │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

**Why HTTP API over MCP?**
- Single data source (MTBS) doesn't need MCP abstraction overhead
- Simpler debugging and monitoring
- 200ms latency vs 500ms+ for MCP roundtrip
- Pivot to MCP if we add 3+ geospatial sources (soil, vegetation, weather)

---

## Consequences

### Positive
- Zero additional backend services for raster/vector rendering
- Leverages existing MapLibre investment
- Cost-effective ($540-1,092/year for geospatial layer)
- Clear upgrade path (add TiTiler if dynamic styling needed)
- Aligns with Skills-First: geospatial data accessible to agent skills
- FedRAMP compliant via GCS + Cloud Run

### Negative
- COGs must be pre-processed to EPSG:3857 (one-time per fire)
- maplibre-cog-protocol is newer (2024), smaller community
- Client CPU rendering may struggle on low-power devices
- No dynamic band math without TiTiler pivot

### Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **EPSG:3857 preprocessing** | HIGH | MEDIUM | Automated GDAL script in data pipeline, validate in Week 1 |
| **Browser CPU bottleneck** | MEDIUM | MEDIUM | Lazy load severity layer, loading indicator, defer to deck.gl if <30fps |
| **COG not optimized** | MEDIUM | HIGH | Validate with `rio cogeo validate --strict`, enforce 512x512 blocks |
| **GCS CORS issues** | MEDIUM | HIGH | Test HTTP range requests in Week 1, document CORS config |
| **GCS egress cost spike** | LOW | MEDIUM | Cloud CDN (cache 1 year), GCS Nearline for archives |
| **maplibre-cog-protocol bugs** | LOW | HIGH | Pin to v0.5.0+, maintain TiTiler fallback in backlog |
| **Large COG initial load** | MEDIUM | MEDIUM | Viewport-based loading, progress indicator, tile coalescing |

---

## Alternatives Considered

| Alternative | Verdict | Rationale |
|-------------|---------|-----------|
| TiTiler on Cloud Run | Deferred | Adds infrastructure; MTBS is static; keep as fallback |
| Pre-rendered XYZ tiles | Rejected | Storage explosion (~100x COG size), inflexible |
| GeoServer | Rejected | Heavy, Java stack, not FedRAMP-friendly |
| deck.gl for everything | Rejected | Overkill for current volumes, MapLibre works |
| MCP for agent queries | Deferred | Single source doesn't justify MCP overhead |
| OpenLayers instead of MapLibre | Rejected | Already invested in MapLibre, smaller bundle |

---

## Implementation Plan

### Phase 1: Validation & Data Pipeline (Week 1-2)

**Week 1: Critical Path Validation**
1. Download sample MTBS data for Cedar Creek Fire (smallest available)
2. Run full preprocessing pipeline:
   ```bash
   gdal_translate -of COG \
     -co TILING_SCHEME=GoogleMapsCompatible \
     -co BLOCKSIZE=512 \
     -co COMPRESS=DEFLATE \
     -co PREDICTOR=2 \
     -co NUM_THREADS=ALL_CPUS \
     -t_srs EPSG:3857 \
     mtbs_input.tif cedar_creek_cog.tif
   ```
3. Validate COG structure: `rio cogeo validate --strict cedar_creek_cog.tif`
4. Upload to GCS bucket with CORS configuration
5. Test maplibre-cog-protocol in browser (Chrome, Safari, Edge)
6. **Gate:** If validation fails, escalate to TiTiler architecture

**Week 2: GCS + CDN Setup**
1. Configure GCS bucket with public read
2. Enable Cloud CDN, set cache headers:
   ```
   Cache-Control: public, max-age=31536000, immutable
   ```
3. Verify CDN cache hit rate >80%
4. Document preprocessing script for CI/CD integration

### Phase 2: MapLibre Integration (Week 2-3)

**Week 2 (continued):**
1. Install `@geomatico/maplibre-cog-protocol@^0.5.0`
2. Create `BurnSeverityLayer.tsx` component
3. Implement dNBR colormap (MTBS standard):
   ```typescript
   const SEVERITY_COLORS = {
     unburned: '#006400',      // -500 to -100
     low: '#7CFC00',           // -100 to +100  
     moderate_low: '#FFFF00',  // +100 to +270
     moderate_high: '#FFA500', // +270 to +440
     high: '#FF0000'           // +440 to +1300
   };
   ```
4. Add loading state and error handling

**Week 3:**
1. Install PMTiles protocol: `npm install pmtiles`
2. Create `TreatmentUnitLayer.tsx` (polygon fill)
3. Create `TrailDamageLayer.tsx` (point markers)
4. Integrate with NationalMap component
5. Phase-aware styling (color matches incident phase)

### Phase 3: Layer Control & Data Integration (Week 3-4)

**Week 3 (continued):**
1. Build `LayerControlPanel.tsx`:
   ```typescript
   interface LayerConfig {
     id: string;
     name: string;
     type: 'raster' | 'vector';
     source: 'cog' | 'pmtiles' | 'geojson' | 'api';
     visible: boolean;
     opacity: number;
     legend?: LegendConfig;
   }
   ```
2. Opacity sliders for raster layers
3. Legend component showing dNBR classification

**Week 4:**
1. Connect to MTBS catalog API
2. Build fire → COG URL mapping
3. Implement on-demand COG loading per incident selection
4. Popup/tooltip on click for treatment units

### Phase 4: Agent Integration (Week 4-5)

1. Create Cloud Run service: `geospatial-query-api`
2. Implement endpoints:
   - `POST /api/v1/burn-severity/statistics`
   - `GET /api/v1/treatment-units/{fire_id}`
3. Connect Burn Analyst skill to query API
4. Cache statistics per treatment unit (Redis or in-memory)

### Phase 5: Performance Validation (Week 5-6)

1. Load test with full-size MTBS COGs (2GB)
2. Profile MapLibre rendering at various zoom levels
3. Measure browser memory usage (target: <500MB)
4. Test on mobile devices (target: 30fps)
5. **Gate:** If MapLibre <30fps with FIRMS, add deck.gl ScatterplotLayer

---

## Technical Specifications

### COG Requirements

```bash
# Standard preprocessing script for MTBS data
#!/bin/bash
set -e

INPUT=$1
OUTPUT=$2
FIRE_ID=$3

echo "Processing ${FIRE_ID}..."

# Reproject and convert to COG
gdal_translate -of COG \
  -co TILING_SCHEME=GoogleMapsCompatible \
  -co BLOCKSIZE=512 \
  -co COMPRESS=DEFLATE \
  -co PREDICTOR=2 \
  -co NUM_THREADS=ALL_CPUS \
  -co OVERVIEWS=AUTO \
  -t_srs EPSG:3857 \
  "${INPUT}" "${OUTPUT}"

# Validate
rio cogeo validate --strict "${OUTPUT}"

# Upload to GCS
gsutil -h "Cache-Control:public, max-age=31536000, immutable" \
  cp "${OUTPUT}" "gs://ranger-geospatial/mtbs/${FIRE_ID}.tif"

echo "✅ ${FIRE_ID} processed and uploaded"
```

### GCS CORS Configuration

```json
[
  {
    "origin": ["https://ranger.techtrend.gov", "http://localhost:3000"],
    "method": ["GET", "HEAD"],
    "responseHeader": ["Content-Type", "Content-Range", "Accept-Ranges"],
    "maxAgeSeconds": 3600
  }
]
```

### MapLibre Integration

```typescript
// src/components/map/BurnSeverityLayer.tsx
import { useEffect } from 'react';
import { useMap } from 'react-map-gl/maplibre';
import { cogProtocol } from '@geomatico/maplibre-cog-protocol';
import maplibregl from 'maplibre-gl';

// Register protocol once at app init
maplibregl.addProtocol('cog', cogProtocol);

interface BurnSeverityLayerProps {
  fireId: string;
  visible: boolean;
  opacity: number;
}

export function BurnSeverityLayer({ fireId, visible, opacity }: BurnSeverityLayerProps) {
  const { current: map } = useMap();

  useEffect(() => {
    if (!map) return;

    const sourceId = `burn-severity-${fireId}`;
    const layerId = `burn-severity-layer-${fireId}`;
    const cogUrl = `cog://https://storage.googleapis.com/ranger-geospatial/mtbs/${fireId}.tif`;

    // Add source
    if (!map.getSource(sourceId)) {
      map.addSource(sourceId, {
        type: 'raster',
        url: cogUrl,
        tileSize: 256
      });
    }

    // Add layer
    if (!map.getLayer(layerId)) {
      map.addLayer({
        id: layerId,
        type: 'raster',
        source: sourceId,
        paint: {
          'raster-opacity': opacity
        }
      });
    }

    // Update visibility
    map.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
    map.setPaintProperty(layerId, 'raster-opacity', opacity);

    return () => {
      if (map.getLayer(layerId)) map.removeLayer(layerId);
      if (map.getSource(sourceId)) map.removeSource(sourceId);
    };
  }, [map, fireId, visible, opacity]);

  return null;
}
```

### Layer Control Panel Schema

```typescript
// src/types/layers.ts
export interface LayerConfig {
  id: string;
  name: string;
  type: 'raster' | 'vector';
  source: 'cog' | 'pmtiles' | 'geojson' | 'api';
  visible: boolean;
  opacity: number;
  legend?: {
    type: 'gradient' | 'categorical';
    items: Array<{ color: string; label: string; value?: number }>;
  };
}

export const DEFAULT_LAYERS: LayerConfig[] = [
  {
    id: 'burn-severity',
    name: 'Burn Severity (MTBS)',
    type: 'raster',
    source: 'cog',
    visible: true,
    opacity: 0.7,
    legend: {
      type: 'categorical',
      items: [
        { color: '#006400', label: 'Unburned/Very Low' },
        { color: '#7CFC00', label: 'Low' },
        { color: '#FFFF00', label: 'Moderate-Low' },
        { color: '#FFA500', label: 'Moderate-High' },
        { color: '#FF0000', label: 'High' }
      ]
    }
  },
  {
    id: 'treatment-units',
    name: 'Treatment Units (BAER)',
    type: 'vector',
    source: 'pmtiles',
    visible: true,
    opacity: 0.6
  },
  {
    id: 'trail-damage',
    name: 'Trail Damage Points',
    type: 'vector',
    source: 'api',
    visible: true,
    opacity: 1.0
  },
  {
    id: 'firms-hotspots',
    name: 'Active Hotspots (FIRMS)',
    type: 'vector',
    source: 'api',
    visible: true,
    opacity: 1.0
  }
];
```

---

## Cost Estimate (Annual)

### Recommended Architecture

| Component | Monthly | Annual | Notes |
|-----------|---------|--------|-------|
| **GCS Standard Storage** | $2-6 | $24-72 | 100-300GB MTBS COGs (20-40 fires) |
| **GCS Nearline (archive)** | $1-2 | $12-24 | Historical fires >1 year old |
| **Cloud CDN Egress** | $40-80 | $480-960 | 500GB-1TB/month @ $0.08/GiB |
| **Cloud Run (query API)** | $3-8 | $36-96 | Minimal usage, scale-to-zero |
| **Total Geospatial** | **$46-96** | **$552-1,152** | ~6-13% of $6-9K total budget |

### TiTiler Fallback (If Needed)

| Component | Monthly | Annual | Notes |
|-----------|---------|--------|-------|
| GCS Storage | $3-8 | $36-96 | Same COG storage |
| Cloud Run (TiTiler) | $15-25 | $180-300 | Min instances = 1 |
| Cloud CDN Egress | $30-60 | $360-720 | 70% of direct (tile caching) |
| **Total TiTiler** | **$48-93** | **$576-1,116** | Similar cost, more complexity |

### Cost Optimization Tips

1. Set aggressive CDN cache headers (1 year for immutable COGs)
2. Use GCS Nearline ($0.010/GB) for fires older than 1 year
3. Compress COGs with DEFLATE predictor=2 (30-50% size reduction)
4. Implement client-side tile cache (IndexedDB) for return visits

---

## Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| COG renders in NationalMap | <3 seconds | First meaningful paint |
| Layer toggle shows/hides | Instant | No re-fetch required |
| Colormap accuracy | 100% | Matches MTBS classification |
| Query API response | <200ms | p95 latency |
| Mobile performance | 30fps | All layers enabled |
| Browser memory | <500MB | With 2GB COG loaded |
| CDN cache hit rate | >80% | Measured over 1 week |
| No new backend services | ✓ | For initial launch |

---

## TiTiler Pivot Triggers

Escalate to TiTiler architecture if any of these occur:

1. **Dynamic styling requirement:** Forest Supervisor wants to adjust burn severity thresholds interactively
2. **Multi-band analysis needed:** Burn Analyst skill needs to compute custom indices (RdNBR vs dNBR)
3. **Cross-fire mosaics required:** Displaying regional burn severity across 10+ fires simultaneously
4. **EPSG:3857 preprocessing becomes blocker:** Complex CI/CD integration issues
5. **Client-side rendering fails:** Browser memory >1GB or <15fps consistently

**Fallback cost:** ~$15-25/month additional for TiTiler on Cloud Run (min instances = 1)

---

## References

- [maplibre-cog-protocol GitHub](https://github.com/geomatico/maplibre-cog-protocol)
- [Geomatico: Serverless Rasters in MapLibre](https://geomatico.es/en/serverless-rasters-in-maplibre-the-cog-protocol-extension/)
- [TiTiler Documentation](https://developmentseed.org/titiler/)
- [deck.gl + MapLibre Integration](https://deck.gl/docs/developer-guide/base-maps/using-with-maplibre)
- [Cloud Optimized GeoTIFF Spec](https://cogeo.org/)
- [NASA Earthdata COG Standard](https://www.earthdata.nasa.gov/about/esdis/esco/standards-practices/cloud-optimized-geotiff)
- [MTBS Mapping Methods](https://www.mtbs.gov/mapping-methods)
- [MTBS Data Access](https://www.mtbs.gov/direct-download)
- [GDAL COG Driver](https://gdal.org/en/stable/drivers/raster/cog.html)
- [PMTiles Specification](https://github.com/protomaps/PMTiles)
- [GCS Pricing](https://cloud.google.com/storage/pricing)
- [Cloud CDN Pricing](https://cloud.google.com/cdn/pricing)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2024-12-31 | Created ADR-013 as separate track | Isolate geospatial complexity from UI/agent work |
| 2024-12-31 | Selected maplibre-cog-protocol | Static MTBS data, zero infrastructure, cost-effective |
| 2024-12-31 | Added PMTiles for static vectors | Treatment units, historical perimeters benefit from tile format |
| 2024-12-31 | HTTP API over MCP for agent queries | Single source doesn't justify MCP abstraction overhead |
| 2024-12-31 | Deferred deck.gl to validation phase | MapLibre likely sufficient for current volumes |
| 2024-12-31 | Defined TiTiler pivot triggers | Clear criteria for when to add dynamic tile server |
| 2024-12-31 | **Status: Accepted** | Expert panel review affirmed architecture |
