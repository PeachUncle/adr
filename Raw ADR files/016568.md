# A003: Character Integration Architecture Decision

**Date:** July 31, 2025  
**Status:** Proposed  
**Context:** Architecture decision for UE character creation integration

## Problem Statement

We need to decide on the architecture for character creation integration in our UE project. We have multiple options for how to access D&D 5e data and character creation functionality.

Current situation: We have a working direct toolkit integration but discovered it requires hardcoded data. We also have rpg-api which provides a more complete solution.

## Decision Drivers

### Primary Requirements
- **Dynamic D&D 5e data** (races, classes, backgrounds, spells, equipment)
- **Complete character creation workflow** (draft-based, not single-shot)
- **Production-ready architecture** (proper error handling, persistence)
- **Minimal UE integration complexity** (avoid CGO if possible)

### Strategic Considerations
- **Development velocity** vs **Production readiness**
- **Learning value** vs **Immediate utility**
- **Architectural complexity** vs **Feature completeness**

## Architecture Options

### Option 1: Direct Toolkit Integration (Current)
```
UE Blueprint → RPGCharacterSubsystem → character_bindings.go → rpg-toolkit
```

**Data Flow:**
```cpp
FCharacterResult result = CharacterSubsystem->CreateCharacter(
    "Character Name", "human", "fighter", "soldier"
);
```

**Pros:**
- ✅ Direct access to toolkit functionality
- ✅ No network dependencies
- ✅ Learning experience with CGO/DLL integration
- ✅ Already implemented and working

**Cons:**
- ❌ **No dynamic data access** - all race/class/background data must be hardcoded
- ❌ **Single-shot character creation** - no draft workflow or progress tracking
- ❌ **Limited character creation features** - no skill selection, equipment, etc.
- ❌ **Manual memory management** via CGO automatic cleanup
- ❌ **No persistence** - would need to build custom repository layer

### Option 2: RPG-API Integration (Proposed)
```
UE Blueprint → RPGCharacterService → HTTP/gRPC → rpg-api → dnd5e-api → D&D 5e SRD
                                                    ↓
                                                rpg-toolkit (server-side)
```

**Data Flow:**
```cpp
// Dynamic data access
TArray<FRaceInfo> races = CharacterService->GetAvailableRaces();

// Draft-based workflow  
FString draftID = CharacterService->CreateCharacterDraft("player123");
CharacterService->UpdateDraftRace(draftID, "human");
CharacterService->UpdateDraftClass(draftID, "fighter");
FCharacterResult final = CharacterService->FinalizeDraft(draftID);
```

**Pros:**
- ✅ **Complete D&D 5e SRD data** via dnd5e-api client integration
- ✅ **Professional draft-based character creation** workflow
- ✅ **Built-in Redis persistence** and session management
- ✅ **gRPC service architecture** (production-ready, versioned APIs)
- ✅ **No manual memory management** (HTTP/JSON vs CGO)
- ✅ **All character creation features** (skills, equipment, spells, etc.)
- ✅ **Multi-player ready** (player IDs, session management)

**Cons:**
- ❌ **Network dependency** (localhost for now)
- ❌ **Infrastructure complexity** (Redis + API server)
- ❌ **Less direct control** over toolkit calls
- ❌ **Additional service to manage** during development

## Discovered Architecture: Three-Layer Data System

**Investigation revealed the complete data architecture:**

### Layer 1: D&D 5e SRD Data (dnd5e-api)
- **Purpose:** Official D&D 5e System Reference Document data
- **Source:** https://dnd5eapi.co/ 
- **Data:** Complete races, classes, backgrounds, spells, equipment, monsters
- **Format:** REST API returning structured JSON

**Example Race Data:**
```json
{
  "name": "Human",
  "speed": 30,
  "ability_bonuses": [
    {"ability_score": {"index": "str"}, "bonus": 1},
    {"ability_score": {"index": "dex"}, "bonus": 1}
  ],
  "language_options": {
    "choose": 1,
    "from": ["dwarvish", "elvish", "giant", ...]
  }
}
```

### Layer 2: Game Service (rpg-api)
- **Purpose:** Game logic orchestration + data transformation
- **Dependencies:** dnd5e-api (line 13 in go.mod), rpg-toolkit
- **Features:** Draft workflow, Redis persistence, gRPC APIs
- **Architecture:** Handlers → Orchestrators → Engine → rpg-toolkit

### Layer 3: Game Mechanics (rpg-toolkit)
- **Purpose:** D&D 5e rules calculations and validation
- **Features:** Character generation, dice rolling, conditions, spells
- **Integration:** Server-side via rpg-api engine layer

## Analysis: Why RPG-API Wins

### Dynamic Data Access
**Toolkit Integration:**
```cpp
// Must hardcode everything
TArray<FString> races = {"human", "elf", "dwarf", "halfling"};
// No descriptions, no ability bonuses, no traits
```

**RPG-API Integration:**
```cpp  
// Dynamic access to complete D&D 5e data
auto races = CharacterService->GetAvailableRaces();
// Returns: names, descriptions, ability bonuses, traits, subraces, etc.
```

### Character Creation Workflow
**Toolkit Integration:**
```cpp
// Single function call, no progression
FCharacterResult character = CreateCharacter(name, race, class, background);
```

