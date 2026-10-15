# ADR 012: Event-Driven Architecture

**Status:** Accepted

**Date:** 2024-11-12

**Deciders:** Piotr Świderski

**Technical Story:** BuildFlow bounded contexts need to communicate without tight coupling. Cross-cutting concerns like notifications need to react to business events.

---

## Context

### Current Situation
- Multiple bounded contexts (Quote, Project, Invoice, etc.)
- Business processes span multiple contexts
- Cross-cutting concerns (notifications, audit log, analytics)
- Need for loose coupling between modules

### Example Problem
```php
// ❌ Tight coupling - BAD
class AcceptQuoteService
{
    public function __construct(
        private QuoteRepository $quotes,
        private ProjectService $projectService,      // Direct dependency!
        private InvoiceService $invoiceService,      // Direct dependency!
        private NotificationService $notifications,  // Direct dependency!
        private AuditLogService $auditLog           // Direct dependency!
    ) {}
    
    public function accept(Quote $quote): void
    {
        $quote->accept();
        $this->quotes->save($quote);
        
        // Quote context knows about Project context
        $project = $this->projectService->createFromQuote($quote);
        
        // Quote context knows about Invoice context
        $this->invoiceService->generateFromQuote($quote);
        
        // Quote context knows about Notifications
        $this->notifications->send(new QuoteAcceptedEmail($quote));
        
        // Quote context knows about Audit
        $this->auditLog->log('quote.accepted', $quote);
    }
}
// Problems:
// - Quote context depends on 4 other contexts
// - Hard to test
// - Hard to change
// - Violates Single Responsibility
```

### Requirements
- Bounded contexts communicate without direct dependencies
- Easy to add new reactions to events (new listeners)
- Business logic doesn't know about infrastructure (emails, logs)
- Testable in isolation
- Audit trail of all important actions

---

## Decision

**We will use Domain Events and an Event Bus to enable asynchronous, decoupled communication between bounded contexts.**

### Architecture

```
┌─────────────────────────────────────────┐
│      Quote Management Context           │
│                                         │
│  1. User accepts quote                  │
│  2. Quote.accept() called               │
│  3. QuoteAccepted event recorded        │
│  4. Quote saved to repository           │
│  5. Events dispatched to Event Bus      │
└──────────────┬──────────────────────────┘
               │ QuoteAccepted event
               ↓
        ┌──────────────┐
        │  Event Bus   │ (Laravel Event Dispatcher)
        └──────┬───────┘
               │ Dispatches to all listeners
               │
    ┏━━━━━━━━━┻━━━━━━━━━┓
    ↓                    ↓
┌───────────────┐  ┌────────────────┐
│ Project Mgmt  │  │ Notifications  │
│   Context     │  │    Context     │
│               │  │                │
│ OnQuoteAccepted│  │ SendQuoteEmail │
│ → creates     │  │ → sends email  │
│   project     │  │                │
└───────────────┘  └────────────────┘
    ↓
┌───────────────┐
│ Invoice Mgmt  │
│   Context     │
│               │
│ GenerateInvoice│
│ → optional    │
└───────────────┘
```

### Implementation

#### 1. Domain Event Interface

```php
// app/SharedKernel/Domain/DomainEvent.php
namespace App\SharedKernel\Domain;

interface DomainEvent
{
    public function eventName(): string;
    public function occurredOn(): DateTimeImmutable;
    public function aggregateId(): string;
}
```

#### 2. Aggregate Base Class

```php
// app/SharedKernel/Domain/AggregateRoot.php
namespace App\SharedKernel\Domain;

abstract class AggregateRoot
{
    private array $domainEvents = [];
    
    protected function record(DomainEvent $event): void
    {
        $this->domainEvents[] = $event;
    }
    
    public function releaseEvents(): array
    {
        $events = $this->domainEvents;
        $this->domainEvents = [];
        return $events;
    }
}
```

#### 3. Domain Event Example

```php
// app/Domains/QuoteManagement/Domain/Events/QuoteAccepted.php
namespace App\Domains\QuoteManagement\Domain\Events;

use App\SharedKernel\Domain\DomainEvent;

final class QuoteAccepted implements DomainEvent
{
    public function __construct(
        public readonly string $quoteId,
        public readonly string $clientId,
        public readonly string $organizationId,
        public readonly float $totalAmount,
        public readonly string $currency,
        public readonly DateTimeImmutable $acceptedAt
    ) {}
    
    public function eventName(): string
    {
        return 'quote.accepted';
    }
    
    public function occurredOn(): DateTimeImmutable
    {
        return $this->acceptedAt;
    }
    
    public function aggregateId(): string
    {
        return $this->quoteId;
    }
    
    // Serialization for event store (optional)
    public function toArray(): array
    {
        return [
            'quote_id' => $this->quoteId,
            'client_id' => $this->clientId,
            'organization_id' => $this->organizationId,
            'total_amount' => $this->totalAmount,
            'currency' => $this->currency,
            'accepted_at' => $this->acceptedAt->format('Y-m-d H:i:s'),
        ];
    }
}
```

