# ADR 011: Domain-Driven Design (DDD) Approach

**Status:** Accepted

**Date:** 2024-11-12

**Deciders:** Piotr Świderski

**Technical Story:** BuildFlow needs enterprise-grade architecture that properly models the construction business domain and scales to handle complex business rules.

---

## Context

### Current Situation
- BuildFlow is a construction business management system
- Complex domain with quotes, projects, invoices, payments
- Business rules that must be enforced consistently
- Need for clear module boundaries
- Team (future) needs to understand business logic
- Code must be maintainable as features grow

### Problems with Traditional Approach
```php
// Traditional CRUD approach problems:

// ❌ Business logic in controllers
public function acceptQuote(Request $request, Quote $quote)
{
    $quote->status = 'accepted';
    $quote->save();
    
    $project = Project::create([
        'client_id' => $quote->client_id,
        'name' => $quote->title,
        // ... business logic scattered
    ]);
    
    // What if we forget to create invoice?
    // What if project creation fails?
    // Where are the business rules?
}

// ❌ Anemic domain models
class Quote extends Model
{
    // Just getters and setters, no behavior
    public function setStatus($status) {
        $this->status = $status;
    }
}

// ❌ Business rules not enforced
Quote::where('status', 'sent')->update(['status' => 'accepted']);
// Bypasses all validation!
```

### Requirements
- Business logic must be explicit and testable
- Domain rules enforced consistently
- Clear separation between domain and infrastructure
- Code reflects business language (Ubiquitous Language)
- Maintainable as complexity grows
- Team can understand business flows

---

## Decision

**We will use Domain-Driven Design (DDD) patterns to structure BuildFlow as a modular monolith with clear bounded contexts.**

### Core DDD Patterns We'll Use

#### 1. **Bounded Contexts**
Separate modules with clear boundaries:
- Client Management
- Quote Management  
- Project Management
- Invoice & Payment
- Document Management
- Client Portal
- Team Management
- Notifications

#### 2. **Aggregates**
Business entities with consistency boundaries:

```php
// Quote is an Aggregate Root
class Quote 
{
    private QuoteId $id;
    private ClientId $clientId;
    private QuoteNumber $number;
    private QuoteStatus $status;
    private LineItemCollection $lineItems;
    private Money $total;
    
    // Factory method
    public static function createDraft(
        ClientId $clientId,
        OrganizationId $organizationId
    ): self {
        $quote = new self(
            QuoteId::generate(),
            $clientId,
            $organizationId,
            QuoteNumber::generate(),
            QuoteStatus::draft()
        );
        
        $quote->record(new QuoteDraftCreated($quote->id));
        
        return $quote;
    }
    
    // Business methods
    public function addLineItem(LineItem $item): void
    {
        if ($this->status->isSent()) {
            throw new CannotModifySentQuote();
        }
        
        $this->lineItems->add($item);
        $this->recalculateTotal();
        
        $this->record(new LineItemAdded($this->id, $item));
    }
    
    public function send(): void
    {
        if ($this->lineItems->isEmpty()) {
            throw new CannotSendEmptyQuote();
        }
        
        if (!$this->validUntil->isFuture()) {
            throw new InvalidValidUntilDate();
        }
        
        $this->status = QuoteStatus::sent();
        
        $this->record(new QuoteSent($this->id, now()));
    }
    
    public function accept(): void
    {
        if (!$this->status->isSent()) {
            throw new CanOnlyAcceptSentQuote();
        }
        
        if ($this->validUntil->isPast()) {
            throw new QuoteHasExpired();
        }
        
        $this->status = QuoteStatus::accepted();
        $this->acceptedAt = now();
        
        // Domain event - triggers project creation
        $this->record(new QuoteAccepted(
            $this->id,
            $this->clientId,
            $this->total,
            now()
        ));
    }
    
    // Private - business rule
    private function recalculateTotal(): void
    {
        $subtotal = $this->lineItems->subtotal();
        $tax = $subtotal->multiply($this->taxRate);
        $this->total = $subtotal->add($tax)->subtract($this->discount);
    }
}
```

#### 3. **Value Objects**
Immutable objects representing concepts:

