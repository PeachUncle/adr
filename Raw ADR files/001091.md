# Decision: Media Studio Preset System Architecture

**Date:** 2025-12-02  
**Status:** Approved  
**Context:** Block 9 – Media Studio Advanced Features

## Decision Summary

Implement a **two-tier selection system** for Media Studio:

1. **Model Selection** — Direct provider choice (gemini-3-image-pro, imagen-4, gpt-image-1, veo-3, veo-3.1)
2. **Preset Selection** — One-click food photography configurations

## Context

The Media Studio previously offered basic model selection without context-specific presets. Users needed to:

- Manually select models
- Configure aspect ratios
- Write detailed prompts for food photography styles
- Trial-and-error to find optimal settings

This created friction for non-technical users and slowed down content creation workflows.

## Requirements

1. **Transparency:** Show all available models, even if not configured
2. **Education:** Help users understand model strengths
3. **Speed:** Enable one-click configuration for common scenarios
4. **Flexibility:** Allow manual override of preset selections
5. **Brand Alignment:** Showcase Na'Vi Blue and June Six signature styles

## Options Considered

### Option A: Preset-Only System

- **Pros:** Simplest UX, fastest selection
- **Cons:** Limited flexibility, hides model details

### Option B: Model-Only System with Advanced Prompts

- **Pros:** Maximum control
- **Cons:** High friction, requires expertise

### Option C: Two-Tier System (SELECTED) ✅

- **Pros:** Balances speed and flexibility, educational, scalable
- **Cons:** More complex UI (mitigated with good design)

## Decision

### Implement Option C: Two-Tier Model + Preset System

### Model Selector Design

- Display all 5 advanced models (3 image, 2 video)
- Show metadata: label, description, strength badges
- Indicate availability with Lock icon for unconfigured models
- Allow direct selection when configured

### Preset Selector Design

- 10 curated food photography presets
- Each preset bundles: model + aspect ratio + detail level + style hints
- Grid layout with icons and descriptions
- Active state highlighting

### Preset → Model Mapping Logic

```typescript
onPresetSelect(preset) {
  setModel(preset.modelId);
  setAspectRatio(preset.params.aspectRatio);
  setDetailLevel(preset.params.detailLevel);
  appendStyleHints(preset.params.styleHints);
}
```

## Preset Categories

### Light Photography

1. **Michelin Star Plating** — Studio lighting, precision, elegant
2. **Bright Daylight Social** — Natural sunlight, vibrant, Instagram-ready
3. **Overhead Minimalist** — Soft shadow, clean, balanced

### Dark Photography (Brand Signature)

1. **Dark Food – Na'Vi Blue** — Moody dark + blue accents
2. **Dark Food Premium** — Low-key fine dining, dramatic shadows
3. **Na'Vi Blue Accent** — Signature June Six style
4. **Fine Dining Macro (Dark)** — Macro precision + soft spotlight

### Atmosphere Photography

1. **Rustic Bistro Table** — Warm wood textures, cozy
2. **Rustic Warm Night** — Evening lighting, cinematic
3. **Bar Amber Night** — Amber light, high contrast

## Aspect Ratio Strategy

- **1:1** — Instagram feed, menu items
- **4:5** — Instagram portrait, most presets
- **9:16** — Instagram Stories/Reels
- **16:9** — Landscape, presentations

## Implementation Details

### Files Created

- `MediaModelSelector.tsx` (enhanced)
- `MediaPresetSelector.tsx` (new)

### Dependencies

- Backend: `/api/media/models` for availability
- Frontend: Premium Dark design tokens

### State Management

- Parent component holds model and preset selections
- Preset selection updates model and parameters
- Model selection independent of presets

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Presets don't match user expectations | Iterative feedback; easy to add/modify presets |
| Model availability changes | Dynamic fetching from backend; show Lock icon |
| Too many presets overwhelm users | Start with 10; add categories if we expand to 20+ |
| Preset params become outdated | Version presets; allow overrides |

## Success Metrics

- ✅ Reduced time to first generation (target: <30s)
- ✅ Increased preset usage vs manual configuration
- ✅ Higher satisfaction scores for food photography
- ✅ Lower support requests about model selection

## Future Enhancements

1. **Custom Presets:** Allow users to save their own configurations
2. **Preset Recommendations:** Suggest presets based on prompt analysis
3. **Preset Analytics:** Track which presets are most effective
4. **Batch Processing:** Apply preset to multiple generations
5. **Preset Sharing:** Export/import preset configurations

## References

- `BLOCK_9_MEDIA_STUDIO_PLAN.md` — Implementation plan
- `UI_SPEC_v2.2.md` — Design tokens
- `FOODFRAME_DESIGN_v3.0.md` — Brand guidelines

---

**Decision Owner:** Antigravity  
**Stakeholders:** Chef's Mind AI Team, FoodFrame Agent  
**Review Status:** Pending user validation
