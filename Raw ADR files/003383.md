# Animation Framework Decision for Protogen

## Current State
- **Admin**: Uses **Framer Motion** (v12.23.12)
- **Portal**: No animation library currently installed
- **Shared**: Uses `tailwindcss-animate` for basic CSS animations

## Requirements Analysis

### Immediate Needs (Slide System)
- Simple entrance/exit animations (fade, slide, expand)
- Direction-based animations (left, right, top, bottom)
- Duration and easing control
- Lightweight and performant

### Future Needs (Flow System)
- Complex multi-step animations
- Timeline-based sequences
- Interactive animations (drag, gestures)
- Scroll-triggered animations
- Path animations
- Morphing between states

## Options Comparison

### Option 1: Framer Motion (Current Admin Choice)
**Pros:**
- ✅ Already used in Admin (consistency)
- ✅ Excellent React integration (declarative API)
- ✅ Powerful gesture support (drag, tap, hover)
- ✅ Layout animations (automatic size/position transitions)
- ✅ Exit animations work perfectly
- ✅ Spring physics built-in
- ✅ Scroll animations with `motion.viewport`
- ✅ Great TypeScript support
- ✅ Actively maintained
- ✅ 58KB gzipped (reasonable)

**Cons:**
- ❌ Larger bundle size than CSS-only solutions
- ❌ Less control over raw performance tuning
- ❌ Timeline/sequence API less mature than GSAP

**Best for:** React-centric animations, layout transitions, gestures

### Option 2: GSAP (GreenSock Animation Platform)
**Pros:**
- ✅ Industry standard for complex animations
- ✅ Best-in-class timeline and sequencing
- ✅ Massive plugin ecosystem (ScrollTrigger, Draggable, MotionPath, etc.)
- ✅ Raw performance (especially for complex sequences)
- ✅ Framework-agnostic (works everywhere)
- ✅ SVG morphing and path animations
- ✅ Better for non-React code (like canvas/WebGL)
- ✅ Extremely stable and mature

**Cons:**
- ❌ Less "React-like" (imperative API)
- ❌ Exit animations require extra work with React
- ❌ Layout animations need manual calculations
- ❌ Advanced features require paid license (ScrollTrigger, Draggable are free)
- ❌ Can conflict with React's rendering model if not careful

**Best for:** Complex timelines, scroll animations, SVG/canvas work

### Option 3: CSS Animations + React Spring
**Pros:**
- ✅ Lightest bundle size
- ✅ CSS animations are highly performant
- ✅ React Spring for physics-based animations
- ✅ Good for simple transitions

**Cons:**
- ❌ Limited for complex sequences
- ❌ Manual orchestration required
- ❌ Less power for Flow system needs
- ❌ More code to maintain

**Best for:** Simple projects with basic animation needs

### Option 4: Hybrid Approach
Use different tools for different needs:
- **Framer Motion**: Primary tool for React components, slides, UI animations
- **CSS Animations**: Very simple transitions (loading spinners, basic fades)
- **GSAP** (if needed): Complex Flow system sequences, scroll effects, path animations

**Pros:**
- ✅ Best tool for each job
- ✅ Start simple, add complexity as needed
- ✅ Can gradually introduce GSAP only where needed

**Cons:**
- ❌ Multiple APIs to learn
- ❌ Slightly larger total bundle
- ❌ Need to decide which tool for each case

## Recommendation: **Framer Motion (Primary) + GSAP (Strategic)**

### Primary: Framer Motion
Use **Framer Motion** as the primary animation framework for:
- ✅ **Slide animations** (entrance/exit)
- ✅ **UI component animations** (modals, menus, dropdowns)
- ✅ **Layout transitions** (scene switching, panel sliding)
- ✅ **Gesture-based interactions** (drag-to-navigate, swipe)
- ✅ **Navigator transitions** between scenes/contexts
- ✅ **General React component animations**

**Why Framer Motion for slides:**
```typescript
// Declarative and perfect for our slide system
<motion.div
  initial={{ x: '100%', opacity: 0 }}
  animate={{ x: 0, opacity: 1 }}
  exit={{ x: '-100%', opacity: 0 }}
  transition={{ duration: 0.4, ease: 'easeOut' }}
>
  <Slide content={...} />
</motion.div>
```

### Strategic: GSAP (When Needed)
Add **GSAP** later for specific Flow system needs:
- ⏳ **Complex multi-step sequences** (onboarding flows, tutorials)
- ⏳ **Scroll-triggered animations** (parallax, reveal on scroll)
- ⏳ **Path-based animations** (elements moving along curves)
- ⏳ **SVG morphing** (shape transformations)
- ⏳ **Timeline-based presentations** (synchronized animations)

**Why GSAP for Flow:**
```typescript
// Complex timeline sequences
const tl = gsap.timeline();
tl.to('.step1', { x: 100, duration: 0.5 })
  .to('.step2', { scale: 1.5, duration: 0.3 })
  .to('.step3', { rotation: 360, duration: 0.8 }, '-=0.2');
```

## Implementation Plan

### Phase 1: Slide System (NOW)
```bash
# Add Framer Motion to Portal
npm install framer-motion --workspace=portal
```

- Create `SlideAnimator` using Framer Motion
- Implement fade, slide, expand animations
- Use `AnimatePresence` for exit animations
- Keep bundle size reasonable (~58KB)

