# ADR-005: Single Table DynamoDB Design

## Status
Accepted

## Context
During the goals service implementation, the backend team created separate DynamoDB tables for goals and goal activities. This violates our core architectural principle of using a single-table design pattern for DynamoDB.

The single-table design pattern is a DynamoDB best practice where multiple entity types are stored in one table using composite keys (partition key and sort key patterns). This approach is recommended by AWS and DynamoDB experts for several reasons.

## Decision
We will use a **single DynamoDB table** for ALL application entities including:
- Users
- Goals  
- Activities
- Journal entries
- Meals
- Workouts
- All future entities

### Table Design
```
Table Name: ai-lifestyle-app-main

Primary Key:
- PK (Partition Key): Entity identifier pattern
- SK (Sort Key): Sub-entity or relationship pattern

Entity Patterns:
- Users:       PK: USER#userId,        SK: PROFILE
- Goals:       PK: USER#userId,        SK: GOAL#goalId
- Activities:  PK: USER#userId,        SK: ACTIVITY#goalId#timestamp
- Journals:    PK: USER#userId,        SK: JOURNAL#entryId
- Meals:       PK: USER#userId,        SK: MEAL#mealId
```

### Global Secondary Indexes
- GSI1: Type/Status queries (e.g., all active goals)
- GSI2: Date-based queries (e.g., activities by date)
- GSI3: Cross-entity relationships

## Consequences

### Positive
- **Atomic Transactions**: Can update multiple related entities in a single transaction
- **Cost Efficiency**: One table with on-demand billing vs multiple tables
- **Simplified Operations**: Single table to monitor, backup, and scale
- **Rich Query Patterns**: GSIs enable complex access patterns
- **Consistent Performance**: Predictable performance characteristics
- **Data Locality**: Related data is physically stored together

### Negative
- **Learning Curve**: Developers need to understand single-table patterns
- **Complex Key Design**: Requires careful planning of PK/SK strategies
- **Migration Complexity**: Moving between patterns requires data migration

### Trade-offs Accepted
- We accept the initial complexity of designing access patterns in exchange for long-term operational simplicity
- We prioritize cost efficiency and performance over traditional normalized designs
- We commit to training developers on single-table patterns

## Implementation Notes

### Key Design Patterns
1. **Hierarchical Data**: USER#123 → GOAL#456 → ACTIVITY#timestamp
2. **Many-to-Many**: Use GSIs for inverse relationships
3. **Time Series**: Sort keys with timestamps for chronological data
4. **Status Queries**: GSI with status as partition key

### Anti-Patterns to Avoid
- Creating separate tables per entity type
- Using table names that imply single entity (e.g., "users", "goals")
- Scanning the entire table for queries
- Over-indexing with too many GSIs

### Migration Strategy
For existing multi-table implementations:
1. Design new single-table schema
2. Create data migration scripts
3. Run dual writes during transition
4. Verify data integrity
5. Cut over to single table
6. Remove old tables

## References
- [AWS DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [The What, Why, and When of Single-Table Design](https://www.alexdebrie.com/posts/dynamodb-single-table/)
- [DynamoDB Book by Alex DeBrie](https://www.dynamodbbook.com/)
- [AWS re:Invent DynamoDB Advanced Patterns](https://www.youtube.com/watch?v=HaEPXoXVf2k)

## Decision Date
2025-01-07

## Approvers
- Product Manager Agent
- Backend Team Lead
- Solutions Architect