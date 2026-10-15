# ADR 013: CQRS (Command Query Responsibility Segregation) - Basic

**Status:** Accepted

**Date:** 2024-11-12

**Deciders:** Piotr Świderski

**Technical Story:** As BuildFlow grows, we need to optimize read operations separately from write operations. Complex queries across multiple aggregates become difficult when using domain models.

---

## Context

### Current Situation
- Domain models (aggregates) optimized for writes and business logic
- Complex queries need to join multiple tables
- Dashboard needs aggregated statistics
- List views need different data than detail views
- Performance suffers when loading full aggregates just to display

### Example Problem

```php
// ❌ Bad: Using domain model for read-heavy operations
class QuoteController
{
    public function index()
    {
        // Loads full aggregates with all relationships
        $quotes = Quote::with([
            'client',
            'lineItems',
            'organization',
            'createdBy'
        ])->paginate(20);
        
        // We only need: number, client name, total, status
        // But we load everything!
        
        return QuoteResource::collection($quotes);
    }
    
    public function dashboard()
    {
        // Complex aggregations on domain models
        $stats = [
            'total_quotes' => Quote::count(),
            'pending_quotes' => Quote::where('status', 'sent')->count(),
            'total_value' => Quote::where('status', 'accepted')->sum('total'),
            'acceptance_rate' => // complex calculation
        ];
        
        // Multiple queries, not optimized
    }
}

// ❌ Bad: Search across multiple aggregates
public function search(string $term)
{
    // Need data from multiple contexts
    $clients = Client::where('name', 'like', "%$term%")->get();
    $quotes = Quote::where('title', 'like', "%$term%")->get();
    $projects = Project::where('name', 'like', "%$term%")->get();
    
    // How to combine and sort?
    // How to paginate across different types?
}
```

### Requirements
- Fast read operations (dashboard, lists, search)
- Complex queries without loading full aggregates
- Different representations for different views
- Maintain business logic integrity in writes
- Eventual consistency acceptable for reads

---

## Decision

**We will implement basic CQRS: separate models for Commands (writes) and Queries (reads), synchronized via domain events.**

### Architecture

```
┌─────────────────────────────────────────┐
│           WRITE SIDE (Commands)         │
│                                         │
│  Commands → Handlers → Aggregates       │
│  (Business Logic, Validation)           │
│                                         │
│  - Quote.php (aggregate)                │
│  - AcceptQuoteHandler                   │
│  - Domain Rules Enforced                │
│                                         │
│  Writes to → quotes, quote_line_items   │
└──────────────┬──────────────────────────┘
               │ Domain Events
               ↓
        ┌──────────────┐
        │  Event Bus   │
        └──────┬───────┘
               │
               ↓ Projections update read models
┌─────────────────────────────────────────┐
│            READ SIDE (Queries)          │
│                                         │
│  Queries → Read Models (denormalized)   │
│  (Optimized for Display)                │
│                                         │
│  - QuoteListView                        │
│  - QuoteDashboardStats                  │
│  - QuoteSearchView                      │
│                                         │
│  Reads from → quote_list_view,          │
│               dashboard_stats,          │
│               search_index              │
└─────────────────────────────────────────┘
```

### Key Concepts

#### 1. Write Model (Domain Model)
- Full aggregates with business logic
- Enforces invariants
- Optimized for writes and consistency
- Records domain events

#### 2. Read Model (Projection)
- Denormalized views
- Optimized for specific queries
- No business logic
- Eventually consistent

#### 3. Projectors
- Listen to domain events
- Update read models
- Handle denormalization

---

## Implementation

### Write Side (Commands)

```php
// app/Domains/QuoteManagement/Application/Commands/AcceptQuote.php
namespace App\Domains\QuoteManagement\Application\Commands;

final class AcceptQuote
{
    public function __construct(
        public readonly string $quoteId
    ) {}
}

// Handler uses domain model
class AcceptQuoteHandler
{
    public function __construct(
        private QuoteRepository $quotes
    ) {}
    
    public function handle(AcceptQuote $command): void
    {
        $quote = $this->quotes->findById($command->quoteId);
        
        // Business logic in aggregate
        $quote->accept();
        
        // Save (will dispatch QuoteAccepted event)
        $this->quotes->save($quote);
    }
}
```

