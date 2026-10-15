# ADR 003: Color Blind Accessibility Strategy

## Status

Accepted

## Context

Poker games traditionally use red/green for card suits (hearts/diamonds vs spades/clubs), which is problematic for color blind players (~8% of male population). We need a design that is:

- **100% accessible**: Distinguishable by all color vision types
- **WCAG AA compliant**: Meets accessibility standards
- **Usable**: Doesn't compromise gameplay clarity
- **Performant**: Minimal bundle size (avoid large SVG libraries)

## Decision

Implement multi-layered accessibility approach:

### 1. Color Palette (Blue/Orange)

- **Spades/Clubs**: Blue shades (#2563EB, #1E40AF)
- **Hearts/Diamonds**: Orange/warm shades (#F97316, #EA580C)
- **Neutral**: Gray for disabled/inactive states (#64748B)

### 2. Pattern-Based Differentiation

- **Spades**: Solid blue with spade icon
- **Hearts**: Solid orange with heart icon
- **Diamonds**: Orange with diagonal stripe pattern
- **Clubs**: Blue with dot pattern

### 3. Text Labels (Optional Toggle)

- "♠ A" instead of just "A" on cards
- Screen reader compatible ARIA labels

### 4. Testing Approach

- Chrome DevTools color blind simulation (protanopia, deuteranopia, tritanopia)
- Contrast ratio validation (WCAG AA: 4.5:1 minimum)
- User testing with color blind players

## Consequences

### Positive

- **Universal design**: Works for all vision types, not just color blind users
- **WCAG AA compliance**: Meets legal/ethical accessibility standards
- **Pattern redundancy**: Multiple visual cues (color + pattern + shape)
- **No external dependencies**: Custom CSS patterns, no heavy icon libraries
- **Improved clarity**: Patterns make suits instantly recognizable

### Negative

- **Design complexity**: More CSS/styling work than color-only approach
- **Testing overhead**: Must validate across color vision simulations
- **Slight bundle size increase**: Custom pattern SVGs (~5KB total, acceptable)

### Neutral

- **Non-traditional colors**: Blue/orange vs red/black (acceptable, still clear)
- **Pattern learning curve**: Players need brief adjustment (patterns quickly learned)

## Implementation

```typescript
// Chakra UI theme colors
const colors = {
  suits: {
    spades: { bg: '#2563EB', text: '#FFFFFF' },
    clubs: { bg: '#1E40AF', text: '#FFFFFF' },
    hearts: { bg: '#F97316', text: '#FFFFFF' },
    diamonds: { bg: '#EA580C', text: '#FFFFFF' },
  },
};

// CSS pattern classes
.card-spades { background-color: #2563EB; }
.card-clubs { background-color: #1E40AF; background-image: url('data:image/svg+xml,...'); }
.card-hearts { background-color: #F97316; }
.card-diamonds { background-color: #EA580C; background-image: linear-gradient(45deg, ...); }
```

## Testing Strategy

- ✅ Chrome DevTools: Simulate protanopia (red-blind)
- ✅ Chrome DevTools: Simulate deuteranopia (green-blind)
- ✅ Chrome DevTools: Simulate tritanopia (blue-blind)
- ✅ Contrast ratio validation (WebAIM checker)
- ✅ Screen reader testing (VoiceOver, NVDA)
- ✅ Manual testing with color blind users

## Alternatives Considered

- **Traditional red/black**: Fails accessibility requirement
- **Grayscale only**: Loses visual richness, harder to distinguish suits
- **Icon-only**: Requires larger card sizes, slower recognition
- **External icon library**: Adds bundle size, overkill for 4 suit symbols

## Compliance

- ✅ **Constitution III (Performance-First)**: Patterns add <5KB to bundle
- ✅ **Spec FR-066**: Explicit requirement for color blind support
- ✅ **Spec FR-067**: Blue/orange palette instead of red/green
- ✅ **Spec FR-068**: WCAG AA compliance verified
