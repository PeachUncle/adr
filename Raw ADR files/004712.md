# ADR 0000: Domain Modeling Services Implementation

## Status

Proposed

## Context

The Domain Modeler application needs services to implement the business logic for manipulating domain objects defined in `app/domain/modeling/models.ts`. These services should follow Domain-Driven Design principles and support the core application flow:

1. User inputs business operations and areas to systematize
2. LLM extracts ubiquitous language terms and use cases
3. User reviews and refines terms and use cases
4. LLM derives domain model (bounded contexts, entities, value objects, aggregates)
5. User refines the model through interaction
6. User downloads final results as markdown

The services need to be pure functions that don't mutate their arguments and don't interact directly with repositories.

## Decision

We will implement the following services in `app/domain/modeling/services.ts`:

### 1. ModelExtractionService

**Purpose**: Extract domain model elements from user input and LLM responses.

**Key Functions**:

- `extractUbiquitousLanguage(input: string)`: Extract ubiquitous language terms from user input
- `extractUseCases(input: string)`: Extract use cases from user input
- `generateClarifyingQuestions(terms: UbiquitousLanguage[], useCases: UseCase[], userInputHistory: string[], previousResponses: string[])`: Generate questions to refine understanding based on all available context

### 2. ModelGenerationService

**Purpose**: Generate a cohesive domain model based on ubiquitous language and use cases.

**Key Functions**:

- `generateDomainModel(terms: UbiquitousLanguage[], useCases: UseCase[], descriptions: Record<string, string>)`: Generate a complete domain model including entities, value objects, aggregates, and bounded contexts in an integrated way

This function will return a structured result containing entities, value objects, aggregates, bounded contexts, and their relationships. The implementation will follow an integrated approach that considers the interconnected nature of these domain elements.

### 3. ModelRefinementService

**Purpose**: Support the integrated refinement of the entire domain model based on user feedback.

**Key Functions**:

- `refineDomainModel(currentModel: DomainModelResult, refinementInstruction: string)`: Apply a natural language refinement instruction to update the domain model
- `generateRefinementSuggestions(currentModel: DomainModelResult)`: Analyze the current model and suggest potential improvements as natural language instructions

### 4. ExportService

**Purpose**: Export the domain model in various formats.

**Key Functions**:

- `generateMarkdown(entities: Entity[], valueObjects: ValueObject[], aggregates: Aggregate[], events: Event[], commands: Command[])`: Generate markdown representation of the domain model
- `generateDiagram(entities: Entity[], valueObjects: ValueObject[], aggregates: Aggregate[])`: Generate a visual diagram of the domain model

## Consequences

### Positive

- Services are focused on the core application flow and directly support the user journey
- The integrated approach to domain model generation and refinement reflects the interconnected nature of domain modeling
- Using natural language for refinement instructions provides flexibility and future-proofing
- Pure functions ensure immutability and testability
- Clear separation of concerns between services and repositories

### Negative

- Success is heavily dependent on LLM capabilities, especially for complex domain modeling tasks
- Natural language refinement instructions may be ambiguous or difficult to parse
- The integrated approach may be more complex to implement than separate functions for each domain object type

### Risks and Mitigations

- **Risk**: LLM may struggle with complex domain modeling decisions
  - **Mitigation**: Implement a guided, iterative approach with user validation at each stage

- **Risk**: Natural language refinement instructions may be misinterpreted
  - **Mitigation**: Provide clear feedback on how instructions were interpreted and allow for corrections

- **Risk**: The domain model may become inconsistent during refinement
  - **Mitigation**: Implement validation checks to ensure model consistency after each refinement

## Implementation Notes

1. All services will be implemented as collections of pure functions
2. Functions will not mutate their arguments but return new copies
3. Services will not interact directly with repositories
4. Comprehensive unit tests will be written for all service functions
5. The route actions/loaders will be responsible for using repositories to fetch data, passing it to services for processing, and then saving the results back using repositories
