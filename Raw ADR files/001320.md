# ADR-021: Target Devices

## Status

Accepted

## Context

The project targets a broad range of devices, including smartphones, tablets,
and desktops. Usage analytics and market trends show a significant and growing
portion of users accessing the application from mobile devices. Traditional
desktop-first design workflows often lead to complex overrides and poor
performance on smaller screens.

To ensure a better user experience on mobile and reduce development complexity,
a design and development strategy is needed that prioritizes mobile users
without sacrificing desktop usability.

## Decision

We decided to adopt a **Mobile-First** approach to styling and layout across the
project.

## Reasons

1. **Better Performance on Mobile Devices**:
   - Mobile-first CSS typically results in smaller payloads and fewer overrides,
     leading to faster load times on constrained networks and devices.

2. **Progressive Enhancement**:
   - Mobile-first design encourages building from the simplest use case up,
     layering complexity only where needed for larger screens, which improves
     maintainability.

3. **Improved User Experience on Mobile**:
   - Prioritizing mobile ensures key interactions and content are optimized for
     small screens, which often represent the majority of user traffic.

4. **Simplified CSS Structure**:
   - Using mobile as the base and applying media queries for larger viewports
     minimizes redundant or conflicting styles.

5. **Consistency Across Breakpoints**:
   - Mobile-first enforces clarity in layout decisions and ensures deliberate
     scaling up rather than reactive scaling down.

6. **Alignment with Modern Frameworks**:
   - Frameworks like Tailwind CSS, Bootstrap 5+, and many CSS-in-JS libraries
     are designed with mobile-first philosophies in mind.

## Consequences

1. **Design Team Alignment Required**:
   - Designers must ensure wireframes and prototypes start from mobile views,
     which may require a shift in process or tooling.

2. **Increased Effort for Desktop-Heavy Features**:
   - Some desktop-centric features may require more upfront planning to fit into
     a progressively enhanced layout.

3. **Learning Curve**:
   - Developers unfamiliar with mobile-first thinking may need to adjust how
     they approach layout and component design.

## Alternatives Considered

### Desktop-First Approach:

- **Pros**: Familiar to many developers, may simplify complex desktop UI
  design.
- **Cons**: Often leads to performance and usability issues on mobile,
  requires heavy overrides for responsiveness.

### Platform-Specific Design:

- **Pros**: Tailored experience per platform.
- **Cons**: Not scalable or maintainable; increased complexity and
  duplication.
