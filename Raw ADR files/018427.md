# Maps

The current version uses OpenLayers.
What are the alternatives, and is this still the go-to choice in 2024?

## Status

Go

## Decision

Use OpenLayers to avoid scope creep.

## Rationale

- Avoid scope creep

## Consequences

Openlayer, Leaflet, mapbox and google maps are the most popular choices for mapping applications.
Mapbox and Google Maps are not open source, and need commercial licenses for some use cases.

### OpenLayers

Openlayers is a good choice for the current project, but it is not the only choice.
This is the best choice for complex mapping applications requiring deep customization and integration with various data
sources.
Updated september 2023.
[OpenLayers](https://openlayers.org/)

#### Advantages of OpenLayers

- Flexible and customizable: Offers a wide range of features and controls, allowing for deep customization.
- Open source and free: No licensing fees, perfect for personal or non-commercial projects.
- Large community and support: Extensive documentation, tutorials, and a helpful community for troubleshooting.
- Supports various data formats: Handles vector, raster, and tile data from various sources.
- Advanced control options: Supports multiple map views, overlays, and custom interactions.

#### Disadvantages of OpenLayers

- Steeper learning curve: More complex API and features compared to some alternatives.
- Performance can be demanding: With extensive customization, performance may suffer on weaker devices.
- Limited mobile support: Mobile support is gradually improving, but may not be as advanced as Leaflet.

### Leaflet

Basic mapping needs with emphasis on mobile friendliness and ease of use.
Updated may 2023.
[Leaflet](https://leafletjs.com/)

#### Advantages of Leaflet

- Lightweight and easy to learn: Simple API and smaller library size, suitable for basic mapping needs.
- Mobile-friendly: Optimized for touch devices and various screen sizes.
- Large plugin ecosystem: Numerous community-developed plugins for extending functionality.

#### Disadvantages of Leaflet

- Limited feature set: May not be suitable for complex mapping applications with advanced needs.
- Smaller community: Community and support are not as vast as OpenLayers.
- Limited customization options: Styling and customization options are more restricted compared to OpenLayers.