### Read Side (Queries)

#### Read Model Schema

```php
// Database migration for read model
Schema::create('quote_list_view', function (Blueprint $table) {
    $table->uuid('id')->primary();
    $table->uuid('organization_id')->index();
    
    // Denormalized data from multiple sources
    $table->string('quote_number');
    $table->uuid('client_id');
    $table->string('client_name');      // Denormalized from Client
    $table->string('client_email');     // Denormalized from Client
    $table->string('title');
    $table->enum('status', ['draft', 'sent', 'accepted', 'rejected', 'expired']);
    $table->decimal('total', 10, 2);
    $table->string('currency', 3);
    $table->date('valid_until');
    $table->integer('line_items_count'); // Aggregated
    $table->timestamp('sent_at')->nullable();
    $table->timestamp('accepted_at')->nullable();
    $table->timestamp('created_at');
    $table->timestamp('updated_at');
    
    // Optimized indexes for common queries
    $table->index(['organization_id', 'status']);
    $table->index(['organization_id', 'created_at']);
    $table->index(['client_id', 'status']);
});

// Read model for dashboard
Schema::create('quote_dashboard_stats', function (Blueprint $table) {
    $table->uuid('organization_id')->primary();
    $table->integer('total_quotes')->default(0);
    $table->integer('draft_quotes')->default(0);
    $table->integer('sent_quotes')->default(0);
    $table->integer('accepted_quotes')->default(0);
    $table->integer('rejected_quotes')->default(0);
    $table->decimal('total_value', 12, 2)->default(0);
    $table->decimal('accepted_value', 12, 2)->default(0);
    $table->decimal('pending_value', 12, 2)->default(0);
    $table->decimal('acceptance_rate', 5, 2)->default(0);
    $table->timestamp('last_updated');
});

// Read model for search
Schema::create('search_index', function (Blueprint $table) {
    $table->uuid('id')->primary();
    $table->uuid('organization_id')->index();
    $table->enum('entity_type', ['quote', 'project', 'client', 'invoice']);
    $table->uuid('entity_id');
    $table->string('title');
    $table->text('searchable_text');  // Full-text search
    $table->json('metadata');         // Type-specific data
    $table->timestamp('created_at');
    
    $table->fullText('searchable_text');
    $table->index(['organization_id', 'entity_type']);
});
```

#### Read Model Classes

```php
// app/Domains/QuoteManagement/Infrastructure/ReadModels/QuoteListView.php
namespace App\Domains\QuoteManagement\Infrastructure\ReadModels;

use Illuminate\Database\Eloquent\Model;

class QuoteListView extends Model
{
    protected $table = 'quote_list_view';
    protected $keyType = 'string';
    public $incrementing = false;
    
    protected $casts = [
        'total' => 'float',
        'sent_at' => 'datetime',
        'accepted_at' => 'datetime',
    ];
    
    // This is read-only!
    // No setters, no save(), no update()
    
    public static function forOrganization(string $organizationId)
    {
        return static::where('organization_id', $organizationId);
    }
    
    public function scopePending($query)
    {
        return $query->where('status', 'sent');
    }
    
    public function scopeAccepted($query)
    {
        return $query->where('status', 'accepted');
    }
}

// Query service
class QuoteQueryService
{
    public function list(
        string $organizationId,
        ?string $status = null,
        ?string $clientId = null,
        int $perPage = 20
    ): LengthAwarePaginator {
        return QuoteListView::forOrganization($organizationId)
            ->when($status, fn($q) => $q->where('status', $status))
            ->when($clientId, fn($q) => $q->where('client_id', $clientId))
            ->orderByDesc('created_at')
            ->paginate($perPage);
    }
    
    public function findById(string $quoteId): ?QuoteListView
    {
        return QuoteListView::find($quoteId);
    }
    
    public function getDashboardStats(string $organizationId): array
    {
        return DB::table('quote_dashboard_stats')
            ->where('organization_id', $organizationId)
            ->first();
    }
    
    public function search(
        string $organizationId,
        string $term
    ): Collection {
        return DB::table('search_index')
            ->where('organization_id', $organizationId)
            ->where('entity_type', 'quote')
            ->whereFullText('searchable_text', $term)
            ->get();
    }
}
```