#### 4. Aggregate Recording Events

```php
// app/Domains/QuoteManagement/Domain/Quote.php
namespace App\Domains\QuoteManagement\Domain;

use App\SharedKernel\Domain\AggregateRoot;

class Quote extends AggregateRoot
{
    private QuoteId $id;
    private QuoteStatus $status;
    // ... other properties
    
    public function accept(): void
    {
        // Business rule validation
        if (!$this->status->isSent()) {
            throw new CanOnlyAcceptSentQuote();
        }
        
        if ($this->isExpired()) {
            throw new QuoteHasExpired();
        }
        
        // Change state
        $this->status = QuoteStatus::accepted();
        $this->acceptedAt = now();
        
        // Record domain event
        $this->record(new QuoteAccepted(
            quoteId: $this->id->toString(),
            clientId: $this->clientId->toString(),
            organizationId: $this->organizationId->toString(),
            totalAmount: $this->total->toFloat(),
            currency: $this->total->currency()->code(),
            acceptedAt: new DateTimeImmutable()
        ));
    }
}
```

#### 5. Repository Dispatches Events

```php
// app/Domains/QuoteManagement/Infrastructure/Persistence/EloquentQuoteRepository.php
namespace App\Domains\QuoteManagement\Infrastructure\Persistence;

class EloquentQuoteRepository implements QuoteRepository
{
    public function __construct(
        private EventDispatcher $eventDispatcher
    ) {}
    
    public function save(Quote $quote): void
    {
        // Save to database
        DB::transaction(function () use ($quote) {
            QuoteModel::updateOrCreate(
                ['id' => $quote->id()->toString()],
                $this->mapToDatabase($quote)
            );
            
            // Dispatch all recorded events
            foreach ($quote->releaseEvents() as $event) {
                $this->eventDispatcher->dispatch($event);
            }
        });
    }
}
```

#### 6. Event Listeners (In Other Contexts)

```php
// app/Domains/ProjectManagement/Infrastructure/EventListeners/CreateProjectWhenQuoteAccepted.php
namespace App\Domains\ProjectManagement\Infrastructure\EventListeners;

use App\Domains\QuoteManagement\Domain\Events\QuoteAccepted;
use App\Domains\ProjectManagement\Application\Commands\CreateProjectFromQuote;

class CreateProjectWhenQuoteAccepted
{
    public function __construct(
        private CommandBus $commandBus
    ) {}
    
    public function handle(QuoteAccepted $event): void
    {
        // ProjectManagement context reacts to Quote context event
        $this->commandBus->dispatch(
            new CreateProjectFromQuote(
                quoteId: $event->quoteId,
                clientId: $event->clientId,
                organizationId: $event->organizationId,
                budget: $event->totalAmount
            )
        );
    }
}
```

```php
// app/Domains/Notifications/Infrastructure/EventListeners/SendQuoteAcceptedEmail.php
namespace App\Domains\Notifications\Infrastructure\EventListeners;

use App\Domains\QuoteManagement\Domain\Events\QuoteAccepted;

class SendQuoteAcceptedEmail
{
    public function __construct(
        private Mailer $mailer,
        private ClientRepository $clients
    ) {}
    
    public function handle(QuoteAccepted $event): void
    {
        $client = $this->clients->findById($event->clientId);
        
        $this->mailer->send(
            to: $client->email(),
            template: 'emails.quote-accepted',
            data: [
                'client_name' => $client->name(),
                'quote_number' => $event->quoteId,
                'total' => $event->totalAmount,
            ]
        );
    }
}
```

#### 7. Event Service Provider Registration

```php
// app/Providers/EventServiceProvider.php
namespace App\Providers;

class EventServiceProvider extends ServiceProvider
{
    protected $listen = [
        // Quote Management Events
        QuoteAccepted::class => [
            CreateProjectWhenQuoteAccepted::class,  // Project context
            SendQuoteAcceptedEmail::class,          // Notification context
            LogQuoteAccepted::class,                // Audit context
            UpdateClientStats::class,               // Analytics context
        ],
        
        QuoteRejected::class => [
            NotifyTeamOfRejection::class,
            ScheduleFollowUp::class,
        ],
        
        // Project Management Events
        ProjectCreated::class => [
            SendProjectStartEmail::class,
            CreateInitialMilestone::class,
        ],
        
        ProjectCompleted::class => [
            SendCompletionEmail::class,
            UpdateClientSatisfaction::class,
            GenerateFinalInvoice::class,
        ],
        
        // Payment Events
        PaymentReceived::class => [
            MarkInvoiceAsPaid::class,
            SendPaymentReceipt::class,
            UpdateCashFlow::class,
        ],
    ];
}
```

