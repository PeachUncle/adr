````markdown
# ADR-007: Event Versioning and Schema Evolution Strategy

## Status

Accepted

## Decision Drivers

- Event sourcing immutability requirements from ADR-006
- Long-term maintainability of event streams
- Need to evolve domain model while preserving historical events
- Support for event replay and projection rebuilding
- Minimize downtime during schema changes
- Real-world complexity of schema evolution scenarios

## Context

The platform uses **Event Sourcing** with NeonDB (Postgres) as the event store and Kafka as the streaming bus per ADR-006 and ADR-011. Events are the source of truth and must be immutable. Over time, domain models evolve, requiring schema changes.

We need a comprehensive, provider-agnostic strategy for event versioning and schema evolution that preserves replayability and minimizes consumer breakage across all realistic evolution scenarios.

**Key Challenges:**

- Historical events cannot be modified (immutability principle)
- New code must handle old event formats during replay
- Projection rebuilds must work across all event versions
- Schema changes should not break existing consumers
- Evolution strategy must work across different deployment environments
- Complex multi-version scenarios during system evolution

## Decision

### Comprehensive Versioning Strategy: Advanced Hybrid Approach

We will use an **advanced hybrid versioning strategy** that combines:

1. **Schema versioning** with semantic versioning (v1.0.0, v1.1.0, v2.0.0)
2. **Weak schema evolution** for backward-compatible changes
3. **Strong schema evolution** for breaking changes with explicit upcasting
4. **Multi-version tolerance** for complex evolution scenarios
5. **Schema deprecation lifecycle** for long-term maintenance

### Enhanced Event Schema Structure

```typescript
interface VersionedDomainEvent {
  // Required versioning fields
  eventId: string;
  eventType: string;
  schemaVersion: string; // Semantic version (e.g., "1.2.0")

  // Event sourcing fields (from ADR-006)
  aggregateId: string;
  aggregateType: string;
  aggregateVersion: number;
  timestamp: Date;

  // Enhanced metadata for comprehensive evolution tracking
  metadata: {
    schemaEvolution?: {
      originalVersion: string;
      migrationPath?: string[];
      upcastedAt?: Date;
      upcastedBy?: string; // Service/component that performed upcasting
    };
    compatibility?: {
      backwardCompatibleWith?: string[]; // List of versions this event is compatible with
      forwardCompatibleWith?: string[]; // List of versions this event will work with
    };
    deprecation?: {
      deprecated: boolean;
      deprecatedAt?: Date;
      supersededBy?: string; // Version that replaces this one
      removalScheduled?: Date;
    };
    // Other metadata from ADR-006
  };

  // Event data
  data: Record<string, any>;
}
```

### Evolution Rules and Advanced Compatibility

#### Backward Compatible Changes (Patch/Minor Versions)

**Allowed operations with detailed examples:**

**Adding Optional Fields (Minor Version)**

```typescript
// v1.0.0 → v1.1.0 (Minor: Add optional field)
interface UserRegisteredV1_0_0 {
  userId: string;
  email: string;
  registrationSource: string;
}

interface UserRegisteredV1_1_0 {
  userId: string;
  email: string;
  registrationSource: string;
  referralCode?: string; // New optional field
  marketingPreferences?: {
    emailOptIn: boolean;
    smsOptIn: boolean;
  }; // New optional nested object
}

// Upcasting handler for this change
class UserRegisteredMinorUpcaster implements EventUpcaster {
  upcast(event: VersionedDomainEvent): VersionedDomainEvent {
    const v1Data = event.data as UserRegisteredV1_0_0;
    const v1_1Data: UserRegisteredV1_1_0 = {
      ...v1Data,
      // Optional fields get default values during upcasting
      referralCode: undefined, // Explicitly undefined for old events
      marketingPreferences: undefined, // Will be handled by business logic defaults
    };

    return this.createUpcastedEvent(event, '1.1.0', v1_1Data);
  }
}
```

**Expanding Enums (Minor Version)**

```typescript
// v1.1.0 → v1.2.0 (Minor: Expand enum values)
interface ProjectCreatedV1_1_0 {
  projectId: string;
  projectType: 'PERSONAL' | 'TEAM';
  settings: ProjectSettings;
}

interface ProjectCreatedV1_2_0 {
  projectId: string;
  projectType: 'PERSONAL' | 'TEAM' | 'ENTERPRISE' | 'TRIAL'; // Added new types
  settings: ProjectSettings;
}

// No upcasting needed - old values remain valid
```

