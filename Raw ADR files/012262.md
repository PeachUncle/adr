# ADR-003: Mystery Game Design

Date: 2025-12-09

## Status

Accepted

## Context

We are building a web-based mystery investigation game where players take on the role of a detective solving cases through exploration, dialogue, and clue gathering. The game needs:

**Core Gameplay Elements:**
- Interactive investigation and exploration
- NPC dialogue with branching conversations
- Clue collection and evidence examination
- Logical deduction and case solving
- Story-driven narrative
- Grid-based movement and navigation

**Technical Considerations:**
- Web-based, need to consider file sizes and loading
- Top-down view for clear environmental navigation
- Grid-based movement for precise positioning
- Sprite-based graphics
- Need efficient rendering for detailed environments

## Decision

We will implement a **top-down 2D mystery investigation game** with the following design choices:

### Visual Style
- **Top-down perspective** for clear environmental view
- Tile-based maps (32x32 or 48x48 tiles)
- Sprite-based characters with 4-directional animations (down, up, left, right)
- UI inspired by classic adventure games (dialogue boxes, evidence journal, clue cards)

### Core Systems (To Be Implemented)

1. **Grid System**
   - Rectangular grid for movement
   - Coordinate system: `{x, y}` grid positions
   - Tile types: walkable, obstacle, interactive objects
   - Pathfinding: A* algorithm for movement
   - Interaction zones for examining objects

2. **Investigation System**
   - Clue collection mechanics
   - Evidence journal/inventory
   - Clue relationships and connections
   - Progress tracking per case
   - Multiple clue types: physical evidence, documents, testimonies, photographs

3. **Dialogue System**
   - Branching dialogue trees
   - Dialogue choices with prerequisites (requires certain clues)
   - Character testimony recording
   - Interrogation mechanics
   - Relationship tracking with NPCs

4. **Character System**
   - Player detective character
   - NPCs with unique personalities and knowledge
   - Character classes: Detective, Journalist, Scientist, Officer, etc.
   - Movement and interaction capabilities

5. **Map System**
   - Multiple investigation scenes (crime scenes, offices, locations)
   - Tile layers: ground, objects, collision
   - Interactive hotspots for examination
   - Trigger zones for events and dialogue

6. **UI System**
   - Evidence journal showing collected clues
   - Character portraits during dialogue
   - Dialogue boxes with typewriter effect
   - Menu screens: case files, evidence, map
   - Examination cursor/selection system

### Data Structures

**Clue Definition:**
```typescript
{
  id: string,
  name: string,
  description: string,
  type: 'physical' | 'testimony' | 'document' | 'photograph',
  relatedCharacters: string[],
  relatedClues: string[]
}
```

**Character Definition:**
```typescript
{
  id: string,
  name: string,
  class: string,
  position: { x, y },
  sprite: string,
  dialogueId: string,
  clues: string[], // Clues this character knows about
  isPlayer: boolean
}
```

**Map Definition:**
```typescript
{
  id: string,
  width: number,
  height: number,
  tiles: number[][],
  characters: UnitPlacement[],
  triggers: Trigger[],
  clues: ClueLocation[] // Discoverable clues on this map
}
```

**Dialogue Tree:**
```typescript
{
  id: string,
  nodes: DialogueNode[],
  startNodeId: string
}

DialogueNode: {
  id: string,
  speaker: string,
  text: string,
  choices: DialogueChoice[]
}
```

### Rendering Approach
- Use PixiJS Container for each grid cell layer
- Sprite caching for tiles
- Object pooling for frequently created/destroyed objects
- Cull off-screen entities
- Sprite sheets for character animations
- Particle effects for examination/discovery moments

### Phase 1 Implementation (Boilerplate)
For this initial setup, we have created:
- Grid system structure (types and basic classes)
- Map data format with clue locations
- Character data format with dialogue references
- Clue type definitions and relationships
- Basic game state management
- Screen shells for investigation scenes

## Consequences

### Positive
- Top-down view provides clear overview of investigation areas
- Grid-based system works well for methodical investigation
- Tile-based maps are memory efficient
- Branching dialogue creates engaging NPC interactions
- Clear data structures enable JSON-based content editing
- Architecture supports both exploration and dialogue modes
- Clue system allows for complex mystery narratives

### Negative
- Dialogue tree complexity can grow quickly
- Need careful game design to avoid pixel hunting
- Clue relationships require good UX to make connections clear
- Writing compelling mystery narratives is time-intensive

### Neutral
- May want to add mini-games for certain investigations
- Difficulty balancing between too obvious and too obscure
- Save system needs to track all clues and dialogue states
- Asset requirements are significant (locations, character portraits, UI)

### Future Considerations
- Photo/screenshot evidence system
- Timeline reconstruction mechanics
- Case file organization
- Multiple endings based on investigation thoroughness
- Voice acting for key dialogue
- Mobile touch controls
- Cloud save integration
