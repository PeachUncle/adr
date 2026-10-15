## Status
Accepted

## Context
We're going to store application data in GeoJSON. We need to decide which GeoJSON feature type to use for our data.

## Decision


| Element    | Feature Type | Rationale / Other thoughts                                                                                                                                         |
|------------|--------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Track      | Line String  | If we ever need to support multiple track segments, switch to array of line segments (Multi Line String)                                               |
| Buoy Field | Multi Point  |                                                                                                                                                        |
| Zone       | Polygon      | We may support several different zone shape styles. Shape-specific construction points/dimensions could be stored as properties, but resulting shape stored in polygon.                                                                                                                                                       |
| Line       | Linestring   | In legacy system lines are type of zone, but suggest renaming to avoid confusion.  When loading 3rd party data treat a Line String as `Track` if it contains time data, else `Line`                                                                                                                                                     |
| Point      | Point        |                                                                                                                                                        |
| Metadata   | Point        | Create point feature with empty coordinates, then store app level metadata in properties.  Generate multiple metadata features if logically necessary. |
|            |              |                                                                                                                                                        |


## Consequences
Future maintainers will thank use for wise data storage decisions.


