# A002: Character Storage Architecture

**Date:** July 31, 2025  
**Status:** Accepted  
**Context:** Character integration implementation requires persistent storage solution

## Problem Statement

With D&D 5e character integration complete (P007), we need a storage architecture for persisting created characters. The decision impacts:

- **Development velocity**: How quickly can we iterate on character features?
- **Future multiplayer support**: Will our storage choices support networked gameplay?
- **Architecture flexibility**: Can we adapt to changing requirements without major rewrites?
- **Operational complexity**: What infrastructure dependencies do we introduce?

## Decision Drivers

### Primary Requirements
- Persistent character storage across UE sessions
- Support for multiple characters per user
- Serialization of complete `FCharacterResult` data structure
- Blueprint-accessible storage operations

### Strategic Considerations
- **Multiplayer Future**: "Multiplayer is in our hearts" - eventual networked gameplay
- **Learning Value**: Gain experience with patterns needed for larger systems
- **Migration Risk**: Avoid architectural decisions that require major rewrites later
- **Development Speed**: Need immediate productivity, not infrastructure delays

## Options Considered

### Option 1: Direct Local File Storage
```cpp
// Direct file I/O in character subsystem
bool URPGCharacterSubsystem::SaveCharacter(const FCharacterResult& Character)
{
    FString JSON = SerializeToJSON(Character);
    return FFileHelper::SaveStringToFile(JSON, *GetCharacterFilePath(Character.ID));
}
```

**Pros:**
- Immediate implementation, no dependencies
- Human-readable JSON files for debugging
- Uses UE's built-in file system APIs

**Cons:**
- Storage logic tightly coupled to character subsystem
- Difficult to swap storage backends later
- No abstraction for future Redis/database integration
- Multiplayer migration requires complete rewrite

### Option 2: Redis-First Approach
```cpp
// Direct Redis integration
bool URPGCharacterSubsystem::SaveCharacter(const FCharacterResult& Character)
{
    return RedisClient->Set(Character.ID, SerializeToJSON(Character));
}
```

**Pros:**
- Multiplayer-ready from day 1
- Teaches service-based architecture patterns
- No migration needed for networked gameplay

**Cons:**
- Operational complexity (Redis process management)
- Network dependency for local development
- Higher barrier to entry for testing
- Risk of Redis connection issues blocking development

### Option 3: Repository Pattern with Local Storage First
```cpp
// Abstract repository interface
class ICharacterRepository 
{
public:
    virtual bool SaveCharacter(const FString& ID, const FCharacterResult& Character) = 0;
    virtual TOptional<FCharacterResult> LoadCharacter(const FString& ID) = 0;
    virtual TArray<FString> ListCharacters() = 0;
};

// Start with local implementation
class ULocalFileCharacterRepository : public UObject, public ICharacterRepository
{
    // File-based implementation
};

// Future Redis implementation
class URedisCharacterRepository : public UObject, public ICharacterRepository  
{
    // Redis-based implementation
};
```

**Pros:**
- Clean separation between business logic and storage
- Zero migration cost when adding Redis support
- Can A/B test different storage backends
- Immediate productivity with local storage
- Forces good architectural practices from day 1

**Cons:**
- Additional abstraction layer complexity
- Slightly more initial implementation work

## Decision

**Selected: Option 3 - Repository Pattern with Local Storage First**

### Implementation Architecture

**Location:** `/Source/Seshat/RPGCore/Storage/`
```
RPGCore/Storage/
├── ICharacterRepository.h          # Abstract interface
├── LocalFileCharacterRepository.h  # Local file implementation  
└── LocalFileCharacterRepository.cpp
```

**Integration Pattern:**
```cpp
// RPGCharacterSubsystem uses repository abstraction
UPROPERTY()
TScriptInterface<ICharacterRepository> CharacterRepository;

// Initialize with local storage
void Initialize(FSubsystemCollectionBase& Collection) override
{
    CharacterRepository = NewObject<ULocalFileCharacterRepository>(this);
}
```

### Migration Path to Redis

When multiplayer support is needed:
1. Implement `URedisCharacterRepository` class
2. Swap repository implementation at startup
3. Zero changes to business logic code
4. Can fallback to local storage if Redis issues occur

### Storage Location Strategy

**Local Files:** `Saved/SaveGames/Characters/`
- Individual character files: `Character_{ID}.json`
- Metadata index: `CharacterIndex.json` (for fast listing)
- UE save game system integration for platform compatibility

## Consequences

### Positive
- **Immediate Development**: Can start building character management features today
- **Clean Architecture**: Repository pattern enforces good separation of concerns
- **Risk-Free Migration**: Redis transition becomes implementation detail, not architectural change
- **Testing Simplicity**: Local files are predictable, debuggable, no network dependencies
- **Learning Value**: Gain experience with abstraction patterns needed for larger systems

### Negative
- **Additional Complexity**: One more abstraction layer to maintain
- **Initial Implementation Cost**: Slightly more code to write upfront

### Mitigation Strategies
- **Blueprint Integration**: Make repository operations accessible from Blueprints
- **Error Handling**: Robust file I/O error handling with fallback mechanisms
- **Performance**: Lazy loading and caching for character metadata
- **Future Proofing**: Design interface to accommodate Redis patterns (async operations, connection management)

## Implementation Notes

### Interface Design Principles
- **Async-Ready**: Interface designed to accommodate future async Redis operations
- **Error Handling**: Return types that support both success/failure and error details
- **Batch Operations**: Support for bulk operations (list all characters, bulk save)
- **Blueprint Accessible**: UE Object-based design for Blueprint integration

### File Format Strategy
```json
// Character_{ID}.json
{
  "id": "character_123",
  "name": "Thorin Ironforge", 
  "characterData": {
    // Complete FCharacterResult serialization
  },
  "metadata": {
    "created": "2025-07-31T10:30:00Z",
    "lastModified": "2025-07-31T10:30:00Z"
  }
}
```

## Related Decisions

- **A001**: CGO Memory Management Architecture - Establishes automatic cleanup patterns for character data
- **P007**: Character Integration Implementation Plan - Provides the `FCharacterResult` structure being stored

## Future Considerations

### Redis Integration Requirements
When implementing `URedisCharacterRepository`:
- Connection pooling and retry logic
- Async operation support with UE's async task system
- Redis key naming conventions for multi-user support
- Serialization format compatibility between local and Redis storage

### Additional Storage Backends
Repository pattern enables future backends:
- **Database Integration**: SQL Server, PostgreSQL for complex queries
- **Cloud Storage**: AWS S3, Azure Blob for backup/sync
- **Hybrid Approaches**: Local cache + cloud persistence

## Conclusion

The repository pattern with local storage first provides the optimal balance of immediate productivity and future flexibility. This decision enables rapid character system development while establishing the architectural foundation needed for multiplayer support.

The abstraction cost is minimal compared to the migration cost savings when Redis integration becomes necessary. This approach embodies the principle of "design for change" while maintaining practical development velocity.