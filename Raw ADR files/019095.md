# ADR-023: Contract Management and Multi-Language Support

**Status**: Proposed  
**Date**: 2025-09-10  
**Authors**: AI Agent  
**Reviewers**: **_please check_** - needs review assignment

## Context

Our event-driven architecture requires robust contract management to ensure reliable communication between services, especially as we expand into multi-language microservices. With ADR-022 handling the message bus infrastructure, we need dedicated patterns for contract definition, validation, and evolution across different programming languages and service boundaries.

### Current State

- Event schemas defined in TypeScript interfaces within individual services
- No centralized contract registry or validation
- Manual contract synchronization between producers and consumers
- No versioning strategy for cross-service contracts
- Limited support for non-TypeScript services (planned Java, Python services)

### Problems to Solve

1. **Contract Drift**: Producers and consumers can have mismatched schema expectations
2. **Multi-Language Support**: TypeScript interfaces don't translate well to other languages
3. **Breaking Changes**: No systematic way to handle contract evolution
4. **Discovery**: Services cannot dynamically discover available contracts
5. **Validation**: No runtime validation of contract compliance
6. **Documentation**: Contract documentation is scattered and incomplete

## Decision

We will implement a comprehensive contract management system using **JSON Schema** as the universal contract definition language, with code generation for multiple target languages and runtime validation.

### Core Components

#### 1. Centralized Contract Registry

```typescript
// contracts/registry/ContractRegistry.ts
export interface ContractRegistry {
  registerContract(contract: ContractDefinition): Promise<void>;
  getContract(name: string, version: string): Promise<ContractDefinition>;
  listContracts(service?: string): Promise<ContractSummary[]>;
  validateMessage(contractName: string, message: unknown): ValidationResult;
}

export interface ContractDefinition {
  name: string; // e.g., "UserRegistered"
  version: string; // Semantic version: "1.2.0"
  schema: JSONSchema7; // JSON Schema definition
  producer: string; // Service that publishes this event
  consumers: string[]; // Services that consume this event
  description: string;
  examples: unknown[]; // Sample payloads
  deprecatedIn?: string; // Version when deprecation started
  removedIn?: string; // Version when contract will be removed
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}
```

#### 2. Contract Definition Format

We use JSON Schema with extensions for event-specific metadata:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://contracts.tomriddelsdell.com/events/UserRegistered/v1.2.0",
  "title": "UserRegistered",
  "type": "object",
  "properties": {
    "eventId": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this event"
    },
    "aggregateId": {
      "type": "string",
      "format": "uuid",
      "description": "ID of the user aggregate"
    },
    "userId": {
      "type": "string",
      "format": "uuid",
      "description": "Unique user identifier"
    },
    "email": {
      "type": "string",
      "format": "email",
      "description": "User's email address"
    },
    "profile": {
      "$ref": "#/definitions/UserProfile"
    },
    "occurredAt": {
      "type": "string",
      "format": "date-time",
      "description": "When the event occurred"
    }
  },
  "required": ["eventId", "aggregateId", "userId", "email", "occurredAt"],
  "definitions": {
    "UserProfile": {
      "type": "object",
      "properties": {
        "displayName": { "type": "string" },
        "preferences": { "$ref": "#/definitions/UserPreferences" }
      },
      "required": ["displayName"]
    },
    "UserPreferences": {
      "type": "object",
      "properties": {
        "theme": { "enum": ["light", "dark", "auto"] },
        "notifications": { "type": "boolean" }
      }
    }
  },
  "x-event-metadata": {
    "producer": "accounts-service",
    "consumers": ["entitlements-service", "notification-service"],
    "category": "domain-event",
    "aggregate": "User",
    "version": "1.2.0",
    "deprecatedIn": null,
    "removedIn": null
  }
}
```

#### 3. Code Generation Pipeline

```typescript
// contracts/codegen/CodeGenerator.ts
export interface CodeGenerator {
  generateTypeScript(contracts: ContractDefinition[]): GeneratedCode;
  generateJava(contracts: ContractDefinition[]): GeneratedCode;
  generatePython(contracts: ContractDefinition[]): GeneratedCode;
  generateGo(contracts: ContractDefinition[]): GeneratedCode;
}

export interface GeneratedCode {
  files: GeneratedFile[];
  dependencies: string[];
}

export interface GeneratedFile {
  path: string;
  content: string;
  language: 'typescript' | 'java' | 'python' | 'go';
}

// Example usage in build pipeline
export class ContractCodeGen {
  async generateAllLanguages(): Promise<void> {
    const contracts = await this.registry.listContracts();

    const tsCode = await this.generator.generateTypeScript(contracts);
    await this.writeFiles('generated/typescript', tsCode.files);

    const javaCode = await this.generator.generateJava(contracts);
    await this.writeFiles('generated/java', javaCode.files);

    // Add to package.json / pom.xml / requirements.txt
    await this.updateDependencies(tsCode.dependencies, javaCode.dependencies);
  }
}
```

#### 4. Runtime Validation

```typescript
// contracts/validation/ContractValidator.ts
export class ContractValidator {
  private ajv: Ajv;

