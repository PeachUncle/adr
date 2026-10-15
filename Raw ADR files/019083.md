# ADR-005: Domain Model and Aggregates

## Status

Accepted

## Decision Drivers

- Business domain requirements from ADR-001 (Personal Portfolio Platform)
- Single-tenant architecture from ADR-002
- Event sourcing implementation needs from ADR-006
- Clear aggregate boundaries for consistency and performance
- Domain event design for CQRS and integration patterns

## Context

We need to define the core domain entities, their relationships, aggregate boundaries, and the key domain events for our personal portfolio platform. This will establish the foundation for our event-sourced system and guide all subsequent domain implementation decisions.

The domain model must support the business processes identified in ADR-001: portfolio presentation, app onboarding, user access management, and project demonstration.

## Decision

We propose the following domain model:

### Core Bounded Context: Portfolio Management

#### Aggregates and Their Responsibilities

##### 1. User Aggregate

- **Root Entity**: User
- **Value Objects**: UserId, Email, UserProfile
- **Responsibilities**:
  - User identity and authentication data
  - Profile information and preferences
  - Tenant-level permissions (since single-tenant per ADR-002)
- **Invariants**:
  - Email must be unique and valid
  - User must have at least one contact method
  - Profile must meet professional standards

##### 2. Project Aggregate

- **Root Entity**: Project
- **Value Objects**: ProjectId, ProjectMetadata, ProjectContent, AccessGrant
- **Responsibilities**:
  - Project lifecycle management (create, update, archive)
  - Content and metadata management
  - Access control and visibility rules
- **Invariants**:
  - Project must have an owner (User)
  - Public projects must meet quality standards
  - Access grants must have valid time bounds

##### 3. Contact Aggregate

- **Root Entity**: ContactRequest
- **Value Objects**: ContactId, ContactDetails, MessageContent
- **Responsibilities**:
  - Managing inbound contact requests
  - Communication workflow and status tracking
  - Response management and follow-up
- **Invariants**:
  - Contact requests must include valid email
  - Message content must meet minimum standards
  - Status transitions must follow defined workflow

#### Domain Events (Event Sourcing Integration)

**User Aggregate Events:**

```typescript
interface UserRegistered extends DomainEvent {
  userId: UserId;
  email: Email;
  registrationSource: string;
  tenantId: string; // Single tenant from ADR-002
}

interface UserProfileUpdated extends DomainEvent {
  userId: UserId;
  previousProfile: UserProfile;
  newProfile: UserProfile;
  updatedFields: string[];
}
```

**Project Aggregate Events:**

```typescript
interface ProjectCreated extends DomainEvent {
  projectId: ProjectId;
  ownerId: UserId;
  title: string;
  description: string;
  initialVisibility: ProjectVisibility;
}

interface ProjectContentUpdated extends DomainEvent {
  projectId: ProjectId;
  contentVersion: number;
  updatedSections: string[];
  updateReason: string;
}

interface ProjectAccessGranted extends DomainEvent {
  projectId: ProjectId;
  grantedTo: UserId | 'PUBLIC';
  accessLevel: AccessLevel;
  grantedBy: UserId;
  expirationDate?: Date;
}

interface ProjectAccessRevoked extends DomainEvent {
  projectId: ProjectId;
  revokedFrom: UserId | 'PUBLIC';
  revokedBy: UserId;
  reason: string;
}
```

**Contact Aggregate Events:**

```typescript
interface ContactRequestSubmitted extends DomainEvent {
  contactId: ContactId;
  fromEmail: Email;
  subject: string;
  messagePreview: string; // First 100 chars for privacy
  submissionSource: string;
}

interface ContactRequestProcessed extends DomainEvent {
  contactId: ContactId;
  processedBy: UserId;
  response: ResponseType;
  notes?: string;
}
```

### Event Schema Management with Avro

**Schema Definition Strategy:**
We use Apache Avro schemas for domain events to provide type safety, schema evolution, and cross-language support while maintaining JSON serialization compatibility for event store queryability.

```typescript
// Event schema registry structure
interface EventSchemaRegistry {
  // Schema versioning follows Avro evolution rules
  schemas: {
    [eventType: string]: {
      [version: string]: AvroSchema;
    };
  };

  // Runtime validation and serialization
  validator: {
    validateEvent(event: DomainEvent): ValidationResult;
    serializeToJson(event: DomainEvent): string;
    deserializeFromJson<T>(json: string, schema: AvroSchema): T;
  };
}
```

**Example Event Schema:**