**Adding Metadata Fields (Patch Version)**

```typescript
// v1.2.0 → v1.2.1 (Patch: Add metadata for debugging)
// Metadata additions don't require data structure changes
// Simply update schema to include new metadata possibilities
```

#### Breaking Changes (Major Versions)

**Operations requiring major version bump with comprehensive examples:**

**Field Type Changes (Major Version)**

```typescript
// v1.x.x → v2.0.0 (Major: Field type change)
interface ProjectCreatedV1 {
  projectId: string;
  tags: string; // Comma-separated string
  createdAt: string; // ISO string format
  settings: {
    visibility: string; // 'public' | 'private'
  };
}

interface ProjectCreatedV2 {
  projectId: string;
  tags: string[]; // Array of strings
  createdAt: Date; // Proper Date object
  settings: {
    visibility: {
      level: 'PUBLIC' | 'PRIVATE' | 'RESTRICTED';
      restrictions?: string[];
    }; // Complex object instead of simple string
  };
}

class ProjectCreatedMajorUpcaster implements EventUpcaster {
  upcast(event: VersionedDomainEvent): VersionedDomainEvent {
    const v1Data = event.data as ProjectCreatedV1;
    const v2Data: ProjectCreatedV2 = {
      projectId: v1Data.projectId,
      // String to array conversion with proper parsing
      tags: v1Data.tags
        ? v1Data.tags
            .split(',')
            .map(tag => tag.trim())
            .filter(Boolean)
        : [],
      // String to Date conversion with validation
      createdAt: new Date(v1Data.createdAt),
      // Simple string to complex object conversion
      settings: {
        visibility: {
          level: v1Data.settings.visibility.toUpperCase() as
            | 'PUBLIC'
            | 'PRIVATE',
          restrictions:
            v1Data.settings.visibility === 'private'
              ? ['OWNER_ONLY']
              : undefined,
        },
      },
    };

    return this.createUpcastedEvent(event, '2.0.0', v2Data, ['1.x.x→2.0.0']);
  }
}
```

**Event Splitting (Major Version)**

```typescript
// v2.x.x → v3.0.0 (Major: Split single event into multiple events)
interface UserAccountCreatedV2 {
  userId: string;
  email: string;
  profile: {
    firstName: string;
    lastName: string;
    preferences: UserPreferences;
  };
  subscription: {
    planId: string;
    billingInfo: BillingInfo;
  };
}

// Split into multiple focused events in v3
interface UserRegisteredV3 {
  userId: string;
  email: string;
}

interface UserProfileCreatedV3 {
  userId: string;
  firstName: string;
  lastName: string;
  preferences: UserPreferences;
}

interface UserSubscriptionCreatedV3 {
  userId: string;
  planId: string;
  billingInfo: BillingInfo;
}

class UserAccountSplittingUpcaster implements EventUpcaster {
  upcast(event: VersionedDomainEvent): VersionedDomainEvent[] {
    const v2Data = event.data as UserAccountCreatedV2;

    // Return multiple events for complex splitting scenarios
    return [
      this.createUpcastedEvent(
        event,
        '3.0.0',
        {
          userId: v2Data.userId,
          email: v2Data.email,
        } as UserRegisteredV3,
        ['2.x.x→3.0.0-registration']
      ),

      this.createDerivedEvent(event, 'UserProfileCreated', '3.0.0', {
        userId: v2Data.userId,
        firstName: v2Data.profile.firstName,
        lastName: v2Data.profile.lastName,
        preferences: v2Data.profile.preferences,
      } as UserProfileCreatedV3),

      this.createDerivedEvent(event, 'UserSubscriptionCreated', '3.0.0', {
        userId: v2Data.userId,
        planId: v2Data.subscription.planId,
        billingInfo: v2Data.subscription.billingInfo,
      } as UserSubscriptionCreatedV3),
    ];
  }
}
```

### Advanced Upcasting Strategy

#### Multi-Version Tolerance Framework