### Projectors (Update Read Models)

```php
// app/Domains/QuoteManagement/Infrastructure/Projectors/QuoteListProjector.php
namespace App\Domains\QuoteManagement\Infrastructure\Projectors;

class QuoteListProjector
{
    public function onQuoteDraftCreated(QuoteDraftCreated $event): void
    {
        DB::table('quote_list_view')->insert([
            'id' => $event->quoteId,
            'organization_id' => $event->organizationId,
            'quote_number' => $event->quoteNumber,
            'client_id' => $event->clientId,
            'client_name' => $this->getClientName($event->clientId),
            'client_email' => $this->getClientEmail($event->clientId),
            'title' => $event->title,
            'status' => 'draft',
            'total' => 0,
            'currency' => $event->currency,
            'line_items_count' => 0,
            'created_at' => $event->occurredOn(),
            'updated_at' => $event->occurredOn(),
        ]);
        
        // Update stats
        $this->incrementStat($event->organizationId, 'total_quotes');
        $this->incrementStat($event->organizationId, 'draft_quotes');
    }
    
    public function onLineItemAdded(LineItemAdded $event): void
    {
        $current = DB::table('quote_list_view')
            ->where('id', $event->quoteId)
            ->first();
        
        DB::table('quote_list_view')
            ->where('id', $event->quoteId)
            ->update([
                'total' => $current->total + $event->lineItemTotal,
                'line_items_count' => $current->line_items_count + 1,
                'updated_at' => $event->occurredOn(),
            ]);
    }
    
    public function onQuoteSent(QuoteSent $event): void
    {
        DB::table('quote_list_view')
            ->where('id', $event->quoteId)
            ->update([
                'status' => 'sent',
                'sent_at' => $event->occurredOn(),
                'updated_at' => $event->occurredOn(),
            ]);
        
        $quote = DB::table('quote_list_view')->find($event->quoteId);
        
        // Update stats
        $this->decrementStat($event->organizationId, 'draft_quotes');
        $this->incrementStat($event->organizationId, 'sent_quotes');
        $this->addToStat($event->organizationId, 'pending_value', $quote->total);
    }
    
    public function onQuoteAccepted(QuoteAccepted $event): void
    {
        DB::table('quote_list_view')
            ->where('id', $event->quoteId)
            ->update([
                'status' => 'accepted',
                'accepted_at' => $event->occurredOn(),
                'updated_at' => $event->occurredOn(),
            ]);
        
        // Update stats
        $this->decrementStat($event->organizationId, 'sent_quotes');
        $this->incrementStat($event->organizationId, 'accepted_quotes');
        $this->subtractFromStat($event->organizationId, 'pending_value', $event->totalAmount);
        $this->addToStat($event->organizationId, 'accepted_value', $event->totalAmount);
        $this->recalculateAcceptanceRate($event->organizationId);
    }
    
    // Helper methods
    private function getClientName(string $clientId): string
    {
        return DB::table('clients')
            ->where('id', $clientId)
            ->value('name');
    }
    
    private function incrementStat(string $orgId, string $field): void
    {
        DB::table('quote_dashboard_stats')
            ->where('organization_id', $orgId)
            ->increment($field);
    }
}

// app/Domains/QuoteManagement/Infrastructure/Projectors/SearchIndexProjector.php
class SearchIndexProjector
{
    public function onQuoteDraftCreated(QuoteDraftCreated $event): void
    {
        DB::table('search_index')->insert([
            'id' => Str::uuid(),
            'organization_id' => $event->organizationId,
            'entity_type' => 'quote',
            'entity_id' => $event->quoteId,
            'title' => $event->title,
            'searchable_text' => $this->buildSearchableText($event),
            'metadata' => json_encode([
                'quote_number' => $event->quoteNumber,
                'client_id' => $event->clientId,
                'status' => 'draft',
            ]),
            'created_at' => $event->occurredOn(),
        ]);
    }
    
    private function buildSearchableText(QuoteDraftCreated $event): string
    {
        return implode(' ', [
            $event->title,
            $event->quoteNumber,
            $this->getClientName($event->clientId),
            // Add more searchable fields
        ]);
    }
}
```