```json
{
  "type": "record",
  "name": "ProjectCreated",
  "namespace": "portfolio.domain.events",
  "version": "1.0.0",
  "doc": "Published when a new project is created in the portfolio",
  "fields": [
    {
      "name": "eventId",
      "type": "string",
      "doc": "Unique identifier for this event occurrence"
    },
    {
      "name": "aggregateId",
      "type": "string",
      "doc": "ProjectId that this event relates to"
    },
    {
      "name": "aggregateVersion",
      "type": "long",
      "doc": "Version number of the aggregate after this event"
    },
    {
      "name": "occurredAt",
      "type": "long",
      "logicalType": "timestamp-millis",
      "doc": "When this event occurred"
    },
    {
      "name": "causedBy",
      "type": "string",
      "doc": "UserId who caused this event"
    },
    {
      "name": "projectData",
      "type": {
        "type": "record",
        "name": "ProjectCreatedData",
        "fields": [
          { "name": "ownerId", "type": "string" },
          { "name": "title", "type": "string" },
          { "name": "description", "type": "string" },
          {
            "name": "initialVisibility",
            "type": {
              "type": "enum",
              "name": "ProjectVisibility",
              "symbols": ["PRIVATE", "PUBLIC", "SHARED"]
            }
          }
        ]
      }
    }
  ]
}
```

**Schema Evolution Benefits:**

- **Backward Compatibility**: Add new fields with default values
- **Forward Compatibility**: Remove fields safely with proper versioning
- **Type Generation**: Generate TypeScript interfaces from schemas
- **Cross-Language Support**: Same schemas work in Java, TypeScript, Python
- **Contract Validation**: Ensure producers and consumers stay in sync

**Integration Points:**

- **ADR-006 (Event Sourcing)**: Events stored as Avro JSON, queryable and human-readable
- **ADR-007 (Event Versioning)**: Avro schema evolution provides structured versioning approach
- **ADR-011 (Message Bus)**: Schema registry validates integration events across bounded contexts
- **ADR-022 (Message Bus Architecture)**: Avro schemas define message bus contracts
- **ADR-023 (Contract Management)**: Domain events use Avro schemas; cross-service contracts use JSON Schema for broader language support

### Project Visibility Model (Access-Based)

Projects are considered "live" or "published" when they have public access grants. No explicit publication events are needed - visibility is determined by the presence of access grants:

- **Private**: No access grants exist (only owner can view)
- **Public**: Public access grant exists (anyone can view)
- **Shared**: Specific user access grants exist (selected users can view)

## Rationale

### Aggregate Boundary Decisions

- **User as separate aggregate**: Supports independent user management and profile updates without affecting projects
- **Project as aggregate root**: Encapsulates all project-related data and access rules, ensuring consistency
- **Contact as separate aggregate**: Isolates communication workflow from user/project concerns

### Event Design Principles

- **Rich domain events**: Include enough context for projection building without querying other aggregates
- **Privacy-aware events**: Sensitive data (like full message content) is not included in integration events
- **Access-based visibility**: Simpler than explicit lifecycle states, more flexible for business needs

### DDD Alignment

- **Ubiquitous Language**: All terms match business vocabulary from ADR-001
- **Bounded Context**: Single context for portfolio management aligns with business scale
- **Aggregate Consistency**: Each aggregate maintains its own invariants independently

## Implementation Guidance

### Prerequisites

- ADR-001 (Business Domain) must be understood
- ADR-002 (Tenant Architecture) must be implemented
- Development team must understand DDD aggregate patterns

### Implementation Steps

1. **Implement Value Objects**: Start with strongly-typed identifiers and value objects
2. **Create Aggregate Roots**: Implement each aggregate with basic creation and update operations
3. **Add Domain Events**: Implement event publishing for each state change
4. **Implement Invariants**: Add business rule validation to each aggregate
5. **Create Repositories**: Add persistence abstraction for each aggregate

### Domain Services Needed

```typescript
// ***please check*** if these domain services are needed
interface ProjectVisibilityService {
  calculateVisibility(project: Project): ProjectVisibility;
  canUserAccess(userId: UserId, projectId: ProjectId): boolean;
}

interface ContactWorkflowService {
  determineNextStep(contact: ContactRequest): WorkflowAction;
  escalateIfNeeded(contact: ContactRequest): boolean;
}
```

### Validation Criteria

- All aggregates can be loaded and saved independently
- Domain events are published for all state changes
- Business invariants are enforced within each aggregate
- No cross-aggregate transactions are required
- Event sourcing compatibility verified (JSON serializable events)

## Consequences

### Positive

- Clear ownership and responsibility boundaries
- Event-driven communication enables loose coupling
- Each aggregate can evolve independently
- Rich audit trail through domain events
- Supports event sourcing and CQRS patterns
- Access-based visibility provides business flexibility

### Negative

- Initial complexity for a simple portfolio site
- Eventual consistency between aggregates
- Learning curve for team members unfamiliar with DDD
- More complex testing due to event-driven nature

### Neutral

- Additional abstraction layer over simple CRUD operations
- Need for projection maintenance and synchronization

## Alternatives Considered

### Alternative 1: Single Aggregate Approach