```typescript
interface AdvancedEventUpcaster {
  canUpcast(eventType: string, fromVersion: string, toVersion: string): boolean;
  upcast(
    event: VersionedDomainEvent
  ): VersionedDomainEvent | VersionedDomainEvent[];
  getCompatibilityMatrix(): VersionCompatibilityMatrix;
  validateUpcasting(
    originalEvent: VersionedDomainEvent,
    upcastedEvents: VersionedDomainEvent[]
  ): boolean;
}

interface VersionCompatibilityMatrix {
  [eventType: string]: {
    [fromVersion: string]: {
      compatibleTargets: string[];
      migrationPaths: {
        [toVersion: string]: {
          path: string[];
          complexity: 'SIMPLE' | 'COMPLEX' | 'DANGEROUS';
          dataLossRisk: boolean;
          requiresManualReview: boolean;
        };
      };
    };
  };
}

class ComprehensiveEventUpcaster implements AdvancedEventUpcaster {
  private compatibilityMatrix: VersionCompatibilityMatrix = {
    UserRegistered: {
      '1.0.0': {
        compatibleTargets: ['1.1.0', '1.2.0', '2.0.0'],
        migrationPaths: {
          '1.1.0': {
            path: ['1.0.0→1.1.0'],
            complexity: 'SIMPLE',
            dataLossRisk: false,
            requiresManualReview: false,
          },
          '2.0.0': {
            path: ['1.0.0→1.2.0', '1.2.0→2.0.0'],
            complexity: 'COMPLEX',
            dataLossRisk: false,
            requiresManualReview: true,
          },
        },
      },
    },
  };

  canUpcast(
    eventType: string,
    fromVersion: string,
    toVersion: string
  ): boolean {
    const eventMatrix = this.compatibilityMatrix[eventType];
    if (!eventMatrix || !eventMatrix[fromVersion]) return false;

    return eventMatrix[fromVersion].compatibleTargets.includes(toVersion);
  }

  upcast(
    event: VersionedDomainEvent
  ): VersionedDomainEvent | VersionedDomainEvent[] {
    const migrationPath = this.getMigrationPath(
      event.eventType,
      event.schemaVersion,
      this.targetVersion
    );

    let currentEvent = event;
    const migrationSteps: string[] = [];

    // Execute multi-step migration if needed
    for (const step of migrationPath) {
      const stepUpcaster = this.getUpcasterForStep(step);
      const upcastedEvent = stepUpcaster.upcast(currentEvent);

      if (Array.isArray(upcastedEvent)) {
        // Handle event splitting scenarios
        return this.handleEventSplitting(upcastedEvent, migrationSteps);
      }

      currentEvent = upcastedEvent;
      migrationSteps.push(step);
    }

    // Add complete migration path to metadata
    return {
      ...currentEvent,
      metadata: {
        ...currentEvent.metadata,
        schemaEvolution: {
          ...currentEvent.metadata?.schemaEvolution,
          migrationPath: migrationSteps,
          upcastedAt: new Date(),
          upcastedBy: 'ComprehensiveEventUpcaster',
        },
      },
    };
  }

  validateUpcasting(
    originalEvent: VersionedDomainEvent,
    upcastedEvents: VersionedDomainEvent[]
  ): boolean {
    // Implement comprehensive validation logic
    return (
      this.validateDataIntegrity(originalEvent, upcastedEvents) &&
      this.validateBusinessRules(originalEvent, upcastedEvents) &&
      this.validateSchemaCompliance(upcastedEvents)
    );
  }
}
```

#### Event Store Integration with Advanced Features

```typescript
class AdvancedVersionedEventStore {
  private upcasters: Map<string, AdvancedEventUpcaster[]> = new Map();
  private schemaRegistry: EventSchemaRegistry;
  private migrationTracker: MigrationTracker;

  async loadEvents(
    aggregateId: string,
    targetVersion?: string,
    options: {
      includeDeprecated?: boolean;
      validateUpcasting?: boolean;
      migrationStrategy?: 'LAZY' | 'EAGER' | 'HYBRID';
    } = {}
  ): Promise<VersionedDomainEvent[]> {
    const rawEvents = await this.eventStore.loadEvents(aggregateId);
    const processedEvents: VersionedDomainEvent[] = [];

    for (const event of rawEvents) {
      // Skip deprecated events if requested
      if (!options.includeDeprecated && (await this.isDeprecated(event))) {
        continue;
      }

      if (targetVersion && event.schemaVersion !== targetVersion) {
        const upcastedEvents = await this.upcastEvent(
          event,
          targetVersion,
          options
        );
        processedEvents.push(...upcastedEvents);
      } else {
        processedEvents.push(event);
      }
    }

    return processedEvents;
  }

  private async upcastEvent(
    event: VersionedDomainEvent,
    targetVersion: string,
    options: any
  ): Promise<VersionedDomainEvent[]> {
    const upcasters = this.upcasters.get(event.eventType) || [];

    for (const upcaster of upcasters) {
      if (
        upcaster.canUpcast(event.eventType, event.schemaVersion, targetVersion)
      ) {
        const upcastedEvents = upcaster.upcast(event);
        const eventsArray = Array.isArray(upcastedEvents)
          ? upcastedEvents
          : [upcastedEvents];

        // Validate upcasting if requested
        if (
          options.validateUpcasting &&
          !upcaster.validateUpcasting(event, eventsArray)
        ) {
          throw new UpcastingValidationError(
            `Upcasting validation failed for ${event.eventType}`
          );
        }

        // Track migration for analytics and debugging
        await this.migrationTracker.recordMigration(event, eventsArray);

        return eventsArray;
      }
    }

    // Enhanced fallback behavior with better error context
    throw new NoUpcasterFoundError(
      `No upcaster found for ${event.eventType} ${event.schemaVersion} → ${targetVersion}`,
      {
        eventId: event.eventId,
        availableVersions: await this.schemaRegistry.getVersions(
          event.eventType
        ),
        migrationMatrix: await this.getCompatibilityMatrix(event.eventType),
      }
    );
  }
}
```

