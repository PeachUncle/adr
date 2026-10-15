# ADR-0003: UI Component Consolidation

## Status
Accepted

## Date
2026-01-02

## Context

The SUTEL Nexus project accumulated multiple Card and Button component variants over time, leading to:

- **6 Card variants**: `Card`, `GlassCard`, `EnhancedCard`, `ModernCard`, `NexusCard`, `ProfessionalCard`
- **4 Button variants**: `Button`, `ModernButton`, `LoadingButton`, `FloatingActionButton`
- **CSS magic values**: 817 occurrences of `white/5`, `white/10`, etc. across 47 files
- **Limited ARIA**: ~90 aria attributes project-wide (insufficient for this app size)

This fragmentation caused:
- Inconsistent visual appearance
- Developer confusion about which component to use
- Difficult maintenance and design token updates
- Accessibility gaps

## Decision

### Phase 1: Unified Card Component

Create `src/components/ui/unified-card.tsx` that consolidates all Card variants through props:

```typescript
interface UnifiedCardProps {
  variant?: \"default\" | \"glass\" | \"glass-strong\" | \"glass-subtle\" | 
            \"enhanced\" | \"modern\" | \"gradient\" | \"elevated\" | 
            \"minimal\" | \"nexus\" | \"nexus-flat\" | \"professional\" | \"featured\";
  hover?: \"none\" | \"subtle\" | \"lift\" | \"glow\" | \"scale\";
  padding?: \"none\" | \"sm\" | \"md\" | \"lg\";
  blur?: \"none\" | \"sm\" | \"md\" | \"lg\" | \"xl\";
  shadow?: \"none\" | \"sm\" | \"md\" | \"lg\" | \"dramatic\";
  border?: boolean;
  interactive?: boolean;
}
```

**Migration strategy:**
- Keep original components as deprecated aliases during transition
- New code should use `UnifiedCard` with appropriate variant
- Gradually migrate existing usages file-by-file

### Phase 2: Button Loading Prop

Extend base `Button` component with `loading` and `loadingText` props:

```typescript
interface ButtonProps {
  loading?: boolean;
  loadingText?: string;
  // ... existing props
}
```

This absorbs `LoadingButton` functionality into the base component.

**Keep separate:**
- `ModernButton`: Widely used (33 files), distinct animation style
- `FloatingActionButton`: Specialized positioning/expansion behavior

### Phase 3: Semantic CSS Overlay Tokens

Add utility classes in `nexus-utilities.css` to replace magic values:

| Old Pattern | New Class |
|-------------|-----------|
| `bg-white/5` | `bg-overlay-light` |
| `bg-white/10` | `bg-overlay-medium` |
| `border-white/10` | `border-overlay-light` |
| `text-white/50` | `text-overlay-muted` |

### Phase 4: ARIA Improvements

Add `aria-label` to all icon-only buttons:
- Close buttons (X)
- Navigation buttons
- Action buttons (Edit, Delete, etc.)
- FAB buttons

Add semantic roles:
- `role=\"region\"` on data tables
- `aria-sort` on sortable columns
- `aria-haspopup` on dropdown triggers
- `aria-expanded` on expandable elements

## Consequences

### Positive
- Single source of truth for Card styling
- Easier onboarding for new developers
- Consistent visual appearance
- Better accessibility (target: 140+ ARIA attributes)
- Easier design system updates

### Negative
- Migration effort for existing usages
- Potential for subtle visual differences during transition
- Need to maintain deprecated aliases temporarily

### Risks
- **Visual regression**: Mitigated by keeping exact same CSS classes in variant styles
- **Import breakage**: Mitigated by deprecated alias exports
- **Performance**: No impact expected (consolidation, not addition)

## Files Changed

### New Files
- `src/components/ui/unified-card.tsx`
- `docs/adr/0003-ui-consolidation.md`

### Modified Files
- `src/components/ui/button.tsx` - Added `loading` prop
- `src/styles/nexus-utilities.css` - Added overlay utilities
- `src/components/ui/floating-action-button.tsx` - Added ARIA
- `src/components/layout/ModernHeader.tsx` - Added ARIA
- `src/components/system/ModernDataTable.tsx` - Added ARIA

### Deprecated (not deleted)
- `src/components/ui/glass-card.tsx` → Use `UnifiedCard variant=\"glass\"`
- `src/components/ui/enhanced-card.tsx` → Use `UnifiedCard variant=\"enhanced\"`
- `src/components/ui/loading-button.tsx` → Use `Button loading`

## Migration Guide

### Cards

```tsx
// Before
import { GlassCard } from "@/components/ui/glass-card";
<GlassCard variant=\"strong\">...</GlassCard>

// After
import { UnifiedCard } from "@/components/ui/unified-card";
<UnifiedCard variant=\"glass-strong\">...</UnifiedCard>
```

### Buttons

```tsx
// Before
import { LoadingButton } from "@/components/ui/loading-button";
<LoadingButton loading={isLoading}>Submit</LoadingButton>

// After
import { Button } from "@/components/ui/button";
<Button loading={isLoading}>Submit</Button>
```

### CSS Overlays

```tsx
// Before
className=\"bg-white/10 border-white/5\"

// After
className=\"bg-overlay-medium border-overlay-subtle\"
```

## Verification

- [ ] All UnifiedCard variants render correctly
- [ ] Button loading state works as expected
- [ ] No visual regressions on key pages
- [ ] ARIA attributes increase to 140+
- [ ] Lighthouse accessibility score maintained/improved
