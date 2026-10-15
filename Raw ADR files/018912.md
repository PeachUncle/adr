# Use SwiftData Over CoreData for Persistence

- Status: accepted
- Deciders: Matthias Wallner Géhri
- Date: 2025-10-04

Technical Story: Milestone 1 Task 2.1 - Implement persistent storage for profiles, service configurations, and app settings

## Context and Problem Statement

The app needs a robust persistence layer for storing profiles, service configurations (Radarr, Sonarr, etc.), indexers, external modules, and app settings. This replaces the Flutter app's Hive-based database. Which persistence framework should we use?

## Decision Drivers

- **Swift 6 Compatibility**: Must work with strict concurrency checking
- **Type Safety**: Leverage Swift's type system for data models
- **Modern API**: Prefer modern, declarative API over legacy patterns
- **Migration Support**: Need schema evolution and data migration capabilities
- **Testing**: Easy to test with in-memory storage
- **Maintainability**: Simple API for solo indie development
- **Performance**: Efficient for local database operations
- **SwiftUI Integration**: Native support for SwiftUI data flow

## Considered Options

- **Option 1**: SwiftData (Apple's modern data persistence framework)
- **Option 2**: CoreData (Apple's mature persistence framework)
- **Option 3**: SQLite with GRDB.swift wrapper
- **Option 4**: Realm (third-party mobile database)

## Decision Outcome

Chosen option: **Option 1 - SwiftData**

SwiftData provides a modern, type-safe API with native Swift 6 concurrency support and seamless SwiftUI integration, making it ideal for new development.

### Consequences

- **Good**: Native Swift 6 concurrency with @MainActor isolation
- **Good**: Clean, declarative model definitions with @Model macro
- **Good**: Automatic SwiftUI integration via @Query
- **Good**: Simple schema evolution with MigrationPlan
- **Good**: Native support for complex types (dictionaries, arrays)
- **Good**: In-memory container for testing
- **Neutral**: Relatively new framework (iOS 17+, macOS 14+)
- **Bad**: Less mature than CoreData (fewer resources/examples)
- **Bad**: Some features still evolving

### Implementation Details

**Models Created**:

- Profile (multi-profile support)
- 8 service configurations (Radarr, Sonarr, Lidarr, etc.)
- Indexer (search providers)
- ExternalModule (dashboard widgets)
- AppSettings (app-wide preferences)

**Key Patterns**:

- @Model macro for model definitions
- @Attribute(.unique) for singleton enforcement
- Cascade delete rules for relationships
- ModelContainer with in-memory option for tests
- DataService wrapper for CRUD operations

**Migration Support**:

- SchemaV1 as initial release
- ThriftwoodMigrationPlan for future versions
- LegacyDataMigration service (placeholder for Hive import)

## Pros and Cons of the Options

### Option 1: SwiftData

- **Good**: Modern Swift 6 native API with concurrency support
- **Good**: Macro-based model definitions (less boilerplate)
- **Good**: Automatic SwiftUI integration via @Query
- **Good**: Simple schema migration with MigrationPlan
- **Good**: Native support for Codable and complex types
- **Good**: In-memory testing support
- **Good**: Apple-supported, will receive ongoing updates
- **Neutral**: Requires iOS 17+ / macOS 14+ (acceptable for new project)
- **Bad**: Fewer community resources than CoreData
- **Bad**: Some advanced features still maturing

### Option 2: CoreData

- **Good**: Very mature with extensive documentation
- **Good**: Battle-tested in production apps
- **Good**: Rich ecosystem of tools and examples
- **Good**: Advanced querying and performance optimization
- **Neutral**: Requires .xcdatamodeld file and generated classes
- **Bad**: Verbose API with NSManagedObject subclassing
- **Bad**: Complex concurrency model (contexts, coordinators)
- **Bad**: Less natural SwiftUI integration (requires @FetchRequest)
- **Bad**: Swift 6 concurrency requires workarounds

### Option 3: SQLite with GRDB.swift

- **Good**: Direct SQL control and optimization
- **Good**: Excellent performance for complex queries
- **Good**: Mature third-party library
- **Good**: Good Swift support and type safety
- **Neutral**: Requires SQL knowledge
- **Bad**: More boilerplate than SwiftData/CoreData
- **Bad**: Manual schema migration code
- **Bad**: Less SwiftUI integration
- **Bad**: Third-party dependency (maintenance risk)

### Option 4: Realm

- **Good**: Simple API and good performance
- **Good**: Mobile-optimized (sync support)
- **Good**: Cross-platform (iOS, Android)
- **Neutral**: Acquired by MongoDB
- **Bad**: Third-party dependency (vendor lock-in)
- **Bad**: Swift 6 concurrency support unclear
- **Bad**: Less SwiftUI integration than SwiftData
- **Bad**: Overkill for local-only storage

## More Information

### Testing Approach

All tests use in-memory ModelContainer:

```swift
let container = try ModelContainer(
    for: Profile.self, AppSettings.self, /* ... */,
    configurations: ModelConfiguration(isStoredInMemoryOnly: true)
)
```

### Schema Evolution

Future schema changes handled via MigrationPlan:

```swift
enum ThriftwoodMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [SchemaV1.self, SchemaV2.self]
    }

    static var stages: [MigrationStage] {
        [migrateV1toV2]
    }

    static let migrateV1toV2 = MigrationStage.custom(/* ... */)
}
```

### Legacy Migration

LegacyDataMigration service will import Hive data in future:

```swift
final class LegacyDataMigration {
    func importFromHive(at url: URL) async throws { /* ... */ }
}
```

## Related Decisions

- [0001: Single NavigationStack Per Coordinator](0001-single-navigationstack-per-coordinator.md) - SwiftData's @MainActor isolation aligns with SwiftUI navigation
- 0003: Swift 6 Approachable Concurrency - SwiftData's concurrency model influenced overall approach

## References

- [SwiftData Documentation](https://developer.apple.com/documentation/swiftdata)
- [WWDC23: Meet SwiftData](https://developer.apple.com/videos/play/wwdc2023/10187/)
- [WWDC23: Model your schema with SwiftData](https://developer.apple.com/videos/play/wwdc2023/10195/)
