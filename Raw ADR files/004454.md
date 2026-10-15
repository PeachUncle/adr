# ADR 0005 — Branding Placeholders and Amendment Process

**Date:** 2024-12-04  
**Status:** accepted

## Context

Ursine Arcana requires visual branding (logo, colors, typography) for the mobile app and admin dashboard. Final branding assets are not yet available. Development must proceed with placeholders that can be systematically replaced.

## Decision

### 1. Placeholder Assets

| Asset           | Placeholder                             | Location                  |
| --------------- | --------------------------------------- | ------------------------- |
| Logo (full)     | Text: "URSINE ARCANA" in system font    | `/assets/images/logo.png` |
| Logo (icon)     | Text: "UA" in circle                    | `/assets/images/icon.png` |
| Primary Color   | `#6B7280` (gray-500)                    | `tailwind.config.js`      |
| Secondary Color | `#3B82F6` (blue-500)                    | `tailwind.config.js`      |
| Accent Color    | `#8B5CF6` (violet-500)                  | `tailwind.config.js`      |
| Background      | `#111827` (gray-900)                    | `tailwind.config.js`      |
| Typography      | System default (San Francisco / Roboto) | `tailwind.config.js`      |

### 2. Centralized Theme Configuration

All branding values will be centralized in:

- `packages/shared/src/theme/colors.ts` — Color palette
- `packages/shared/src/theme/typography.ts` — Font configuration
- `apps/mobile/tailwind.config.js` — Tailwind theme extension
- `apps/admin/tailwind.config.js` — Tailwind theme extension

### 3. Amendment Process

When final branding is provided:

1. **Create ADR 0005-A**: Document final branding decisions
2. **Update theme files**: Replace placeholder values in centralized locations
3. **Replace assets**: Swap placeholder images in `/assets/images/`
4. **Generate app icons**: Use final logo to generate iOS/Android icons
5. **Update splash screen**: Replace placeholder splash
6. **Review PR**: Design review before merge
7. **Update ADR 0005**: Mark as superseded by ADR 0005-A

### 4. Asset Requirements (for future)

When providing final branding, the following are needed:

- Logo (SVG, PNG @1x, @2x, @3x)
- App icon (1024x1024 PNG, no transparency)
- Color palette (hex values for primary, secondary, accent, backgrounds)
- Typography (font files or Google Fonts names)
- Splash screen design

## Consequences

**Positive:**

- Development can proceed without final branding
- Single source of truth for theme values
- Clear process for branding updates
- No hardcoded colors/fonts scattered in codebase

**Negative:**

- Placeholder UI may not reflect final aesthetic
- Some design decisions may need revision post-branding

**Mitigations:**

- Use neutral placeholders that work with any color scheme
- Avoid design patterns that depend on specific brand colors
