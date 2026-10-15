## Context
The current site is a static HTML/CSS/JS marketing page that already ships Anime.js via CDN and uses it for hover and section animations in combination with IntersectionObserver and CSS transitions.

The goal is to evolve the visuals and motion to an Apple-like glassy minimal aesthetic (upgraded) while keeping:
- Performance predictable (mobile-friendly).
- Accessibility strong (reduced motion, focus states, readable contrast).
- Maintenance manageable (less ad-hoc JS/CSS).

## Goals / Non-Goals
### Goals
- A cohesive motion language across the site (durations, easings, patterns).
- A cohesive visual language (gradients, glow, glass surfaces, accents).
- Centralized motion control:
  - One place to initialize motion.
  - One place to detect/handle reduced motion.
  - Avoid duplicate event listeners.
- Use Anime.js where it adds value (timelines, stagger, complex sequences), and prefer CSS for simple state transitions.

### Non-Goals
- Introducing a build step, bundler, or framework.
- Heavy GPU/CPU effects (e.g., WebGL backgrounds) unless explicitly approved.
- Changing copy/SEO schema as part of the motion refactor.

## Key Decisions
### Decision: Keep Anime.js via CDN and treat it as an optional enhancement
- Reason: Matches current architecture and constraints.
- Behavior: All animations must have a CSS-only or “no motion” fallback.

### Decision: Introduce a small motion controller abstraction in `js/main.js`
The controller is a pattern (not a framework) to:
- Own all observers/listeners.
- Provide helpers for:
  - `reveal()` animations (scroll-triggered)
  - `stagger()` sequences (Anime.js `stagger`)
  - `hover()` micro-interactions (enter/leave)
  - `loop()` decorative loops (bounded and cancelable)
- Provide cleanup hooks:
  - Use `anime.remove(targets)` to stop/remove animations when needed.

### Decision: Standardize motion tokens
- CSS custom properties for durations/easings.
- A mapping of tokens to Anime.js easing strings.

### Decision: Reduced motion as a first-class constraint
- CSS already contains a `prefers-reduced-motion: reduce` override.
- JS should also detect reduced motion (`matchMedia`) and avoid:
  - Parallax
  - Looping decorative animations
  - Large transforms

### Decision: Fix parallax architecture
Current design risk: parallax registers scroll handlers repeatedly.
Proposed pattern:
- A single scroll listener with `passive: true`.
- Use `requestAnimationFrame` to batch DOM writes.
- Ensure parallax is disabled under reduced motion.

### Decision: Allow subtle decorative background motion as progressive enhancement
- Decorative background motion (e.g., gentle gradient/glow movement) is allowed on the landing page.
- It MUST be subtle, bounded, and disabled under reduced motion.

### Decision: Keep legal pages mostly static
- Legal pages under `pages/` remain primarily static content.
- Only shared base styles (typography, spacing, header/footer consistency) should be aligned as needed.
- Avoid adding scroll-triggered animations, parallax, or looping decorative motion to legal pages.

## Risks / Trade-offs
- More structure in JS may feel like “overhead,” but it reduces long-term complexity.
- Visual refresh risks unintended brand drift; require review checkpoints.
- More motion can harm performance if not bounded; enforce a motion/perf budget.

## Migration Plan
- Phase 1: Establish tokens + reduced-motion gating + fix parallax listener duplication.
- Phase 2: Refactor existing section animations into controller patterns.
- Phase 3: Visual refresh pass (gradients/glow/section transitions) with regression checks.
- Phase 4: Polish micro-interactions + QA across browsers.

## Open Questions
- None.
