# ADR 0008: Multi-Verse Concept and Design

## Status

Accepted (with future expansion planned)

## Context

The game was initially conceived with a single theme/universe, but we wanted to expand the concept to support multiple themed games ("universes") within a cohesive framework. This required decisions about:

1. How to structure and organize multiple game themes
2. How to present the multi-verse concept to users
3. How to maintain a consistent game experience while allowing for theme-specific variations
4. How to plan for future expansion of the multi-verse concept

## Decision

We implemented a multi-verse framework with these key components:

1. **Theme-Based Game Universes**:
   - Each universe has its own configuration, cards, resources, and visual style
   - Consistent underlying game mechanics across all universes
   - Universe-specific asset sets (card images, resource icons, backgrounds)

2. **Game Selection Interface**:
   - Carousel-based selection of available universes
   - Visual representation through distinctive card backs
   - Brief descriptions that highlight the theme/setting of each universe

3. **Multi-Verse Portal Placeholder**:
   - Special "coming soon" card in the selection carousel
   - Visually distinct from completed universes
   - Hints at future expansion of the multi-verse concept

4. **Shared Game History**:
   - Achievement and statistics tracking across all universes
   - Universe-specific statistics and achievements
   - Combined view in the achievements screen

## Rationale

- **Content Variety**: Multiple universes provide more content without changing core gameplay
- **Thematic Expression**: Allows exploration of different settings and themes within same game structure
- **Expandability**: Creates a framework for continuous content additions
- **User Investment**: Players can find themes that resonate with their interests
- **Narrative Cohesion**: The multi-verse concept provides a meta-narrative that connects disparate themes
- **Development Flexibility**: New universes can be developed without changing core game systems

## Alternatives Considered

### Multiple Separate Applications

Instead of a multi-verse within one application, we could have released separate applications for each theme:
- Simpler implementation per application
- More focused marketing for each theme

This was rejected because:
- Would fragment the user base
- Duplicated code and development effort
- Lost opportunity for cross-theme engagement
- More complicated deployment and maintenance

### DLC/Add-on Model

A base game with downloadable content packs was considered:
- More traditional game monetization approach
- Potentially simpler initial implementation

Rejected because:
- Adds complexity around content delivery
- Creates friction in the player experience
- Less conceptually aligned with the multi-verse narrative

### User-Created Universes

Allowing users to create and share their own universes:
- Would create unlimited content possibilities
- Community engagement opportunity

Postponed for future consideration because:
- Significantly more complex implementation
- Moderation and quality control challenges
- Core universe offerings needed first

## Consequences

### Positive

- More varied content within a single application
- Strong conceptual framework for future expansion
- Unified player progress across different themes
- Increased replayability and player engagement

### Negative

- More complex configuration management
- Increased asset management requirements
- Potential theme consistency challenges
- More testing required across multiple universes

## Implementation Notes

The multi-verse concept is implemented through:

- Configuration system with theme-specific JSON files
- Asset management with theme folders and fallback mechanism
- Game selection UI with the carousel interface
- Asset processor service to handle theme-specific visual styles
- Placeholder for future multi-verse portal

The codebase now references "games" or "universes" rather than a single game, with naming changes throughout to reflect this multi-verse approach.

## Related Decisions

- ADR 0001: Package Renaming and Project Structure
- ADR 0002: Configuration Structure and Game Data Model
- ADR 0003: Theming System and Asset Management
- ADR 0006: Game Selection UI - Carousel vs Grid

## Notes

Future enhancements being considered:
- A true "Multi-Verse Portal" feature that creates gameplay connections between universes
- User-created or customizable universes
- Procedurally generated universe variants
- Collaborative universe creation tools