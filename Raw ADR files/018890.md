# Architectural Decision Record: Choosing STL File Format for the Thickening Tool

## Status

Accepted

## Context

The goal of this project is to build a tool that thickens 3D models stored in STL files,
particularly for tabletop miniatures. STL is a widely-used file format in 3D printing and
computer-aided design (CAD) for representing the geometry of 3D objects. Given that many
free models available for tabletop games are stored in this format, we need to decide
whether to stick with STL or consider other 3D model formats (e.g., OBJ, PLY, GLTF).

Several factors need to be considered:

- STL is simple and widely supported by 3D modeling tools and 3D printers.
- There are many Python libraries available to parse and manipulate STL files.
- Other file formats such as OBJ or GLTF are more complex and support additional features
- like textures and materials, which are not required for this tool.
- The tool's primary use case is focused on modifying the geometry (thickening) of 3D
- models, not on handling advanced features.

## Decision

We will use the **STL file format** for this tool, with the following rationale:

- **Simplicity**: STL files are straightforward to parse, manipulate, and generate. We
- can leverage existing Python libraries (e.g., `numpy-stl`, `stl`) to read and write
- the files.
- **Wide Adoption**: STL is the most common format for 3D models in tabletop games, and
- most miniatures are shared in STL format.
- **Focus on Geometry**: The tool's purpose is to thicken models while preserving their
- geometric shape. STL files are well-suited for this use case as they store the 3D shape
- in a simple, triangular mesh format.

We will implement the thickening algorithm using STL files as the input/output format,
and avoid the complexities of other formats unless additional features are required later.

## Consequences

- We are constrained to working within the limitations of the STL file format, which
- does not support advanced features such as textures, materials, or animations.
- Future support for other formats like OBJ or GLTF will require additional work and
- may add unnecessary complexity at this stage.
- We need to ensure proper handling of STL files, including potential issues with
- file size or
- mesh complexity as the thickening algorithm is applied.

## Decision Owner

Tom Willis

## Date

2024-12-10