---

## Consequences

### Positive
- ✅ **Loose Coupling**: Contexts don't know about each other
- ✅ **Easy to Extend**: Add new listeners without changing existing code
- ✅ **Testable**: Test aggregates without infrastructure
- ✅ **Audit Trail**: All events = complete history
- ✅ **Async Processing**: Events can be queued
- ✅ **Single Responsibility**: Each listener does one thing
- ✅ **Open/Closed Principle**: Open for extension, closed for modification

### Negative
- ⚠️ **Eventual Consistency**: Events processed asynchronously
- ⚠️ **Debugging Complexity**: Flow harder to trace
- ⚠️ **Event Versioning**: Need strategy for event changes
- ⚠️ **Failure Handling**: What if listener fails?

### Risks & Mitigation

**Risk: Listener fails, event lost**
```php
// Mitigation: Queue events
class CreateProjectWhenQuoteAccepted implements ShouldQueue
{
    public $tries = 3;
    public $backoff = [60, 300, 900]; // Exponential backoff
    
    public function handle(QuoteAccepted $event): void
    {
        try {
            // Create project
        } catch (Exception $e) {
            Log::error('Failed to create project from quote', [
                'quote_id' => $event->quoteId,
                'error' => $e->getMessage(),
            ]);
            
            // Will retry automatically
            throw $e;
        }
    }
    
    public function failed(QuoteAccepted $event, Throwable $exception): void
    {
        // After all retries failed
        Notification::route('slack', config('slack.webhooks.errors'))
            ->notify(new EventProcessingFailed($event, $exception));
    }
}
```

**Risk: Event schema changes**
```php
// Mitigation: Version events
class QuoteAcceptedV2 implements DomainEvent
{
    // New fields added
    public readonly ?string $notes;
    
    // Keep backward compatibility
    public static function fromV1(QuoteAccepted $v1): self
    {
        return new self(
            quoteId: $v1->quoteId,
            // ... map old to new
            notes: null // New field, default value
        );
    }
}
```

**Risk: Debugging event flow**
```php
// Mitigation: Event tracking
class EventTracker
{
    public function track(DomainEvent $event): void
    {
        DB::table('event_log')->insert([
            'event_id' => Str::uuid(),
            'event_type' => get_class($event),
            'aggregate_id' => $event->aggregateId(),
            'payload' => json_encode($event->toArray()),
            'occurred_at' => $event->occurredOn(),
            'trace_id' => request()->header('X-Trace-ID'),
        ]);
    }
}
```

---

## Event Categories

### 1. State Change Events
**When:** Entity state changes
**Examples:** QuoteAccepted, ProjectCompleted, InvoicePaid

### 2. Creation Events
**When:** New entity created
**Examples:** ClientRegistered, ProjectCreated, InvoiceGenerated

### 3. Time-Based Events
**When:** Scheduled/periodic
**Examples:** QuoteExpired, InvoiceBecameOverdue, ReminderDue

### 4. Integration Events
**When:** External system interaction
**Examples:** PaymentProviderConnected, EmailSent, SMSDelivered

---

## Event Naming Conventions

```php
// ✅ Good: Past tense, specific, domain language
QuoteAccepted
ProjectStarted
PaymentReceived
InvoiceSent
ClientRegistered
DocumentUploaded

// ❌ Bad: Present tense, vague, technical
AcceptQuote        // This is a command
StartingProject    // Present tense
PaymentProcessed   // Too vague
EmailSending       // Technical, not domain
```

---

## Saga Pattern (Process Manager)

For complex workflows spanning multiple contexts:

