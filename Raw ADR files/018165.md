# ADR 0009: Virtual Card Display Design

## Status

Accepted

## Context

The core interaction in our game revolves around cards that players swipe to make decisions. The design and implementation of these virtual cards is critical to the user experience. We needed to make decisions about:

1. How to visually represent cards in the UI
2. How to implement swipe interactions across different devices
3. How to handle card animations and transitions
4. How to present card information and effects

## Decision

We implemented a virtual card display system with these key features:

1. **Card Visual Design**:
   - Full-bleed card images with overlaid text
   - Title at top of card with semi-transparent background
   - Description text at bottom with semi-transparent background
   - Theme-specific visual styling (borders, backgrounds, filters)

2. **Swipe Interaction**:
   - Drag-based swipe with position tracking
   - Direction indicators that appear while dragging
   - Swipe threshold for commitment (cards return to center if below threshold)
   - Visual feedback showing potential choice while dragging

3. **Card Animation**:
   - Smooth entrance animation for new cards
   - Physics-based exit animation when swiped
   - Subtle hover/breathing animation while card is active
   - Rotation effect during drag to simulate physical card manipulation

4. **Information Display**:
   - Clear visual indication of potential resource changes
   - Dynamic update of indicators based on swipe direction
   - Accessible text contrast for readability
   - Tooltip for additional information on hover/tap-hold

## Rationale

- **Physical Metaphor**: Card design mimics physical cards to create intuitive interaction
- **Gestural Interaction**: Swiping is natural on touchscreens and translates well to mouse/trackpad
- **Visual Clarity**: Clear indication of choices and consequences
- **Responsive Design**: Works across different screen sizes and input methods
- **Accessibility**: Text contrast and size considerations for readability
- **Theme Integration**: Card design allows for theme-specific styling while maintaining consistent interaction

## Alternatives Considered

### Button-Based Selection

Instead of swiping, using yes/no buttons:
- Potentially more accessible for some users
- Simpler implementation

Rejected as primary interface because:
- Less engaging interaction
- Doesn't match the "swipe fate" concept
- Less immersive than the physical card metaphor

### 3D Card Representation

A more realistic 3D card with perspective:
- More visually impressive
- Stronger physical metaphor

Postponed for consideration in future versions because:
- More complex implementation
- Performance concerns on lower-end devices
- Potential accessibility issues
- Core experience works well with 2D approach

### Split-Screen Choice Presentation

Showing both options simultaneously in split-screen:
- More information density
- Clear visualization of alternatives

Rejected because:
- Dilutes the focus on the current decision
- Reduces impact of individual card art
- Less aligned with the card swiping metaphor

## Consequences

### Positive

- Engaging and intuitive interaction model
- Works well across different devices and input methods
- Supports theme-specific visual styling
- Creates a distinctive game experience

### Negative

- More complex implementation than button-based interaction
- Animation and physics calculations have performance cost
- Testing required across different devices and screen sizes
- Some accessibility challenges for users with motor limitations

## Implementation Notes

The virtual card system is implemented through:

- `CardDisplay` component in `ui/components/card_display.py`
- Gesture detection and processing in the UI layer
- Integration with the game logic system to process decisions
- Theme-specific card styling through the asset management system
- CSS animations and transforms for visual effects
- Responsive design adjustments for different screen sizes

The implementation uses Flet's GestureDetector and animation capabilities to create the swipe interaction, with custom logic to determine swipe direction and commitment threshold.

## Related Decisions

- ADR 0003: Theming System and Asset Management
- ADR 0004: Visual Filters Implementation

## Notes

Future enhancements being considered:
- Optional button controls as an accessibility feature
- More elaborate card animations for special events
- Card flipping mechanic for two-sided information
- Haptic feedback on mobile devices
- Support for multi-touch gestures for power users