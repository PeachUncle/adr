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
| 256px | 0.096 | 0.901 | 0.171 | [0.059-0.292] |
| 512px | 0.163 | 0.792 | 0.263 | [0.083-0.469] |
| 1024px | 0.284 | 0.371 | 0.311 | [0.125-0.425] |

**Note**: 1024px tiles were processed with `media_resolution=HIGH` to prevent internal tiling by the Gemini API.

## Decision Rationale

Per the pre-registered decision criteria:

| Comparison | Threshold | Actual Difference | Result |
|------------|-----------|-------------------|--------|
| 256 vs 512 | 256px F1 >= 0.05 better -> switch | F1 diff = -0.092 | 256px is **worse** |
| 256 vs 512 | Within 0.03 -> stay | Outside range | N/A |
| 1024 vs 512 | F1 >= 0.10 worse -> confirms smaller better | F1 diff = +0.048 | 1024px marginally better |
| 1024 vs 512 | Within 0.05 -> consider 1024px | Within range | Consider 1024px |

**Findings contrary to hypothesis**: The pilot hypothesised smaller tiles would perform better due to reduced visual clutter. Results show the opposite trend:

- **256px tiles**: Very high recall (0.901) but extremely low precision (0.096). The model detects most mounds but generates many false positives (556 FP at 1/5 threshold).
- **512px tiles**: Balanced performance with reasonable precision-recall trade-off.
- **1024px tiles**: Higher precision (0.284) but substantially lower recall (0.371)—fewer false positives but misses ~63% of mounds.

## Interpretation

Several factors may explain these results:

1. **Internal tiling**: By default, Gemini tiles images larger than 384px into 768x768 patches. For 1024px tiles, this creates 4 internal patches that are processed separately, potentially losing spatial context at patch boundaries. We mitigated this with `media_resolution=HIGH` which processes the full image at native resolution.

2. **Contextual information**: Larger tiles provide more surrounding context, helping the model distinguish mound symbols from similar visual noise. However, this comes at a cost of recall—the model may miss symbols when presented with more competing visual information.

3. **Symbol density**: With fewer symbols per tile at 256px, the model may over-detect to avoid missing genuine mounds, inflating false positives.

4. **Recall vs precision trade-off**: For archaeological survey, high recall is often preferred (better to investigate false positives than miss genuine sites). The severe recall drop at 1024px (0.371 vs 0.792 at 512px) makes it unsuitable despite higher precision.

5. **Bootstrap uncertainty**: Wide confidence intervals indicate substantial uncertainty with only 10 regions. The true performance difference between sizes may differ from point estimates.

## Decision: Stay with 512px

Given:
- 256px F1 is significantly worse than 512px (-0.092)
- 1024px F1 is marginally better (+0.048), within the "consider 1024px" range, but with unacceptably low recall (0.371)
- 512px offers best precision-recall balance for archaeological survey goals
- 512px avoids the 4x cost increase of 256px tiles with no performance benefit

**512px remains the tile size for the main experiment.**

## Archived Outputs

| File | Description |
|------|-------------|
| `pilot_results.json` | Structured metrics with bootstrapped CIs |
| `pilot_summary.md` | Human-readable summary table |
| `256/detections.json` | Raw detections for 256px tiles |
| `512/detections.json` | Raw detections for 512px tiles |
| `1024/detections.json` | Raw detections for 1024px tiles (media_resolution=HIGH) |

## Reproducibility

- **Random seed**: Recorded in `inputs/pilot/pilot_selection_metadata.json`
- **Total API calls**: 1,050 (210 tiles × 5 passes)
- **Detection timestamp**: 2026-01-07
- **Analysis script**: `analyze_pilot_results.py` v1.2.0 (region-level pooling)
- **Analysis parameters**: 20m spatial tolerance, 1000 bootstrap iterations
- **Pooling methodology**: Region-level pooling with within-pass deduplication (corrects for tile boundary artifacts)
- **Ground truth**: Reference region from 1024px tiles, filtered to 48px margins (19 mounds)
- **API configuration**: v1alpha endpoint with `media_resolution=HIGH` for 1024px tiles

---

*This pilot was conducted as part of pre-registration calibration before committing to the main factorial design.*
