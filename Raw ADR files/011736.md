# Technical Design: GameCreator Player Component Targeting Research

## Context

In a **multiplayer game**, each connected client has their own **Local Player** - the character they control. GameCreator components (Triggers, Hotspots, Camera Shots, etc.) need to correctly resolve which player they should interact with:

- **Local Player**: The player controlled by THIS client (owns NetworkObject)
- **Remote Players**: Players controlled by OTHER clients (not owned locally)
- **Any Player**: Any player that meets criteria (for shared world objects)

The core problem: GameCreator's default `GetGameObjectPlayer` uses tag-based lookup (`"Player"` tag), which doesn't work correctly in multiplayer where multiple characters exist.

## Goals / Non-Goals

### Goals
- Comprehensive audit of all GameCreator components that reference players
- Clear targeting strategy for each component category
- Identify root causes for positioning and duplicate trigger issues
- Document which components need `GetGameObjectLocalNetworkPlayer`
- Create testing checklist for validation

### Non-Goals
- Implementation of fixes (separate proposal)
- Performance optimization
- New feature development
- Refactoring existing code

## Research Methodology

### Phase 1: Component Inventory

**Target:** Identify ALL GameCreator components that reference players

```
Search patterns:
1. PropertyGetGameObject usage
2. m_Target fields in components
3. "Player" tag references
4. Character references in Visual Scripting
5. Transform/Position targets
```

**Component Categories:**
| Category | Examples | Expected Count |
|----------|----------|----------------|
| Triggers | OnTriggerEnter, OnTriggerStay | ~20 |
| Hotspots | Interactive objects | ~10 |
| Camera System | CameraShot, ShotType | ~15 |
| Actions/Instructions | Move, Follow, Look | ~50 |
| Conditions | Distance, Visibility | ~30 |
| Properties | GetPosition, GetRotation | ~40 |

### Phase 2: Targeting Analysis

For each component, determine:

1. **Current Implementation**
   - How does it currently resolve "Player"?
   - Is it tag-based, reference-based, or event-based?

2. **Multiplayer Requirement**
   - Should it target Local Player only?
   - Should it target Any Player?
   - Should it be Server-authoritative?

3. **Network Authority**
   - Client-side execution (visual/audio)
   - Server-validated execution (game state changes)
   - Owner-only execution (input-driven)

### Phase 3: Positioning Investigation

**Spawn Flow Analysis:**
```
NetworkPlayerManager.SpawnPlayer()
    ↓
NetworkObject.Spawn()
    ↓
NetworkCharacterAdapter.OnNetworkSpawn()
    ↓
Character.InitializeNetwork()
    ↓
CharacterController setup
    ↓
Final position
```

**Investigation Points:**
1. When is `CharacterController.center` set?
2. When is `transform.position` finalized?
3. Are there race conditions with physics?
4. Does prediction/interpolation affect initial position?

### Phase 4: Trigger Duplicate Analysis

**Hypothesis Testing:**
1. Is trigger firing once per player? (4 players = 4 triggers)
2. Is trigger firing multiple times per frame?
3. Is trigger firing on both client and server?
4. Is NetworkTriggerAdapter being used correctly?

**Test Cases:**
- Single player scenario
- 2-player scenario (host + client)
- Trigger with NetworkObject vs without
- Trigger targeting "Player" vs "Local Network Player"

## Decisions

### Decision 1: Research-First Approach
**Choice:** Complete full audit before implementing fixes
**Rationale:** Previous fixes were targeted but missed systemic issues

### Decision 2: Component Categorization
**Choice:** Use 6 targeting categories:
1. **LocalPlayer** - Only affects the local player
2. **AnyPlayer** - Any player can trigger
3. **OwnerOnly** - Only the owning player
4. **ServerAuth** - Server decides outcome
5. **AllClients** - Visual effects for all
6. **Irrelevant** - Doesn't involve players

### Decision 3: PropertyGetGameObject Strategy
**Choice:** Create network-aware variants for each targeting need:
- `GetGameObjectLocalNetworkPlayer` (exists)
- `GetGameObjectAnyNetworkPlayer` (new)
- `GetGameObjectNearestNetworkPlayer` (new)
- `GetGameObjectNetworkPlayerByClientId` (new)

## Risks / Trade-offs

### Risk 1: Scope Creep
- **Risk:** Research expands indefinitely
- **Mitigation:** Fixed time-box, prioritized component list

### Risk 2: Breaking Existing Scenes
- **Risk:** Fixes break working configurations
- **Mitigation:** Document all changes, provide migration path

### Risk 3: GameCreator Updates
- **Risk:** Future GC updates override changes
- **Mitigation:** Use extension patterns where possible, document invasive changes

## Component Investigation List

### Priority 1 - High Impact (Likely Broken)
| Component | File | Issue |
|-----------|------|-------|
| Trigger m_Target | `Trigger.cs` | Uses tag lookup |
| Hotspot m_Target | `Hotspot.cs` | Uses tag lookup |
| CameraShot m_Target | `ShotCamera.cs` | Uses tag lookup |
| Character.Get() | `PropertyGetGameObject*` | Multiple variants |

### Priority 2 - Medium Impact
| Component | File | Issue |
|-----------|------|-------|
| Actions with targets | `Instruction*.cs` | PropertyGetGameObject |
| Conditions with targets | `Condition*.cs` | PropertyGetGameObject |
| Marker/Waypoint targets | `Marker.cs` | Transform reference |

### Priority 3 - Low Impact
| Component | File | Issue |
|-----------|------|-------|
| Debug components | Various | Development only |
| Editor-only | `*Editor.cs` | Not runtime |

## Output Artifacts

1. **Component Inventory Spreadsheet** - All components with player references
2. **Targeting Strategy Matrix** - Decision for each component
3. **Positioning Timeline** - Spawn flow with timing issues identified
4. **Trigger Analysis Report** - Root cause of duplicate firing
5. **Implementation Recommendations** - Prioritized fix list

## Open Questions

1. Should we create a unified `INetworkPlayerTarget` interface?
2. How do we handle components that need different targeting based on context?
3. Should targeting be configurable per-instance or per-component-type?
4. How do we validate scene configurations in Editor?
