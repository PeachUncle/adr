# ADR-021: Testing Strategy for Event-Sourced DDD Architecture

## Status

Proposed

## Decision Drivers

- Event sourcing and CQRS architecture complexity from ADR-006
- Domain-driven design patterns from ADR-005
- Multiple bounded contexts and aggregates
- Message bus integration from ADR-011
- Projection and read model validation from ADR-012
- API testing requirements from ADR-020

## Context

The personal portfolio platform uses event sourcing, CQRS, and DDD patterns which require specialized testing approaches. Traditional testing strategies don't adequately address:

- Event stream consistency and replay behavior
- Aggregate boundary enforcement and invariants
- Projection accuracy and eventual consistency
- Integration between command and query sides
- Event versioning and schema evolution from ADR-007

We need a comprehensive testing strategy that validates both business logic and architectural patterns while supporting rapid development cycles.

## Decision

### Testing Pyramid Adapted for Event Sourcing

```
                   E2E Tests (5%)
              ┌─────────────────────┐
              │ Business Scenarios  │
              │ User Journeys      │
              └─────────────────────┘

         Integration Tests (20%)
    ┌─────────────────────────────────┐
    │ Event Store Integration         │
    │ Projection Workers             │
    │ Message Bus Integration        │
    │ API Contract Testing           │
    └─────────────────────────────────┘

        Unit Tests (75%)
┌─────────────────────────────────────────┐
│ Domain Logic (Aggregates)              │
│ Event Handlers                         │
│ Command Handlers                       │
│ Value Objects & Entities               │
│ Domain Services                        │
└─────────────────────────────────────────┘
```

### Unit Testing Strategy

#### Domain Aggregate Testing

```typescript
// Test pattern for domain aggregates
describe('Project Aggregate', () => {
  describe('when creating a project', () => {
    it('should emit ProjectCreated event with correct data', () => {
      // Arrange
      const projectId = ProjectId.generate();
      const ownerId = UserId.generate();
      const command = new CreateProjectCommand(
        projectId,
        ownerId,
        'Test Project',
        'Description'
      );

      // Act
      const project = Project.create(command);
      const events = project.getUncommittedEvents();

      // Assert
      expect(events).toHaveLength(1);
      expect(events[0]).toBeInstanceOf(ProjectCreatedEvent);
      expect(events[0].projectId).toEqual(projectId);
      expect(events[0].ownerId).toEqual(ownerId);
    });

    it('should enforce business invariants', () => {
      // Test domain rules and constraints
      const invalidCommand = new CreateProjectCommand(
        ProjectId.generate(),
        UserId.empty(), // Invalid owner
        '', // Invalid title
        'Description'
      );

      expect(() => Project.create(invalidCommand)).toThrow(
        DomainValidationError
      );
    });
  });

  describe('when replaying events', () => {
    it('should restore aggregate state correctly', () => {
      // Test event sourcing replay
      const events = [
        new ProjectCreatedEvent(projectId, ownerId, 'Title', 'Description'),
        new ProjectUpdatedEvent(projectId, { title: 'New Title' }),
        new ProjectAccessGrantedEvent(
          projectId,
          UserId.generate(),
          AccessLevel.VIEW
        ),
      ];

      const project = Project.fromEvents(events);

      expect(project.title).toBe('New Title');
      expect(project.accessGrants).toHaveLength(1);
    });
  });
});
```

#### Command Handler Testing

```typescript
describe('CreateProjectCommandHandler', () => {
  let handler: CreateProjectCommandHandler;
  let projectRepository: Mock<ProjectRepository>;
  let eventPublisher: Mock<EventPublisher>;

  beforeEach(() => {
    projectRepository = createMock<ProjectRepository>();
    eventPublisher = createMock<EventPublisher>();
    handler = new CreateProjectCommandHandler(
      projectRepository,
      eventPublisher
    );
  });

  it('should create project and publish events', async () => {
    const command = new CreateProjectCommand(/* ... */);

    await handler.handle(command);

    expect(projectRepository.save).toHaveBeenCalledWith(
      expect.objectContaining({ id: command.projectId })
    );
    expect(eventPublisher.publishAll).toHaveBeenCalledWith(
      expect.arrayContaining([
        expect.objectContaining({ eventType: 'ProjectCreated' }),
      ])
    );
  });
});
```

#### Event Handler Testing

