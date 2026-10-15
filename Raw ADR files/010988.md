# Tile Size Pilot: Decision Documentation

**Date**: 2026-01-07
**Pilot Version**: pilot_tilesize
**Model**: gemini-3-flash-preview

## Summary

The tile size calibration pilot compared detection performance at 256px, 512px, and 1024px tile sizes across 10 stratified regions (3 empty, 4 sparse, 3 dense). Each tile received 5 independent detection passes with spatial voting.

**Decision: Retain 512px tile size** (no change from baseline)

## Results at 2/5 Voting Threshold

| Size | Precision | Recall | F1 | 95% CI |
|------|-----------|--------|------|--------|
| 256px | 0.098 | 0.854 | 0.174 | [0.090-0.264] |
| 512px | 0.151 | 0.736 | 0.245 | [0.077-0.447] |
| 1024px | 0.218 | 0.461 | 0.284 | [0.078-0.479] |

## Decision Rationale

Per the pre-registered decision criteria:

| Comparison | Threshold | Actual Difference | Result |
|------------|-----------|-------------------|--------|
| 256 vs 512 | 256px F1 ≥ 0.05 better → switch | F1 diff = -0.071 | 256px is **worse** |
| 256 vs 512 | Within 0.03 → stay | Outside range | N/A |
| 1024 vs 512 | F1 ≥ 0.10 worse → confirms smaller better | F1 diff = +0.039 | 1024px marginally better |
| 1024 vs 512 | Within 0.05 → consider 1024px | **Within range** | Consider but not switch |

**Findings contrary to hypothesis**: The pilot hypothesised smaller tiles would perform better due to reduced visual clutter. Results show the opposite trend:

- **256px tiles**: Very high recall (0.854) but extremely low precision (0.098). The model detects most mounds but generates many false positives (603 FP at 1/5 threshold).
- **512px tiles**: Balanced performance with reasonable precision-recall trade-off.
- **1024px tiles**: Higher precision but lower recall—fewer false positives but misses more mounds.

## Interpretation

Several factors may explain these results:

1. **Image upscaling**: Gemini upscales images smaller than 768×768 to that minimum. 256px tiles are upscaled 3×, potentially introducing artifacts that degrade discrimination.

2. **Contextual information**: Larger tiles provide more surrounding context, helping the model distinguish mound symbols from similar visual noise.

3. **Symbol density**: With fewer symbols per tile at 256px, the model may over-detect to avoid missing genuine mounds.

4. **Bootstrap uncertainty**: Wide confidence intervals (especially for 512px and 1024px) indicate substantial uncertainty with only 10 regions.

## Decision: Stay with 512px

Given:
- 256px F1 is significantly worse than 512px (-0.071)
- 1024px F1 is only marginally better (+0.039, within noise)
- 512px offers best precision-recall balance at moderate voting thresholds
- 512px avoids the 4× cost increase of 256px tiles with no performance benefit

**512px remains the tile size for the main experiment.**

## Archived Outputs

| File | Description |
|------|-------------|
| `pilot_results.json` | Structured metrics with bootstrapped CIs |
| `pilot_summary.md` | Human-readable summary table |
| `256/detections.json` | Raw detections for 256px tiles |
| `512/detections.json` | Raw detections for 512px tiles |
| `1024/detections.json` | Raw detections for 1024px tiles |

## Reproducibility

- **Random seed**: Recorded in `inputs/pilot/pilot_selection_metadata.json`
- **Total API calls**: 1,050 (210 tiles × 5 passes)
- **Detection timestamp**: 2026-01-07
- **Analysis parameters**: 20m spatial tolerance, 1000 bootstrap iterations

---

*This pilot was conducted as part of pre-registration calibration before committing to the main factorial design.*