### Comprehensive Schema Registry Integration

```typescript
interface AdvancedEventSchema {
  eventType: string;
  version: string;
  schema: JSONSchema;
  compatibilityLevel: 'BACKWARD' | 'FORWARD' | 'FULL' | 'NONE';
  deprecated?: {
    deprecatedAt: Date;
    supersededBy?: string;
    removalScheduledAt?: Date;
    migrationGuide?: string;
  };
  examples: {
    valid: any[];
    invalid: any[];
    upcastingExamples?: {
      from: string;
      to: string;
      before: any;
      after: any;
    }[];
  };
  changelog: {
    version: string;
    changes: string[];
    breakingChanges: string[];
    migrationNotes: string[];
  }[];
}

class AdvancedEventSchemaRegistry {
  async validateEvent(event: VersionedDomainEvent): Promise<ValidationResult> {
    const schema = await this.getSchema(event.eventType, event.schemaVersion);
    const validationResult = this.validator.validate(event.data, schema.schema);

    if (!validationResult.valid) {
      return {
        valid: false,
        errors: validationResult.errors,
        suggestions: await this.generateValidationSuggestions(event, schema),
        compatibleVersions: await this.findCompatibleVersions(event),
      };
    }

    return {
      valid: true,
      metadata: {
        schemaCompliance: 'FULL',
        deprecationWarnings: schema.deprecated
          ? [this.generateDeprecationWarning(schema)]
          : [],
      },
    };
  }

  async getLatestVersion(eventType: string): Promise<string> {
    const schemas = await this.getSchemasForType(eventType);
    return schemas
      .filter(
        s =>
          !s.deprecated ||
          !s.deprecated.removalScheduledAt ||
          s.deprecated.removalScheduledAt > new Date()
      )
      .sort((a, b) => semver.compare(b.version, a.version))[0]?.version;
  }

  async planMigration(
    eventType: string,
    fromVersion: string,
    toVersion: string
  ): Promise<MigrationPlan> {
    const compatibility = await this.getCompatibilityMatrix(eventType);
    const migrationPath = this.findOptimalMigrationPath(
      fromVersion,
      toVersion,
      compatibility
    );

    return {
      fromVersion,
      toVersion,
      migrationPath,
      estimatedComplexity: this.calculateMigrationComplexity(migrationPath),
      dataLossRisk: this.assessDataLossRisk(migrationPath),
      requiredUpcasters: await this.getRequiredUpcasters(migrationPath),
      testingRecommendations:
        this.generateTestingRecommendations(migrationPath),
    };
  }
}
```

## Comprehensive Implementation Examples

### Real-World Evolution Scenario: User Management System