**RPG-API Integration:**
```cpp
// Complete draft-based workflow
FString draftID = CreateCharacterDraft(playerID);
UpdateDraftRace(draftID, selectedRace);
UpdateDraftClass(draftID, selectedClass);
UpdateDraftAbilityScores(draftID, rolledStats);
UpdateDraftSkills(draftID, selectedSkills);
UpdateDraftEquipment(draftID, selectedEquipment);
FCharacterResult final = FinalizeDraft(draftID);
```

### Production Architecture Comparison
**Toolkit Integration:**
- Custom memory management (CGO cleanup)
- Custom error handling 
- Custom persistence layer needed
- Single-user only

**RPG-API Integration:**  
- Standard HTTP error codes
- Redis-backed persistence
- Session management
- Multi-player ready

## Decision

**Selected: Option 2 - RPG-API Integration**

### Implementation Strategy

**Phase 1: Parallel Implementation**
- Keep existing `RPGCharacterSubsystem` for toolkit testing
- Add new `RPGCharacterService` for production character creation
- Update T001 UI to use rpg-api integration

**Phase 2: Primary Integration**
- Complete T001 with full character creation workflow
- Leverage draft-based character creation
- Implement error handling and offline capabilities

**Phase 3: Future Expansion**
- Multi-player character sessions
- Advanced character features (spells, equipment, leveling)
- Cross-platform character portability

### Technical Implementation

**New UE Components:**
```
Source/Seshat/RPGCore/Api/
├── RPGAPIClient.h/.cpp           # HTTP client for rpg-api
├── RPGAPITypes.h                 # Request/Response structs
└── RPGCharacterService.h/.cpp    # High-level character service
```

**Key Integration Points:**
- **HTTP Client:** UE's built-in HTTP module (no external dependencies)
- **Data Format:** JSON over HTTP (simpler than binary gRPC)
- **Async Operations:** Blueprint-friendly delegate callbacks
- **Error Handling:** Standard HTTP status codes + custom error types

## Consequences

### Positive
- **T001 becomes production-ready** with real D&D data and complete workflow
- **Eliminates hardcoded data limitations** - all race/class/background data dynamic
- **Professional architecture patterns** - gRPC services, proper error handling
- **Multi-player foundation** - session management, player IDs built-in
- **Feature completeness** - skills, equipment, spells, character progression
- **Reduced UE complexity** - HTTP calls vs CGO memory management

### Negative
- **Infrastructure dependency** - requires local rpg-api server + Redis
- **Network complexity** - handle connectivity issues, timeouts, retries
- **Service management** - one more service to run during development
- **Learning curve** - HTTP client integration vs direct function calls

### Mitigation Strategies
- **Local development** - rpg-api server on localhost (minimal network issues)
- **Graceful degradation** - cache data locally, handle offline scenarios
- **Fallback option** - keep toolkit integration for toolkit-specific testing
- **Documentation** - clear setup instructions for rpg-api server

## Implementation Requirements

### Infrastructure Setup
1. **rpg-api server** running locally (port 50051)
2. **Redis instance** for character draft persistence
3. **HTTP connectivity** from UE to localhost

### UE Integration Work
1. **HTTP client wrapper** for rpg-api communication
2. **Data structure mapping** (rpg-api JSON → UE structs)
3. **Async callback system** for Blueprint integration
4. **Error handling** and retry logic

### Estimated Effort
- **Total: 8-12 hours** across 2-3 development sessions
- **Session 1:** Infrastructure setup + HTTP client (3-4 hours)
- **Session 2:** Character service implementation (3-4 hours)
- **Session 3:** T001 UI integration + testing (2-4 hours)

## Success Metrics

### Technical Success
- **Dynamic data loading** - race/class buttons populate from API
- **Draft workflow completion** - can create character through full process
- **API reliability** - >95% success rate for character creation operations
- **Performance** - <500ms response time for data queries

### User Experience Success
- **No hardcoded data** visible in character creation UI
- **Progress tracking** - clear indication of character creation progress  
- **Error recovery** - graceful handling of API failures
- **Feature completeness** - skill selection, equipment choices, etc.

## Related Decisions

- **A001**: CGO Memory Management Architecture - provides fallback integration approach
- **A002**: Character Storage Architecture - now handled server-side via rpg-api
- **T001**: Character Creation UI Integration Test - becomes production-ready with this decision

## Future Considerations

### Advanced Features Enabled
- **Character advancement** - leveling up, skill point allocation
- **Equipment management** - inventory, item effects on stats
- **Spell system** - spell lists, spell slot management
- **Multi-character parties** - session-based character management

### Cross-Platform Opportunities
- **Mobile/Web clients** - same gRPC APIs work across platforms
- **Character portability** - characters work in different game clients
- **Campaign management** - DM tools, session coordination

### Integration Opportunities
- **VTT Integration** - export characters to Roll20, Foundry VTT
- **D&D Beyond compatibility** - import/export character data
- **Custom rule systems** - extend beyond D&D 5e SRD

## Conclusion

**RPG-API integration provides the professional foundation needed for production character creation** while maintaining the learning value of our toolkit integration work.

This decision transforms T001 from a proof-of-concept with hardcoded data into a production-ready character creation system with complete D&D 5e SRD integration.

**The three-layer architecture (dnd5e-api → rpg-api → UE) provides:**
- Complete D&D 5e data access
- Professional service patterns
- Multi-player readiness
- Extensibility for future features

**Recommendation: Proceed with rpg-api integration while preserving toolkit integration for toolkit-specific development and testing.**