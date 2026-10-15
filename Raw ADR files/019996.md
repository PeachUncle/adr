---
status: accepted
date: 2025-01-02
decision-makers: [development team]
consulted: [product owner, design team]
informed: [all team members]
---

# Implement Precise Viewport Layout Specifications Using Viewport-Relative Units

## Context and Problem Statement

The current CSS layout implementation uses generic responsive design patterns with arbitrary spacing values (like `min-height: 40vh`, `var(--space-8)`) rather than the precise viewport percentage allocations specified in BIZ-VIEWPORT-LAYOUT story. This creates layout inconsistencies across device types and fails to optimize the above-the-fold experience for immediate visual impact.

The BIZ-VIEWPORT-LAYOUT specification requires exact viewport percentage allocations for each element (logo: 15% desktop, cube: 35% desktop, etc.) to ensure consistent visual hierarchy and proper content positioning across all device types.

## Decision Drivers

- Need to match exact viewport layout specifications from BIZ-VIEWPORT-LAYOUT story
- Requirement for consistent visual hierarchy across desktop, tablet, and mobile
- Above-the-fold content must be visible without scrolling on all target devices
- Mathematical spacing relationships must be implemented for professional appearance
- Layout optimization directly supports message validation goals

## Considered Options

- **Option 1**: Continue with current generic responsive design approach
- **Option 2**: Implement precise viewport-relative unit system (vh, vw) with exact percentages
- **Option 3**: Use fixed pixel-based layouts with media queries
- **Option 4**: Hybrid approach mixing viewport units with CSS custom properties

## Decision Outcome

Chosen option: "**Option 2: Implement precise viewport-relative unit system**", because it directly implements the BIZ-VIEWPORT-LAYOUT specifications with exact percentage allocations, ensures consistent cross-device experience, and provides mathematical precision required for professional layout optimization.

### Consequences

- Good, because layout will exactly match BIZ-VIEWPORT-LAYOUT specifications
- Good, because viewport-relative units automatically scale with device viewport
- Good, because mathematical precision ensures consistent visual hierarchy
- Good, because above-the-fold content guaranteed visible on all target devices
- Bad, because requires significant CSS refactoring from current implementation
- Bad, because viewport units can behave differently across browsers (mitigated by modern browser standardization)

### Confirmation

Implementation compliance will be validated through:

- Viewport-specific screenshot testing at 6 viewports: desktop (1920x1080), laptop (1366x768), tablet portrait (768x1024), tablet landscape (1024x768), mobile portrait (375x667), mobile landscape (667x375)
- Mathematical verification of element height percentages matching specifications
- Above-the-fold content visibility testing without scrolling
- Visual hierarchy assessment across all device types and orientations
- Automated E2E testing with precise viewport sizing and business area coverage

## Pros and Cons of the Options

### Option 1: Continue with current generic responsive design

- Good, because requires no changes to existing implementation
- Good, because familiar CSS patterns for development team
- Neutral, because existing implementation works functionally
- Bad, because fails to meet BIZ-VIEWPORT-LAYOUT specification requirements
- Bad, because creates inconsistent visual hierarchy across devices
- Bad, because above-the-fold optimization not guaranteed

### Option 2: Implement precise viewport-relative unit system

- Good, because directly implements required specifications with mathematical precision
- Good, because viewport units automatically scale with device size
- Good, because ensures above-the-fold content visibility
- Good, because creates consistent professional appearance
- Good, because supports message validation through optimized layout
- Neutral, because requires CSS refactoring effort
- Bad, because viewport units have subtle browser differences (minimal in modern browsers)

### Option 3: Use fixed pixel-based layouts with media queries

- Good, because provides pixel-perfect control
- Good, because predictable behavior across browsers
- Neutral, because familiar development patterns
- Bad, because doesn't scale with actual viewport variations
- Bad, because requires extensive media query management
- Bad, because fails to handle viewport variations within breakpoints

### Option 4: Hybrid approach mixing viewport units with CSS custom properties

- Good, because combines benefits of both approaches
- Good, because maintains some existing CSS structure
- Neutral, because allows gradual migration
- Bad, because creates complex CSS architecture
- Bad, because doesn't fully implement specification requirements
- Bad, because mixing units can create inconsistent scaling

## More Information

This decision implements the mathematical layout requirements from BIZ-VIEWPORT-LAYOUT story:

**Desktop (1920x1080)**: Logo 15%, Cube 35%, Headline 15%, Description 15%, CTA 20%
**Laptop (1366x768)**: Proportional scaling with optimized spacing for laptop displays
**Tablet Portrait (768x1024)**: Logo 12%, Cube 30%, Headline+Description 25%, CTA+margin 33%  
**Tablet Landscape (1024x768)**: Horizontal layout optimization with landscape-specific spacing
**Mobile Portrait (375x667)**: Logo 10%, Cube 25%, Headline 15%, Description 20%, CTA 15%, Margin 15%
**Mobile Landscape (667x375)**: Compact horizontal layout maintaining visual hierarchy

The implementation will use CSS viewport units (vh) for height allocations and maintain responsive width management with existing container patterns. This decision directly supports the goal of optimizing initial viewport layout for immediate visual impact and clear content hierarchy across all device orientations.
