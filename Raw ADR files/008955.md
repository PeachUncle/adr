# ADR-002: Vanilla JavaScript Framework Decision

## Status
Accepted

## Context

The DuperHeroes game requires interactive UI components including:
- Dynamic game state management (timer, score, questions)
- Real-time UI updates during gameplay
- Form handling for user interactions
- DOM manipulation for game feedback and animations
- Client-side routing between game screens

The project constraints include:
- Single-file architecture requirement (from ADR-001)
- Minimal external dependencies for fast loading
- Simple deployment without build processes
- Team familiarity with web fundamentals over complex frameworks
- Mobile performance considerations with limited bandwidth

The application has moderate complexity with clear state management needs but does not require advanced features like server-side rendering, complex component hierarchies, or extensive third-party integrations.

## Decision

We will use vanilla JavaScript (ES6+) without any frontend frameworks or libraries for all application logic and DOM manipulation.

The implementation will use:
- ES6 classes for game state management and organization
- Template literals for dynamic HTML generation
- Native DOM APIs for element manipulation and event handling
- Modern JavaScript features (arrow functions, destructuring, modules)
- Direct onclick attributes and method calls for event handling
- Browser native APIs (localStorage, fetch, timers)

## Alternatives Considered

### Option 1: React.js with CDN
- **Description**: Use React via CDN without build process, JSX via Babel in browser
- **Pros**: Component-based architecture, large community, industry standard, excellent state management
- **Cons**: Larger bundle size, runtime JSX transformation performance cost, complexity overhead for simple game, requires understanding of React concepts
- **Risk Level**: Low

### Option 2: Vue.js with CDN
- **Description**: Use Vue.js via CDN for reactive components and state management
- **Pros**: Gentle learning curve, excellent documentation, smaller than React, good performance
- **Cons**: Additional dependency, overkill for simple game logic, framework-specific patterns
- **Risk Level**: Low

### Option 3: Alpine.js
- **Description**: Lightweight framework for adding reactivity to existing HTML
- **Pros**: Very small footprint (8kb), minimal learning curve, works with existing HTML
- **Cons**: Limited ecosystem, less suitable for complex state management, still an external dependency
- **Risk Level**: Medium

### Option 4: Svelte (Compiled)
- **Description**: Use Svelte with compilation step for optimal performance
- **Pros**: No runtime overhead, excellent performance, modern developer experience
- **Cons**: Requires build process (conflicts with static architecture), complexity overhead, learning curve
- **Risk Level**: High

### Option 5: jQuery
- **Description**: Use jQuery for DOM manipulation and event handling
- **Pros**: Familiar API, extensive documentation, cross-browser compatibility
- **Cons**: Large dependency for modern browsers, outdated approach, performance overhead
- **Risk Level**: Low

## Consequences

### Positive
- **Zero framework overhead**: No runtime performance penalty from framework abstractions
- **Complete control**: Full control over DOM manipulation and performance optimization
- **Small bundle size**: Only the code we write is included in the final application
- **No build process**: Direct development and deployment without compilation steps
- **Educational value**: Reinforces fundamental web development concepts
- **Browser compatibility**: Modern JavaScript features well-supported in target browsers
- **Debugging simplicity**: No framework-specific debugging tools or concepts required
- **Long-term stability**: No framework version updates or breaking changes to manage

### Negative
- **More boilerplate**: Manual DOM manipulation and event handling code
- **State management complexity**: Manual implementation of reactive state patterns
- **Code organization challenges**: No framework-enforced structure or component patterns
- **Testing complexity**: No framework-provided testing utilities
- **Developer productivity**: Slower development for complex UI interactions
- **Potential for inconsistency**: Manual patterns may lead to inconsistent code organization
- **Missing abstractions**: No built-in solutions for common patterns like routing or data binding

### Neutral
- **Learning curve**: Easier for developers familiar with fundamentals, harder for framework-only developers
- **Community support**: Large vanilla JavaScript community but fewer game-specific resources
- **Maintenance**: Simpler dependency management but potentially more custom code to maintain

## Implementation Notes

### Code Organization Patterns
- Use ES6 classes to encapsulate game state and behavior
- Implement clear separation of concerns with dedicated methods for rendering, state management, and event handling
- Use template literals for clean HTML generation
- Organize code into logical sections within the single file

### State Management Strategy
- Centralize state in a GameState class with clear methods for updates
- Use reactive patterns with manual DOM updates after state changes
- Implement event-driven architecture for loose coupling between game components

### Performance Considerations
- Minimize DOM queries by caching element references
- Use event delegation where appropriate for dynamic content
- Implement efficient rendering patterns to avoid unnecessary DOM manipulation

### Browser Support
- Target modern browsers with ES6+ support (Chrome 60+, Firefox 55+, Safari 12+)
- Use feature detection for any advanced APIs
- Provide graceful degradation for unsupported features

### Success Metrics
- Application bundle size under 50KB total
- Interactive time under 1 second on target devices
- Memory usage under 10MB during gameplay
- Zero framework-related bugs or compatibility issues

## References
- [Modern JavaScript Features](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [DOM Manipulation Best Practices](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)
- [Vanilla JavaScript Performance Patterns](https://javascript.info/)