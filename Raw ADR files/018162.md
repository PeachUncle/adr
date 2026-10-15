# User Interface Navigation Patterns

## Status

Accepted

## Context

Swipe Verse requires an intuitive user interface that works well across different screen sizes and supports its card-swiping gameplay mechanic. We needed to decide on:

1. Overall UI architecture and navigation patterns
2. How to handle swipe interactions for card decisions
3. Screen transitions and component organization
4. Menu structure and accessibility
5. Responsive design considerations

## Decision

We implemented a UI architecture with the following key patterns:

1. **Screen-Based Navigation**:
   - Distinct screens for different functions (Title, Game, Settings, Achievements)
   - Clear navigation paths between screens
   - Stateful management of current screen

2. **Swipe Mechanics**:
   - Gesture-based card interaction as the core gameplay mechanic
   - Visual feedback during swipe (rotation, border changes)
   - Fallback button controls for accessibility

3. **UI Organization**:
   - Consistent placement of navigation elements
   - Contextual menus based on current screen
   - Modal dialogs for focused interactions

4. **Responsive Design**:
   - Mobile-first approach
   - Dynamic sizing based on screen dimensions
   - Adaptive layouts for different device types

5. **Navigation Consistency**:
   - "Back" options on all non-main screens
   - Game-specific controls segregated from navigation controls
   - Breadcrumb-like mental model for screen history

## Rationale

- **Distinct Screens**: Creates a clear mental model for users about where they are in the application.
- **Gesture-First Design**: Emphasizes the swipe mechanic that gives the game its name and core interaction.
- **Fallback Controls**: Ensures accessibility for users who may have difficulty with swipe gestures.
- **Modal Approach**: Focuses user attention on specific interactions when needed.
- **Responsive Foundation**: Ensures the game works well on mobile devices, tablets, and desktops.

Alternative approaches considered:
- Single-page UI with component swapping (rejected for clarity reasons)
- Tab-based navigation (rejected as less immersive)
- More complex gesture system (rejected for simplicity and accessibility)

## Consequences

### Positive
- Clear navigation model that's easy to understand
- Swipe mechanics create an engaging, tactile feel
- UI adapts well to different screen sizes
- Modal dialogs provide focused interaction for important decisions
- Consistent patterns make the application predictable

### Negative
- More complex state management compared to single-screen approach
- Transitions between screens require careful management
- Swipe detection needs fallbacks for accessibility

## Related Decisions

- [ADR-0006: Game Selection Carousel vs Grid](0006-game-selection-carousel-vs-grid.md)
- [ADR-0009: Virtual Card Display Design](0009-virtual-card-display-design.md)

## Notes

The navigation structure follows this pattern:

```
Title Screen
├── Game Selection Carousel
├── Game Screen
│   ├── Card Interaction
│   ├── Resource Displays
│   └── Game Controls
├── Settings Screen
│   ├── Filter Selection
│   ├── Theme Selection
│   └── Difficulty Settings
└── Achievements Screen
    ├── Achievements List
    └── Statistics Display
```

For swipe interactions, we use both touch gestures and mouse drag events, with visual feedback that includes:
- Card rotation proportional to swipe distance
- Color-coded borders indicating choice direction
- Subtle animations to enhance the tactile feel of card manipulation