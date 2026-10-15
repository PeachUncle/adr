# ADR-005: Spatial Visualization with LeafletJS

## Status
Accepted

## Context
ToolVault's analysis tools frequently consume and produce GeoJSON data representing spatial features. Tools typically receive a GeoJSON feature as input and return a modified version (often as LineString), or may split/combine features. Users need to visualize both input and output spatial data to understand tool transformations, with geographic context provided by background tile maps.

## Decision
We will implement spatial visualization using LeafletJS with the following characteristics:

### Library Choice
- **LeafletJS**: Selected for simplicity and ease of integration with metadata-driven UI
- **Native GeoJSON support**: Leverages Leaflet's built-in GeoJSON rendering capabilities
- **Lightweight footprint**: Minimal impact on bundle size and loading performance

### Visualization Layout
- **Flexible dual-map layout**: Side-by-side input/output maps on wide screens (≥1200px)
- **Responsive stacking**: Vertical layout on narrow screens with output map below input
- **Dynamic map presence**: Auto-detect spatial content in tool input/output data
- **Manual override**: User controls to show/hide individual map views when auto-detection fails

### Background Tile Strategy
- **Hybrid tile approach**: Default to online tile services (OpenStreetMap) when internet available
- **Offline fallback**: Basic offline tile set bundled for operation without connectivity
- **Deployment flexibility**: Configurable tile sources to accommodate organizational requirements

### Integration Architecture
- **Metadata-driven configuration**: Map views configured based on tool output schemas in `index.json`
- **Runtime detection**: Examine actual tool input/output for GeoJSON content to determine map visibility
- **Before/after comparison**: Clear visual distinction between input and output features

## Rationale

### Simplicity Over Features
LeafletJS provides sufficient functionality for GeoJSON visualization without the complexity of advanced GIS libraries. This aligns with ToolVault's metadata-driven approach where maps are dynamically configured without complex setup.

### Responsive Spatial Analysis
The 1200px breakpoint ensures adequate viewing area for spatial analysis while supporting mobile/tablet access. Side-by-side layout allows direct visual comparison of input/output transformations.

### Hybrid Connectivity Model
Online-first with offline fallback supports both connected and air-gapped deployments while providing optimal user experience when possible.

### Auto-Detection with Manual Override
Runtime detection of spatial content provides intelligent defaults while manual controls ensure usability when tools have complex or non-standard spatial I/O patterns.

## Consequences

### Positive
- **Simple integration**: LeafletJS integrates easily with metadata-driven UI generation
- **Responsive design**: Layout adapts to different screen sizes and spatial analysis needs
- **Flexible deployment**: Works online and offline across different organizational environments
- **Clear visualization**: Before/after comparison helps users understand tool transformations
- **Low maintenance**: Minimal configuration required for basic GeoJSON rendering

### Negative
- **Limited advanced GIS**: No support for complex projections or advanced spatial operations
- **Tile management**: Offline tile bundles require storage space and maintenance
- **Performance ceiling**: May struggle with extremely large datasets (thousands of features)

### Mitigation Strategies
- **Simple use case focus**: Advanced GIS features not required for target tool types
- **Tile optimization**: Use appropriate zoom levels and compression for offline tiles
- **Feature limiting**: Implement reasonable limits on feature rendering for performance

## Implementation Notes
- LeafletJS will be integrated into the frontend SPA framework
- Tile source configuration will be environment-specific
- GeoJSON styling will use consistent visual hierarchy (input vs output distinction)
- Map container responsive behavior handled via CSS media queries at 1200px breakpoint
- Auto-detection logic will examine tool I/O schemas and actual data content