```typescript
// Evolution timeline showing realistic progression

// v1.0.0 - Initial simple user registration
interface UserRegisteredV1_0_0 {
  userId: string;
  email: string;
  registeredAt: string;
}

// v1.1.0 - Add optional profile information (backward compatible)
interface UserRegisteredV1_1_0 {
  userId: string;
  email: string;
  registeredAt: string;
  profile?: {
    firstName?: string;
    lastName?: string;
  };
}

// v1.2.0 - Add marketing preferences (backward compatible)
interface UserRegisteredV1_2_0 {
  userId: string;
  email: string;
  registeredAt: string;
  profile?: {
    firstName?: string;
    lastName?: string;
  };
  marketingPreferences?: {
    emailOptIn: boolean;
    smsOptIn: boolean;
    updatedAt: string;
  };
}

// v2.0.0 - Breaking change: Split into focused events and improve typing
interface UserRegisteredV2_0_0 {
  userId: string;
  email: string;
  registeredAt: Date; // Changed from string to Date
  registrationSource: 'ORGANIC' | 'REFERRAL' | 'SOCIAL' | 'IMPORT'; // New required field
}

// Separate profile event introduced in v2.0.0
interface UserProfileCreatedV2_0_0 {
  userId: string;
  profile: {
    firstName: string; // Now required
    lastName: string; // Now required
    displayName?: string;
  };
  createdAt: Date;
}

// Complex upcaster handling the v1.x.x → v2.0.0 migration
class UserRegistrationV2Upcaster implements AdvancedEventUpcaster {
  canUpcast(
    eventType: string,
    fromVersion: string,
    toVersion: string
  ): boolean {
    return (
      eventType === 'UserRegistered' &&
      semver.satisfies(fromVersion, '1.x.x') &&
      semver.satisfies(toVersion, '2.x.x')
    );
  }

  upcast(event: VersionedDomainEvent): VersionedDomainEvent[] {
    const v1Data = event.data as
      | UserRegisteredV1_0_0
      | UserRegisteredV1_1_0
      | UserRegisteredV1_2_0;

    // Primary user registration event
    const userRegisteredV2: UserRegisteredV2_0_0 = {
      userId: v1Data.userId,
      email: v1Data.email,
      registeredAt: new Date(v1Data.registeredAt),
      registrationSource: 'ORGANIC', // Default for old events
    };

    const events: VersionedDomainEvent[] = [
      this.createUpcastedEvent(event, '2.0.0', userRegisteredV2, [
        '1.x.x→2.0.0',
      ]),
    ];

    // Create separate profile event if profile data exists
    if (
      'profile' in v1Data &&
      v1Data.profile &&
      v1Data.profile.firstName &&
      v1Data.profile.lastName
    ) {
      const userProfileCreated: UserProfileCreatedV2_0_0 = {
        userId: v1Data.userId,
        profile: {
          firstName: v1Data.profile.firstName,
          lastName: v1Data.profile.lastName,
          displayName: `${v1Data.profile.firstName} ${v1Data.profile.lastName}`,
        },
        createdAt: new Date(v1Data.registeredAt),
      };

      events.push(
        this.createDerivedEvent(
          event,
          'UserProfileCreated',
          '2.0.0',
          userProfileCreated
        )
      );
    }

    return events;
  }

  validateUpcasting(
    originalEvent: VersionedDomainEvent,
    upcastedEvents: VersionedDomainEvent[]
  ): boolean {
    // Validate that essential data is preserved
    const original = originalEvent.data as any;
    const userRegistered = upcastedEvents.find(
      e => e.eventType === 'UserRegistered'
    )?.data as UserRegisteredV2_0_0;

    if (!userRegistered) return false;
    if (userRegistered.userId !== original.userId) return false;
    if (userRegistered.email !== original.email) return false;

    // Validate date conversion
    const originalDate = new Date(original.registeredAt);
    if (userRegistered.registeredAt.getTime() !== originalDate.getTime())
      return false;

    return true;
  }
}
```

## Rationale

### Why Advanced Hybrid Approach

- **Comprehensive evolution support** handles realistic complexity scenarios
- **Multi-version tolerance** enables gradual migrations and rollbacks
- **Validation framework** ensures data integrity throughout evolution
- **Deprecation lifecycle** provides clear path for technical debt management
- **Migration planning** helps teams understand evolution complexity upfront

### Why Enhanced Semantic Versioning

- **Industry standard** that developers understand intuitively
- **Clear compatibility rules** reduce decision-making overhead
- **Automated tooling support** for version management and validation
- **Migration path planning** enables predictable evolution strategies

## Implementation Guidance

### Prerequisites

- ADR-006 (Event Sourcing) must be implemented
- Event store must support metadata fields
- Development team must understand semantic versioning and schema evolution principles

### Implementation Steps

1. **Add versioning to existing events**: Retrofit current events with version 1.0.0
2. **Implement advanced schema registry**: Create centralized schema storage and validation with evolution tracking
3. **Create comprehensive upcasting framework**: Build the advanced upcaster interface and registry with multi-version support
4. **Add version validation**: Ensure all new events include valid schema versions with compatibility checking
5. **Implement comprehensive monitoring**: Track version distribution, upcasting performance, and migration health
6. **Create migration planning tools**: Build tools to plan and validate complex schema migrations