  constructor(private registry: ContractRegistry) {
    this.ajv = new Ajv({
      allErrors: true,
      formats: {
        uuid: uuidFormat,
        'date-time': dateTimeFormat,
      },
    });
  }

  async validateEvent(
    eventName: string,
    payload: unknown
  ): Promise<ValidationResult> {
    const contract = await this.registry.getContract(eventName, 'latest');
    const validate = this.ajv.compile(contract.schema);

    const valid = validate(payload);
    return {
      valid,
      errors:
        validate.errors?.map(err => `${err.instancePath}: ${err.message}`) ||
        [],
      warnings: this.checkDeprecations(contract, payload),
    };
  }

  private checkDeprecations(
    contract: ContractDefinition,
    payload: unknown
  ): string[] {
    const warnings: string[] = [];

    if (contract.deprecatedIn) {
      warnings.push(
        `Contract ${contract.name} is deprecated since version ${contract.deprecatedIn}`
      );
    }

    // Check for deprecated fields in payload
    // Implementation depends on schema annotations

    return warnings;
  }
}
```

### Contract Evolution Strategy

#### Semantic Versioning for Contracts

- **Major Version (2.0.0)**: Breaking changes that require consumer updates
- **Minor Version (1.1.0)**: Backward-compatible additions (new optional fields)
- **Patch Version (1.0.1)**: Non-functional changes (documentation, examples)

#### Backward Compatibility Rules

```typescript
export interface CompatibilityChecker {
  checkCompatibility(
    oldContract: ContractDefinition,
    newContract: ContractDefinition
  ): CompatibilityResult;
}

export interface CompatibilityResult {
  compatible: boolean;
  breakingChanges: BreakingChange[];
  additions: Addition[];
  deprecations: Deprecation[];
}

export interface BreakingChange {
  type: 'field-removed' | 'type-changed' | 'constraint-added';
  field: string;
  description: string;
  migrationRequired: boolean;
}
```

#### Contract Lifecycle

1. **Draft**: Contract is being developed, not yet published
2. **Active**: Contract is published and in use
3. **Deprecated**: Contract is marked for future removal, consumers should migrate
4. **Removed**: Contract is no longer available (after grace period)

### Multi-Language Support

#### TypeScript Generation

```typescript
// Generated file: contracts/typescript/events/UserRegistered.ts
export interface UserRegistered {
  eventId: string;
  aggregateId: string;
  userId: string;
  email: string;
  profile: UserProfile;
  occurredAt: string;
}

export interface UserProfile {
  displayName: string;
  preferences?: UserPreferences;
}

export const UserRegisteredSchema = {
  /* JSON Schema object */
};
```

#### Java Generation

```java
// Generated file: contracts/java/events/UserRegistered.java
@JsonIgnoreProperties(ignoreUnknown = true)
public class UserRegistered {
    @NotNull
    private UUID eventId;

    @NotNull
    private UUID aggregateId;

    @NotNull
    private UUID userId;

    @Email
    private String email;

    @NotNull
    private UserProfile profile;

    @NotNull
    private Instant occurredAt;

    // Constructors, getters, setters, equals, hashCode
}
```

#### Python Generation

```python
# Generated file: contracts/python/events/user_registered.py
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime

@dataclass
class UserRegistered:
    event_id: UUID
    aggregate_id: UUID
    user_id: UUID
    email: str
    profile: 'UserProfile'
    occurred_at: datetime

    def validate(self) -> ValidationResult:
        # Use jsonschema library for validation
        pass
```

### Integration with Message Bus

#### Publisher Integration

```typescript
// services/accounts/app/handlers/UserRegistrationHandler.ts
export class UserRegistrationHandler {
  constructor(
    private messageBus: MessageBus,
    private contractValidator: ContractValidator
  ) {}

  async handle(command: RegisterUserCommand): Promise<void> {
    // Business logic...

    const event: UserRegistered = {
      eventId: generateId(),
      aggregateId: user.id,
      userId: user.id,
      email: user.email,
      profile: user.profile,
      occurredAt: new Date().toISOString(),
    };

    // Validate against contract before publishing
    const validation = await this.contractValidator.validateEvent(
      'UserRegistered',
      event
    );
    if (!validation.valid) {
      throw new ContractValidationError(validation.errors);
    }

    await this.messageBus.publish('user.registered', event);
  }
}
```

#### Consumer Integration

```typescript
// services/entitlements/app/handlers/UserRegisteredHandler.ts
export class UserRegisteredHandler {
  constructor(private contractValidator: ContractValidator) {}