```typescript
describe('ProjectCreatedEventHandler', () => {
  it('should update projection when project is created', async () => {
    const event = new ProjectCreatedEvent(/* ... */);
    const projectionStore = createMock<ProjectionStore>();
    const handler = new ProjectCreatedEventHandler(projectionStore);

    await handler.handle(event);

    expect(projectionStore.upsert).toHaveBeenCalledWith(
      'project-catalog',
      expect.objectContaining({
        projectId: event.projectId,
        title: event.title,
      })
    );
  });
});
```

### Integration Testing Strategy

#### Test Database Configuration

**Local Development**: Developers use local Neon dev branches or in-memory event stores for fast iteration.

**CI/CD Pipeline**: Integration tests use dedicated Neon test branches (not generic PostgreSQL containers) to ensure:
- Tests validate against production-like infrastructure (Neon serverless)
- Serverless connection patterns are tested (connection pooling, cold starts)
- No architectural drift between test and production environments
- Neon-specific features are validated (branching, point-in-time recovery)

**Configuration**:
```yaml
# GitHub Actions - .github/workflows/test.yml
integration-tests:
  steps:
    - name: Install Doppler CLI
      uses: dopplerhq/cli-action@v3
    
    - name: Run integration tests
      run: doppler run -- npm run test:integration
      env:
        DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN_CI }}
        # DATABASE_URL automatically injected from Doppler (Neon test branch)
```

**Benefits**:
- ✅ Tests against actual Neon serverless Postgres
- ✅ Validates production connection patterns
- ✅ No mock databases or service containers
- ✅ Centralized secret management via Doppler
- ✅ Environment parity across dev/staging/CI/production

#### Event Store Integration Tests

```typescript
describe('Event Store Integration', () => {
  let eventStore: EventStore;
  let database: TestDatabase;

  beforeEach(async () => {
    // Uses DATABASE_URL from environment (Neon test branch in CI)
    database = await TestDatabase.create();
    eventStore = new NeonEventStore(database.connection);
  });

  afterEach(async () => {
    await database.cleanup();
  });

  it('should save and load events correctly', async () => {
    const aggregateId = ProjectId.generate();
    const events = [
      new ProjectCreatedEvent(/* ... */),
      new ProjectUpdatedEvent(/* ... */),
    ];

    await eventStore.saveEvents(aggregateId.toString(), events, 0);
    const loadedEvents = await eventStore.loadEvents(aggregateId.toString());

    expect(loadedEvents).toHaveLength(2);
    expect(loadedEvents[0].eventType).toBe('ProjectCreated');
  });

  it('should handle optimistic concurrency conflicts', async () => {
    const aggregateId = ProjectId.generate();
    const event1 = new ProjectCreatedEvent(/* ... */);
    const event2 = new ProjectUpdatedEvent(/* ... */);

    await eventStore.saveEvents(aggregateId.toString(), [event1], 0);

    // Attempt to save with wrong expected version
    await expect(
      eventStore.saveEvents(aggregateId.toString(), [event2], 0)
    ).rejects.toThrow(ConcurrencyError);
  });
});
```

#### Projection Worker Integration Tests

```typescript
describe('Projection Worker Integration', () => {
  let worker: ProjectionWorker;
  let eventStore: EventStore;
  let projectionStore: ProjectionStore;

  it('should rebuild projections from event history', async () => {
    // Arrange: Save events to event store
    const events = [
      new ProjectCreatedEvent(/* ... */),
      new UserRegisteredEvent(/* ... */),
      new ProjectAccessGrantedEvent(/* ... */),
    ];

    for (const event of events) {
      await eventStore.saveEvents(event.aggregateId, [event], 0);
    }

    // Act: Rebuild projection
    await worker.rebuildProjection('project-catalog');

    // Assert: Verify projection state
    const projection = await projectionStore.get('project-catalog');
    expect(projection.projects).toHaveLength(1);
    expect(projection.lastEventProcessed).toBeDefined();
  });
});
```

#### Message Bus Integration Tests

```typescript
describe('Message Bus Integration', () => {
  let messageBus: MessageBus;
  let testContainer: TestContainer;

  beforeEach(async () => {
    testContainer = await TestContainer.start(['kafka', 'zookeeper']);
    messageBus = new KafkaMessageBus(
      testContainer.getConnectionString('kafka')
    );
  });

  afterEach(async () => {
    await testContainer.stop();
  });

  it('should publish and consume events correctly', async () => {
    const receivedEvents: DomainEvent[] = [];

    await messageBus.subscribe('ProjectCreated', event => {
      receivedEvents.push(event);
    });

    const event = new ProjectCreatedEvent(/* ... */);
    await messageBus.publish(event);

    // Wait for message processing
    await waitFor(() => receivedEvents.length > 0);

    expect(receivedEvents[0]).toEqual(event);
  });
});
```

