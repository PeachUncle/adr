## Context

The python-geo-cli template needs structured multi-layer visualization. Users want:
1. Automatic spatial context without manual index creation
2. Simple API: load GeoJSON → create map with index + target layers

## Goals / Non-Goals

**Goals:**
- Auto-generate H3 index layer from input data using SRAI
- Support GeoJSON (FeatureCollection) and GeoDataFrame inputs
- Default styling (target=red, index=blue) with auto geometry detection
- Configurable Mapbox basemaps (streets-v12, outdoor-v12)
- Auto-center map on densest H3 cell

**Non-Goals:**
- Custom styling API (future iteration)
- Non-H3 indexing methods
- Non-Mapbox basemaps

## Decisions

### Decision 1: H3 Index Generation with SRAI
Use SRAI library for H3 regionalization:

```python
from srai.regionalizers import H3Regionalizer
from srai.joiners import IntersectionJoiner

regionalizer = H3Regionalizer(resolution=9)
joiner = IntersectionJoiner()

regions = regionalizer.transform(gdf)
joint = joiner.transform(regions, gdf)

region_counts = joint.groupby(level='region_id').size()
normalized = region_counts / region_counts.max()
```

**Rationale**: SRAI provides battle-tested H3 operations. Resolution 9 (~174m edge) balances detail with performance.

### Decision 2: Layer Structure
```
┌─────────────────────────────────┐
│  Target Layer (red, opacity=0.9)│  ← actual features
├─────────────────────────────────┤
│  Index Layer (blue, opacity=0.5)│  ← H3 cells with feature counts
├─────────────────────────────────┤
│  Basemap (Mapbox streets-v12)   │  ← configurable
└─────────────────────────────────┘
```

### Decision 3: Data Pipeline
```
Input (GeoJSON/GeoDataFrame)
         │
         ▼
    GeoDataFrame (EPSG:4326)
         │
    ┌────┴────┐
    ▼         ▼
 Target    H3 Index
  Layer     Layer
    │         │
    └────┬────┘
         ▼
    KeplerGL Config
         │
         ▼
    HTML Output
```

### Decision 4: Module Organization
```
viz/
├── __init__.py       # Public API: create_map()
├── kepler_maps.py    # Existing - keep unchanged
├── indexer.py        # NEW - H3 index generation
├── basemaps.py       # NEW - basemap configurations
└── renderer.py       # NEW - KeplerGL config + HTML generation
```

### Decision 5: Basemap Configuration
```python
BASEMAPS = {
    "streets": "mapbox://styles/mapbox/streets-v12",
    "outdoor": "mapbox://styles/mapbox/outdoors-v12",
}
```
Extensible dict for future basemaps.

### Decision 6: Default Styles
| Layer  | Color       | Opacity | Auto-detect |
|--------|-------------|---------|-------------|
| Target | #FF0000 red | 0.9     | Point/Line/Polygon from GDF |
| Index  | #0000FF blue| 0.5     | Always Polygon (H3 cells) |

### Decision 7: Map Positioning
1. Calculate feature count per H3 cell
2. Find cell with max count
3. Center map on that cell's centroid
4. Auto-zoom based on data extent

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| SRAI adds dependency | Worth it for robust H3 ops |
| Resolution 9 may not fit all data | Make resolution configurable later |

## Open Questions

None - scope is intentionally minimal for first iteration.