### Register Projectors

```php
// app/Providers/EventServiceProvider.php
protected $listen = [
    QuoteDraftCreated::class => [
        QuoteListProjector::class . '@onQuoteDraftCreated',
        SearchIndexProjector::class . '@onQuoteDraftCreated',
        DashboardStatsProjector::class . '@onQuoteDraftCreated',
    ],
    
    LineItemAdded::class => [
        QuoteListProjector::class . '@onLineItemAdded',
    ],
    
    QuoteSent::class => [
        QuoteListProjector::class . '@onQuoteSent',
        SearchIndexProjector::class . '@onQuoteSent',
        DashboardStatsProjector::class . '@onQuoteSent',
    ],
    
    QuoteAccepted::class => [
        QuoteListProjector::class . '@onQuoteAccepted',
        DashboardStatsProjector::class . '@onQuoteAccepted',
        CreateProjectWhenQuoteAccepted::class, // Different context
    ],
];
```

### Controller Usage

```php
// app/Http/Controllers/Api/QuoteController.php
class QuoteController extends Controller
{
    public function __construct(
        private CommandBus $commandBus,
        private QuoteQueryService $queries
    ) {}
    
    // WRITE: Use command
    public function store(CreateQuoteRequest $request)
    {
        $quoteId = $this->commandBus->dispatch(
            new CreateQuoteDraft(
                clientId: $request->client_id,
                title: $request->title,
                validUntil: $request->valid_until
            )
        );
        
        return response()->json(['id' => $quoteId], 201);
    }
    
    // WRITE: Use command
    public function accept(Quote $quote)
    {
        $this->commandBus->dispatch(
            new AcceptQuote($quote->id)
        );
        
        return response()->json(['message' => 'Quote accepted']);
    }
    
    // READ: Use query service
    public function index(Request $request)
    {
        $quotes = $this->queries->list(
            organizationId: auth()->user()->organization_id,
            status: $request->status,
            clientId: $request->client_id,
            perPage: $request->per_page ?? 20
        );
        
        return QuoteListResource::collection($quotes);
    }
    
    // READ: Use query service
    public function show(string $id)
    {
        // For list view, use read model
        $quote = $this->queries->findById($id);
        
        return new QuoteListResource($quote);
    }
    
    // READ: Use query service
    public function dashboard()
    {
        $stats = $this->queries->getDashboardStats(
            auth()->user()->organization_id
        );
        
        return response()->json($stats);
    }
}
```

---

## Consequences

### Positive
- ✅ **Performance**: Read operations extremely fast
- ✅ **Scalability**: Can optimize reads and writes separately
- ✅ **Flexibility**: Different representations for different needs
- ✅ **Simplicity**: Queries are simple SQL, no ORM overhead
- ✅ **Evolution**: Can add new read models without touching write side

### Negative
- ⚠️ **Complexity**: More code (projectors, read models)
- ⚠️ **Eventual Consistency**: Read models slightly behind
- ⚠️ **Synchronization**: Must keep projectors in sync
- ⚠️ **Storage**: Duplicate data (write DB + read models)

### When to Use CQRS