### Phase 2: Navigator & UI (SOON)
- Use Framer Motion for all Navigator transitions
- Scene-to-scene animations
- Context history panel sliding
- Engagement drawer animations

### Phase 3: Flow System (LATER)
Evaluate if GSAP is needed:
```bash
# Only if complex sequences are required
npm install gsap --workspace=portal
```

- Start with Framer Motion for basic flows
- Add GSAP only if timeline complexity demands it
- Use GSAP's free plugins (ScrollTrigger is free!)

## Bundle Size Impact

### Current Portal Bundle: ~0KB animation
**Adding Framer Motion:** +58KB gzipped
**Adding GSAP (if needed):** +50KB gzipped (core) + plugins

**Acceptable?** Yes. 58KB for Framer Motion is reasonable for the functionality it provides.

### Optimization Strategies
- Tree-shaking (Framer Motion supports it well)
- Lazy load GSAP only when Flow system is accessed
- Use CSS animations for trivial cases (spinners, pulses)
- Code-split animation-heavy features

## API Comparison for Our Slide System

### Framer Motion (Recommended for Slides)
```typescript
// Simple, declarative, perfect for React
<AnimatePresence mode="wait">
  <motion.div
    key={slideIndex}
    initial={{ x: '100%' }}
    animate={{ x: 0 }}
    exit={{ x: '-100%' }}
    transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
  >
    <SlideContent {...slide} />
  </motion.div>
</AnimatePresence>

// Variants for reusability
const slideVariants = {
  enter: (direction: number) => ({ x: direction > 0 ? '100%' : '-100%' }),
  center: { x: 0 },
  exit: (direction: number) => ({ x: direction > 0 ? '-100%' : '100%' })
};
```

### GSAP (Alternative, more imperative)
```typescript
// More manual, requires refs and lifecycle management
const slideRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (slideRef.current) {
    gsap.fromTo(slideRef.current, 
      { x: '100%' },
      { x: 0, duration: 0.4, ease: 'power2.out' }
    );
  }
  
  // Exit animation needs manual handling in React
  return () => {
    gsap.to(slideRef.current, { x: '-100%', duration: 0.3 });
  };
}, [slideIndex]);

<div ref={slideRef}>
  <SlideContent {...slide} />
</div>
```

## Decision Matrix

| Criteria | Framer Motion | GSAP | Hybrid |
|----------|---------------|------|--------|
| React Integration | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Slide Animations | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Complex Timelines | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Bundle Size | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Learning Curve | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Exit Animations | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Gestures | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Scroll Effects | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Total** | **33/40** | **30/40** | **35/40** |

## Final Recommendation

### ✅ Start with Framer Motion
1. **Install Framer Motion in Portal NOW** for Slide System
2. Benefit from consistency with Admin project
3. Excellent developer experience for React
4. Perfectly suited for our slide entrance/exit needs
5. Great for UI animations (modals, panels, drawers)

### ⏳ Add GSAP Later if Needed
1. Evaluate during Flow System development
2. Add only if timeline complexity demands it
3. Use for scroll effects, path animations, complex sequences
4. Free plugins cover most needs (ScrollTrigger!)

### 📦 Keep CSS for Trivial Cases
1. Simple spinners and loading states
2. Hover effects
3. Basic transitions that don't need JavaScript

## Code Example: Slide Animator with Framer Motion

```typescript
// portal/src/systems/scene/SlideAnimator.tsx
import { motion, AnimatePresence, Variants } from 'framer-motion';

interface SlideAnimatorProps {
  slide: Slide;
  direction: 'forward' | 'reverse';
  animation: SlideAnimation;
}

const getSlideVariants = (animation: SlideAnimation, direction: 'forward' | 'reverse'): Variants => {
  const isForward = direction === 'forward';
  
  switch (animation.type) {
    case 'slide': {
      const distance = animation.distance === 'edge' ? '100%' : '50px';
      const enterX = isForward ? distance : `-${distance}`;
      const exitX = isForward ? `-${distance}` : distance;
      
      return {
        enter: { x: enterX, opacity: 0 },
        center: { x: 0, opacity: 1 },
        exit: { x: exitX, opacity: 0 }
      };
    }
    
    case 'fade':
      return {
        enter: { opacity: 0 },
        center: { opacity: 1 },
        exit: { opacity: 0 }
      };
    
    case 'expand':
      return {
        enter: { scale: 0, opacity: 0 },
        center: { scale: 1, opacity: 1 },
        exit: { scale: 0.8, opacity: 0 }
      };
  }
};

export const SlideAnimator: React.FC<SlideAnimatorProps> = ({ 
  slide, 
  direction, 
  animation 
}) => {
  const variants = getSlideVariants(animation, direction);
  
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={slide.id}
        variants={variants}
        initial="enter"
        animate="center"
        exit="exit"
        transition={{
          duration: animation.duration / 1000,
          ease: animation.easing
        }}
      >
        <SlideContent slide={slide} />
      </motion.div>
    </AnimatePresence>
  );
};
```

## Conclusion

**Framer Motion** is the best choice for our immediate needs (Slide System, Navigator, UI animations). It's React-native, declarative, and handles entrance/exit animations beautifully. GSAP can be added later strategically for complex Flow system sequences if needed. This hybrid approach gives us the best of both worlds without over-engineering the initial implementation.

**Action Item:** Install Framer Motion in Portal and implement SlideAnimator using it.