  async handle(message: IntegrationMessage): Promise<void> {
    // Validate incoming message against contract
    const validation = await this.contractValidator.validateEvent(
      'UserRegistered',
      message.payload
    );
    if (!validation.valid) {
      throw new ContractValidationError(validation.errors);
    }

    // Type-safe payload access using generated types
    const event = message.payload as UserRegistered;

    // Business logic...
    await this.entitlementService.createDefaultEntitlements(event.userId);
  }
}
```

### Build Integration

#### Contract-First Development

```json
{
  "scripts": {
    "contracts:validate": "contract-validator validate contracts/schemas",
    "contracts:generate": "contract-codegen generate --output generated/",
    "contracts:publish": "contract-registry publish contracts/schemas",
    "contracts:check-compatibility": "contract-checker check-breaking-changes",
    "prebuild": "npm run contracts:validate && npm run contracts:generate"
  }
}
```

#### CI/CD Pipeline Integration

```yaml
# .github/workflows/contracts.yml
name: Contract Validation
on: [push, pull_request]

jobs:
  validate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Contract Schemas
        run: npm run contracts:validate

      - name: Check Breaking Changes
        run: npm run contracts:check-compatibility

      - name: Generate Code
        run: npm run contracts:generate

      - name: Run Tests with Generated Code
        run: npm test
```

## Consequences

### Positive

- **Type Safety**: Generated types ensure compile-time contract compliance
- **Multi-Language Support**: Single source of truth works across different languages
- **Automated Validation**: Runtime validation catches contract violations
- **Version Management**: Clear versioning and compatibility checking
- **Documentation**: Self-documenting contracts with examples
- **Breaking Change Detection**: Automated detection prevents accidental breaking changes

### Negative

- **Build Complexity**: Additional build steps for code generation
- **Tool Chain**: Need to maintain code generators for multiple languages
- **Learning Curve**: Teams need to understand JSON Schema
- **Performance**: Runtime validation adds overhead (can be disabled in production)

### Risks

- **Generator Bugs**: Faulty code generation could introduce bugs
- **Schema Complexity**: Very complex schemas might be hard to maintain
- **Tooling Dependency**: Heavy dependency on custom tooling

## Implementation Plan

### Phase 1: Foundation (2-3 weeks)

1. Set up contract registry infrastructure
2. Create JSON Schema definitions for existing events
3. Implement TypeScript code generator
4. Add validation to existing message publishers

### Phase 2: Multi-Language Support (2-3 weeks)

1. Implement Java code generator
2. Implement Python code generator
3. Create contract validation CLI tools
4. Add CI/CD integration

### Phase 3: Advanced Features (2-3 weeks)

1. Contract compatibility checking
2. Contract lifecycle management
3. Breaking change detection
4. Performance optimization

### Phase 4: Production Hardening (1-2 weeks)

1. Production monitoring
2. Error handling and fallback strategies
3. Performance tuning
4. Documentation and training

## Alternatives Considered

### Apache Avro

- **Pros**: Mature, efficient binary serialization, good schema evolution
- **Cons**: Limited JSON support, complex tooling, less human-readable

### Protocol Buffers

- **Pros**: Efficient, mature, good multi-language support
- **Cons**: Binary format, complex schema evolution, less flexible than JSON

### OpenAPI/AsyncAPI

- **Pros**: Industry standard, good tooling
- **Cons**: Focused on API contracts, not event contracts, limited code generation

### GraphQL Schema

- **Pros**: Strong typing, good tooling
- **Cons**: Query-focused, not event-focused, complex for simple events

## Related ADRs

- **ADR-006**: Event Sourcing Implementation (provides events to contract)
- **ADR-007**: Event Versioning (contracts implement versioning strategy)
- **ADR-022**: Message Bus Architecture (contracts integrate with message bus)
- **ADR-020**: API Design Standards (contracts align with API standards)
- **ADR-021**: Testing Strategy (contracts enable better testing)

## AI Agent Guidance

### For Code Generation

```typescript
// When implementing contract validation:
const validator = new ContractValidator(contractRegistry);
const result = await validator.validateEvent(eventName, payload);
if (!result.valid) {
  // Handle validation errors appropriately
  // Consider logging vs throwing vs fallback strategies
}
```

### For Adding New Contracts

1. Define JSON Schema in `/contracts/schemas/events/`
2. Add examples and documentation
3. Run `npm run contracts:validate` to check syntax
4. Run `npm run contracts:generate` to generate types
5. Update consuming services to use new types
6. Test with contract validation enabled

### Common Pitfalls to Avoid

- Don't modify existing contracts without version bumping
- Always validate backward compatibility before publishing
- Include comprehensive examples in contract definitions
- Use descriptive field names and documentation
- Consider optional vs required fields carefully

### Integration Points

- Message bus publishers must validate contracts before sending
- Message bus consumers should validate contracts on receive
- Generated types should be imported, not manually defined
- Contract violations should be monitored and alerted

---

**Status**: Proposed  
**Next Review**: 2025-09-17  
**Implementation Owner**: **_please check_** - needs assignment
