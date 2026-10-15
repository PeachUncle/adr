# ADR-0004: UI Component Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "UI Component Strategy" includes component library, accessibility approach, animation system).

- **Status:** Accepted
- **Date:** 2025-12-11
- **Feature:** 001-phase-2-web-app
- **Context:** Phase 2 requires a modern, accessible, and visually polished UI that works on mobile (320px+) and desktop. The UI must be built rapidly (hackathon timeline) while maintaining high quality (WCAG 2.1 Level AA compliance). The application needs both functional components (buttons, forms, dialogs) and visual effects (landing page animations) to differentiate from standard CRUD apps. Components must integrate with Tailwind CSS and support both light/dark themes.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines component architecture and accessibility approach
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Material-UI, Chakra UI, Headless UI evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all UI development, theming, and accessibility
-->

## Decision

We will adopt the following integrated UI component strategy:

- **Base Component Library:** Shadcn/ui (copy-paste components built on Radix UI primitives)
- **Visual Effects Library:** Aceternity UI (landing page animations and effects)
- **Accessibility Primitives:** Radix UI (WCAG 2.1 compliant, keyboard navigation, ARIA attributes)
- **Animation System:** Framer Motion 11+ (for micro-interactions and transitions)
- **Form Handling:** React Hook Form + Zod validation
- **Styling:** Tailwind CSS 4.0 (utility-first, configured for theme variables)
- **Icons:** Lucide React (consistent icon set)
- **Theme System:** CSS variables for light/dark mode switching

### Component Approach

- **Shadcn/ui Philosophy:** Components are copied into `src/components/ui/` rather than installed as NPM dependencies. This gives full control over component code, styling, and behavior. Components can be customized without ejecting or forking.
- **Aceternity UI Purpose:** Provides high-impact visual effects (background beams, text generation, moving borders) for the landing page to create a modern, premium feel. Used sparingly to avoid performance impact.
- **Radix UI Foundation:** Both Shadcn/ui and our custom components use Radix UI primitives (Dialog, Popover, Dropdown) for accessible, unstyled building blocks that handle keyboard navigation, focus management, and screen readers.

### Installation Pattern

```bash
# Install Shadcn/ui components (copies files to project)
npx shadcn@latest init
npx shadcn@latest add button card input checkbox dialog

# Install Aceternity UI manually (copy from documentation)
# Components: background-beams, text-generate-effect, moving-border
```

### Rationale

Shadcn/ui strikes a balance between rapid development (pre-built components) and full control (copy-paste, not NPM). Radix UI provides battle-tested accessibility, eliminating the need to implement keyboard navigation and ARIA attributes manually. Aceternity UI differentiates the landing page visually without adding complexity to functional pages. This strategy aligns with the "Modern UI/UX Standards" constitutional principle while maintaining performance (<1.5s FCP target).

## Consequences

### Positive

- **Full Control:** Copy-paste components mean we can modify any behavior without fighting a library
- **Zero Lock-in:** Components are just TypeScript files in our codebase, no vendor dependency
- **Accessibility by Default:** Radix UI handles WCAG compliance, keyboard navigation, and focus management
- **Tailwind Integration:** Components use Tailwind classes, enabling consistent theming and easy customization
- **Small Bundle Size:** Only the components we use are included (no tree-shaking required)
- **Type Safety:** All components are TypeScript-first with proper prop types
- **Theme Flexibility:** CSS variables allow runtime theme switching (light/dark mode)
- **Visual Differentiation:** Aceternity UI effects create a modern, premium feel for landing page
- **Rapid Development:** Pre-built components accelerate development without sacrificing quality
- **Consistency:** Shadcn/ui components share consistent patterns (variants, sizes, states)

### Negative

- **Manual Updates:** Component updates require manually copying new versions (not `npm update`)
  - *Mitigation:* Shadcn/ui components are stable; updates are rare and documented clearly
- **Component Duplication:** Each project copies the same components (not shared via NPM)
  - *Mitigation:* This is intentional; gives each project control without shared dependency hell
- **Aceternity Learning Curve:** Complex animation components require understanding Framer Motion and Tailwind
  - *Mitigation:* Used only on landing page; functional pages use simpler Shadcn/ui components
- **Bundle Size (Framer Motion):** Adds ~30KB gzipped for animations
  - *Mitigation:* Code-split landing page animations; acceptable for Phase 2 scope
- **Customization Overhead:** Changing component behavior requires editing local files (not config)
  - *Mitigation:* This is a feature, not a bug; prevents hidden config complexity

## Alternatives Considered

### Alternative A: Material-UI (MUI)
- **Pros:** Comprehensive component library, mature ecosystem, enterprise-proven
- **Cons:** Heavy bundle size (100KB+ gzipped), opinionated Material Design style, harder to customize, NPM dependency
- **Why Rejected:** Material Design aesthetic conflicts with our modern, minimal design; bundle size threatens <1.5s FCP target; customization requires fighting MUI's styling system (JSS/Emotion).

### Alternative B: Chakra UI
- **Pros:** Good accessibility, built-in dark mode, composable components
- **Cons:** NPM dependency (lock-in), less customization flexibility, styled-components runtime overhead
- **Why Rejected:** Chakra uses Emotion (CSS-in-JS) which adds runtime overhead; Tailwind is faster and more flexible. Chakra's component API is opinionated, making deep customization harder than Shadcn/ui's copy-paste approach.

### Alternative C: Headless UI (Tailwind Labs)
- **Pros:** Minimal, fully unstyled, Tailwind-first, from Tailwind team
- **Cons:** Lower-level primitives (more work to build complete components), no pre-styled components, requires writing more CSS
- **Why Rejected:** Headless UI is closer to Radix UI (primitives) than Shadcn/ui (complete components). For a hackathon timeline, pre-styled Shadcn/ui components accelerate development while still using accessible primitives (Radix) under the hood.

### Alternative D: Custom Components (No Library)
- **Pros:** Complete control, zero dependencies, smallest possible bundle
- **Cons:** Requires building buttons, dialogs, dropdowns from scratch; hard to get accessibility right; massive time investment
- **Why Rejected:** Violates "don't reinvent the wheel" principle; building accessible components (keyboard nav, ARIA, focus management) is complex and error-prone. Shadcn/ui + Radix UI provide accessibility for free.

### Animation Alternative: React Spring
- **Pros:** Physics-based animations, smaller bundle than Framer Motion
- **Cons:** Steeper learning curve, less intuitive API, smaller community
- **Why Rejected:** Framer Motion has better TypeScript support, clearer API, and larger community. React Spring's physics-based approach is overkill for our simple micro-interactions.

## References

- Feature Spec: [specs/001-phase-2-web-app/spec.md](../../specs/001-phase-2-web-app/spec.md)
- Implementation Plan: [specs/001-phase-2-web-app/plan.md](../../specs/001-phase-2-web-app/plan.md)
- Research Notes: [specs/001-phase-2-web-app/research.md](../../specs/001-phase-2-web-app/research.md)
- Related ADRs: ADR-0001 (Frontend Stack - Tailwind CSS, Framer Motion)
- Context7 Research: Shadcn/ui (/websites/ui_shadcn), Framer Motion (community best practices)
- Constitution Principle: "Modern UI/UX Standards" (constitution-prompt-phase-2.md)
