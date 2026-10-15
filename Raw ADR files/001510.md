# ADR-004: Repository Pattern Implementation

## Status
Accepted

## Date
2025-01-14

## Context
The EdgeRush LootMan codebase needed a consistent approach to data access that:
- Abstracts database implementation details from business logic
- Enables testing of business logic without database dependencies
- Provides a clean separation between domain and infrastructure layers
- Supports multiple storage implementations (PostgreSQL, in-memory for testing)
- Follows Domain-Driven Design principles

Without a clear repository pattern, we had:
- Direct database access scattered throughout service classes
- Tight coupling between business logic and Spring Data
- Difficulty testing business logic in isolation
- Inconsistent data access patterns across the codebase

## Decision
We will implement the Repository Pattern with the following characteristics:

### Repository Interface in Domain Layer
Repository interfaces are defined in the domain layer and work with domain models:

```kotlin
// domain/loot/repository/LootAwardRepository.kt
interface LootAwardRepository {
    fun findById(id: LootAwardId): LootAward?
    fun findByRaiderId(raiderId: RaiderId): List<LootAward>
    fun findByGuildId(guildId: GuildId, activeOnly: Boolean = true): List<LootAward>
    fun save(lootAward: LootAward): LootAward
    fun delete(id: LootAwardId)
}
```

### Repository Implementation in Infrastructure Layer
Concrete implementations live in the infrastructure layer and handle persistence details:

```kotlin
// infrastructure/persistence/repository/JdbcLootAwardRepository.kt
@Repository
class JdbcLootAwardRepository(
    private val jdbcTemplate: JdbcTemplate,
    private val mapper: LootAwardMapper
) : LootAwardRepository {
    
    override fun findById(id: LootAwardId): LootAward? {
        val sql = "SELECT * FROM loot_awards WHERE id = ?"
        return jdbcTemplate.query(sql, mapper::toDomain, id.value)
            .firstOrNull()
    }
    
    // Other implementations...
}
```

### Entity-Domain Mapping
Separate entity classes for persistence with mappers to convert to/from domain models:

```kotlin
// infrastructure/persistence/entity/LootAwardEntity.kt
@Table("loot_awards")
data class LootAwardEntity(
    @Id val id: Long?,
    val itemId: Long,
    val raiderId: String,
    val guildId: String,
    val awardedAt: Instant,
    val flpsScore: Double,
    val tier: String,
    val status: String
)

// infrastructure/persistence/mapper/LootAwardMapper.kt
@Component
class LootAwardMapper {
    fun toDomain(entity: LootAwardEntity): LootAward {
        // Convert entity to domain model
    }
    
    fun toEntity(domain: LootAward): LootAwardEntity {
        // Convert domain model to entity
    }
}
```

### Repository Characteristics
- **Domain-Focused**: Work with domain models, not database entities
- **Collection-Like**: Provide collection-like interface (findById, save, delete)
- **Query Methods**: Named methods that express business intent
- **No Business Logic**: Pure data access, no business rules
- **Technology Agnostic**: Interface doesn't expose database details

## Consequences

### Positive
- **Testability**: Business logic can be tested with in-memory repositories
- **Separation of Concerns**: Domain layer independent of persistence technology
- **Flexibility**: Can swap database implementations without changing domain
- **Clear Contracts**: Repository interfaces document data access needs
- **Domain Purity**: Domain models don't need persistence annotations
- **Multiple Implementations**: Can have JDBC, JPA, in-memory implementations

### Negative
- **More Code**: Requires entity classes, mappers, and repository implementations
- **Mapping Overhead**: Converting between entities and domain models adds complexity
- **Learning Curve**: Team needs to understand the pattern and when to use it
- **Potential Performance**: Mapping adds slight overhead (usually negligible)

### Neutral
- **Spring Data**: Can still use Spring Data for implementation, just hidden behind interface
- **Transaction Management**: Handled at application layer (use case level)
- **Query Complexity**: Complex queries may require custom SQL in repository implementations

## Implementation Guidelines

### Repository Naming
- Interface: `{Entity}Repository` (e.g., `LootAwardRepository`)
- Implementation: `Jdbc{Entity}Repository` or `InMemory{Entity}Repository`

### Method Naming Conventions
- **Find**: `findById`, `findByRaiderId`, `findByGuildId`
- **Query**: `findAll`, `findActive`, `findByDateRange`
- **Save**: `save` (handles both create and update)
- **Delete**: `delete`, `deleteById`
- **Exists**: `existsById`, `existsByName`
- **Count**: `count`, `countByStatus`

### Return Types
- Single entity: `Entity?` (nullable for not found)
- Multiple entities: `List<Entity>` (empty list if none found)
- Existence check: `Boolean`
- Count: `Int` or `Long`

### Error Handling
- Return `null` for not found (single entity queries)
- Return empty list for no results (collection queries)
- Throw exceptions for infrastructure failures (database connection, etc.)
- Don't throw exceptions for business rule violations (that's domain layer's job)

### Testing Strategy
- **Unit Tests**: Use in-memory repository implementations
- **Integration Tests**: Test actual repository implementations with Testcontainers
- **Test Data Builders**: Create builders for domain models used in tests

## Examples

### In-Memory Repository for Testing
```kotlin
class InMemoryLootAwardRepository : LootAwardRepository {
    private val storage = mutableMapOf<LootAwardId, LootAward>()
    
    override fun findById(id: LootAwardId): LootAward? = storage[id]
    
    override fun save(lootAward: LootAward): LootAward {
        storage[lootAward.id] = lootAward
        return lootAward
    }
    
    // Other implementations...
}
```

### Usage in Use Case
```kotlin
@Service
class AwardLootUseCase(
    private val lootAwardRepository: LootAwardRepository,
    private val raiderRepository: RaiderRepository
) {
    fun execute(command: AwardLootCommand): Result<LootAward> = runCatching {
        val raider = raiderRepository.findById(command.raiderId)
            ?: throw RaiderNotFoundException(command.raiderId)
        
        val lootAward = LootAward.create(
            itemId = command.itemId,
            raiderId = command.raiderId,
            guildId = command.guildId,
            flpsScore = command.flpsScore,
            tier = command.tier
        )
        
        lootAwardRepository.save(lootAward)
    }
}
```

## Migration Strategy
- New code uses repository pattern from the start
- Existing code refactored incrementally by bounded context
- Spring Data repositories wrapped behind repository interfaces initially
- Gradual migration to JDBC-based implementations for better control

## Alternatives Considered

### Direct Spring Data Repositories
**Rejected**: Tight coupling to Spring Data, difficult to test, exposes persistence details to domain

### Active Record Pattern
**Rejected**: Mixes persistence logic with domain models, violates single responsibility

### DAO Pattern
**Rejected**: Too focused on database operations, doesn't align with DDD principles

## References
- [Repository Pattern by Martin Fowler](https://martinfowler.com/eaaCatalog/repository.html)
- [DDD Repository Pattern](https://www.domainlanguage.com/ddd/reference/)
- [Implementing Repository Pattern in Spring](https://www.baeldung.com/spring-data-repository-vs-dao)
