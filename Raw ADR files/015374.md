# Storage in GeoJSON FeatureCollection

## Status

Accepted
  
## Context

Users will load tracks and spatial data into a session. They will also make cosmetic and/or spatial edits to this data.  They will also add new data.

We need to allow them to persist this data between sessions using local file storage.

It could also be useful to have a strategy for persistent (and possibly in-memory) storage of data.

## Decision

We are going to use a GeoJSON FeatureCollection as the structure to store sessions.  The structure allows for the storage of an array of Spatial (GeoJSON)
 children (Features), which could accomodate both vessel tracks and spatial annotations.
 
The GeoJSON specification does allow for a Feature that has an empty set of coordinates - resulting in an object with `id` and `properties` This would allow the creation of a `metadata` feature which could be used to store of a wide set of document level metadata, including:
 - current time filter
 - current viewport
 - any other preferences related to this document

For a vessel track we will always a series of observations/measurements for position and time, and usually also values for course and speed. The current GeoJSON specification only allows for coordinate elements with values for lat, long, and optionally elevation.  Time, course and speed will be stored as arrays in the `properties` element, stored as `times`, `courses` and `speeds`. These arrays will be of the same length as the series of coordinates.  If no measurements of that type are available then the item will not be present.  Where only some values are present the other array items will be left as undefined/empty (such as `courses: [,,23.3, 23.4, 23.5,,,,]`. 

## Consequences

- Datafiles can be transferred to partner agencies, and/or rendered in other software applications.
- Partner agencies can be encouraged to provide data in GeoJSON format, for easy loading.  Data provided in this way will have varying amounts of integration, according to to the degree of adherence to the practices detailed here (to be formally captured once they have matured, later in the project).