### Validation Criteria

- All events include valid schema versions with proper semantic versioning
- Upcasting works correctly for complex multi-step scenarios
- Projection rebuilds succeed across all version changes and edge cases
- Schema registry correctly validates events and tracks compatibility
- Version migration paths are documented, tested, and validated
- Advanced upcasting scenarios (splitting, merging) work correctly
- Migration validation prevents data loss and maintains business rule integrity

## Consequences

### Positive

- **Safe evolution** of event schemas over time with comprehensive validation
- **Preserves ability** to replay all historical events across complex migrations
- **Clear versioning strategy** for development teams with detailed examples
- **Supports both gradual and breaking changes** with proper tooling
- **Maintains event sourcing immutability principle** throughout evolution
- **Advanced migration planning** enables confident schema evolution
- **Comprehensive validation** ensures data integrity during complex transformations

### Negative

- **Additional complexity** in event handling code with advanced upcasting logic
- **Performance overhead** for complex multi-step upcasting during replay
- **Need to maintain multiple event versions** and their upcasters over time
- **Additional testing required** for complex version compatibility scenarios
- **Schema registry adds operational complexity** with advanced features
- **Advanced upcasting scenarios** require careful design and thorough testing

### Neutral

- **Event payloads slightly larger** due to comprehensive versioning metadata
- **Development process includes** advanced schema design and migration planning considerations
- **Migration validation adds** safety at the cost of initial setup complexity

## Alternatives Considered

### Alternative 1: Copy-and-Transform Strategy

- **Description**: Create new events when schemas change, copy old data
- **Pros**: Simple implementation, no upcasting complexity
- **Cons**: Loses historical accuracy, violates event sourcing principles, no audit trail
- **Why rejected**: Breaks immutability and audit trail requirements

### Alternative 2: Additive-Only Evolution

- **Description**: Never remove or change fields, only add new ones
- **Pros**: No breaking changes, simple compatibility
- **Cons**: Event schemas grow indefinitely, semantic drift over time, technical debt
- **Why rejected**: Technical debt accumulates, unclear semantics long-term

### Alternative 3: Database Schema Migration Approach

- **Description**: Migrate events in-place like database schema changes
- **Pros**: Clean current state, no version complexity
- **Cons**: Violates event sourcing immutability, loses historical context, dangerous
- **Why rejected**: Fundamentally incompatible with event sourcing principles

### Alternative 4: Simple Version Numbers (v1, v2, v3)

- **Description**: Use simple incrementing version numbers instead of semantic versioning
- **Pros**: Simple numbering, less confusion
- **Cons**: No compatibility information, unclear change impact, limited tooling
- **Why rejected**: Semantic versioning provides much better compatibility guidance

## Related ADRs

### Dependencies

- **Requires**: ADR-006 (Event Sourcing) - Defines event structure and storage requirements
- **Requires**: ADR-005 (Domain Model) - Defines events that need versioning strategy

### Influences

- **Influences**: ADR-008 (Snapshots) - Snapshots must handle version evolution correctly
- **Influences**: ADR-009 (Replay Strategy) - Replay must work across all versions
- **Influences**: ADR-011 (Message Bus) - Integration events need comprehensive versioning
- **Influences**: ADR-012 (Projection Strategy) - Projections must handle multiple versions and complex upcasting

### Conflicts

- **None identified** - Strategy designed to complement other ADRs with advanced capabilities

## AI Agent Guidance

### Implementation Priority

**High** - Required before any significant domain model changes and complex event evolution

### Code Generation Patterns

```typescript
// Always include comprehensive version in new events
const newEvent: VersionedDomainEvent = {
  eventId: generateId(),
  eventType: 'UserRegistered',
  schemaVersion: '1.0.0', // Current version with semantic meaning
  // ... other required fields
  metadata: {
    compatibility: {
      backwardCompatibleWith: [], // Will be populated as versions evolve
      forwardCompatibleWith: [],
    },
  },
};

// Always implement comprehensive upcasters for breaking changes
class MyAdvancedEventUpcaster implements AdvancedEventUpcaster {
  // Implementation pattern with validation and multi-version support
  canUpcast(
    eventType: string,
    fromVersion: string,
    toVersion: string
  ): boolean {
    // Check compatibility matrix and version ranges
  }

  upcast(
    event: VersionedDomainEvent
  ): VersionedDomainEvent | VersionedDomainEvent[] {
    // Handle complex upcasting including event splitting/merging
  }

  validateUpcasting(
    originalEvent: VersionedDomainEvent,
    upcastedEvents: VersionedDomainEvent[]
  ): boolean {
    // Validate data integrity and business rules
  }
}
```

