# ADR-008: Saga Pattern for Distributed Transactions

## Status

**Accepted** - January 2026

## Context

Sentinel RFP has several workflows that span multiple services/modules:

1. **Document Ingestion**: Upload → Parse → Chunk → Embed → Index
2. **Response Generation**: Plan → Search → Generate → Review → Store
3. **Integration Sync**: External change → Update local → Notify users
4. **Proposal Submission**: Validate → Export → Upload → Confirm

These workflows require:

- Coordination across multiple steps
- Failure handling and compensation
- Progress tracking
- Retry logic
- Eventual consistency

We need to decide how to handle distributed transactions:

1. **Two-Phase Commit (2PC)**: Distributed locks
2. **Saga Pattern**: Choreography or orchestration
3. **Process Manager**: Centralized workflow control
4. **Simple Async**: Independent job processors

## Decision

**Implement the Saga Pattern with Orchestration for complex workflows.**

### Why Saga over 2PC

| Factor          | 2PC                          | Saga                 |
| --------------- | ---------------------------- | -------------------- |
| Locking         | Distributed locks (complex)  | No locks             |
| Availability    | Lower (coordinator required) | Higher               |
| Performance     | Slower (sync)                | Faster (async)       |
| Recovery        | Complex rollback             | Compensating actions |
| Railway support | Not practical                | Natural fit          |

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SAGA ORCHESTRATION                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                         ┌────────────────┐                          │
│                         │     SAGA       │                          │
│                         │  ORCHESTRATOR  │                          │
│                         │                │                          │
│                         │ • State machine│                          │
│                         │ • Step tracking│                          │
│                         │ • Compensation │                          │
│                         └───────┬────────┘                          │
│                                 │                                    │
│            ┌──────────────┬─────┴─────┬──────────────┐              │
│            │              │           │              │              │
│            ▼              ▼           ▼              ▼              │
│     ┌───────────┐  ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│     │  Step 1   │  │  Step 2   │ │  Step 3   │ │  Step 4   │       │
│     │           │  │           │ │           │ │           │       │
│     │  Upload   │─▶│  Parse    │─▶│  Embed   │─▶│  Index   │       │
│     │           │  │           │ │           │ │           │       │
│     │  ✓ Done   │  │  ✓ Done   │ │  ⏳ Run   │ │  ○ Wait  │       │
│     └───────────┘  └───────────┘ └───────────┘ └───────────┘       │
│            │              │           │              │              │
│            │              │           │              │              │
│            ▼              ▼           ▼              ▼              │
│     ┌───────────┐  ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│     │  Compen-  │  │  Compen-  │ │  Compen-  │ │  Compen-  │       │
│     │  sation   │  │  sation   │ │  sation   │ │  sation   │       │
│     │           │  │           │ │           │ │           │       │
│     │  Delete   │  │  Delete   │ │  Delete   │ │  Delete   │       │
│     │  file     │  │  chunks   │ │  vectors  │ │  indexes  │       │
│     └───────────┘  └───────────┘ └───────────┘ └───────────┘       │
│                                                                      │
│  ON FAILURE: Execute compensations in reverse order                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation

#### Saga Definition

```typescript
// packages/saga/src/types.ts
export interface SagaStep<TContext> {
  name: string;
  execute: (context: TContext) => Promise<TContext>;
  compensate: (context: TContext) => Promise<void>;
  retryPolicy?: RetryPolicy;
}

export interface SagaDefinition<TContext> {
  name: string;
  steps: SagaStep<TContext>[];
  onComplete?: (context: TContext) => Promise<void>;
  onFailed?: (context: TContext, error: Error) => Promise<void>;
}

export interface SagaExecution {
  id: string;
  sagaName: string;
  status: 'running' | 'completed' | 'failed' | 'compensating';
  currentStep: number;
  context: Record<string, unknown>;
  completedSteps: string[];
  error?: string;
  createdAt: Date;
  updatedAt: Date;
}
```

#### Document Ingestion Saga

