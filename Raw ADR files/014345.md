# Guidelines for Web Component Generation

- **Status**: Proposed
- **Deciders**: [Your Name, Team Members]
- **Date**: [YYYY-MM-DD] <!-- Replace with the actual date -->

---

## Context and Problem Statement

The goal is to create reusable, maintainable Web Components using **Lit** that follow modern web standards. A critical part of this is defining a clear approach for **CSS variable naming** and styling, ensuring that components integrate into different design systems while remaining self-sufficient and flexible.

Web components must adhere to styling guidelines to:
1. Enable **global theming** via design tokens.
2. Expose **predictable CSS variables** for consumers.
3. Avoid naming conflicts or unclear variable purposes.

---

## Decision Drivers

- **Consistency**: CSS variable names must follow a predictable pattern for easier use across components.
- **Customizability**: Theming and runtime adaptability (e.g., dark mode) rely on clear variable hooks.
- **Encapsulation**: Variable naming must ensure no conflicts with global variables outside the component scope.
- **Scalability**: The naming conventions should allow extensibility when additional styles or tokens are needed.

---

## CSS Variable Naming Guidelines

### 1. **Use a Clear Namespace for Each Component**

Prefix all CSS variables with a unique component-specific identifier (`<component-name>`) to avoid conflicts and identify ownership.

- **Good Example**:
  `--button-bg-color`, `--button-font-size`, `--card-padding`
- **Bad Example**:
  `--bg-color`, `--font` (too generic, prone to name clashes)

---

### 2. **Group Variables by Purpose**

Organize variable names to reflect their function or purpose in UI styling:
- **Color**: Use `-color` suffix for all colors (background, text, borders).
  - Example: `--button-bg-color`, `--button-text-color`
- **Space/Size**: Use `-padding`, `-margin`, `-width`, or `-height` suffixes.
  - Example: `--card-padding`, `--modal-height`
- **Typography**: Use `-font-family`, `-font-size`, `-font-weight`, or `-line-height`.
  - Example: `--title-font-size`, `--text-line-height`

---

### 3. **Use a Hierarchical Naming Structure**

Align variable names to follow the **structure of the component**:
- Start with the global/parent component name.
- Nest variables for child parts of the component.
- Example for a card component:
  ```css
  :host {
    --card-bg-color: #ffffff; /* Background of the card */
    --card-header-font-size: 18px; /* Font size of the card header */
    --card-header-padding: 16px; /* Padding for the card header */
    --card-content-padding: 24px; /* Padding for the card content area */
  }
  ```

---

### 4. **Leverage Design Token Conventions**

If a design system (e.g., Material Design Tokens) is in use, align variable names closely with those global tokens wherever possible. Use a **mapping layer** to bridge design tokens and internal variables.

Example:
```css
:host {
  /* Mapping CSS variables to tokens */
  --button-bg-color: var(--md-sys-color-primary); /* Uses Material Design's primary color */
  --button-text-color: var(--md-sys-color-on-primary);
}
```

This ensures consistency with the overall design system while still allowing component-specific overrides.

---

### 5. **Prioritize Readability**

Use clear, human-readable variable names so developers and designers can understand their purpose without referencing documentation.

**Clear Example**:
`--tooltip-bg-color`
**Unclear Example**:
`--tooltip-accent`

---

### 6. **Default Fallbacks**

Always define sensible **defaults** for CSS variables directly in the component's styles to ensure components render correctly even without customization.

Example:
```css
:host {
  --button-bg-color: #6200ee; /* Default color */
  --button-padding: 12px; /* Default padding */
}
```

---

### 7. **Document Exposed Variables**

For every component, document the exposed CSS variables and describe their purpose. Example in documentation:

| Variable Name            | Description                      | Default Value |
|--------------------------|----------------------------------|---------------|
| `--button-bg-color`      | Background color of the button  | `#6200ee`     |
| `--button-text-color`    | Text color of the button        | `#ffffff`     |
| `--button-padding`       | Padding inside the button       | `12px`        |

---

## Decision Outcome

We chose this standardized naming strategy to ensure consistent, maintainable, and extensible use of CSS variables for Web Components.

---

### Positive Consequences

- Clear naming ensures variables are intuitive and reusable across similar components.
- Avoids naming conflicts by using component-specific prefixes.
- Aligns components with design systems via token mapping.

### Negative Consequences

- Requires some discipline when defining variable names.
- If naming conventions are ignored, it could lead to inconsistencies.

---

## Implementation Practices for Lit-Based Web Components

1. **Scoped Styles with Clear Variables**
   Use shadow DOM encapsulation while exposing customization points via CSS variables.

   ```css
   static styles = css`
     :host {
       --button-bg-color: #6200ee; /* Default background */
       --button-text-color: #ffffff; /* Default text color */
       background-color: var(--button-bg-color);
       color: var(--button-text-color);
     }
   `;
   ```

2. **Expose Slots for Content Customization**
   ```html
   <my-button>
     <span slot="icon">⭐</span> Click Me
   </my-button>
   ```

3. **Leverage Properties for Dynamic Behavior**
   ```javascript
   @property({ type: Boolean, reflect: true }) disabled = false;

   updated(changedProperties) {
     if (changedProperties.has('disabled')) {
       this.style.setProperty('--button-bg-color', this.disabled ? '#c0c0c0' : '#6200ee');
     }
   }
   ```

4. **Document Styling Hooks**
   In component documentation, list all exposed variables and how they interact with the component.

---

## Links

- [CSS Variables Best Practices (MDN)](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Lit Documentation](https://lit.dev)
- [Material Design Tokens](https://m3.material.io)