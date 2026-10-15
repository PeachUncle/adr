# Astro Chosen for Portfolio Site SSG Frontend

- **Status**: Accepted
- **Deciders**: Developer (self)
- **Date**: 2024-12-10

---

## Context and Problem Statement

- **Business goal**: Host my portfolio site using GitHub Pages and fetch content directly from a CMS on the page.
- **Technical problem**: Select a static site generator (SSG) solution that seamlessly integrates with React components (specifically MUI), supports Google Tag Manager (GTM), and doesn’t require additional hosting infrastructure beyond GitHub Pages.

---

## Decision Drivers

1. The solution should integrate smoothly with React components, particularly MUI (Material-UI).
2. The solution should allow seamless integration with Google Tag Manager (GTM).
3. GitHub Pages should remain the only hosting infrastructure, minimizing deployment complexity.

---

## Considered Options

1. **Astro**  
   Astro is a modern SSG with a strong focus on DX (developer experience) while delivering and optimizing static assets by default.

2. **Gatsby**  
   Gatsby integrates with React and has a large plugin ecosystem, but developers often rely heavily on plugins for common functionality.

3. **Next.js**  
   Next.js is powerful and feature-rich, designed for both static site generation and dynamic rendering, but many of its features are unnecessary for this project.

---

## Decision Outcome

- **Chosen Option**: **Astro**
  - **Reasoning**: Astro offers the best trade-off between simplicity, ease of implementation, and performance. While all options supported the required integrations (TinaCMS, MUI, and GTM), Astro stood out for its excellent developer experience, straightforward implementation, and minimal complexity.

### Positive Consequences

- The site remains lightweight, as Astro optimizes delivery by default and limits JavaScript sent to the client.
- Astro ensures smooth integration with MUI, GTM, and TinaCMS.
- The straightforward setup supports low-maintenance deployment on GitHub Pages.

### Negative Consequences

- Requires learning some Astro-specific syntax, which may involve a small learning curve.

---

## Risks and Mitigations

- **Risk**: Limited familiarity with Astro-specific syntax.
  - **Mitigation**: Spend time studying Astro's component syntax and consulting official documentation.
- **Risk**: Potential scaling limitations if dynamic server-side rendering is needed in the future.
  - **Mitigation**: Explore expanding infrastructure if app requirements grow; Next.js could be reconsidered for dynamic needs.

---

## Analysis of the Options

### **Option 1: Astro**

- **Pros**:
  - Supports React components and offers first-class support for frameworks like MUI.
  - Smooth integration with GTM and TinaCMS.
  - Lightweight: Delivers no JavaScript by default, resulting in fast load times.
  - Excellent developer experience during development, including hot reloading.

- **Cons**:
  - Limited adoption compared to Gatsby or Next.js.
  - Requires learning some Astro-specific syntax, which may not be immediately familiar.

---

### **Option 2: Gatsby**

- **Pros**:
  - Large plugin ecosystem for common integrations.
  - Pure React syntax allows for familiarity if already using React exclusively.

- **Cons**:
  - Heavy reliance on plugins for implementations, which can lead to plugin dependencies and complexities.
  - Poor developer experience with GTM—tracker injection fails during development, and builds lack hot reloading.
  - Builds result in client-side rendered websites instead of pre-optimized static content, increasing load times unnecessarily.

---

### **Option 3: Next.js**

- **Pros**:
  - Feature-rich SSG solution with strong support for SSR (server-side rendering) and dynamic capabilities.
  - Integrates well with modern frameworks and environments.

- **Cons**:
  - Overkill for this project, as many of its advanced features (like dynamic rendering) are irrelevant.
  - Complex initial setup for starting with static site generation on GitHub Pages.

---

## Future Considerations

- If future portfolio requirements include dynamic content, consider whether migrating to Next.js would make sense.
- Keep tabs on Astro’s ecosystem and adoption rate to ensure long-term support.

---

## Links

- [Astro Example Implementation](https://github.com/neviaumi/portfolio/tree/01a13b5474975d993d23a6511cadd20fdf0c47cf/systems/web)
- [Gatsby Example Implementation](https://github.com/neviaumi/portfolio/tree/8e586e18ec0ddd5998d3a2f2a4509a9d5cb72d4b/systems/web/src)
- [Astro Documentation](https://astro.build/)