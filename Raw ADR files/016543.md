# ADR-007: CQRS for Proposals Domain

## Status

**Accepted** - January 2026

## Context

The Proposals domain in Sentinel RFP has distinct read and write patterns:

**Write Operations (Commands)**:

- Create proposal from RFP document
- Add/update questions and responses
- Generate AI responses
- Update proposal status
- Complex workflows with validations

**Read Operations (Queries)**:

- Dashboard views (aggregated stats)
- Proposal list with filters
- Full proposal detail with relations
- Search across proposals
- Analytics and reporting

These patterns have different requirements:

- Writes need strong consistency and validation
- Reads need fast response times and flexible queries
- Some reads need eventual consistency is acceptable

We need to decide between:

1. **Traditional CRUD**: Single model for read/write
2. **CQRS**: Separate read and write models
3. **Full Event Sourcing**: Events as source of truth

## Decision

**Implement CQRS (Command Query Responsibility Segregation) for the Proposals domain without full event sourcing.**

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CQRS ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                            USER REQUEST                              │
│                                 │                                    │
│            ┌────────────────────┴────────────────────┐              │
│            │                                         │              │
│            ▼                                         ▼              │
│  ┌─────────────────────┐               ┌─────────────────────┐     │
│  │   COMMAND SIDE      │               │    QUERY SIDE       │     │
│  │                     │               │                     │     │
│  │  ┌───────────────┐  │               │  ┌───────────────┐  │     │
│  │  │   Commands    │  │               │  │   Queries     │  │     │
│  │  │               │  │               │  │               │  │     │
│  │  │ CreateProposal│  │               │  │ GetProposal   │  │     │
│  │  │ AddQuestion   │  │               │  │ ListProposals │  │     │
│  │  │ GenerateResp  │  │               │  │ SearchProposal│  │     │
│  │  │ UpdateStatus  │  │               │  │ GetStats      │  │     │
│  │  └───────┬───────┘  │               │  └───────┬───────┘  │     │
│  │          │          │               │          │          │     │
│  │          ▼          │               │          ▼          │     │
│  │  ┌───────────────┐  │               │  ┌───────────────┐  │     │
│  │  │   Handlers    │  │               │  │   Handlers    │  │     │
│  │  │               │  │               │  │               │  │     │
│  │  │ • Validation  │  │               │  │ • Cache check │  │     │
│  │  │ • Business    │  │               │  │ • Optimized   │  │     │
│  │  │   rules       │  │               │  │   queries     │  │     │
│  │  │ • Events      │  │               │  │ • Transform   │  │     │
│  │  └───────┬───────┘  │               │  └───────┬───────┘  │     │
│  │          │          │               │          │          │     │
│  └──────────┼──────────┘               └──────────┼──────────┘     │
│             │                                      │                │
│             ▼                                      ▼                │
│  ┌─────────────────────┐               ┌─────────────────────┐     │
│  │   WRITE DATABASE    │──── Events ───▶│   READ MODELS      │     │
│  │   (PostgreSQL)      │               │   (Cache/Denorm)   │     │
│  │                     │               │                     │     │
│  │  Normalized tables  │               │  • Redis cache      │     │
│  │  Strong consistency │               │  • Denormalized     │     │
│  │                     │               │    views            │     │
│  └─────────────────────┘               └─────────────────────┘     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation

#### Command Side

```typescript
// apps/api/src/modules/proposal/commands/create-proposal.command.ts
export class CreateProposalCommand {
  constructor(
    public readonly organizationId: string,
    public readonly userId: string,
    public readonly title: string,
    public readonly clientName: string,
    public readonly dueDate: Date,
    public readonly sourceDocumentId?: string,
  ) {}
}

// Handler
@CommandHandler(CreateProposalCommand)
export class CreateProposalHandler implements ICommandHandler<CreateProposalCommand> {
  constructor(
    private readonly prisma: PrismaService,
    private readonly eventEmitter: EventEmitter2,
  ) {}

  async execute(command: CreateProposalCommand): Promise<Proposal> {
    // 1. Validate
    await this.validate(command);

    // 2. Execute business logic
    const proposal = await this.prisma.proposal.create({
      data: {
        organizationId: command.organizationId,
        title: command.title,
        clientName: command.clientName,
        dueDate: command.dueDate,
        status: ProposalStatus.DRAFT,
        createdById: command.userId,
      },
    });

    // 3. Emit domain event
    this.eventEmitter.emit('proposal.created', {
      proposalId: proposal.id,
      organizationId: command.organizationId,
      userId: command.userId,
    });

    // 4. Invalidate read caches
    await this.invalidateCaches(command.organizationId);

    return proposal;
  }

  private async validate(command: CreateProposalCommand): Promise<void> {
    // Check organization limits
    const count = await this.prisma.proposal.count({
      where: { organizationId: command.organizationId },
    });

    const org = await this.prisma.organization.findUnique({
      where: { id: command.organizationId },
    });

    if (count >= org.maxProposalsPerYear) {
      throw new ProposalLimitExceededException();
    }
  }
}
```

#### Query Side

