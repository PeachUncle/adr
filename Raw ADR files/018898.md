# Implement Cross-Section Analysis for Targeted Thickening of Thin Areas in Figurine Models

## Status

✅ **Accepted**
**Date:** January 3, 2025
**Decision Maker:** Tom Willis

## Context

Many FDM-printed figurines have **weak areas** in regions like **ankles, legs, arms, and hands**, which
often leads to **failed prints** or **fragile models**. These weak areas typically have
**thin cross-sections**, making them vulnerable during printing. Our current cylindrical
thickening transformation applies a uniform thickening across the entire model, which helps
improve robustness but is **not targeted enough** to address **specific thin areas**.

To improve the printability of these figurines, we need a transformation method that can
**detect and thicken thin areas more precisely**, particularly those **normal to their long axes**.

## Decision

We have decided to implement **Approach 2: Cross-Section Analysis** to identify and thicken
**thin regions** of a figurine model. This approach involves:

1. **Slicing the mesh along the z-axis** at regular intervals to create cross-sections.
2. **Calculating the minimum and maximum radius** for each cross-section to detect **thin regions**.
3. **Applying a targeted thickening transformation** to these regions based on the **radius and offset**
values.

This approach will start by analyzing **vertical cross-sections**, assuming limbs are
**approximately aligned with the z-axis** (e.g., standing figures with arms at the sides).
The method will use **a heuristic to ignore the base** and focus on the actual figurine.

## Rationale

1. **Precision:** This approach will allow us to **identify specific thin areas** rather than
uniformly thickening the entire model.
2. **Efficiency:** It focuses computational resources on **weak areas** that are most prone to failure during
printing.
3. **Modularity:** The cross-section analysis can be easily extended to more complex transformations in the future.

## Alternative Approaches Considered

| Approach                | Description                                      | Why Rejected?                                           |
|-------------------------|--------------------------------------------------|--------------------------------------------------------|
| Global Thickening        | Uniformly thickening the entire model            | Not targeted enough to address specific weak areas.     |
| Manual Region Selection  | Allow users to mark thin areas manually          | Too time-consuming and impractical for general use.     |
| Adaptive Volume Scaling  | Scaling regions based on volume density analysis | More complex and harder to control for specific areas.  |

## Consequences

This decision will result in a more robust **process_thickening** use case by enabling the
**detection of weak areas** based on **cross-section analysis**. This will improve
**print success rates** for FDM-printed figurines and make them **more durable**.

The new functionality will:

- Calculate the **height and radius** of each cross-section.
- Detect cross-sections with **radius below a threshold**.
- Apply thickening transformations to these **thin areas**.

## Future Evolution

While this initial implementation will assume that **limbs are vertical**, the approach can
evolve to handle **limbs at various orientations** by:

1. **Identifying principal axes** of each detected thin region.
2. **Adapting the slicing planes** to be **perpendicular to the limb's axis**.
3. Applying **normal thickening** based on the limb's orientation.

This would allow us to handle **more complex poses**, such as **outstretched arms** or
**figures in action stances**.