- **Description**: Everything in one large Portfolio aggregate
- **Pros**: Simpler, strong consistency, fewer moving parts
- **Cons**: Violates aggregate size guidelines, poor separation of concerns
- **Why rejected**: Would become unwieldy as system grows, breaks DDD principles

### Alternative 2: Entity-per-Service Pattern

- **Description**: Separate microservices for User, Project, Contact
- **Pros**: Clear service boundaries, independent deployment
- **Cons**: Over-engineering for current scale, network complexity
- **Why rejected**: ADR-001 specifies personal portfolio scale, not enterprise

### Alternative 3: Explicit Project Lifecycle Events

- **Description**: ProjectPublished, ProjectArchived, ProjectDrafted events
- **Pros**: Explicit state management, clear workflow
- **Cons**: Less flexible than access-based model, more complex state machine
- **Why rejected**: Access grants provide more flexible visibility control

## Related ADRs

### Dependencies

- **Requires**: ADR-001 (Business Domain) - Defines the portfolio platform scope
- **Requires**: ADR-002 (Tenant Architecture) - Single tenant model affects User aggregate

### Influences

- **Influences**: ADR-006 (Event Sourcing) - Domain events must be serializable and replayable
- **Influences**: ADR-007 (Event Versioning) - Event schemas need evolution strategy
- **Influences**: ADR-012 (Projection Strategy) - Events feed read model projections

## AI Agent Guidance

### Implementation Priority

**High** - This is foundational for all domain logic implementation

### Code Generation Patterns

```typescript
// Avro-Enhanced Aggregate Root Pattern
abstract class AggregateRoot<TId> {
  private uncommittedEvents: DomainEvent[] = [];

  protected addEvent(event: DomainEvent): void {
    // Validate against Avro schema before adding
    this.eventSchemaValidator.validate(event);
    this.uncommittedEvents.push(event);
  }

  getUncommittedEvents(): DomainEvent[] {
    return [...this.uncommittedEvents];
  }

  markEventsAsCommitted(): void {
    this.uncommittedEvents = [];
  }
}

// Event Factory with Schema Validation
class EventFactory {
  static createProjectCreated(data: ProjectCreatedData): ProjectCreated {
    const event = {
      eventId: generateEventId(),
      eventType: 'ProjectCreated',
      aggregateId: data.projectId,
      aggregateVersion: data.version,
      occurredAt: new Date().getTime(),
      causedBy: data.ownerId,
      projectData: data,
    };

    // Validate against Avro schema
    SchemaRegistry.validate('ProjectCreated', event);
    return event;
  }
}

// Value Object Pattern
abstract class ValueObject {
  abstract equals(other: ValueObject): boolean;
  abstract toString(): string;
}
```

### Schema Management Patterns

```typescript
// Schema Registry Integration
interface SchemaRegistry {
  // ***please check*** if we need schema versioning strategy
  getSchema(eventType: string, version?: string): AvroSchema;
  validateEvent(eventType: string, eventData: unknown): ValidationResult;
  evolveSchema(eventType: string, newSchema: AvroSchema): SchemaEvolutionResult;
}

// Event Serialization
interface EventSerializer {
  toJson(event: DomainEvent): string;
  fromJson<T extends DomainEvent>(json: string, eventType: string): T;
  toBinary(event: DomainEvent): Uint8Array; // For performance-critical paths
}
```

### Common Pitfalls

- **Cross-aggregate transactions**: Never modify multiple aggregates in single transaction
- **Anemic domain model**: Ensure business logic stays in aggregates, not services
- **Large aggregates**: Keep aggregates focused on single business concept
- **Event coupling**: Don't couple events to specific projection needs

### Avro Schema Pitfalls

- **Schema Evolution**: Always follow Avro compatibility rules (add fields with defaults)
- **Field Naming**: Use consistent naming conventions across all schemas
- **Logical Types**: Use Avro logical types for timestamps, UUIDs, decimals
- **Documentation**: Include "doc" fields for all schema elements
- **Namespace Management**: Use consistent namespacing (e.g., portfolio.domain.events)

### Integration Points

- Events must be JSON serializable for ADR-006 (Event Sourcing)
- Access grants integrate with ADR-003 (Authentication Strategy)
- Domain events feed ADR-012 (Projection Strategy) read models

## Technical Debt Introduced

- **Testing Complexity**: Event-driven testing is more complex than simple unit tests
- **Avro Schema Management**: Need tooling for schema registry, validation, and code generation
- **Event Schema Evolution**: Must maintain backward compatibility across schema versions
- **Projection Synchronization**: Must maintain consistency between aggregates and projections
- **Schema Registry Dependency**: Additional infrastructure component for schema management

## Evolution Path

- **Trigger for Review**: When business processes from ADR-001 change significantly
- **Planned Evolution**: May split aggregates further as business complexity grows
- **Migration Strategy**: Event sourcing allows safe refactoring through event replay

---
