# ADR 002: Adoption of Domain-Driven Design

## Status

Accepted

## Context

The Documentation System needs a clear domain model that accurately represents the complex business rules and workflows of enterprise documentation management. The Level 3 Audit identified several domain modeling issues:

1. No well-defined domain model with clear aggregates and entities
2. Service layer responsibilities overlap with data access patterns
3. Business logic scattered across different layers without clear organization
4. Lack of a ubiquitous language throughout the codebase

We need an approach that:
- Creates a shared understanding of the problem domain
- Isolates complex business logic in a coherent model
- Provides clear boundaries between different parts of the system
- Establishes consistent terminology across all components

## Decision

We will adopt Domain-Driven Design (DDD) principles as outlined by Eric Evans to organize our business logic and create a rich domain model. This includes:

### Strategic Design

1. **Bounded Contexts**: Define explicit boundaries around domain models, with each context having its own ubiquitous language. The initial bounded contexts are:
   - Document Management Context
   - User Management Context
   - Workflow Context
   - Template Context
   - Audit Context

2. **Context Map**: Create explicit relationships between bounded contexts with well-defined integration patterns.

3. **Ubiquitous Language**: Develop a consistent vocabulary for each bounded context that is used in code, documentation, and discussions.

### Tactical Design

1. **Entities**: Objects with a distinct identity that runs through time and different states.
   - Example: Document, User, Workflow

2. **Value Objects**: Immutable objects that describe aspects of the domain.
   - Example: DocumentVersion, Permission, Metadata

3. **Aggregates**: Clusters of domain objects that are treated as a unit for data changes.
   - Example: Document (root) with DocumentVersions and Comments

4. **Domain Events**: Record of something significant that happened in the domain.
   - Example: DocumentCreated, WorkflowCompleted

5. **Repositories**: Provide methods to obtain and persist aggregates.
   - Example: DocumentRepository, WorkflowRepository

6. **Domain Services**: Operations that don't logically belong to any entity or value object.
   - Example: DocumentPublishingService, AccessControlService

7. **Application Services**: Thin layer that orchestrates domain objects to perform use cases.
   - Example: CreateDocumentService, AssignWorkflowService

## Consequences

### Positive

1. **Rich Domain Model**: Business rules are encapsulated within the domain model, making them explicit and testable.
2. **Shared Understanding**: The ubiquitous language bridges the gap between technical and business stakeholders.
3. **Clear Boundaries**: Bounded contexts provide modularity and define integration points.
4. **Focused Complexity**: Complex business logic is isolated in the domain layer.
5. **Evolution Support**: The model can evolve over time within bounded contexts without affecting the entire system.

### Negative

1. **Learning Curve**: DDD concepts require investment to understand and apply correctly.
2. **Overhead for Simple Cases**: Simple CRUD operations become more complex.
3. **Design Effort**: Significant upfront effort to define bounded contexts and the domain model.
4. **Potential Overengineering**: Risk of creating unnecessary complexity if applied dogmatically.

## Implementation Details

### Domain Model Structure

Each bounded context will have its own domain model with the following components:

```
boundedContext/
├── entities/         # Domain entities
├── value-objects/    # Value objects
├── events/           # Domain events
├── repositories/     # Repository interfaces
├── services/         # Domain services
└── exceptions/       # Domain-specific exceptions
```

### Entity Example

```javascript
class Document {
  constructor(id, title, content, ownerId) {
    this.id = id;
    this.title = title;
    this.content = content;
    this.ownerId = ownerId;
    this.versions = [];
    this.status = DocumentStatus.DRAFT;
    this.lastModified = new Date();
    this.created = new Date();
    this.domainEvents = [];
  }

  publish() {
    if (this.status === DocumentStatus.DRAFT) {
      this.status = DocumentStatus.PUBLISHED;
      this.lastModified = new Date();
      this.addDomainEvent(new DocumentPublishedEvent(this.id));
      return true;
    }
    return false;
  }

  createVersion(content) {
    const versionNumber = this.versions.length + 1;
    const version = new DocumentVersion(
      this.id,
      versionNumber,
      content,
      this.lastModified
    );
    this.versions.push(version);
    this.content = content;
    this.lastModified = new Date();
    this.addDomainEvent(new DocumentVersionCreatedEvent(this.id, versionNumber));
    return version;
  }

  addDomainEvent(event) {
    this.domainEvents.push(event);
  }

  clearDomainEvents() {
    this.domainEvents = [];
  }
}
```

### Repository Interface Example

```javascript
// Repository interfaces are defined in the domain layer
class DocumentRepository {
  getById(id) {
    throw new Error('Method not implemented');
  }

  save(document) {
    throw new Error('Method not implemented');
  }

  findByOwner(ownerId) {
    throw new Error('Method not implemented');
  }

  findByStatus(status) {
    throw new Error('Method not implemented');
  }
}
```

### Domain Service Example

```javascript
class DocumentPublishingService {
  constructor(documentRepository, workflowRepository, notificationService) {
    this.documentRepository = documentRepository;
    this.workflowRepository = workflowRepository;
    this.notificationService = notificationService;
  }

  publishDocument(documentId, userId) {
    const document = this.documentRepository.getById(documentId);
    
    if (!document) {
      throw new DocumentNotFoundException(documentId);
    }
    
    if (!this.hasPublishingPermission(document, userId)) {
      throw new InsufficientPermissionException('publish', documentId, userId);
    }
    
    const activeWorkflow = this.workflowRepository.findActiveForDocument(documentId);
    if (activeWorkflow && !activeWorkflow.isCompleted()) {
      throw new WorkflowIncompleteException(documentId, activeWorkflow.id);
    }
    
    const published = document.publish();
    
    if (published) {
      this.documentRepository.save(document);
      this.notificationService.notifyDocumentPublished(document);
      return true;
    }
    
    return false;
  }
  
  hasPublishingPermission(document, userId) {
    // Domain logic for permission checking
    return document.ownerId === userId || this.isEditor(userId);
  }
  
  isEditor(userId) {
    // Domain logic for role checking
    return true; // Simplified for example
  }
}
```

### Event Handling

Domain events will be collected and published after the transaction completes:

```javascript
class CreateDocumentHandler {
  constructor(documentRepository, unitOfWork, eventPublisher) {
    this.documentRepository = documentRepository;
    this.unitOfWork = unitOfWork;
    this.eventPublisher = eventPublisher;
  }
  
  async handle(command) {
    return this.unitOfWork.execute(async () => {
      const document = new Document(
        command.id,
        command.title,
        command.content,
        command.ownerId
      );
      
      await this.documentRepository.save(document);
      
      // Publish domain events after successful transaction
      const events = document.domainEvents;
      document.clearDomainEvents();
      
      events.forEach(event => this.eventPublisher.publish(event));
      
      return document.id;
    });
  }
}
```

## Compliance

This approach directly addresses the Level 3 Audit findings by:
1. Creating a well-defined domain model with clear aggregates and entities
2. Separating service layer responsibilities from data access concerns
3. Organizing business logic within the domain layer
4. Establishing a ubiquitous language for consistent terminology

## References

1. Eric Evans, "Domain-Driven Design: Tackling Complexity in the Heart of Software"
2. Vaughn Vernon, "Implementing Domain-Driven Design"
3. [DDD Reference](https://www.domainlanguage.com/ddd/reference/) by Eric Evans
4. [Strategic Domain-Driven Design](https://vaadin.com/blog/ddd-part-1-strategic-domain-driven-design)