```typescript
// apps/api/src/modules/proposal/queries/get-proposal.query.ts
export class GetProposalQuery {
  constructor(
    public readonly proposalId: string,
    public readonly organizationId: string,
  ) {}
}

// Handler with caching
@QueryHandler(GetProposalQuery)
export class GetProposalHandler implements IQueryHandler<GetProposalQuery> {
  constructor(
    private readonly prisma: PrismaService,
    private readonly cache: CacheService,
  ) {}

  async execute(query: GetProposalQuery): Promise<ProposalDetailDto> {
    // 1. Check cache
    const cacheKey = `proposal:${query.proposalId}`;
    const cached = await this.cache.get<ProposalDetailDto>(cacheKey);
    if (cached) return cached;

    // 2. Optimized query with all relations
    const proposal = await this.prisma.proposal.findFirst({
      where: {
        id: query.proposalId,
        organizationId: query.organizationId,
      },
      include: {
        sections: {
          include: {
            questions: {
              include: {
                responses: {
                  where: { isCurrent: true },
                  include: { citations: true },
                },
              },
            },
          },
        },
        createdBy: { select: { id: true, name: true } },
        sourceDocument: true,
      },
    });

    if (!proposal) throw new ProposalNotFoundException();

    // 3. Transform to DTO
    const dto = this.toDetailDto(proposal);

    // 4. Cache for 5 minutes
    await this.cache.set(cacheKey, dto, 300);

    return dto;
  }
}

// Dashboard stats query (heavily cached)
@QueryHandler(GetProposalStatsQuery)
export class GetProposalStatsHandler {
  async execute(query: GetProposalStatsQuery): Promise<ProposalStats> {
    const cacheKey = `stats:${query.organizationId}`;
    const cached = await this.cache.get<ProposalStats>(cacheKey);
    if (cached) return cached;

    // Aggregation query
    const [active, winRate, avgResponseTime] = await Promise.all([
      this.prisma.proposal.count({
        where: {
          organizationId: query.organizationId,
          status: { in: ['DRAFT', 'IN_PROGRESS', 'REVIEW'] },
        },
      }),
      this.calculateWinRate(query.organizationId),
      this.calculateAvgResponseTime(query.organizationId),
    ]);

    const stats = { active, winRate, avgResponseTime };
    await this.cache.set(cacheKey, stats, 300); // 5 min cache

    return stats;
  }
}
```

#### Event-Driven Cache Invalidation

```typescript
// apps/api/src/modules/proposal/events/proposal-events.handler.ts
@Injectable()
export class ProposalEventsHandler {
  constructor(private readonly cache: CacheService) {}

  @OnEvent('proposal.created')
  @OnEvent('proposal.updated')
  @OnEvent('proposal.deleted')
  async handleProposalChange(event: ProposalEvent) {
    // Invalidate specific proposal cache
    await this.cache.del(`proposal:${event.proposalId}`);

    // Invalidate list caches
    await this.cache.delPattern(`proposals:${event.organizationId}:*`);

    // Invalidate stats
    await this.cache.del(`stats:${event.organizationId}`);
  }

  @OnEvent('response.generated')
  async handleResponseGenerated(event: ResponseEvent) {
    await this.cache.del(`proposal:${event.proposalId}`);
  }
}
```

### NestJS CQRS Module Setup

```typescript
// apps/api/src/modules/proposal/proposal.module.ts
import { CqrsModule } from '@nestjs/cqrs';

const CommandHandlers = [
  CreateProposalHandler,
  AddQuestionHandler,
  GenerateResponseHandler,
  UpdateProposalStatusHandler,
];

const QueryHandlers = [
  GetProposalHandler,
  ListProposalsHandler,
  SearchProposalsHandler,
  GetProposalStatsHandler,
];

const EventHandlers = [ProposalEventsHandler];

@Module({
  imports: [CqrsModule],
  providers: [...CommandHandlers, ...QueryHandlers, ...EventHandlers],
})
export class ProposalModule {}
```

### Read Model Patterns

```typescript
// Denormalized view for list queries
interface ProposalListItem {
  id: string;
  title: string;
  clientName: string;
  status: string;
  dueDate: Date;
  progress: number; // Pre-calculated
  questionCount: number; // Pre-calculated
  answeredCount: number; // Pre-calculated
  pwinScore: number;
  createdByName: string; // Denormalized
  updatedAt: Date;
}

// Materialized in Redis or separate table
// Updated on relevant events
```

## Consequences

### Positive

- **Performance**: Optimized queries for read paths
- **Scalability**: Read and write scale independently
- **Flexibility**: Different models for different needs
- **Caching**: Natural cache invalidation points
- **Maintainability**: Clear separation of concerns

### Negative

- **Complexity**: More code than simple CRUD
- **Eventual consistency**: Reads may lag writes briefly
- **Learning curve**: Team needs CQRS understanding
- **Over-engineering risk**: Not needed for simple domains

### Mitigations

- Apply CQRS only to Proposals (complex domain)
- Keep simple domains as traditional CRUD
- Document patterns clearly
- Start with minimal separation, evolve as needed

## When NOT to Use CQRS

Keep traditional CRUD for:

- User management (simple reads/writes)
- Settings (low traffic)
- Simple lookup tables

## Related ADRs

- ADR-001: Event-Driven Architecture
- ADR-008: Saga Pattern for Distributed Transactions

## References

- [CQRS by Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [NestJS CQRS](https://docs.nestjs.com/recipes/cqrs)