```php
// Money value object
final class Money
{
    private function __construct(
        private int $amount,    // in cents
        private Currency $currency
    ) {
        if ($amount < 0) {
            throw new NegativeMoneyException();
        }
    }
    
    public static function fromCents(int $cents, Currency $currency): self
    {
        return new self($cents, $currency);
    }
    
    public static function fromFloat(float $amount, Currency $currency): self
    {
        return new self((int)($amount * 100), $currency);
    }
    
    public function add(Money $other): self
    {
        $this->ensureSameCurrency($other);
        return new self($this->amount + $other->amount, $this->currency);
    }
    
    public function multiply(float $factor): self
    {
        return new self((int)($this->amount * $factor), $this->currency);
    }
    
    public function toFloat(): float
    {
        return $this->amount / 100;
    }
    
    public function equals(Money $other): bool
    {
        return $this->amount === $other->amount 
            && $this->currency->equals($other->currency);
    }
}

// Email value object
final class Email
{
    private function __construct(private string $value)
    {
        if (!filter_var($value, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidEmailException($value);
        }
    }
    
    public static function fromString(string $email): self
    {
        return new self(strtolower(trim($email)));
    }
    
    public function toString(): string
    {
        return $this->value;
    }
}

// QuoteStatus value object
final class QuoteStatus
{
    private const DRAFT = 'draft';
    private const SENT = 'sent';
    private const ACCEPTED = 'accepted';
    private const REJECTED = 'rejected';
    private const EXPIRED = 'expired';
    
    private function __construct(private string $value) {}
    
    public static function draft(): self
    {
        return new self(self::DRAFT);
    }
    
    public static function sent(): self
    {
        return new self(self::SENT);
    }
    
    public function isSent(): bool
    {
        return $this->value === self::SENT;
    }
    
    public function canBeEdited(): bool
    {
        return $this->value === self::DRAFT;
    }
}
```

#### 4. **Domain Events**
Things that happened in the domain:

```php
// Domain event
final class QuoteAccepted implements DomainEvent
{
    public function __construct(
        public readonly QuoteId $quoteId,
        public readonly ClientId $clientId,
        public readonly Money $total,
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
}
```

#### 5. **Repositories (Interfaces in Domain)**
```php
// Domain defines interface
namespace App\Domains\QuoteManagement\Domain;

interface QuoteRepository
{
    public function nextIdentity(): QuoteId;
    public function save(Quote $quote): void;
    public function findById(QuoteId $id): ?Quote;
    public function findByNumber(QuoteNumber $number): ?Quote;
}

// Infrastructure implements
namespace App\Domains\QuoteManagement\Infrastructure;

class EloquentQuoteRepository implements QuoteRepository
{
    public function save(Quote $quote): void
    {
        QuoteModel::updateOrCreate(
            ['id' => $quote->id()->toString()],
            [
                'client_id' => $quote->clientId()->toString(),
                'number' => $quote->number()->toString(),
                'status' => $quote->status()->value(),
                // ... map domain to persistence
            ]
        );
        
        // Dispatch domain events
        foreach ($quote->releaseEvents() as $event) {
            event($event);
        }
    }
}
```

#### 6. **Application Services**
Orchestrate use cases:

```php
namespace App\Domains\QuoteManagement\Application;

class AcceptQuoteHandler
{
    public function __construct(
        private QuoteRepository $quotes,
        private ClientRepository $clients
    ) {}
    
    public function handle(AcceptQuoteCommand $command): void
    {
        // Load aggregate
        $quote = $this->quotes->findById($command->quoteId);
        
        if (!$quote) {
            throw new QuoteNotFoundException();
        }
        
        // Execute business logic (domain)
        $quote->accept();
        
        // Save (will dispatch QuoteAccepted event)
        $this->quotes->save($quote);
        
        // Event listener in ProjectManagement will create project
    }
}
```

---

## Implementation Structure

### Folder Structure
```
app/
├── SharedKernel/              # Shared across domains
│   ├── Domain/
│   │   ├── AggregateRoot.php
│   │   ├── DomainEvent.php
│   │   ├── ValueObject.php
│   │   └── Entity.php
│   └── Infrastructure/
│       ├── EventBus.php
│       └── UuidGenerator.php
│
├── Domains/                   # Bounded Contexts
│   │
│   ├── QuoteManagement/
│   │   ├── Domain/           # Pure business logic
│   │   │   ├── Quote.php           (Aggregate Root)
│   │   │   ├── QuoteId.php         (Value Object)
│   │   │   ├── QuoteStatus.php     (Value Object)
│   │   │   ├── QuoteNumber.php     (Value Object)
│   │   │   ├── LineItem.php        (Entity)
│   │   │   ├── Money.php           (Value Object)
│   │   │   ├── QuoteRepository.php (Interface)
│   │   │   └── Events/
│   │   │       ├── QuoteDraftCreated.php
│   │   │       ├── QuoteAccepted.php
│   │   │       └── LineItemAdded.php
│   │   │
│   │   ├── Application/      # Use cases
│   │   │   ├── Commands/
│   │   │   │   ├── CreateQuoteDraft.php
│   │   │   │   ├── AcceptQuote.php
│   │   │   │   └── AddLineItem.php
│   │   │   ├── Handlers/
│   │   │   │   ├── CreateQuoteDraftHandler.php
│   │   │   │   ├── AcceptQuoteHandler.php
│   │   │   │   └── AddLineItemHandler.php
│   │   │   └── Queries/
│   │   │       ├── FindQuoteQuery.php
│   │   │       └── ListQuotesQuery.php
│   │   │
│   │   └── Infrastructure/   # Technical details
│   │       ├── Persistence/
│   │       │   ├── EloquentQuoteRepository.php
│   │       │   └── QuoteModel.php (Eloquent)
│   │       ├── Http/
│   │       │   ├── QuoteController.php
│   │       │   └── Resources/
│   │       │       └── QuoteResource.php
│   │       └── EventListeners/
│   │           └── SendQuoteEmail.php
│   │
│   ├── ProjectManagement/
│   │   ├── Domain/
│   │   │   ├── Project.php
│   │   │   └── Events/
│   │   │       └── ProjectCreated.php
│   │   ├── Application/
│   │   │   ├── Commands/
│   │   │   │   └── CreateProjectFromQuote.php
│   │   │   └── Handlers/
│   │   │       └── CreateProjectFromQuoteHandler.php
│   │   ├── Infrastructure/
│   │   │   ├── Persistence/
│   │   │   ├── Http/
│   │   │   └── EventListeners/
│   │   │       └── OnQuoteAccepted.php (creates project)
│   │   │
│   └── ClientManagement/
│       ├── Domain/
│       ├── Application/
│       └── Infrastructure/
```