### End-to-End Testing Strategy

#### Business Scenario Testing

```typescript
describe('Project Management User Journey', () => {
  let app: TestApplication;
  let apiClient: APIClient;

  beforeEach(async () => {
    app = await TestApplication.start();
    apiClient = new APIClient(app.baseUrl);
  });

  it('should complete full project lifecycle', async () => {
    // User registration
    const registerResponse = await apiClient.commands.registerUser({
      email: 'test@example.com',
      name: 'Test User',
    });
    expect(registerResponse.status).toBe('accepted');

    // Login
    const authToken = await apiClient.auth.login(
      'test@example.com',
      'password'
    );
    apiClient.setAuth(authToken);

    // Create project
    const createProjectResponse = await apiClient.commands.createProject({
      title: 'My Test Project',
      description: 'A test project for E2E testing',
    });
    expect(createProjectResponse.status).toBe('accepted');
    const projectId = createProjectResponse.aggregateId;

    // Wait for projection update (eventual consistency)
    await waitFor(async () => {
      const projects = await apiClient.queries.getProjects();
      return projects.data.projects.length > 0;
    });

    // Verify project appears in listing
    const projectsResponse = await apiClient.queries.getProjects();
    expect(projectsResponse.data.projects).toContainEqual(
      expect.objectContaining({
        id: projectId,
        title: 'My Test Project',
      })
    );

    // Grant public access
    const grantAccessResponse = await apiClient.commands.grantProjectAccess({
      projectId,
      grantTo: 'PUBLIC',
      accessLevel: 'VIEW',
    });
    expect(grantAccessResponse.status).toBe('accepted');

    // Verify public access works (no auth)
    const publicClient = new APIClient(app.baseUrl);
    const publicProjectResponse =
      await publicClient.queries.getProject(projectId);
    expect(publicProjectResponse.data.project.title).toBe('My Test Project');
  });
});
```

### Contract Testing Strategy

#### API Contract Tests

```typescript
describe('API Contracts', () => {
  it('should match OpenAPI specification', async () => {
    const spec = await loadOpenAPISpec('./api/openapi.yaml');
    const validator = new OpenAPIValidator(spec);

    // Test all command endpoints
    const createProjectRequest = {
      title: 'Test Project',
      description: 'Test description',
    };

    const response = await apiClient.post(
      '/api/v1/commands/projects/create',
      createProjectRequest
    );

    expect(
      validator.validateRequest(
        'POST',
        '/api/v1/commands/projects/create',
        createProjectRequest
      )
    ).toBe(true);
    expect(
      validator.validateResponse(
        'POST',
        '/api/v1/commands/projects/create',
        response
      )
    ).toBe(true);
  });
});
```

#### Event Contract Tests

```typescript
describe('Event Contracts', () => {
  it('should validate event schemas', () => {
    const event = new ProjectCreatedEvent(
      ProjectId.generate(),
      UserId.generate(),
      'Test Project',
      'Description'
    );

    const schema = EventSchemaRegistry.getSchema('ProjectCreated', '1.0.0');
    const isValid = schema.validate(event);

    expect(isValid).toBe(true);
  });

  it('should handle event versioning correctly', () => {
    // Test event upcasting from ADR-007
    const oldEvent = {
      eventType: 'ProjectCreated',
      schemaVersion: '1.0.0',
      data: {
        /* old format */
      },
    };

    const upcaster = new ProjectCreatedUpcaster();
    const newEvent = upcaster.upcast(oldEvent, '2.0.0');

    expect(newEvent.schemaVersion).toBe('2.0.0');
    expect(newEvent.data).toMatchSchema(ProjectCreatedV2Schema);
  });
});
```

### Test Data Management

#### Test Data Builders

