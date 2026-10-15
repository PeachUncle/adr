# ADR-002: CSS-Only Animation System

**Status**: Approved
**Date**: 2025-12-09
**Deciders**: Development Team
**Context**: Premium UI/UX Enhancement Feature

## Context and Problem Statement

The premium UI/UX enhancement requires smooth, performant animations for:
- Hero section entrance (fade-in + slide-up)
- Feature card hover effects (scale + shadow)
- Scroll-triggered animations (fade-in on viewport entry)
- Button hover transitions (gradient overlays)

We need to choose an animation approach that:
- Achieves 60fps performance
- Respects `prefers-reduced-motion` for accessibility
- Minimizes bundle size
- Integrates well with Tailwind CSS and Docusaurus
- Supports complex orchestrated animations if needed

## Decision Drivers

- **Performance**: Must achieve 60fps on all animations (SC-003)
- **Bundle Size**: Keep total bundle under budget (~60KB total impact)
- **Accessibility**: Must respect `prefers-reduced-motion` media query (FR-007)
- **Developer Experience**: Easy to implement and debug
- **Maintainability**: Clear, understandable animation code

## Considered Options

### Option 1: Framer Motion
Full-featured React animation library with declarative API.

**Pros:**
- Powerful orchestration capabilities
- Built-in gesture support
- Layout animations
- Spring physics
- Excellent TypeScript support

**Cons:**
- **Bundle size**: ~60KB gzipped (entire feature budget)
- Additional JavaScript overhead
- More complex debugging
- Overkill for simple transitions
- Requires learning library-specific API

**Bundle Impact**: +60KB (exceeds budget)

### Option 2: React Spring
Physics-based animation library focused on natural motion.

**Pros:**
- Natural spring animations
- Good performance
- Imperative and declarative APIs

**Cons:**
- **Bundle size**: ~35KB gzipped
- Learning curve for physics-based approach
- More complex than needed for simple transitions
- Still significant bundle impact

**Bundle Impact**: +35KB

### Option 3: Pure CSS Animations (SELECTED)
CSS transitions, keyframe animations, and IntersectionObserver for scroll triggers.

**Pros:**
- **Zero bundle cost** (CSS is already loaded)
- **Best performance**: GPU-accelerated transforms and opacity
- Native `prefers-reduced-motion` support
- Simple to debug (Chrome DevTools Animations panel)
- Works with Tailwind utility classes
- No JavaScript overhead

**Cons:**
- More verbose for complex orchestrated animations
- No built-in spring physics (can approximate with cubic-bezier)
- Requires manual IntersectionObserver for scroll triggers

**Bundle Impact**: 0KB (only CSS)

### Option 4: Tailwind CSS + Headless UI Transitions
Tailwind's animation utilities with Headless UI for enter/exit transitions.

**Pros:**
- Integrates perfectly with Tailwind
- Utility-first approach
- Good for modal/dropdown transitions

**Cons:**
- Headless UI adds ~15KB
- Limited to enter/exit transitions
- Still requires custom CSS for complex animations

**Bundle Impact**: +15KB

## Decision Outcome

**Chosen Option**: Pure CSS Animations with Tailwind Utilities

### Implementation Approach

**1. Tailwind Animation Configuration**
```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      animation: {
        'fade-in': 'fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1)',
        'slide-up': 'slideUp 0.4s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        slideUp: {
          '0%': { transform: 'translateY(40px)' },
          '100%': { transform: 'translateY(0)' }
        }
      },
      transitionDuration: {
        '200': '200ms',  // Buttons
        '300': '300ms',  // Cards
        '600': '600ms',  // Hero
      },
      transitionTimingFunction: {
        'hero': 'cubic-bezier(0.4, 0, 0.2, 1)',
      }
    }
  }
}
```

**2. Accessibility: Prefers-Reduced-Motion**
```css
/* src/css/custom.css */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**3. Performance Optimization**
```css
/* Use only GPU-accelerated properties */
.animated-element {
  will-change: transform, opacity;
  /* Avoid will-change: auto after animation completes */
}

/* Only animate transform and opacity for 60fps */
.hover-effect {
  transition: transform 0.3s ease-in-out,
              opacity 0.3s ease-in-out;
}
```

**4. Scroll Triggers with IntersectionObserver**
```typescript
// src/hooks/useIntersectionObserver.ts
export function useIntersectionObserver(
  elementRef: RefObject<Element>,
  options?: IntersectionObserverInit
) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsVisible(true);
        observer.disconnect(); // Trigger once
      }
    }, options);

    if (elementRef.current) {
      observer.observe(elementRef.current);
    }

    return () => observer.disconnect();
  }, [elementRef, options]);

  return isVisible;
}
```

### Animation Specifications (from plan.md)

| Element | Duration | Easing | Properties |
|---------|----------|--------|------------|
| Buttons | 200ms | ease-out | background, transform |
| Cards | 300ms | ease-in-out | transform, box-shadow |
| Hero | 600ms | cubic-bezier(0.4, 0, 0.2, 1) | opacity, transform |
| Scroll | 400ms | ease-out | opacity, transform |

## Consequences

### Positive Consequences

1. **Zero Bundle Impact**: No additional JavaScript libraries required
2. **Best Performance**: GPU-accelerated CSS animations achieve 60fps easily
3. **Native Accessibility**: `prefers-reduced-motion` works automatically
4. **Simple Debugging**: Chrome DevTools Animations panel shows all animations
5. **Tailwind Integration**: Animation utilities fit naturally with utility-first approach
6. **Maintainability**: CSS animations are well-understood by all developers

### Negative Consequences

1. **Orchestration Complexity**: Complex sequential animations require more code than Framer Motion
2. **Manual Scroll Handling**: Must implement IntersectionObserver hooks manually
3. **No Spring Physics**: Cannot easily create spring-based natural motion (acceptable trade-off)

### Mitigation Strategies

1. **Reusable Hooks**: Create `useIntersectionObserver` and `useAnimatedSection` hooks
2. **Tailwind Utilities**: Define common animations in Tailwind config for reuse
3. **CSS Modules**: Use CSS Modules for component-specific complex animations
4. **Documentation**: Document animation patterns and cubic-bezier values

## Performance Targets (from spec.md)

- ✅ **SC-003**: All animations run at 60fps (verified with Chrome DevTools Performance monitor)
- ✅ **FR-011**: Animations use only transform and opacity (GPU-accelerated)
- ✅ **FR-007**: Respects `prefers-reduced-motion` media query
- ✅ **Bundle Budget**: 0KB impact (within ~60KB total budget)

## Links and References

- [CSS Animations Performance](https://web.dev/animations-guide/)
- [GPU-Accelerated Properties](https://www.html5rocks.com/en/tutorials/speed/high-performance-animations/)
- [prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
- [Cubic-bezier.com](https://cubic-bezier.com/) - Visual easing function tool
- Related ADRs: ADR-001 (Component Architecture), ADR-004 (Performance Testing)