```typescript
// apps/worker/src/sagas/document-ingestion.saga.ts
export const documentIngestionSaga: SagaDefinition<DocumentIngestionContext> = {
  name: 'document-ingestion',

  steps: [
    {
      name: 'upload',
      execute: async (ctx) => {
        const storagePath = await storageService.upload(ctx.file);
        return { ...ctx, storagePath };
      },
      compensate: async (ctx) => {
        await storageService.delete(ctx.storagePath);
      },
    },

    {
      name: 'parse',
      execute: async (ctx) => {
        const content = await documentParser.parse(ctx.storagePath);
        const document = await prisma.document.create({
          data: {
            organizationId: ctx.organizationId,
            filename: ctx.filename,
            storagePath: ctx.storagePath,
            content: content.text,
            structure: content.structure,
            processingStatus: 'parsed',
          },
        });
        return { ...ctx, documentId: document.id, content };
      },
      compensate: async (ctx) => {
        await prisma.document.delete({ where: { id: ctx.documentId } });
      },
      retryPolicy: { maxAttempts: 3, backoffMs: 1000 },
    },

    {
      name: 'chunk',
      execute: async (ctx) => {
        const chunks = await chunkingService.chunk(ctx.content);
        const chunkRecords = await prisma.chunk.createMany({
          data: chunks.map((chunk, i) => ({
            documentId: ctx.documentId,
            content: chunk.content,
            pageNumber: chunk.pageNumber,
            hierarchyPath: chunk.hierarchyPath,
            sequenceNumber: i,
          })),
        });
        return { ...ctx, chunkCount: chunkRecords.count };
      },
      compensate: async (ctx) => {
        await prisma.chunk.deleteMany({
          where: { documentId: ctx.documentId },
        });
      },
    },

    {
      name: 'embed',
      execute: async (ctx) => {
        const chunks = await prisma.chunk.findMany({
          where: { documentId: ctx.documentId },
        });

        const embeddings = await embeddingService.batchEmbed(chunks.map((c) => c.content));

        await Promise.all(
          chunks.map((chunk, i) =>
            prisma.chunk.update({
              where: { id: chunk.id },
              data: { contentEmbedding: embeddings[i] },
            }),
          ),
        );

        return ctx;
      },
      compensate: async (ctx) => {
        // Embeddings cleaned up with chunks
      },
      retryPolicy: { maxAttempts: 5, backoffMs: 2000 },
    },

    {
      name: 'index',
      execute: async (ctx) => {
        const chunks = await prisma.chunk.findMany({
          where: { documentId: ctx.documentId },
          select: { id: true, content: true },
        });

        await searchService.indexDocument(ctx.documentId, chunks);

        await prisma.document.update({
          where: { id: ctx.documentId },
          data: { processingStatus: 'completed' },
        });

        return ctx;
      },
      compensate: async (ctx) => {
        await searchService.deleteDocument(ctx.documentId);
      },
    },
  ],

  onComplete: async (ctx) => {
    eventEmitter.emit('document.processed', {
      documentId: ctx.documentId,
      organizationId: ctx.organizationId,
    });
  },

  onFailed: async (ctx, error) => {
    eventEmitter.emit('document.failed', {
      documentId: ctx.documentId,
      error: error.message,
    });
  },
};
```

#### Saga Orchestrator

