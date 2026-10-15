# ADR 0006: Game Selection UI - Carousel vs Grid

## Status

Accepted

## Context

As we expanded the game to support multiple themes/universes, we needed to design a user interface for game selection. The primary decision was between two common patterns for displaying selectable content:

1. **Carousel**: A horizontal scrolling list of game options
2. **Grid**: A multi-row grid of game options

This decision would impact the user experience, especially as the number of available games grows over time.

## Decision

We decided to implement a horizontal carousel for game selection with the following characteristics:

- Horizontally scrolling row of game cards
- Each card shows a representative card back image
- Cards include game title and brief description on hover
- Visual distinction for special items (like the "Multi-Verse Portal" placeholder)
- Left/right navigation controls for desktop/large screen users
- Touch swipe navigation for mobile/touchscreen users

## Rationale

- **Visual Focus**: The carousel design allows each game option to have more screen real estate, making the visual design of each card back more impactful
- **Future Expandability**: The horizontal scrolling design can accommodate an unlimited number of games without requiring UI redesign
- **Narrative Flow**: The linear arrangement better supports the conceptual "journey" through different game universes
- **Touch-Friendly**: The swipe gesture for carousel navigation aligns naturally with the core swipe mechanic of the game itself
- **Reduced Cognitive Load**: Presenting fewer options at once reduces decision paralysis when compared to a dense grid
- **Consistent with Modern UX**: Follows patterns common in streaming services and mobile apps, making the interaction model familiar to users

## Alternatives Considered

### Grid Layout

A grid-based selection screen would have:
- Multiple rows of smaller game cards
- More visible options at once without scrolling
- Potentially faster selection for users who know what they want

We rejected this approach because:
- It would reduce the visual impact of each game's unique art style
- Grid layouts can appear cluttered and overwhelming as the number of options grows
- The Multi-Verse concept is better represented by a linear journey between universes

### Tabbed Interface

A tabbed selection approach was also considered:
- Categories of games accessible via tabs
- Full-screen focus on the selected game category

This was rejected because:
- The current game library size doesn't warrant this level of categorization
- It would add an extra click/interaction step to the game selection process

## Consequences

### Positive

- More visually engaging selection experience
- Better showcases the unique art style of each game
- Natural touch interaction model that matches the core game mechanics
- Easy to add new games without UI redesign

### Negative

- Less efficient use of screen space compared to a grid
- May require more scrolling/swiping as the game library grows
- Selection efficiency decreases with more options

## Implementation Notes

The carousel is implemented using Flet's Row component with horizontal scrolling enabled:

- GameSelector component manages the overall carousel
- GameCard components represent individual game options
- The carousel automatically adjusts to available screen width
- Visual indicators show available navigation directions
- Special styling for the "coming soon" placeholder creates visual distinction

## Related Decisions

- ADR 0003: Theming System and Asset Management
- ADR 0005: User Interface Navigation Patterns

## Notes

As the game library grows beyond a certain threshold (approximately 8-10 games), we may need to revisit this decision and consider:

1. Adding category filtering to the carousel
2. Implementing a hybrid approach with category tabs and carousels within each category
3. Providing a grid view option as an alternative navigation mode