```php
// app/SharedKernel/Application/Saga.php
abstract class Saga
{
    abstract public function start(DomainEvent $event): void;
    abstract public function handle(DomainEvent $event): void;
}

// Example: Quote Acceptance Saga
class QuoteAcceptanceSaga extends Saga
{
    private SagaState $state;
    
    public function start(QuoteAccepted $event): void
    {
        $this->state = new SagaState([
            'quote_id' => $event->quoteId,
            'client_id' => $event->clientId,
            'steps_completed' => [],
        ]);
        
        // Step 1: Create project
        $this->commandBus->dispatch(
            new CreateProjectFromQuote($event->quoteId)
        );
    }
    
    public function handle(DomainEvent $event): void
    {
        match (get_class($event)) {
            ProjectCreated::class => $this->onProjectCreated($event),
            InvoiceGenerated::class => $this->onInvoiceGenerated($event),
            default => null,
        };
    }
    
    private function onProjectCreated(ProjectCreated $event): void
    {
        $this->state->markCompleted('project_created');
        
        // Step 2: Generate invoice (optional)
        if ($this->shouldGenerateInvoice()) {
            $this->commandBus->dispatch(
                new GenerateInvoiceFromQuote($this->state->quoteId)
            );
        } else {
            $this->complete();
        }
    }
    
    private function onInvoiceGenerated(InvoiceGenerated $event): void
    {
        $this->state->markCompleted('invoice_generated');
        $this->complete();
    }
    
    private function complete(): void
    {
        event(new QuoteAcceptanceSagaCompleted($this->state->quoteId));
    }
}
```

---

## Testing Strategy

### Unit Test: Aggregate Records Events
```php
class QuoteTest extends TestCase
{
    /** @test */
    public function accepting_quote_records_domain_event(): void
    {
        // Arrange
        $quote = $this->createSentQuote();
        
        // Act
        $quote->accept();
        
        // Assert
        $events = $quote->releaseEvents();
        $this->assertCount(1, $events);
        $this->assertInstanceOf(QuoteAccepted::class, $events[0]);
        $this->assertEquals($quote->id()->toString(), $events[0]->quoteId);
    }
}
```

### Integration Test: Events Are Dispatched
```php
class AcceptQuoteHandlerTest extends TestCase
{
    /** @test */
    public function accepting_quote_dispatches_event(): void
    {
        // Arrange
        Event::fake([QuoteAccepted::class]);
        $quote = $this->createSentQuote();
        
        // Act
        $this->handler->handle(new AcceptQuote($quote->id()));
        
        // Assert
        Event::assertDispatched(QuoteAccepted::class, function ($event) use ($quote) {
            return $event->quoteId === $quote->id()->toString();
        });
    }
}
```

### Integration Test: Listener Reacts
```php
class CreateProjectWhenQuoteAcceptedTest extends TestCase
{
    /** @test */
    public function creates_project_when_quote_accepted(): void
    {
        // Arrange
        $event = new QuoteAccepted(
            quoteId: 'quote-123',
            clientId: 'client-456',
            organizationId: 'org-789',
            totalAmount: 5000.00,
            currency: 'USD',
            acceptedAt: now()
        );
        
        // Act
        $this->listener->handle($event);
        
        // Assert
        $this->assertDatabaseHas('projects', [
            'origin_quote_id' => 'quote-123',
            'client_id' => 'client-456',
        ]);
    }
}
```

---

## Event Store (Optional - Advanced)

For full event sourcing:

```php
// Store all events for audit/replay
class EventStore
{
    public function append(DomainEvent $event): void
    {
        DB::table('event_store')->insert([
            'event_id' => Str::uuid(),
            'event_type' => get_class($event),
            'aggregate_id' => $event->aggregateId(),
            'aggregate_type' => $event->aggregateType(),
            'payload' => json_encode($event->toArray()),
            'metadata' => json_encode([
                'user_id' => auth()->id(),
                'ip_address' => request()->ip(),
                'user_agent' => request()->userAgent(),
            ]),
            'occurred_at' => $event->occurredOn(),
            'sequence' => $this->nextSequence($event->aggregateId()),
        ]);
    }
    
    public function getStream(string $aggregateId): array
    {
        return DB::table('event_store')
            ->where('aggregate_id', $aggregateId)
            ->orderBy('sequence')
            ->get()
            ->map(fn($row) => $this->deserialize($row))
            ->toArray();
    }
}

// Rebuild aggregate from events
class QuoteProjector
{
    public function project(array $events): Quote
    {
        $quote = null;
        
        foreach ($events as $event) {
            $quote = match (get_class($event)) {
                QuoteDraftCreated::class => Quote::reconstruct($event),
                LineItemAdded::class => $quote->applyLineItemAdded($event),
                QuoteAccepted::class => $quote->applyAccepted($event),
                default => $quote,
            };
        }
        
        return $quote;
    }
}
```

---

## Related Decisions

- [ADR-011](011-domain-driven-design.md) - DDD enables event-driven
- [ADR-013](013-cqrs-basic.md) - CQRS complements event-driven

---

## References

- [Event-Driven Microservices (Chris Richardson)](https://microservices.io/patterns/data/event-driven-architecture.html)
- [Domain Events (Martin Fowler)](https://martinfowler.com/eaaDev/DomainEvent.html)
- [Laravel Event Sourcing (Spatie)](https://github.com/spatie/laravel-event-sourcing)

---

**Last Updated:** 2024-11-12