### Common Pitfalls

- **Forgetting version fields**: All events must include schemaVersion with proper semantic versioning
- **Breaking compatibility**: Minor version changes should be backward compatible
- **Missing advanced upcasters**: Complex changes require comprehensive upcaster implementation
- **Version validation**: Always validate event structure against schema and compatibility matrix
- **Complex migration testing**: Test multi-step migrations and edge cases thoroughly
- **Data loss validation**: Always validate that upcasting preserves essential business data

### Integration Points

- Must integrate with advanced event store from ADR-006
- Schema registry should connect to ADR-011 message bus with version awareness
- Advanced upcasting must work with ADR-012 projection rebuilds and complex scenarios
- Migration planning tools should integrate with deployment and testing pipelines

## Technical Debt Introduced

- **Advanced upcaster maintenance**: Complex upcasters need ongoing maintenance and comprehensive testing
- **Schema registry operations**: Additional operational complexity for advanced schema management features
- **Multi-version testing**: Must test compatibility across multiple event versions and complex scenarios
- **Migration validation complexity**: Advanced validation requires ongoing maintenance and updates

## Evolution Path

- **Review trigger**: When event volume makes complex upcasting performance critical
- **Evolution options**:
  - Migrate to eager upcasting for high-volume complex events
  - Implement distributed schema registry clustering for high availability
  - Add machine learning-based schema compatibility testing
  - Create automated migration path optimization
- **Migration strategy**: Advanced event versioning supports its own evolution through meta-versioning and advanced planning tools

---

_Last Updated: September 15, 2025_
_Enhanced with comprehensive examples and advanced upcasting strategies_
````

## Consequences

### Positive

- Safe evolution of event schemas over time
- Preserves ability to replay all historical events
- Clear versioning strategy for development teams
- Supports both gradual and breaking changes
- Maintains event sourcing immutability principle

### Negative

- Additional complexity in event handling code
- Performance overhead for upcasting during replay
- Need to maintain multiple event versions
- Additional testing required for version compatibility
- Schema registry adds operational complexity

### Neutral

- Event payloads slightly larger due to versioning metadata
- Development process includes schema design considerations

## Alternatives Considered

### Alternative 1: Copy-and-Transform Strategy

- **Description**: Create new events when schemas change, copy old data
- **Pros**: Simple implementation, no upcasting complexity
- **Cons**: Loses historical accuracy, violates event sourcing principles
- **Why rejected**: Breaks immutability and audit trail requirements

### Alternative 2: Additive-Only Evolution

- **Description**: Never remove or change fields, only add new ones
- **Pros**: No breaking changes, simple compatibility
- **Cons**: Event schemas grow indefinitely, semantic drift over time
- **Why rejected**: Technical debt accumulates, unclear semantics

### Alternative 3: Database Schema Migration Approach

- **Description**: Migrate events in-place like database schema changes
- **Pros**: Clean current state, no version complexity
- **Cons**: Violates event sourcing immutability, loses historical context
- **Why rejected**: Fundamentally incompatible with event sourcing

## Related ADRs

### Dependencies

- **Requires**: ADR-006 (Event Sourcing) - Defines event structure and storage
- **Requires**: ADR-005 (Domain Model) - Defines events that need versioning

### Influences

- **Influences**: ADR-008 (Snapshots) - Snapshots must handle version evolution
- **Influences**: ADR-009 (Replay Strategy) - Replay must work across versions
- **Influences**: ADR-011 (Message Bus) - Integration events need versioning
- **Influences**: ADR-012 (Projection Strategy) - Projections must handle multiple versions

### Conflicts

- **None identified** - Strategy designed to complement other ADRs

## AI Agent Guidance

### Implementation Priority

**High** - Required before any significant domain model changes

### Code Generation Patterns

```typescript
// Always include version in new events
const newEvent: VersionedDomainEvent = {
  eventId: generateId(),
  eventType: 'UserRegistered',
  schemaVersion: '1.0.0', // Current version
  // ... other required fields
};

// Always implement upcasters for breaking changes
class MyEventUpcaster implements EventUpcaster {
  // Implementation pattern shown above
}
```

### Common Pitfalls