```typescript
// packages/saga/src/orchestrator.ts
export class SagaOrchestrator {
  constructor(
    private readonly prisma: PrismaService,
    private readonly logger: Logger,
  ) {}

  async start<T>(saga: SagaDefinition<T>, initialContext: T): Promise<string> {
    // Create execution record
    const execution = await this.prisma.sagaExecution.create({
      data: {
        sagaName: saga.name,
        status: 'running',
        currentStep: 0,
        context: initialContext as any,
        completedSteps: [],
      },
    });

    // Start processing asynchronously
    this.processAsync(execution.id, saga);

    return execution.id;
  }

  private async processAsync<T>(executionId: string, saga: SagaDefinition<T>): Promise<void> {
    let execution = await this.prisma.sagaExecution.findUnique({
      where: { id: executionId },
    });

    let context = execution.context as T;

    try {
      for (let i = execution.currentStep; i < saga.steps.length; i++) {
        const step = saga.steps[i];

        this.logger.log(`Executing step: ${step.name}`);

        context = await this.executeWithRetry(step, context);

        // Update progress
        await this.prisma.sagaExecution.update({
          where: { id: executionId },
          data: {
            currentStep: i + 1,
            context: context as any,
            completedSteps: { push: step.name },
          },
        });
      }

      // All steps completed
      await this.prisma.sagaExecution.update({
        where: { id: executionId },
        data: { status: 'completed' },
      });

      if (saga.onComplete) {
        await saga.onComplete(context);
      }
    } catch (error) {
      this.logger.error(`Saga failed: ${error.message}`);

      // Mark as compensating
      await this.prisma.sagaExecution.update({
        where: { id: executionId },
        data: { status: 'compensating', error: error.message },
      });

      // Run compensations in reverse
      await this.compensate(saga, execution.completedSteps, context);

      // Mark as failed
      await this.prisma.sagaExecution.update({
        where: { id: executionId },
        data: { status: 'failed' },
      });

      if (saga.onFailed) {
        await saga.onFailed(context, error);
      }
    }
  }

  private async compensate<T>(
    saga: SagaDefinition<T>,
    completedSteps: string[],
    context: T,
  ): Promise<void> {
    // Reverse order
    for (const stepName of completedSteps.reverse()) {
      const step = saga.steps.find((s) => s.name === stepName);
      if (step?.compensate) {
        try {
          this.logger.log(`Compensating step: ${stepName}`);
          await step.compensate(context);
        } catch (error) {
          this.logger.error(`Compensation failed for ${stepName}: ${error.message}`);
          // Continue with other compensations
        }
      }
    }
  }

  private async executeWithRetry<T>(step: SagaStep<T>, context: T): Promise<T> {
    const policy = step.retryPolicy ?? { maxAttempts: 1, backoffMs: 0 };

    for (let attempt = 1; attempt <= policy.maxAttempts; attempt++) {
      try {
        return await step.execute(context);
      } catch (error) {
        if (attempt === policy.maxAttempts) throw error;

        const delay = policy.backoffMs * Math.pow(2, attempt - 1);
        await this.sleep(delay);
      }
    }
  }
}
```

#### Integration with BullMQ

```typescript
// apps/worker/src/processors/saga.processor.ts
@Processor('sagas')
export class SagaProcessor {
  constructor(private readonly orchestrator: SagaOrchestrator) {}

  @Process('document-ingestion')
  async handleDocumentIngestion(job: Job<DocumentIngestionContext>) {
    await this.orchestrator.start(documentIngestionSaga, job.data);
  }

  @Process('response-generation')
  async handleResponseGeneration(job: Job<ResponseGenerationContext>) {
    await this.orchestrator.start(responseGenerationSaga, job.data);
  }
}
```

### Monitoring & Observability

```typescript
// Saga execution tracking
interface SagaMetrics {
  saga_executions_total: Counter; // By saga name, status
  saga_step_duration_seconds: Histogram; // By saga name, step
  saga_compensations_total: Counter; // By saga name
}

// Dashboard query
const pendingSagas = await prisma.sagaExecution.findMany({
  where: { status: { in: ['running', 'compensating'] } },
  orderBy: { createdAt: 'desc' },
});
```

## Consequences

### Positive

- **Resilience**: Automatic rollback on failure
- **Visibility**: Clear progress tracking
- **Retry handling**: Built-in retry policies
- **Async**: Non-blocking, scalable
- **Testable**: Each step testable in isolation

### Negative

- **Complexity**: More code than simple jobs
- **Eventual consistency**: State may be inconsistent during saga
- **Compensations**: Must design reversible operations
- **Debugging**: Distributed tracing required

### Mitigations

- Start with simple sagas, add complexity as needed
- Implement comprehensive logging
- Build admin UI for saga management
- Document compensation behavior

## Sagas in Sentinel RFP

| Saga                | Steps                                  | Compensations              |
| ------------------- | -------------------------------------- | -------------------------- |
| Document Ingestion  | Upload → Parse → Chunk → Embed → Index | Delete file/chunks/vectors |
| Response Generation | Plan → Search → Generate → Review      | Mark question as pending   |
| Integration Sync    | Fetch → Transform → Store → Notify     | Revert to previous state   |
| Proposal Export     | Validate → Generate → Upload → Confirm | Delete generated files     |

## Related ADRs

- ADR-001: Event-Driven Architecture
- ADR-007: CQRS for Proposals Domain

## References

- [Saga Pattern by Chris Richardson](https://microservices.io/patterns/data/saga.html)
- [Compensating Transactions](https://docs.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction)
