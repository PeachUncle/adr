# ADR-001: Framer Motion as Primary Animation Driver

**Status**: Accepted

**Date**: 2024-2025 (retroactive documentation)

## Context

The Animation Catalog project needed a robust animation library to power hundreds of diverse animation components. Key requirements included:

- **Declarative API**: Easy to learn and maintain
- **Performance**: Smooth 60fps animations with hardware acceleration
- **Flexibility**: Support for complex animations, gestures, and transitions
- **TypeScript Support**: Strong typing for better DX
- **Bundle Size**: Reasonable overhead for production
- **Ecosystem**: Good documentation and community support

Alternatives considered:
1. **React Spring**: Physics-based animations, good performance
2. **GSAP**: Industry-standard, powerful but requires license for commercial use
3. **CSS Animations + React Transition Group**: Native performance but limited flexibility
4. **Framer Motion**: Declarative, powerful, excellent DX

## Decision

We chose **Framer Motion** as the primary animation driver for the following reasons:

1. **Declarative React-First API**: Components like `<motion.div>` integrate naturally with React patterns
2. **Variants System**: Allows defining animation states declaratively, making complex orchestrations manageable
3. **Layout Animations**: Built-in support for animating layout changes (layoutId, layout prop)
4. **Gesture Support**: Drag, hover, tap, and pan gestures built-in
5. **TypeScript First**: Excellent type definitions out of the box
6. **Performance**: Automatic GPU acceleration and optimization
7. **MIT License**: No licensing concerns for commercial use
8. **Active Maintenance**: Regular updates and strong community

## Consequences

### Positive

- **Developer Velocity**: Fast iteration on animations with declarative syntax
- **Consistency**: Variants and motion tokens ensure consistent animation patterns
- **Maintainability**: Easier to understand and modify animations
- **Bundle Size**: ~30KB gzipped is acceptable for the value provided
- **Future-Proof**: Can leverage new Framer Motion features (e.g., scroll-triggered animations)

### Negative

- **Bundle Overhead**: All components include Framer Motion (~30KB)
- **Learning Curve**: Team needs to learn Framer Motion patterns
- **Performance Edge Cases**: Some complex animations may need optimization
- **Vendor Lock-in**: Migrating to another library would be significant work

### Mitigation Strategies

1. **Code Splitting**: Load animation groups on demand to reduce initial bundle
2. **Motion Tokens**: Centralize animation configs in `src/motion/tokens.ts` for consistency
3. **Performance Monitoring**: Profile animations with React DevTools and Chrome DevTools
4. **Fallbacks**: Provide CSS-based fallbacks for critical animations if needed

## Alternatives Not Chosen

### React Spring
- **Pros**: Physics-based animations, smaller bundle
- **Cons**: More imperative API, less intuitive for layout animations

### GSAP
- **Pros**: Most powerful, industry-standard
- **Cons**: Licensing for commercial use, less React-idiomatic

### CSS Animations
- **Pros**: Native performance, zero JS overhead
- **Cons**: Limited flexibility, hard to orchestrate complex sequences

## Notes

- We also maintain CSS-based versions of some animations for comparison
- Framer Motion v10+ uses lazy loading which improves initial bundle size
- Consider React Spring for specific physics-based effects if needed

## References

- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Performance Comparison](https://github.com/framer/motion/discussions)
- `docs/meta/animation-guide.md` - Our internal animation patterns