✅ **Use CQRS when:**
- Complex queries across multiple aggregates
- High read:write ratio
- Need different representations
- Performance critical reads (dashboard, search)
- Reports and analytics

❌ **Don't use CQRS when:**
- Simple CRUD
- Low traffic
- Strong consistency required immediately
- Team unfamiliar with pattern

---

## Testing Strategy

### Write Side Tests
```php
// Test commands and aggregates (existing DDD tests)
class AcceptQuoteHandlerTest extends TestCase
{
    /** @test */
    public function accepting_quote_dispatches_event(): void
    {
        Event::fake([QuoteAccepted::class]);
        
        $this->handler->handle(new AcceptQuote($this->quote->id));
        
        Event::assertDispatched(QuoteAccepted::class);
    }
}
```

### Projector Tests
```php
class QuoteListProjectorTest extends TestCase
{
    /** @test */
    public function creates_list_view_on_quote_created(): void
    {
        $event = new QuoteDraftCreated(
            quoteId: 'quote-123',
            // ... event data
        );
        
        $this->projector->onQuoteDraftCreated($event);
        
        $this->assertDatabaseHas('quote_list_view', [
            'id' => 'quote-123',
            'status' => 'draft',
        ]);
    }
    
    /** @test */
    public function updates_stats_on_quote_accepted(): void
    {
        $this->createListView('quote-123', total: 5000);
        
        $event = new QuoteAccepted(
            quoteId: 'quote-123',
            totalAmount: 5000,
            // ...
        );
        
        $this->projector->onQuoteAccepted($event);
        
        $stats = DB::table('quote_dashboard_stats')
            ->where('organization_id', $this->orgId)
            ->first();
            
        $this->assertEquals(1, $stats->accepted_quotes);
        $this->assertEquals(5000, $stats->accepted_value);
    }
}
```

### Read Model Tests
```php
class QuoteQueryServiceTest extends TestCase
{
    /** @test */
    public function lists_quotes_for_organization(): void
    {
        $this->createListView('quote-1', org: 'org-1');
        $this->createListView('quote-2', org: 'org-1');
        $this->createListView('quote-3', org: 'org-2');
        
        $quotes = $this->queryService->list('org-1');
        
        $this->assertCount(2, $quotes);
    }
    
    /** @test */
    public function filters_by_status(): void
    {
        $this->createListView('quote-1', status: 'sent');
        $this->createListView('quote-2', status: 'accepted');
        
        $quotes = $this->queryService->list('org-1', status: 'sent');
        
        $this->assertCount(1, $quotes);
    }
}
```

---

## Rebuild Projections

For when projections are out of sync:

```php
// app/Console/Commands/RebuildProjections.php
class RebuildProjections extends Command
{
    protected $signature = 'projections:rebuild {projection?}';
    
    public function handle(): void
    {
        $projection = $this->argument('projection');
        
        if ($projection === 'quote-list' || !$projection) {
            $this->rebuildQuoteList();
        }
        
        if ($projection === 'dashboard-stats' || !$projection) {
            $this->rebuildDashboardStats();
        }
    }
    
    private function rebuildQuoteList(): void
    {
        $this->info('Rebuilding quote list view...');
        
        DB::table('quote_list_view')->truncate();
        
        // Replay events or rebuild from write model
        Quote::chunk(100, function ($quotes) {
            foreach ($quotes as $quote) {
                DB::table('quote_list_view')->insert(
                    $this->mapQuoteToListView($quote)
                );
            }
        });
        
        $this->info('Done!');
    }
}
```

---

## Related Decisions

- [ADR-011](011-domain-driven-design.md) - DDD aggregates are write models
- [ADR-012](012-event-driven-architecture.md) - Events synchronize read models

---

## References

- [CQRS by Martin Fowler](https://martinfowler.com/bliki/CQRS.html)
- [CQRS Journey (Microsoft)](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10))
- [Event Sourcing (Greg Young)](https://www.eventstore.com/blog/what-is-event-sourcing)

---

**Last Updated:** 2024-11-12
