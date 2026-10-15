# ADR-002: Use EDS Blocks for Content-Driven Components

**Status**: Accepted

**Date**: 2024-11-15

**Decision Makers**: BuildRight Implementation Team

---

## Context

BuildRight needs many custom UI components that are not standard e-commerce functions:
- Template selector dashboard (Sarah's experience)
- Project wizard with multi-step flow (Marcus)
- Luxury package builder (Lisa)
- Interactive deck builder (David)
- Restock dashboard (Kevin)
- Loading overlays
- Wizard progress indicators
- Filter sidebars
- Custom product tiles

We need to decide how to build these custom components within the Adobe Edge Delivery Services (EDS) architecture.

### Key Constraints
1. **EDS Compliance**: Must follow EDS best practices and patterns
2. **Performance**: Need fast loading and rendering
3. **Maintainability**: Team must be able to update components easily
4. **Consistency**: Should integrate seamlessly with Adobe Commerce Dropins
5. **Content-Driven**: Many components are content-heavy, not purely commerce

### Research Findings
- EDS provides a "block" system for custom components
- Blocks use a `decorate()` function pattern
- Blocks can manipulate DOM or generate new DOM
- EDS blocks are lightweight and performant
- Blocks follow file conventions: `block-name.html`, `block-name.css`, `block-name.js`
- Blocks can emit events for inter-block communication
- Adobe Commerce Dropins are also technically "blocks" but with heavier commerce logic

---

## Decision

**We will use EDS Blocks for all BuildRight-specific, content-driven custom components.**

### EDS Blocks We Will Build:

#### Shared Components
- **Loading Overlay** - Progress messages during CCDM filtering
- **Wizard Progress** - Step indicators for multi-step flows
- **Template Card** - Reusable template display component
- **Product Tile** - Custom product display with persona-specific info
- **Package Comparison** - Side-by-side package comparison

#### Persona-Specific Components
- **Template Dashboard** (Sarah) - Grid of home templates
- **Project Wizard** (Marcus) - Multi-phase project builder
- **Package Builder** (Lisa) - Luxury package selector
- **Deck Wizard** (David) - Interactive deck configuration
- **Restock Dashboard** (Kevin) - Quick reorder interface

#### Page Components
- **Filters Sidebar** - Category and attribute filters
- **Product Grid** - Product listing with CCDM support
- **Header** - Site navigation with persona awareness
- **Footer** - Site footer

### What We Will NOT Build as EDS Blocks:
- Authentication (use Auth Dropin)
- Shopping cart (use Cart Dropin)
- Account management (use Account Dropin)
- Checkout flow (use Checkout Dropin)

---

## Consequences

### Positive Outcomes

✅ **EDS Performance**
- Lightweight JavaScript bundles
- Fast initial page load
- Progressive enhancement approach
- Minimal DOM manipulation

✅ **Full Control**
- Complete customization of UI and behavior
- No constraints from third-party components
- Can implement any UX pattern needed
- Easy to iterate and refine

✅ **Content-Friendly**
- EDS blocks are designed for content-driven experiences
- Easy to integrate with content authoring
- Can leverage EDS's content delivery features
- Future: could be authored in Franklin (EDS authoring)

✅ **Team Familiarity**
- Team can work in familiar HTML/CSS/JS
- No need to learn complex framework
- Standard web development practices
- Easy to debug and test

✅ **Maintainability**
- Clear separation of concerns (one block per component)
- Standard file structure
- Reusable across pages
- Easy to update independently

✅ **Integration**
- Blocks can listen to dropin events
- Blocks can emit events for other blocks
- Can wrap dropins in blocks if needed
- Consistent decoration pattern

### Negative Outcomes

⚠️ **More Development Work**
- Need to build these components from scratch
- More code to write than using pre-built solutions
- Need to handle edge cases ourselves

⚠️ **State Management**
- No built-in state management like React/Vue
- Must manage component state manually
- Need to coordinate state between blocks

⚠️ **Testing Overhead**
- Must write tests for custom components
- No pre-existing test coverage
- More surface area to test

⚠️ **Consistency Risk**
- Must ensure consistent UX across custom blocks
- Need discipline to follow design system
- Risk of UI drift if not careful

---

## Alternatives Considered

### Alternative 1: Build with React/Vue Components

**Approach**: Use a modern JavaScript framework for all custom components.

**Pros**:
- Rich ecosystem of libraries and tools
- Built-in state management
- Component lifecycle management
- Developer familiarity with frameworks

**Cons**:
- Doesn't fit EDS architecture
- Larger JavaScript bundles
- Slower initial page load
- Mixing paradigms (EDS + React) is awkward
- Would need build tooling

**Why Rejected**: EDS is not a React/Vue environment. Mixing paradigms creates architectural confusion.

---

### Alternative 2: Use More Dropins for Everything

**Approach**: Try to use Adobe Commerce Dropins for as many components as possible.

**Pros**:
- Consistent with commerce components
- Potentially faster development
- Adobe maintains the code

**Cons**:
- No dropins exist for BuildRight-specific features (templates, wizards, etc.)
- Dropins are commerce-focused, not content-focused
- Would be forcing square pegs into round holes
- Less flexibility for custom UX

**Why Rejected**: Dropins don't exist for our unique persona-driven features. They're designed for standard commerce, not custom workflows.

---

### Alternative 3: Server-Side Rendering with Minimal JS

**Approach**: Render all HTML server-side, use minimal JavaScript for interactions.

**Pros**:
- Fastest initial page load
- Best SEO
- Progressive enhancement

**Cons**:
- Doesn't fit EDS client-side architecture
- Harder to build interactive wizards and dashboards
- Would need server infrastructure
- Goes against EDS's edge-first approach

**Why Rejected**: EDS is designed for client-side rendering with edge delivery. Server-side rendering doesn't fit the architecture.

---

## Implementation Guidelines

### EDS Block Structure

Every block follows this structure:

```
blocks/
└── block-name/
    ├── block-name.html   (optional: template structure)
    ├── block-name.css    (block-specific styles)
    └── block-name.js     (block decoration logic)
```

### Decoration Pattern

All blocks use the `decorate()` function:

```javascript
export default function decorate(block) {
  // Query existing DOM or generate new DOM
  // Add event listeners
  // Integrate with other blocks via events
  // Return block for chaining
}
```

### Design System Compliance

All blocks must:
- Use design tokens from `base.css` for colors, spacing, typography
- Follow naming conventions
- Use custom SVG icons (no emojis)
- Be responsive and accessible
- Emit events for state changes

### Event-Driven Integration

Blocks communicate via custom events:

```javascript
// Emit event
window.dispatchEvent(new CustomEvent('cart:item-added', {
  detail: { productId, quantity }
}));

// Listen to event
window.addEventListener('cart:item-added', (e) => {
  updateMiniCart(e.detail);
});
```

### Loading Strategy

- **Eager**: Critical blocks (header, hero)
- **Lazy**: Below-the-fold blocks
- **Delayed**: Non-critical blocks (footer, tracking)

---

## Decision Matrix: When to Use What

| Use Case | Solution | Reason |
|----------|----------|--------|
| Authentication | **Dropin** | Standard commerce, Adobe handles security |
| Shopping Cart | **Dropin** | Standard commerce, complex state management |
| Product Display | **Dropin** | Standard commerce, inventory/pricing integration |
| Template Selector | **EDS Block** | BuildRight-specific, content-driven |
| Project Wizard | **EDS Block** | Custom workflow, not in any dropin |
| Loading Overlay | **EDS Block** | Simple UI component |
| Header/Footer | **EDS Block** | Content-driven, site-specific |

See [Block vs Dropin Matrix](../BLOCK-VS-DROPIN-MATRIX.md) for full decision framework.

---

## Related Decisions

- [ADR-001: Use Adobe Commerce Dropins](./ADR-001-use-dropins-for-commerce.md) - Explains commerce component strategy
- [ADR-003: Mock ACO Service](./ADR-003-mock-aco-service.md) - How blocks integrate with mock backend

---

## References

- [EDS Block Patterns Documentation](../EDS-BLOCK-PATTERNS.md)
- [Block vs Dropin Decision Matrix](../BLOCK-VS-DROPIN-MATRIX.md)
- [AEM Edge Delivery Services Documentation](https://www.aem.live/)

---

**Last Updated**: November 15, 2024

