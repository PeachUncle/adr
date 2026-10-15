# Architectural Decision Record: Domain Mesh Format

## Status

Accepted

## Context

The project involves applying transformations, such as thickening, to 3D shapes. To enforce clean architecture
principles, the domain and use cases must remain decoupled from specific file formats like STL or OBJ. Instead,
a generic and abstract representation of shapes is needed to facilitate transformations independently of the
input/output formats.

## Decision

We will adopt a polygonal mesh representation as the standard format for 3D shapes in the domain layer. This
representation will include the following components:

1. **Vertices**: A list of points in 3D space (x, y, z coordinates).
   - Example: `[(x1, y1, z1), (x2, y2, z2), ...]`
2. **Edges**: A list of pairs of vertex indices representing connections.
   - Example: `[(0, 1), (1, 2), ...]`
3. **Faces**: A list of sets of vertex indices representing polygons (typically triangles or quads).
   - Example: `[(0, 1, 2), (2, 3, 0), ...]`

This format will be encapsulated in a `Mesh` class within the domain layer and serve as the standard data format
for all thickening transformations.

## Reasons

1. **Abstraction**: Decouples domain logic from file-specific details, enabling transformations to operate on
generic shape data.
2. **Simplicity**: The representation is straightforward and widely understood in 3D modeling.
3. **Interoperability**: Aligns with common 3D processing libraries, making it easier to integrate external tools
when needed.
4. **Extensibility**: Additional features like normals, UV mappings, or other attributes can be added to the mesh
structure in the future without breaking compatibility.
5. **Clean Architecture Compliance**: Ensures domain logic is independent of external I/O or file format concerns.

## Consequences

1. **Connectors**: Input/output connectors must handle conversion between specific file formats (e.g., STL) and the
`Mesh` format.
2. **Domain Isolation**: All domain and use case logic will operate on `Mesh` objects, ensuring separation of concerns.
3. **Implementation Overhead**: Additional effort may be required to implement robust connectors for reading/writing
4. external file formats.

## Implementation

1. Define a `Mesh` class with the following structure:

   ```python
   from typing import List, Tuple

   class Mesh:
       def __init__(self, vertices: List[Tuple[float, float, float]],
                    edges: List[Tuple[int, int]],
                    faces: List[Tuple[int, int, int]]):
           self.vertices = vertices
           self.edges = edges
           self.faces = faces
   ```

2. Create connectors to:
   - Convert STL and other file formats to `Mesh` objects.
   - Convert `Mesh` objects back to the desired output format.

3. Update domain use cases to utilize `Mesh` as the input and output data format for transformations.

## Alternatives Considered

1. **Using STL Structures Directly**: Rejected because STL lacks an edge representation and is tied to a specific file
2. format, violating clean architecture principles.
**Point Clouds**: Rejected because they lack explicit surface definitions, making transformations like thickening
3. ambiguous.
**Other Mesh Formats**: More complex formats with additional attributes (e.g., normals, textures) were considered
4. but deemed unnecessary for the current requirements.

## Decision Owner

Tom Willis

## Date

2024.12.10