```typescript
class ProjectTestDataBuilder {
  private project: Partial<Project> = {};

  withTitle(title: string): ProjectTestDataBuilder {
    this.project.title = title;
    return this;
  }

  withOwner(owner: User): ProjectTestDataBuilder {
    this.project.owner = owner;
    return this;
  }

  build(): Project {
    return new Project({
      id: ProjectId.generate(),
      title: 'Default Title',
      description: 'Default Description',
      owner: UserTestDataBuilder.default().build(),
      ...this.project,
    });
  }

  static default(): ProjectTestDataBuilder {
    return new ProjectTestDataBuilder();
  }
}

// Usage in tests
const project = ProjectTestDataBuilder.default()
  .withTitle('Custom Title')
  .withOwner(someUser)
  .build();
```

### Performance Testing

#### Lighthouse CI Integration

```yaml
# .github/workflows/deploy-landing-page.yml
lighthouse-ci:
  needs: [deploy-staging, deploy-production]
  runs-on: ubuntu-latest
  steps:
    - name: Run Lighthouse CI against staging
      run: |
        pnpm run lighthouse:staging
```

**Performance Thresholds:**
- Performance Score: ≥ 90
- First Contentful Paint: < 1.8s
- Largest Contentful Paint: < 2.5s
- Cumulative Layout Shift: < 0.1
- Total Blocking Time: < 200ms

**Resource Budgets:**
- JavaScript: < 200KB
- CSS: < 50KB
- Images: < 500KB
- Total Page Size: < 1MB

**Implementation Details:**
- Lighthouse CI runs post-deployment on staging and production
- Configuration files use `.cjs` extension (CommonJS) to work with `"type": "module"` in package.json
- Tests HTML endpoints only (JSON APIs excluded)
- Reports uploaded as GitHub Actions artifacts
- Failures reported as warnings (non-blocking for deployment)

#### Load Testing for Event Processing

```typescript
describe('Event Processing Performance', () => {
  it('should handle high event throughput', async () => {
    const events = Array.from(
      { length: 1000 },
      () => new ProjectCreatedEvent(/* generate test data */)
    );

    const startTime = Date.now();

    await Promise.all(
      events.map(event => eventStore.saveEvents(event.aggregateId, [event], 0))
    );

    const duration = Date.now() - startTime;
    expect(duration).toBeLessThan(5000); // 5 second max for 1000 events
  });
});
```

## Rationale

### Event Sourcing Testing Focus

- **Event-first testing**: Validate behavior through events rather than state
- **Replay testing**: Ensure aggregates can be rebuilt from events
- **Eventual consistency**: Test async projection updates

### DDD Testing Patterns

- **Aggregate boundaries**: Test invariants and business rules within aggregates
- **Domain events**: Verify events capture business intent correctly
- **Ubiquitous language**: Test names and concepts match domain language

### Testing Pyramid Adaptation

- **Unit tests dominate**: Complex domain logic needs thorough unit testing
- **Integration focus**: Event sourcing integration points are critical
- **Minimal E2E**: Expensive but necessary for user journey validation

## Implementation Guidance

### Prerequisites

- All ADRs that define architecture must be implemented first
- Test infrastructure must align with production infrastructure (Neon branches for databases)
- Centralized secrets management (Doppler) must be configured
- Development team must understand event sourcing and DDD patterns

### Test Infrastructure Setup

#### Local Development

```bash
# Create personal Neon dev branch
neonctl branches create dev-$(whoami) --project-id <project-id>

# Configure local environment
doppler setup --project tomriddelsdell-infra --config dev_personal
```

#### CI/CD Environment

```bash
# Create dedicated CI test branch
neonctl branches create ci-test --project-id <project-id>

# Add to Doppler CI config
doppler secrets set DATABASE_URL "<neon-ci-connection-string>" \
  --project tomriddelsdell-infra --config ci_tests

# Create service token for GitHub Actions
doppler configs tokens create "GitHub Actions CI" \
  --config ci_tests --project tomriddelsdell-infra --plain

# Add token to GitHub repository
gh secret set DOPPLER_TOKEN_CI --body "<service-token>"
```

**Important**: Do NOT use generic PostgreSQL containers in CI. Use Neon test branches to ensure environment parity with production.

### Implementation Steps

1. **Set up test infrastructure**: Neon test branches, Doppler configs, service tokens
2. **Configure CI/CD pipeline**: GitHub Actions with Doppler integration
3. **Implement domain unit tests**: Start with aggregate testing patterns
4. **Add integration tests**: Event store, projection, message bus integration (using Neon)
6. **Create contract tests**: API and event schema validation
7. **Build E2E test suite**: Critical user journeys and business scenarios
8. **Add performance tests**: Event processing and projection performance

