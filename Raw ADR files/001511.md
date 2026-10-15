# ADR-005: Use Case Pattern for Application Layer

## Status
Accepted

## Date
2025-01-14

## Context
The EdgeRush LootMan application needed a clear way to organize business operations and orchestrate domain logic. Without a consistent pattern, we had:
- Business logic scattered across controller and service classes
- Unclear transaction boundaries
- Difficulty understanding what operations the system supports
- Inconsistent error handling and validation
- Tight coupling between API layer and domain logic
- Challenges testing business workflows

We needed a pattern that:
- Makes system capabilities explicit
- Provides clear entry points for business operations
- Orchestrates domain services and repositories
- Handles cross-cutting concerns (transactions, validation, error handling)
- Enables testing business workflows independently of API layer

## Decision
We will implement the Use Case Pattern for the application layer, where each business operation is represented by a dedicated use case class.

### Use Case Structure
Each use case is a single-purpose class that orchestrates a specific business operation:

```kotlin
@Service
class AwardLootUseCase(
    private val lootAwardRepository: LootAwardRepository,
    private val lootBanRepository: LootBanRepository,
    private val lootDistributionService: LootDistributionService
) {
    @Transactional
    fun execute(command: AwardLootCommand): Result<LootAward> = runCatching {
        // 1. Validate inputs
        val raider = raiderRepository.findById(command.raiderId)
            ?: throw RaiderNotFoundException(command.raiderId)
        
        // 2. Check business rules
        val activeBans = lootBanRepository.findActiveByRaiderId(command.raiderId)
        if (activeBans.isNotEmpty()) {
            throw LootBanActiveException(raider, activeBans)
        }
        
        // 3. Execute domain logic
        val lootAward = LootAward.create(
            itemId = command.itemId,
            raiderId = command.raiderId,
            guildId = command.guildId,
            flpsScore = command.flpsScore,
            tier = command.tier
        )
        
        // 4. Persist changes
        lootAwardRepository.save(lootAward)
    }
}
```

### Command Objects
Use cases accept command objects that encapsulate all input parameters:

```kotlin
data class AwardLootCommand(
    val itemId: ItemId,
    val raiderId: RaiderId,
    val guildId: GuildId,
    val flpsScore: FlpsScore,
    val tier: LootTier
)
```

### Query Objects
For read operations, use query objects:

```kotlin
data class GetLootHistoryQuery(
    val guildId: GuildId,
    val activeOnly: Boolean = true
)
```

### Use Case Characteristics
- **Single Responsibility**: Each use case handles one business operation
- **Explicit**: Use case name clearly describes what it does
- **Orchestration**: Coordinates domain services and repositories
- **Transaction Boundary**: Use case defines transaction scope
- **Error Handling**: Converts domain exceptions to application-level results
- **No Business Logic**: Delegates to domain layer, doesn't contain business rules

## Consequences

### Positive
- **Explicit Operations**: System capabilities are clearly documented by use case classes
- **Testability**: Use cases can be tested independently of controllers
- **Clear Transactions**: Transaction boundaries are explicit and well-defined
- **Separation of Concerns**: API layer separated from business orchestration
- **Reusability**: Use cases can be called from multiple API endpoints or background jobs
- **Maintainability**: Changes to business workflows are localized to use cases
- **Documentation**: Use case names serve as living documentation
- **Consistent Error Handling**: All use cases follow same error handling pattern

### Negative
- **More Classes**: Each operation requires a dedicated use case class
- **Boilerplate**: Command/query objects add some boilerplate
- **Learning Curve**: Team needs to understand when to create new use cases
- **Potential Over-Engineering**: Very simple operations may feel heavyweight

### Neutral
- **One Use Case Per Operation**: Keeps classes small and focused
- **Command/Query Separation**: Different objects for writes vs reads
- **Result Type**: Use Kotlin Result type for error handling

## Implementation Guidelines

### Use Case Naming
- **Commands** (writes): `{Verb}{Noun}UseCase` (e.g., `AwardLootUseCase`, `ScheduleRaidUseCase`)
- **Queries** (reads): `Get{Noun}UseCase` (e.g., `GetLootHistoryUseCase`, `GetFlpsReportUseCase`)

### Method Naming
- Primary method: `execute(command/query)` or specific name like `awardLoot(command)`
- Return type: `Result<T>` for operations that can fail, direct type for queries

### Transaction Management
- Use `@Transactional` annotation on use case execute methods
- Transaction scope = use case execution
- Read-only transactions for query use cases: `@Transactional(readOnly = true)`

### Error Handling
- Use Kotlin `Result` type to wrap success/failure
- Convert domain exceptions to application-level exceptions if needed
- Let infrastructure exceptions bubble up (database connection, etc.)

### Validation
- Input validation in use case (command/query validation)
- Business rule validation in domain layer
- Don't duplicate validation logic

