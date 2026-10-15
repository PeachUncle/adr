# Centroid-Based Thickening for Vertical Slices**

## Status

Accepted

## Date

January 5, 2025

## Context

The existing cylindrical thickening transformation improves the robustness of 3D printed models by thickening narrow
vertical sections based on their distance from the z-axis. However, this approach is limited to models where narrow
features (such as limbs) are approximately aligned with the z-axis. It also fails to account for offset features, such
as arms or legs that are not centered on the z-axis.

In practice, many figurines have limbs or other features that are offset from the central vertical axis of the model.
For example, arms outstretched to the sides or legs positioned away from the center will not be properly thickened if
the transformation assumes the z-axis is the center of the cross-section. To improve thickening accuracy, we need to
shift from z-axis-based thickening to **centroid-based thickening** of detected narrow cross-sections.

## Decision

We will implement **centroid-based thickening** for vertical slices:

- Each detected **narrow cross-section** will be treated as a slice of vertices.
- The **centroid** of each slice will be calculated to determine the "local axis" for thickening.
- The thickening transformation will apply an offset normal to the centroid, ensuring that the cross-section is
- thickened **around its own axis** rather than the global z-axis.

In cases where a vertex coincides with the centroid (resulting in a zero difference), no thickening will be
applied along that axis to avoid division by zero errors.

## Consequences

✅ **Benefits:**

- More accurate thickening for offset features like arms, legs, and hands.
- The transformation adapts to the unique geometry of each narrow cross-section, ensuring uniform thickening.
- Lays the foundation for handling non-vertical limbs in future work.

⚠️ **Trade-offs:**

- **Increased computational complexity:** Calculating centroids and applying localized transformations requires
- more processing than a simple cylindrical thickening.
- **Additional handling for edge cases:** Division by zero and edge cases where vertices align with centroids require
- careful handling.

## Alternatives Considered

1. **Continue with z-axis-based thickening:**
   Rejected, as it cannot accurately thicken offset or angled features.

2. **Use bounding boxes or spheres to detect narrow features:**
   Rejected due to lack of precision compared to centroid-based thickening.

## Decision Makers

Tom Willis