### Testing Tools and Frameworks

```typescript
// Recommended testing stack
const testingStack = {
  unitTesting: 'Jest + TypeScript',
  mocking: 'ts-mockito or jest.mock',
  integration: 'Testcontainers + Docker',
  e2e: 'Playwright or Cypress',
  performance: 'k6 or Artillery',
  contracts: 'Pact or OpenAPI validators',
};
```

### Validation Criteria

- All domain aggregates have comprehensive unit tests
- Integration tests cover all event sourcing components
- E2E tests cover critical business scenarios
- Test coverage > 90% for domain logic
- All API contracts validated against specifications

## Consequences

### Positive

- High confidence in domain logic correctness
- Early detection of architectural pattern violations
- Comprehensive regression testing for event sourcing
- Clear documentation of system behavior through tests
- Support for safe refactoring and evolution

### Negative

- Higher initial investment in test infrastructure
- Complexity of testing event-driven systems
- Learning curve for event sourcing testing patterns
- Additional maintenance overhead for test data and scenarios

### Neutral

- More test code to maintain alongside production code
- Need for specialized testing knowledge in the team

## Alternatives Considered

### Alternative 1: Traditional Testing Approach

- **Description**: Standard unit/integration/E2E without event sourcing focus
- **Pros**: Familiar patterns, existing tooling, simpler setup
- **Cons**: Doesn't validate event sourcing patterns, misses critical failure modes
- **Why rejected**: Inadequate for event-sourced architecture

### Alternative 2: Behavior-Driven Development (BDD)

- **Description**: Gherkin scenarios for all testing levels
- **Pros**: Business-readable tests, clear scenario documentation
- **Cons**: Overhead for technical unit tests, tool complexity
- **Why rejected**: Better suited as addition to, not replacement for, technical tests

### Alternative 3: Property-Based Testing Focus

- **Description**: Heavy use of property-based/fuzzing testing
- **Pros**: Excellent for finding edge cases, mathematical correctness
- **Cons**: Complex to set up, harder to debug failures
- **Why rejected**: Valuable addition but not primary strategy for business logic

## Related ADRs

### Dependencies

- **Requires**: ADR-005 (Domain Model) - Defines aggregates to test
- **Requires**: ADR-006 (Event Sourcing) - Testing patterns for event store
- **Requires**: ADR-007 (Event Versioning) - Testing event evolution
- **Requires**: ADR-011 (Message Bus) - Integration testing patterns
- **Requires**: ADR-012 (Projection Strategy) - Testing read model consistency
- **Requires**: ADR-020 (API Design) - API contract testing

### Influences

- **Influences**: All implementation ADRs - Testing validates implementation

### Conflicts

- **None identified** - Testing strategy supports all other ADRs

## AI Agent Guidance

### Implementation Priority

**High** - Critical for maintaining system quality and confidence

### Code Generation Patterns

```typescript
// Always generate test builders for domain objects
class EntityTestBuilder<T> {
  // Builder pattern implementation
}

// Always test aggregate event emission
expect(aggregate.getUncommittedEvents()).toContain(
  expect.objectContaining({ eventType: 'ExpectedEvent' })
);

// Always test event sourcing replay
const aggregate = AggregateType.fromEvents(testEvents);
```

### Common Pitfalls

- **Testing implementation details**: Focus on behavior, not internal state
- **Ignoring eventual consistency**: Use waitFor patterns for async operations
- **Inadequate test data**: Use builders for complex domain objects
- **Missing edge cases**: Test domain invariants and error conditions

### Integration Points

- Tests must validate all ADR-defined patterns
- Event tests must use schemas from ADR-007
- API tests must validate contracts from ADR-020
- Performance tests must align with ADR-010 observability

## Technical Debt Introduced

- **Test maintenance overhead**: Complex test scenarios require ongoing maintenance
- **Test data management**: Need strategy for managing test databases and fixtures
- **Test execution time**: Comprehensive test suite may become slow

## Evolution Path

- **Review trigger**: When test execution becomes too slow or maintenance burden high
- **Planned evolution**: Add mutation testing, improve performance testing
- **Migration strategy**: Gradual improvement of test quality and coverage

---

**Last Updated**: October 6, 2025

**Change History**:
- October 6, 2025: Added CI/CD database configuration guidance (Neon test branches)
- September 10, 2025: Initial version

