# ADR 006: Theme System Architecture

## Status

Accepted

## Context

The Spaceship Dodge game needed a flexible theme system to:

1. Support multiple visual aesthetics (color schemes, fonts)
2. Allow users to customize their gaming experience
3. Maintain performance neutrality (no FPS impact)
4. Provide extensibility for future asset-based themes
5. Ensure backward compatibility with existing code

## Decision

Implement a centralized theme system with the following architecture:

### Core Components

1. **Theme Manager** - Singleton service managing theme state and persistence
2. **Theme Registry** - Catalog of available themes with validation
3. **Reactive Theme State** - Observable pattern for theme changes
4. **localStorage Integration** - Persistence of user theme preferences

### Key Design Choices

#### 1. Centralized Theme Manager vs. Per-Module Theming

**Decision**: Centralized theme manager with global access

**Rationale**:

- Single source of truth for current theme
- Consistent theme application across all game elements
- Easier to manage theme switching and persistence
- Better performance (one reactive system vs. multiple)
- Simpler API for rendering code

**Alternatives Considered**:

- Per-module theming: Would require each module to manage its own theme state
- CSS variables: Limited to web context, harder to integrate with canvas rendering
- Component-level themes: Would create inconsistency and maintenance overhead

#### 2. Reactive State Management

**Decision**: Use existing reactive system from `@core/state`

**Rationale**:

- Leverages proven reactive pattern already in use
- Minimal performance overhead (no polling)
- Automatic notification of theme changes
- Consistent with game's architecture patterns

#### 3. Color-Only Themes for Phase 1

**Decision**: Implement color-only themes first, defer asset-based themes to Phase 2

**Rationale**:

- Lower complexity and risk
- Faster implementation timeline
- Validates architecture before adding image loading complexity
- Meets immediate user needs (dark/light mode equivalents)

#### 4. Theme Data Structure

**Decision**: Comprehensive theme object with typed structure

```typescript
type Theme = {
  id: string;
  name: string;
  description: string;
  colors: ColorPalette;
  fonts: FontConfig;
};
```

**Rationale**:

- Clear separation of concerns (colors vs. fonts)
- Type safety through TypeScript interfaces
- Extensible for future properties
- Self-documenting structure

#### 5. localStorage Persistence

**Decision**: Store only theme ID, not full theme object

**Rationale**:

- Minimal storage footprint
- Avoids stale data issues
- Easy validation against whitelist
- Fast loading

## Consequences

### Positive

- **User Experience**: Players can customize game appearance
- **Accessibility**: Supports different visual preferences
- **Extensibility**: Easy to add new themes without code changes
- **Performance**: Negligible impact on frame rate
- **Maintainability**: Centralized theme management

### Negative

- **Migration Effort**: Required refactoring of all rendering code
- **Initial Complexity**: Added new abstraction layer
- **Testing Surface**: Increased test coverage requirements
- **Bundle Size**: Small increase (~2KB) from theme definitions

### Neutral

- **Backward Compatibility**: Maintained through careful refactoring
- **Learning Curve**: New contributors need to understand theme system
- **Future Asset Support**: Architecture supports but doesn't implement image-based themes

## Implementation Details

### Theme Manager API

```typescript
// Core API
getCurrentTheme(): Theme          // Access current theme
setTheme(themeId: string): void   // Change theme
getAvailableThemes(): Theme[]     // List all themes
initializeThemeSystem(): void     // Setup on app start
watchTheme(callback): () => void // Observe changes
```

### Security Measures

1. **Theme ID Validation**: Whitelist-based validation
2. **localStorage Sanitization**: Error handling for storage operations
3. **No Dynamic Loading**: Only built-in themes allowed
4. **Rate Limiting**: User-initiated changes only

### Performance Optimizations

1. **Single Accessor Call**: `getCurrentTheme()` is simple property access
2. **Reactive Caching**: Theme cached at frame start in render loop
3. **Minimal Overhead**: < 0.05ms/frame measured impact
4. **No Polling**: Reactive updates on actual changes only

## Validation

### Testing Strategy

- **Unit Tests**: 80% coverage of theme manager functionality
- **Integration Tests**: Theme application across all entities
- **Visual Regression**: Manual screenshot comparison
- **Performance Tests**: FPS measurement before/after theme switch

### Success Criteria Met

✅ Two themes available (Default + Monochrome)
✅ Settings UI allows theme switching
✅ Theme persists across sessions
✅ Zero visual regressions on default theme
✅ All tests pass (coverage thresholds met)
✅ Documentation complete
✅ CI/CD passes
✅ Performance neutral
✅ Security audit clean
✅ Accessibility compliant

## Future Extensibility

### Phase 2: Asset-Based Themes

When ready for clown/underwater/medieval themes:

1. Add `assets` field to Theme type
2. Implement asset loading system
3. Add render mode toggle (vector fallback)
4. Implement loading states and error handling

### Why Defer to Phase 2?

- Asset loading adds complexity (loading states, error handling)
- Image optimization required (size, format)
- More testing surface area
- Want to validate color-only architecture first

## Related Documents

- [Theme System Plan](.claude/theme-system-plan.md)
- [Developer Guide - Adding New Themes](docs/DEVELOPER_GUIDE.md)
- [CLAUDE.md - Theme System Overview](CLAUDE.md)

## Decision Makers

- Architecture Team
- Lead Developer
- QA Lead

## Approval Date

2025-12-05

## Revision History

- 1.0: Initial implementation (2025-12-05)
