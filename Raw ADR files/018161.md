# Configuration Structure & Game Data Model

## Status

Accepted

## Context

Creating a flexible card-based decision game required a robust data model and configuration system that could support:

1. Multiple game themes with different resources, cards, and content
2. Customizable win/loss conditions and game mechanics
3. Dynamic loading of game configurations
4. Consistent validation of game data
5. Extensibility for future features

We needed to decide how to structure game configuration files and what data model to use for representing game state, cards, and resources.

## Decision

We implemented a JSON-based configuration system with the following key components:

1. **Pydantic Data Models**:
   - `GameConfig`: Top-level configuration
   - `GameInfo`: Basic metadata about the game
   - `Theme`: Visual and theming information
   - `GameSettings`: Rules and mechanics settings
   - `Card`: Individual card definitions with choices
   - `CardChoice`: Decision options for each card

2. **Structured JSON Configuration Files**:
   - Theme-specific files (e.g., `kingdom_game.json`, `business_game.json`)
   - Consistent structure across all game themes
   - Support for descriptive backstories
   - Resource definitions and initial values
   - Win/loss condition specifications

3. **Configuration Loading System**:
   - Ability to load configs from local files or URLs
   - Validation of configuration data against models
   - Fallback to default configurations when needed

## Rationale

- **JSON Format**: Chose JSON for its readability, widespread support, and ability to be edited by both developers and potentially non-technical game designers.
- **Pydantic Models**: Used for strong typing, automatic validation, and clear documentation of the data structure.
- **Separation of Game Logic and Content**: Allows for creating new game themes without changing the core logic.
- **Theme-specific Configuration Files**: Makes it easy to add new game themes without code changes.
- **Backstory Support**: Enhances player immersion with narrative context for each game theme.

Alternative approaches considered:
- YAML configuration (rejected due to less widespread editing support)
- Database storage (rejected as overly complex for the initial implementation)
- Hardcoded configurations (rejected as inflexible)

## Consequences

### Positive
- Game themes can be created without modifying code
- Clear separation between game mechanics and content
- Strong validation prevents runtime errors from configuration issues
- Flexible resource definition allows for theme-specific resources
- Configuration can be extended without breaking existing games

### Negative
- More complex initial setup compared to hardcoded configurations
- Requires careful schema evolution to maintain backward compatibility
- JSON files can grow large with many cards and detailed content

## Related Decisions

- [ADR-0003: Theming System & Asset Management](0003-theming-system-asset-management.md)
- [ADR-0007: Achievement & Statistics System](0007-achievement-statistics-system.md)

## Notes

Example configuration structure:
```json
{
  "game_info": {
    "title": "Kingdom Fate",
    "description": "Rule your medieval kingdom",
    "version": "0.1.0",
    "author": "Swipe Verse Team",
    "backstory": "The old king has died without an heir..."
  },
  "theme": {
    "name": "Kingdom Theme",
    "card_back": "assets/themes/kingdom/card_back.png",
    "resource_icons": {
      "treasury": "assets/themes/kingdom/resource_icons/treasury.png",
      "population": "assets/themes/kingdom/resource_icons/population.png"
    }
  },
  "game_settings": {
    "initial_resources": {
      "treasury": 50,
      "population": 50
    },
    "win_conditions": [
      {"resource": "treasury", "min": 10, "max": 90}
    ]
  },
  "cards": [
    {
      "id": "card_001",
      "title": "The Harvest",
      "text": "This year's harvest is meager...",
      "image": "assets/themes/kingdom/card_fronts/harvest.png",
      "choices": {
        "left": {
          "text": "Raise taxes",
          "effects": {
            "treasury": 15,
            "population": -10
          }
        },
        "right": {
          "text": "Distribute grain",
          "effects": {
            "treasury": -10,
            "population": 15
          }
        }
      }
    }
  ]
}
```