- **Forgetting version fields**: All events must include schemaVersion
- **Breaking compatibility**: Minor version changes should be backward compatible
- **Missing upcasters**: Breaking changes require upcaster implementation
- **Version validation**: Always validate event structure against schema

### Integration Points

- Must integrate with event store from ADR-006
- Schema registry should connect to ADR-011 message bus
- Upcasting must work with ADR-012 projection rebuilds

## Technical Debt Introduced

- **Upcaster maintenance**: Old upcasters need ongoing maintenance and testing
- **Schema registry operations**: Additional operational complexity for schema management
- **Version testing**: Must test compatibility across multiple event versions

## Evolution Path

- **Review trigger**: When event volume makes upcasting performance critical
- **Evolution options**:
  - Migrate to eager upcasting for high-volume events
  - Implement schema registry clustering for high availability
  - Add automated schema compatibility testing
- **Migration strategy**: Event versioning supports its own evolution through meta-versioning

---

*Last Updated: September 10, 2025*Event Versioning and Schema Evolution

## Status

Accepted

## Context

The platform uses **Event Sourcing** with NeonDB (Postgres) as the event store and Kafka as the streaming bus.  
Events are the source of truth and must be immutable. Over time, domain models evolve, requiring schema changes.  
We need a consistent, provider-agnostic strategy for event versioning and schema evolution that preserves replayability and minimizes consumer breakage.

## Decision

- **Event schemas will be defined in Avro**.
- Each bounded context will have its own **schema registry**, versioned in source control under `/contracts/events/<bounded-context>`.
- CI/CD will validate that new event schemas are backward-compatible with existing ones.
- Events will be wrapped in a **common envelope** including metadata.
- Breaking changes will be introduced as new event types.

### Event Envelope

Every event is wrapped in a standard envelope:

```json
{
  "event_id": "uuid",
  "stream_id": "aggregate-123",
  "type": "UserRegistered",
  "version": 1,
  "occurred_at": "2025-09-08T12:34:56Z",
  "actor": "admin-456",
  "tenant_id": "tenant-abc",
  "metadata": {},
  "payload": { ... }
}
```

- `type` + `version` uniquely identifies an Avro schema in the bounded context registry.
- `payload` must conform to the registered Avro schema.

### Schema Evolution Rules

- **Additive changes (backward-compatible):**
  - Add new optional fields with defaults.
  - Add metadata fields.
  - Consumers that do not recognize a field must ignore it.

- **Breaking changes (incompatible):**
  - Removing required fields.
  - Changing field type or meaning.
  - Renaming event types.

Breaking changes require a **new event type** (e.g., `UserRegisteredV2`).  
Older events remain valid in the store and can still be replayed by consumers that support their version.

### Schema Registry per Bounded Context

- Each bounded context maintains its own registry under `/contracts/events/<context>`.
- Example:
  ```
  /contracts/events/accounts/UserRegistered.avsc
  /contracts/events/accounts/UserRegisteredV2.avsc
  /contracts/events/entitlements/AppAccessGranted.avsc
  ```
- This enforces domain isolation and makes evolution decisions local to each bounded context.

### Replay & Projections

- Projections must tolerate multiple versions of the same event type.
- Translation/adapters may be used to upgrade old events to the latest version during replay.
- Consumers must be idempotent and able to skip unknown fields.

## Rationale

- **Avro** provides compact binary encoding, strong typing, and built-in schema evolution rules.
- **Per-context registry in source control** avoids vendor lock-in and keeps schema history auditable.
- This strategy supports **backward compatibility** while allowing breaking changes via new event types.
- Enforcing a shared envelope ensures consistency across all contexts and simplifies observability.

## Consequences

- Developers must define and evolve event schemas in Avro, committed to `/contracts/events`.
- CI/CD must validate schema compatibility (using Avro tools).
- Projection logic must support multiple event versions until migration is complete.
- Replay may require **upgrade adapters** for older event versions.

## Alternatives Considered

- **JSON Schema only**: easier to read, but less efficient and weaker type guarantees.
- **Centralized schema registry (e.g., Confluent)**: convenient, but introduces vendor coupling and operational dependency.
- **Manual migration of stored events**: breaks immutability principle, adds complexity.

## Next Steps

1. Scaffold `/contracts/events/<context>` directories with initial Avro schemas.
2. Add CI checks for Avro schema backward compatibility.
3. Document schema evolution rules in `/docs/conventions.md`.
4. Implement event envelope contract in `/contracts/events/envelope.avsc`.
5. Update projections to support multi-version event handling.
