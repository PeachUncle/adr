# Location of Height and Radius Calculation for Transformations

## Status

Accepted

## Context

The `HemisphericalCylinderTransformation` requires height and radius parameters to perform its calculations. These
parameters could logically be part of either:

- **Domain Layer:** As properties of the `Mesh` object, directly computed from its vertices.
- **Use Case Layer:** As inferred values based on the specific application and user expectations.

In the context of our STL transformation application for tabletop miniature figures:

1. Users expect the application to work seamlessly without requiring input for model dimensions.
2. The height and radius may not always be intrinsic to the `Mesh` object but can depend on the application context or
3. user intent.

Additionally, during development, we observed that the simple cylindrical transformation often resulted in undesirable
geometry at the top of the model, particularly a flat spot that did not align with the natural curvature of a humanoid
figure (e.g., the rounded top of a head). To address this issue and produce more realistic results for humanoid models,
we decided to switch to a hemisphere-topped cylindrical transformation.

This transformation better approximates the natural geometry of humanoid figures while retaining the simplicity and
computational efficiency of cylindrical transformations for the main body.

## Decision

The height and radius will be determined in the **use case layer**. Specifically:

1. The use case layer will compute these values using heuristics (e.g., bounding box calculations for height and
maximum distance from the z-axis for radius).
2. This approach keeps the domain layer pure, focusing solely on the structure and transformation of meshes, without
adding application-specific logic.
The inferred parameters allow the transformation logic to adapt to the context of tabletop miniature models.

## Consequences

- **Pros:**
  - Keeps the domain layer clean and focused on mesh representation and transformation.
  - Supports seamless user experience by eliminating the need for additional input.
  - Provides a transformation that more closely aligns with the geometry of humanoid models, improving visual results.
  - Allows for application-specific customization or future extensibility in the use case layer.

- **Cons:**
  - Heuristics in the use case layer may introduce assumptions that could fail for edge cases or atypical STL models.
  - Increased complexity in the use case layer, as it must handle dimension inference.

- **Mitigation for Cons:**
  - Document assumptions for height and radius calculations in code and user documentation.
  - Allow future overrides or user input to refine these heuristics.

## Alternatives Considered

1. **Simple cylindrical transformation**:
   - **Rejected**: While easier to implement, this transformation often produced unrealistic flat spots at the top of
   - humanoid models. It lacked the nuance needed to replicate natural human-like geometry.
2. **Calculate height and radius in the `Mesh` object (domain layer)**:
   - **Rejected**: This approach would couple the domain logic to application-specific assumptions, reducing reusability
   - of the `Mesh` class.
3. **Require the user to provide height and radius**:
   - **Rejected**: This approach burdens the user with additional complexity and detracts from the seamless experience
   - we aim to provide.

## Decision Owner

Tom Willis

## Date

2024-12-28
