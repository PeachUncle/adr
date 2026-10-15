# Design: UI Design System Redesign

## Context

Pithy Jaunt's current UI was built quickly with placeholder components, resulting in:
- Inconsistent styling across pages
- Hardcoded Tailwind colors (gray-*, blue-*) instead of brand colors
- Duplicated component logic
- No shared component library
- Poor visual hierarchy
- Limited accessibility

The design brief specifies using Aceternity UI as the foundation, with our brand palette (Chestnut, Sky Blue, Charcoal, Platinum) and modern design principles.

## Goals / Non-Goals

### Goals
- Create a unified, modern design system with semantic tokens
- Establish a reusable component library
- Improve visual hierarchy and user experience
- Ensure WCAG 2.1 AA accessibility compliance
- Implement brand colors consistently
- Create mobile-first responsive design
- Add smooth animations and micro-interactions

### Non-Goals
- Dark mode (future enhancement)
- Complete redesign of functionality (only visual/styling changes)
- Breaking API or data model changes
- New features (only design improvements)

## Decisions

### Decision: Use Aceternity UI as Foundation
**Rationale**: Aceternity UI provides 53+ modern React components with Tailwind CSS and Framer Motion, offering:
- Consistent design patterns
- Built-in animations
- Accessibility features
- Easy customization with Tailwind
- Mobile-responsive by default

**Alternatives considered**:
- Build from scratch: Too time-consuming, reinventing the wheel
- Use ShadCN UI only: Already using it, but Aceternity offers more modern patterns
- Use Material UI: Too opinionated, doesn't match our aesthetic

### Decision: Semantic Color Token System
**Rationale**: Instead of hardcoded colors, use semantic tokens (primary, secondary, neutral, success, error, warning, info) that map to brand colors:
- Primary: Sky Blue (#73C5F3) - actions, links, focus
- Secondary/Accent: Chestnut (#932F29) - destructive, warnings, errors
- Neutral: Charcoal (#565555) - text, borders
- Background: Platinum (#EBEBEB) - subtle backgrounds

**Alternatives considered**:
- Direct color usage: Harder to maintain, no theme flexibility
- CSS variables only: Less integrated with Tailwind

### Decision: 4px Base Unit Spacing System
**Rationale**: 4px base unit creates consistent rhythm and is divisible by common screen sizes. Scale: 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px.

**Alternatives considered**:
- 8px base unit: Too large for fine-grained control
- Arbitrary spacing: Inconsistent, harder to maintain

### Decision: Inter Font Family
**Rationale**: Inter is modern, highly readable, professional, and optimized for screens. JetBrains Mono for code/logs.

**Alternatives considered**:
- System fonts: Too generic, no brand identity
- Custom fonts: Performance overhead, licensing complexity

### Decision: Component-First Approach
**Rationale**: Create base components first (Button, Card, Input, etc.), then update pages to use them. This ensures consistency and makes future changes easier.

**Alternatives considered**:
- Page-first approach: Would lead to more duplication
- Hybrid approach: Less clear, harder to maintain

### Decision: Incremental Implementation
**Rationale**: Implement in phases (tokens → components → layouts → pages) to allow testing and validation at each stage.

**Alternatives considered**:
- Big bang approach: Too risky, harder to debug
- Component-by-component: Too slow, less cohesive

## Risks / Trade-offs

### Risk: Breaking Existing Functionality
**Mitigation**: 
- No API or data model changes
- Only visual/styling changes
- Thorough testing at each phase
- Can rollback individual components if needed

### Risk: Performance Impact from Animations
**Mitigation**:
- Use CSS transitions where possible (better performance than JS)
- Respect prefers-reduced-motion
- Lazy load heavy animations
- Test on low-end devices

### Risk: Accessibility Regression
**Mitigation**:
- WCAG AA compliance as requirement
- Test with screen readers
- Verify color contrast
- Ensure keyboard navigation
- Add ARIA labels

### Risk: Inconsistent Implementation
**Mitigation**:
- Clear component API documentation
- Design token system prevents arbitrary values
- Code review for consistency
- Shared component library

### Trade-off: Time vs. Completeness
**Decision**: Prioritize core components and high-traffic pages first. Less critical pages can be updated incrementally.

## Migration Plan

### Phase 1: Foundation (Week 1)
1. Set up design tokens in Tailwind config
2. Update globals.css
3. Create base components
4. Test components in isolation

### Phase 2: Layout & Navigation (Week 2)
1. Create layout components
2. Update app/layout.tsx
3. Test navigation across pages

### Phase 3: Page Redesigns (Week 3-4)
1. Update existing components to use new design system
2. Redesign pages one by one
3. Test each page thoroughly

### Phase 4: Polish & Accessibility (Week 5)
1. Add interactions and animations
2. Accessibility audit and fixes
3. Final testing and refinement

### Rollback Plan
- Each phase can be rolled back independently
- Git branches for each major phase
- Keep old components until new ones are validated

## Open Questions

- Should we implement dark mode in this change or defer? **Decision**: Defer to future enhancement
- How to handle existing inline styles? **Decision**: Replace with component classes
- Should we create Storybook for component documentation? **Decision**: Defer, document in code comments for now

