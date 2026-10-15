# 5. Repository Testing Strategy

## Status

Accepted

Date: 2025-07-01

## Context

Repositories form the critical data access layer in our architecture, interfacing directly with databases and other 
persistence mechanisms. Testing these components effectively is crucial for system reliability but presents unique 
challenges:

- Mocking database behavior is complex and can miss important integration points
- SQL/NoSQL queries often have subtle behaviors that are hard to verify with unit tests
- Database-specific features (like MongoDB's partial indexes) need real validation
- Schema changes and migrations need to be tested against actual databases
- Performance characteristics can only be properly assessed with real database interactions

We need to decide whether to use unit tests with mocks or integration tests with real databases for repository testing.

## Decision

We will implement repository tests as integration tests exclusively, avoiding unit tests with mocks for this layer. 
Key aspects of this approach:

1. **Test Environment**
   - Use real database instances (via Docker Compose)
   - Create unique databases for each test run
   - Clean up data after each test

2. **Test Scope**
   - Test actual SQL/NoSQL queries
   - Verify database constraints and indexes
   - Include error cases and edge conditions
   - Test transaction behavior where applicable

3. **Test Isolation**
   - Each test gets its own database
   - Clean state for every test run
   - No shared data between tests

4. **Test Data Management**
   - Use factories for test data creation for complex scenarios
   - Include data setup in test cases
   - Clear data cleanup strategies

## Consequences

### Positive

- Tests verify actual database behavior
- Catches real integration issues early
- No need to maintain complex database mocks
- Tests actual SQL/NoSQL queries
- Validates database constraints and indexes
- More confidence in database operations
- Better coverage of edge cases and error conditions

### Negative

- Slower test execution compared to unit tests
- Requires database setup for test runs
- More complex test environment setup
- CI/CD pipeline needs database support

### Neutral

- Different approach from other layers testing
- Need for careful test data management
- Regular database cleanup required

## Implementation Notes

### Test Structure Example

```go
type repositoryTestCase[P, W any] struct {
    name            string
    insertDocuments func(t *testing.T, coll *mongo.Collection)
    params          P
    want            W
    wantErr         error
}

func TestRepository_Operation(t *testing.T) {
    // Setup test database
    tdb := mongodb.NewTestDB(t)
    defer tdb.Close(t)

    // Initialize collection with indexes
    coll := setupTestCollection(t, tdb.DB)

    // Run test cases
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // Setup test data
            if tt.insertDocuments != nil {
                tt.insertDocuments(t, coll)
            }

            // Execute operation
            got, err := repository.Operation(tt.params)

            // Verify results
            assert.ErrorIs(t, err, tt.wantErr)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

### Database Setup

```go
func setupTestCollection(t *testing.T, db *mongo.Database) *mongo.Collection {
    coll := db.Collection("test_collection")

    // Create indexes
    indexModel := mongo.IndexModel{
        Keys: bson.D{{Key: "field", Value: 1}},
        Options: options.Index().SetUnique(true),
    }

    _, err := coll.Indexes().CreateOne(context.Background(), indexModel)
    if err != nil {
        t.Fatalf("Failed to create index: %v", err)
    }

    return coll
}
```

### Test Cases Example

```go
tests := []repositoryTestCase[CreateParams, Entity]{
    {
        name: "when unique constraint is violated, then it returns an error",
        insertDocuments: func(t *testing.T, coll *mongo.Collection) {
            // Insert document that will cause constraint violation
        },
        params: CreateParams{...},
        want: Entity{},
        wantErr: ErrUniqueViolation,
    },
    {
        name: "when valid data is provided, then it creates the entity",
        params: CreateParams{...},
        want: Entity{...},
        wantErr: nil,
    },
}
```

## Related Documents

- [ADR-0004: Integration Testing Framework](0004-integration-testing-framework.md)
- [ADR-0002: Table-Driven Tests Implementation](0002-table-driven-tests-implementation.md)
- [ADR-0003: Build Tags for Test Categorization](0003-build-tags-for-test-categorization.md)
- [MongoDB Go Driver Documentation](https://pkg.go.dev/go.mongodb.org/mongo-driver/mongo)

## Contributors

- Àlex Grau Roca