### Dependencies
- Inject repositories and domain services
- Don't inject other use cases (compose at controller level if needed)
- Keep dependencies minimal and focused

## Use Case Organization

### Package Structure
```
application/
├── flps/
│   ├── CalculateFlpsScoreUseCase.kt
│   ├── UpdateModifiersUseCase.kt
│   └── GetFlpsReportUseCase.kt
├── loot/
│   ├── AwardLootUseCase.kt
│   ├── ManageLootBansUseCase.kt
│   └── GetLootHistoryUseCase.kt
└── shared/
    ├── GetGuildConfigUseCase.kt
    └── UpdateGuildConfigUseCase.kt
```

### Command/Query Location
Commands and queries are defined in the same file or package as their use case:

```kotlin
// AwardLootUseCase.kt
data class AwardLootCommand(...)

@Service
class AwardLootUseCase(...) {
    fun execute(command: AwardLootCommand): Result<LootAward> { ... }
}
```

## Examples

### Command Use Case (Write Operation)
```kotlin
@Service
class ScheduleRaidUseCase(
    private val raidRepository: RaidRepository,
    private val raidSchedulingService: RaidSchedulingService
) {
    @Transactional
    fun execute(command: ScheduleRaidCommand): Result<Raid> = runCatching {
        // Validate scheduling rules
        raidSchedulingService.validateSchedule(
            command.scheduledDate,
            command.startTime,
            command.endTime
        )
        
        // Create raid
        val raid = Raid.schedule(
            guildId = command.guildId,
            scheduledAt = command.scheduledDate.atTime(command.startTime),
            difficulty = command.difficulty
        )
        
        // Persist
        raidRepository.save(raid)
    }
}
```

### Query Use Case (Read Operation)
```kotlin
@Service
class GetFlpsReportUseCase(
    private val flpsModifierRepository: FlpsModifierRepository,
    private val raiderRepository: RaiderRepository,
    private val flpsCalculationService: FlpsCalculationService
) {
    @Transactional(readOnly = true)
    fun execute(query: GetFlpsReportQuery): Result<FlpsReport> = runCatching {
        val modifiers = flpsModifierRepository.findByGuildId(query.guildId)
        val raiders = raiderRepository.findActiveByGuildId(query.guildId)
        
        val scores = raiders.map { raider ->
            RaiderFlpsScore(
                raider = raider,
                score = flpsCalculationService.calculateScore(raider, modifiers)
            )
        }
        
        FlpsReport(
            guildId = query.guildId,
            modifiers = modifiers,
            raiderScores = scores,
            generatedAt = Instant.now()
        )
    }
}
```

### Controller Integration
```kotlin
@RestController
@RequestMapping("/api/v1/loot")
class LootController(
    private val awardLootUseCase: AwardLootUseCase,
    private val getLootHistoryUseCase: GetLootHistoryUseCase
) {
    @PostMapping("/awards")
    fun awardLoot(@RequestBody request: AwardLootRequest): ResponseEntity<LootAwardResponse> {
        val command = request.toCommand()
        
        return awardLootUseCase.execute(command)
            .map { lootAward -> 
                ResponseEntity.status(HttpStatus.CREATED)
                    .body(LootAwardResponse.from(lootAward))
            }
            .getOrElse { exception ->
                throw ApiException.from(exception)
            }
    }
}
```

## Testing Strategy

### Unit Testing Use Cases
```kotlin
class AwardLootUseCaseTest {
    private val lootAwardRepository = mockk<LootAwardRepository>()
    private val lootBanRepository = mockk<LootBanRepository>()
    private val useCase = AwardLootUseCase(lootAwardRepository, lootBanRepository)
    
    @Test
    fun `should award loot when raider has no active bans`() {
        // Given
        val command = AwardLootCommand(...)
        every { lootBanRepository.findActiveByRaiderId(any()) } returns emptyList()
        every { lootAwardRepository.save(any()) } returns lootAward
        
        // When
        val result = useCase.execute(command)
        
        // Then
        result.isSuccess shouldBe true
        verify { lootAwardRepository.save(any()) }
    }
}
```

## Alternatives Considered

### Service Layer Pattern
**Rejected**: Too generic, doesn't make operations explicit, tends to accumulate unrelated methods

### CQRS with Separate Handlers
**Rejected**: Too complex for current needs, can evolve to this if needed

### Direct Controller to Domain
**Rejected**: Mixes API concerns with business orchestration, difficult to test

## Future Considerations
- **Domain Events**: Use cases could publish domain events for cross-context communication
- **CQRS**: Could separate command and query use cases into different patterns
- **Saga Pattern**: For complex multi-step operations across contexts
- **Use Case Composition**: For complex workflows that span multiple use cases

## References
- [Use Case Pattern](https://www.martinfowler.com/bliki/UseCases.html)
- [Application Layer in DDD](https://www.domainlanguage.com/ddd/reference/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