---

## Consequences

### Positive
- ✅ **Business Logic Explicit**: Clear where rules are enforced
- ✅ **Testable**: Domain logic pure, no dependencies
- ✅ **Maintainable**: Changes localized to bounded contexts
- ✅ **Scalable**: Can extract context to microservice later
- ✅ **Team Understanding**: Code reflects business language
- ✅ **Consistency**: Aggregates ensure data integrity
- ✅ **Flexibility**: Easy to change persistence or UI
- ✅ **Portfolio Value**: Shows senior-level thinking

### Negative
- ⚠️ **More Complex**: More files and layers
- ⚠️ **Learning Curve**: Team needs to understand DDD
- ⚠️ **Initial Overhead**: Takes longer to set up
- ⚠️ **Over-engineering Risk**: Can be too much for simple CRUD

### Mitigation
- Start with one bounded context (Quote Management)
- Document patterns clearly
- Use consistent naming conventions
- Gradual adoption, not big bang

---

## Rules and Patterns

### When to Use Aggregates
✅ **Use when:**
- Entity has complex business rules
- Need to enforce consistency
- Multiple related entities (Quote + LineItems)
- State transitions are important

❌ **Don't use when:**
- Simple CRUD (Client might be simpler)
- No business rules
- Just data storage

### When to Use Value Objects
✅ **Always use for:**
- Money (amount + currency)
- Email addresses
- Phone numbers
- Status enums
- Identifiers (IDs)

### Domain Event Guidelines
```php
// ✅ Good: Past tense, what happened
QuoteAccepted
ProjectCreated
PaymentReceived

// ❌ Bad: Commands or present tense
AcceptQuote
CreateProject
ReceivePayment

// ✅ Include relevant data
class QuoteAccepted {
    public readonly QuoteId $quoteId;
    public readonly Money $total;
    public readonly ClientId $clientId;
}

// ❌ Don't include everything
class QuoteAccepted {
    public readonly Quote $quote; // Too much!
}
```

---

## Testing Strategy

### Domain Tests (Pure)
```php
class QuoteTest extends TestCase
{
    /** @test */
    public function cannot_send_empty_quote(): void
    {
        $quote = Quote::createDraft(
            ClientId::fromString('123'),
            OrganizationId::fromString('org-1')
        );
        
        $this->expectException(CannotSendEmptyQuote::class);
        
        $quote->send();
    }
    
    /** @test */
    public function accepting_quote_raises_event(): void
    {
        $quote = $this->createSentQuote();
        
        $quote->accept();
        
        $events = $quote->releaseEvents();
        $this->assertInstanceOf(QuoteAccepted::class, $events[0]);
        $this->assertEquals($quote->id(), $events[0]->quoteId);
    }
}
```

### Application Tests
```php
class AcceptQuoteHandlerTest extends TestCase
{
    /** @test */
    public function accepting_quote_creates_project(): void
    {
        // Arrange
        $quote = $this->createSentQuote();
        $this->quotes->save($quote);
        
        // Act
        $this->handler->handle(
            new AcceptQuoteCommand($quote->id())
        );
        
        // Assert
        Event::assertDispatched(QuoteAccepted::class);
        
        // Project will be created by event listener
        $this->assertProjectExists($quote->clientId());
    }
}
```

---

## Migration Path

### Phase 1: Core Aggregate (Quote)
- Implement Quote as full DDD aggregate
- Show the pattern
- Document learnings

### Phase 2: Expand
- Add Project aggregate
- Add Client (simpler, good contrast)

### Phase 3: Events
- Connect Quote → Project via events
- Show saga pattern

### Phase 4: Full DDD
- All contexts follow pattern
- Consistent structure

---

## References

- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)
- [Implementing Domain-Driven Design by Vaughn Vernon](https://vaughnvernon.com/)
- [Laravel Beyond CRUD](https://laravel-beyond-crud.com/)
- [Milan's DDD in Laravel](https://github.com/spatie/laravel-event-sourcing)

---

## Notes

This is a learning project first, business second. We'll implement DDD properly to understand the patterns, even if some contexts could be simpler. The goal is to show we understand when and how to apply enterprise patterns.

Some contexts (like Client) might be intentionally simpler to show we know when NOT to over-engineer.

---

**Last Updated:** 2024-11-12
