---
docid: ADR-057
title: ADR 023 Erp Plugin Architecture
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR-023: ERP/CRM/PIM Plugin Architecture

**Status:** Proposed  
**Date:** 2026-01-02  
**Owner:** @Architect  
**Stakeholders:** @Backend, @DevOps, @ProductOwner, @Security

## Context

B2X requires integration with various ERP/CRM/PIM systems (starting with enventa Trade ERP) while maintaining:
- Multi-tenant isolation
- Customer-specific customizations
- System stability and maintainability
- Modern .NET 10 architecture compatibility

Legacy ERP systems often use .NET Framework 4.8, requiring isolation strategies.

### Data Volume Challenge

**Large Catalogs**: Some customers have extremely large catalogs:
- 1.5 million articles
- 30 million attributes/Merkmale
- Images, references, cross-references

**Synchronization Strategy** (based on eGate implementation):
- **Master Data** → Synchronized (acceptable time delay)
  - Articles, attributes, images, references
  - Background sync jobs (hourly/nightly)
  - Eventual consistency acceptable
- **Customer-Specific Data** → Live queries (must be current)
  - Kundenindividuelle Preise (customer prices)
  - Bestände (stock levels)
  - Vorgangsdaten (order status)
  - Always query ERP directly

### Technical Constraints

1. **.NET Framework 4.8 Limitations**
   - No native `IAsyncEnumerable<T>` support (requires C# 8.0 / .NET Core 3.0+)
   - Limited async/await patterns compared to modern .NET
   - Windows-only deployment for Framework assemblies

2. **enventa Trade ERP Specifics**
   - Uses proprietary ORM mapper (FrameworkSystems - not EF Core compatible)
   - Direct assembly integration required for performance
   - Millions of records require optimized bulk operations
   - **⚠️ CRITICAL: NOT MULTITHREADING-SAFE** - All operations must be serialized
   - **⚠️ CRITICAL: EXPENSIVE INITIALIZATION (>2s)** - Connection must be pooled/cached
   - **Multi-Tenant via BusinessUnit** - Tenant selected during initialization

3. **Single-Threading Constraint**
   - enventa ERP assemblies cannot handle concurrent access
   - Login/Logout operations require exclusive locks
   - All data access must go through a single-threaded worker
   - Concurrent requests must be queued and processed sequentially

4. **Connection Pooling & Initialization**
   - **Initialization cost**: >2 seconds per tenant (BusinessUnit setup)
   - **Connection strategy**: Keep-alive with idle timeout (30 min default)
   - **Warmup**: Pre-initialize connections for active tenants
   - **Health checks**: Periodic ping to maintain connection state
   - **Lazy initialization**: Create connection on first request, keep alive
   - **Cache invalidation**: Release after prolonged inactivity (configurable)

4. **Cross-Framework Communication**
   - Provider containers run .NET Framework 4.8
   - B2X core runs .NET 10
   - Need framework-agnostic communication protocols

## Decision

Implement a **Plugin-based Architecture** using containerized ERP providers with standardized interfaces.

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   B2X     │────│  Provider        │────│  ERP Container  │
│   Core System   │    │  Manager         │    │  (Docker)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────┴──────┐
                       │ Connection  │
                       │ Pool        │
                       │ (per-tenant)│
                       └──────┬──────┘
                              │ Keep-Alive (30min idle timeout)
                              │ Init: >2s (expensive!)
                              ▼
                       ┌─────────────────┐
                       │  Plugin         │
                       │  Registry       │
                       └─────────────────┘
```

### Key Components

1. **Standardized Interfaces**
   - `IErpProvider`: Core ERP operations
   - `ICrmProvider`: CRM functionality
   - `IPimProvider`: Product Information Management

2. **Containerized Providers**
   - Each ERP system runs in isolated Docker containers
   - Windows containers for .NET Framework compatibility
   - Linux containers for modern implementations

3. **Provider Manager**
   - Dynamic container orchestration
   - Tenant-specific provider instantiation
   - Health monitoring and failover

4. **Plugin Registry**
   - Centralized catalog of available providers
   - Version management and compatibility matrix
   - Customer-specific provider deployments

## Implementation Details

### Provider Interface Contracts

```csharp
public interface IErpProvider
{
    // Single Operations (for simple queries)
    Task<PimData> GetProductAsync(string productId, TenantContext context);
    Task<CrmData> GetCustomerAsync(string customerId, TenantContext context);
    Task<ErpOrder> CreateOrderAsync(OrderRequest request, TenantContext context);
    
    // Bulk Operations (to reduce chatty interfaces)
    Task<IEnumerable<PimData>> GetProductsAsync(IEnumerable<string> productIds, TenantContext context);
    Task<IEnumerable<CrmData>> GetCustomersAsync(IEnumerable<string> customerIds, TenantContext context);
    Task<BatchResult> CreateOrdersAsync(IEnumerable<OrderRequest> requests, TenantContext context);
    
    // Streaming Operations (for large datasets)
    IAsyncEnumerable<PimData> StreamProductsAsync(ProductFilter filter, TenantContext context);
    IAsyncEnumerable<CrmData> StreamCustomersAsync(CustomerFilter filter, TenantContext context);
    
    // Batch Sync Operations (optimized for bulk data transfer)
    Task SyncProductsAsync(IEnumerable<Product> products, TenantContext context);
    Task SyncCustomersAsync(IEnumerable<Customer> customers, TenantContext context);
    Task<SyncResult> BulkSyncAsync(BulkSyncRequest request, TenantContext context);
}

public interface ICrmProvider
{
    Task<CrmContact> GetContactAsync(string contactId, TenantContext context);
    Task<IEnumerable<CrmActivity>> GetActivitiesAsync(string customerId, TenantContext context);
    
    // Bulk operations to minimize network roundtrips
    Task<IEnumerable<CrmContact>> GetContactsAsync(IEnumerable<string> contactIds, TenantContext context);
    Task<Dictionary<string, IEnumerable<CrmActivity>>> GetActivitiesBatchAsync(IEnumerable<string> customerIds, TenantContext context);
}

public interface IPimProvider
{
    Task<PimProduct> GetProductDetailsAsync(string productId, TenantContext context);
    Task<IEnumerable<PimCategory>> GetCategoriesAsync(TenantContext context);
    
    // Optimized for catalog operations
    Task<CatalogData> GetCatalogAsync(CatalogFilter filter, TenantContext context);
    IAsyncEnumerable<PimProduct> StreamCatalogAsync(CatalogFilter filter, TenantContext context);
}
```

### .NET Framework 4.8 Compatibility Layer

Since `IAsyncEnumerable<T>` is not available in .NET Framework 4.8, provider implementations use alternative patterns:

#### Framework-Agnostic Streaming Patterns

```csharp
// Option 1: Callback-based streaming (works in .NET 4.8)
public interface IErpProviderLegacy
{
    Task StreamProductsAsync(
        ProductFilter filter, 
        Func<PimData, Task> onItem,  // Callback per item
        TenantContext context,
        CancellationToken ct = default);
}

// Option 2: Chunked/Paged responses (works in .NET 4.8)
public interface IErpProviderPaged
{
    Task<PagedResult<PimData>> GetProductsPagedAsync(
        ProductFilter filter,
        int pageSize,
        string continuationToken,
        TenantContext context);
}

// Option 3: gRPC streaming (framework-agnostic)
// Uses HTTP/2 server streaming - works across framework boundaries
service ErpProviderService {
    rpc StreamProducts(ProductFilter) returns (stream PimData);
}
```

#### Communication Protocol Strategy

| Pattern | .NET 4.8 Support | Use Case | Latency |
|---------|------------------|----------|----------|
| **gRPC Streaming** | ✅ (via Grpc.Core) | Large datasets, real-time | Low |
| **Callback Pattern** | ✅ Native | In-process streaming | Very Low |
| **Paged Results** | ✅ Native | REST APIs, simple integration | Medium |
| **SignalR** | ✅ (via AspNet.SignalR) | Bi-directional, events | Low |

#### Recommended Approach: gRPC with Fallback

```csharp
// B2X side (.NET 10) - consumes as IAsyncEnumerable
public async IAsyncEnumerable<PimData> StreamProductsAsync(
    ProductFilter filter, 
    TenantContext context,
    [EnumeratorCancellation] CancellationToken ct = default)
{
    // gRPC client streams from .NET 4.8 provider container
    using var call = _grpcClient.StreamProducts(filter);
    await foreach (var item in call.ResponseStream.ReadAllAsync(ct))
    {
        yield return item;
    }
}

// Provider side (.NET 4.8) - uses Grpc.Core for streaming
public override async Task StreamProducts(
    ProductFilter request,
    IServerStreamWriter<PimData> responseStream,
    ServerCallContext context)
{
    // Use enventa's proprietary ORM with yield-style iteration
    foreach (var product in _enventaOrm.QueryProducts(request))
    {
        await responseStream.WriteAsync(MapToProto(product));
    }
}
```

#### Proprietary ORM Integration

enventa Trade ERP uses a proprietary ORM that requires specific handling:

```csharp
// Wrapper for enventa's proprietary ORM
public class EnventaOrmAdapter : IErpDataAccess
{
    private readonly IcECArticle _articleService; // enventa assembly
    
    public IEnumerable<Product> QueryProducts(ProductFilter filter)
    {
        // Use enventa's query builder pattern
        var query = new NVArticleQueryBuilder()
            .ByCategory(filter.CategoryId)
            .WithPricing(filter.IncludePrices);
        
        // Yield results to avoid loading all into memory
        foreach (var article in query.Execute())
        {
            yield return MapToProduct(article);
        }
    }
    
    public void BulkSync(IEnumerable<Product> products, int batchSize = 1000)
    {
        // Use enventa's batch processing capabilities
        foreach (var batch in products.Chunk(batchSize))
        {
            using var scope = FSUtil.CreateScope();
            foreach (var product in batch)
            {
                _articleService.Update(MapToArticle(product));
            }
            scope.Commit();
        }
    }
}
```

#### Query Descriptor Pattern

**Problem**: Complex query building (NVArticleQueryBuilder) cannot be serialized across framework boundaries without exposing SQL or creating an explosion of API methods.

**Solution**: Serialize queries as structured **Query Descriptors** that can be transmitted via gRPC and reconstructed into native enventa QueryBuilder calls.

##### Query Descriptor Structure

```csharp
// Serialisierbare Query-Struktur (gRPC-kompatibel)
public class ProductQueryDescriptor
{
    public string[] Categories { get; set; }
    public PriceFilter PriceRange { get; set; }
    public StockFilter StockCriteria { get; set; }
    public AttributeFilters Attributes { get; set; }
    public SortDescriptor[] SortBy { get; set; }
    public PaginationDescriptor Pagination { get; set; }
    public bool IncludePricing { get; set; }
    public bool IncludeStock { get; set; }
    public bool IncludeImages { get; set; }
    
    // Komplexe Filter-Bäume (AND/OR Logik)
    public QueryNode FilterTree { get; set; }
}

// Rekursive Filter-Bäume für komplexe Logik
public class QueryNode
{
    public QueryOperator Operator { get; set; } // AND, OR, NOT
    public QueryCondition[] Conditions { get; set; }
    public QueryNode[] Children { get; set; }
}

public class QueryCondition
{
    public string Field { get; set; }
    public QueryOperator Operator { get; set; } // EQ, GT, LT, LIKE, IN, etc.
    public object[] Values { get; set; }
}
```

##### Fluent API Builder (Client-Seite)

```csharp
// Fluent API ähnlich enventa, aber serialisierbar
public class ProductQueryBuilder
{
    private readonly ProductQueryDescriptor _descriptor = new();
    
    public ProductQueryBuilder ByCategory(params string[] categoryIds)
    {
        _descriptor.Categories = categoryIds;
        return this;
    }
    
    public ProductQueryBuilder WithPricing(decimal? min = null, decimal? max = null)
    {
        _descriptor.IncludePricing = true;
        _descriptor.PriceRange = new PriceFilter { Min = min, Max = max };
        return this;
    }
    
    public ProductQueryBuilder Where(Func<ProductQueryBuilder, QueryCondition> condition)
    {
        _descriptor.FilterTree = BuildNode(condition);
        return this;
    }
    
    public ProductQueryBuilder OrderBy(string field, SortDirection direction = SortDirection.Ascending)
    {
        _descriptor.SortBy = _descriptor.SortBy?.Append(new SortDescriptor 
        { 
            Field = field, 
            Direction = direction 
        }).ToArray() ?? new[] { new SortDescriptor { Field = field, Direction = direction } };
        return this;
    }
    
    // Ausführung über gRPC
    public async IAsyncEnumerable<Product> ExecuteAsync(TenantContext context)
    {
        var grpcClient = await GetGrpcClientAsync(context);
        using var call = grpcClient.StreamProducts(_descriptor);
        
        await foreach (var product in call.ResponseStream.ReadAllAsync())
        {
            yield return product;
        }
    }
}
```

##### Proxy-Seite: Descriptor → enventa QueryBuilder

```csharp
// EnventaQueryBuilderAdapter.cs (.NET Framework 4.8)
public class EnventaQueryBuilderAdapter
{
    public NVArticleQueryBuilder BuildFromDescriptor(ProductQueryDescriptor descriptor)
    {
        var query = new NVArticleQueryBuilder();
        
        // Kategorien
        if (descriptor.Categories?.Length > 0)
        {
            query = query.ByCategory(descriptor.Categories);
        }
        
        // Preise
        if (descriptor.IncludePricing)
        {
            query = query.WithPricing();
            if (descriptor.PriceRange != null)
            {
                query = query.WherePrice(descriptor.PriceRange.Min, descriptor.PriceRange.Max);
            }
        }
        
        // Stock
        if (descriptor.IncludeStock)
        {
            query = query.WithStock();
            if (descriptor.StockCriteria != null)
            {
                query = ApplyStockFilter(query, descriptor.StockCriteria);
            }
        }
        
        // Komplexe Filter-Bäume
        if (descriptor.FilterTree != null)
        {
            query = ApplyFilterTree(query, descriptor.FilterTree);
        }
        
        // Sortierung
        if (descriptor.SortBy?.Length > 0)
        {
            foreach (var sort in descriptor.SortBy)
            {
                query = query.OrderBy(sort.Field, sort.Direction == SortDirection.Ascending);
            }
        }
        
        // Pagination
        if (descriptor.Pagination != null)
        {
            query = query.Skip(descriptor.Pagination.Offset)
                        .Take(descriptor.Pagination.Limit);
        }
        
        return query;
    }
    
    private NVArticleQueryBuilder ApplyFilterTree(NVArticleQueryBuilder query, QueryNode node)
    {
        // Rekursive Verarbeitung des Filter-Baums
        switch (node.Operator)
        {
            case QueryOperator.AND:
                foreach (var child in node.Children ?? Array.Empty<QueryNode>())
                {
                    query = ApplyFilterTree(query, child);
                }
                break;
            case QueryOperator.OR:
                // enventa unterstützt möglicherweise OR nicht direkt
                // Fallback: Client-seitige Filterung oder UNION-Abfragen
                break;
        }
        
        foreach (var condition in node.Conditions ?? Array.Empty<QueryCondition>())
        {
            query = ApplyCondition(query, condition);
        }
        
        return query;
    }
    
    private NVArticleQueryBuilder ApplyCondition(NVArticleQueryBuilder query, QueryCondition condition)
    {
        return condition.Field switch
        {
            "Name" => condition.Operator switch
            {
                QueryOperator.LIKE => query.WhereNameContains((string)condition.Values[0]),
                QueryOperator.EQ => query.WhereNameEquals((string)condition.Values[0]),
                _ => throw new NotSupportedException($"Operator {condition.Operator} not supported for field {condition.Field}")
            },
            "ArticleNumber" => condition.Operator switch
            {
                QueryOperator.EQ => query.WhereArticleNumberEquals((string)condition.Values[0]),
                _ => throw new NotSupportedException($"Operator {condition.Operator} not supported for field {condition.Field}")
            },
            _ => throw new NotSupportedException($"Field {condition.Field} not supported")
        };
    }
}
```

##### Vorteile

✅ **Sicherheit**: Keine SQL-Injection durch direkte SQL-Strings über Netzwerk  
✅ **Skalierbarkeit**: Eine `StreamProducts` Methode deckt alle Query-Komplexität ab  
✅ **Type-Safe**: Stark typisierte Query-Descriptors  
✅ **Erweiterbar**: Neue Filter ohne API-Änderungen hinzufügbar  
✅ **Performance**: Server-seitige Filterung, nur relevante Daten übertragen  

##### Handling von enventa Limitierungen

- **OR-Queries**: Wenn nicht nativ unterstützt → Client-seitige Post-Filterung
- **Komplexe Operatoren**: Fallback zu Approximation oder Fehlermeldung
- **Performance**: Query-Optimierung auf Proxy-Seite

#### Thread-Safe Data Access: Actor Pattern

Since enventa ERP is **not thread-safe**, all operations must be serialized through an Actor pattern:

```csharp
/// <summary>
/// Thread-safe ERP access using Actor pattern.
/// All ERP operations are serialized through a single worker thread.
/// </summary>
public class EnventaErpActor : IAsyncDisposable
{
    private readonly Channel<ErpOperation> _operationQueue;
    private readonly Task _workerTask;
    private readonly IFSGlobalObjects _erpConnection;
    
    public EnventaErpActor(NVIdentity identity)
    {
        _operationQueue = Channel.CreateBounded<ErpOperation>(
            new BoundedChannelOptions(1000)
            {
                FullMode = BoundedChannelFullMode.Wait,
                SingleReader = true,  // Critical: only one reader!
                SingleWriter = false
            });
        
        _erpConnection = CreateAndLoginConnection(identity);
        _workerTask = Task.Run(() => ProcessOperationsAsync());
    }
    
    /// <summary>
    /// Enqueue an operation and wait for result.
    /// Thread-safe: can be called from multiple threads.
    /// </summary>
    public async Task<TResult> ExecuteAsync<TResult>(
        Func<IFSGlobalObjects, TResult> operation,
        CancellationToken ct = default)
    {
        var tcs = new TaskCompletionSource<object>();
        var erpOp = new ErpOperation(
            conn => tcs.SetResult(operation(conn)),
            ex => tcs.SetException(ex));
        
        await _operationQueue.Writer.WriteAsync(erpOp, ct);
        return (TResult)await tcs.Task;
    }
    
    /// <summary>
    /// Single-threaded worker processing all ERP operations.
    /// </summary>
    private async Task ProcessOperationsAsync()
    {
        await foreach (var operation in _operationQueue.Reader.ReadAllAsync())
        {
            try
            {
                // Execute on single thread - thread-safe for enventa
                operation.Execute(_erpConnection);
            }
            catch (Exception ex)
            {
                operation.SetException(ex);
            }
        }
    }
}

/// <summary>
/// Manages per-tenant ERP actors with thread isolation.
/// </summary>
public class EnventaActorPool : IDisposable
{
    private readonly ConcurrentDictionary<string, Lazy<EnventaErpActor>> _actors;
    
    /// <summary>
    /// Get or create actor for tenant. Thread-safe.
    /// Each tenant gets dedicated single-threaded ERP access.
    /// </summary>
    public EnventaErpActor GetActor(string tenantId)
    {
        return _actors.GetOrAdd(
            tenantId,
            id => new Lazy<EnventaErpActor>(() => CreateActor(id))
        ).Value;
    }
}
```

#### Threading Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    B2X Requests                            │
│              (Multiple concurrent requests)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Request Queue (Channel<T>)                    │
│              Per-Tenant Queue für Isolation                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                Single-Threaded Actor Worker                      │
│              (Dedicated Thread per Tenant)                       │
│              Serialisierte ERP-Zugriffe                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  enventa ERP Assembly                            │
│              (Thread-unsafe operations)                          │
└─────────────────────────────────────────────────────────────────┘
```

### Performance Optimization Strategies

#### 1. **Batch Processing Pattern**
- **Problem**: Multiple individual calls create network overhead
- **Solution**: Bundle related operations into single requests
- **Implementation**: `GetProductsAsync(IEnumerable<string>)` instead of multiple `GetProductAsync(string)`

#### 2. **Streaming for Large Datasets**
- **Problem**: Loading entire result sets into memory
- **Solution**: Async streaming with `IAsyncEnumerable<T>`
- **Benefits**: Reduced memory usage, faster time-to-first-result

#### 3. **Hybrid Data Strategy: Sync + Live Query**
- **Master Data**: Synchronized to B2X database (PostgreSQL + Elasticsearch)
  - Articles, attributes, images, references (1.5M+ articles, 30M+ attributes)
  - Background sync jobs (hourly/nightly, incremental)
  - Acceptable time delay (eventual consistency)
- **Customer-Specific Data**: Live queries to ERP
  - Customer prices (kundenindividuelle Preise)
  - Stock levels (Bestände)
  - Order status (Vorgangsdaten)
  - Always current (strong consistency required)
- **Benefits**: 
  - Fast catalog browsing (local DB)
  - Current prices/stock (live ERP query)
  - Reduced ERP load (only customer-specific queries)

#### 4. **Local Caching in Provider Containers**
- **Strategy**: Redis cache within provider containers for frequently accessed data
- **TTL**: 
  - Master data (synced): Not cached (use local DB)
  - Customer prices/stock (live): 30s-5min TTL
  - Order status: 1-2min TTL
- **Invalidation**: Event-driven cache invalidation via Wolverine messages

#### 5. **Connection Pooling and Keep-Alive**
- **Database Connections**: Maintain persistent connections to ERP databases
- **HTTP Clients**: Reuse connections with keep-alive headers
- **Circuit Breaker**: Polly policies for resilient communication

#### 5. **Connection Pooling and Keep-Alive**
- **Database Connections**: Maintain persistent connections to ERP databases
- **HTTP Clients**: Reuse connections with keep-alive headers
- **Circuit Breaker**: Polly policies for resilient communication
- **enventa Specific**: Connection pooling with 30min idle timeout (>2s initialization cost)

#### 6. **Bulk Synchronization Optimization**
- **Change Detection**: Only sync changed records using timestamps/modified flags
- **Delta Sync**: Incremental updates instead of full dataset transfers
- **Parallel Processing**: Multiple threads for independent sync operations (master data only)
- **Master Data Priority**: Articles → Attributes → Images (staged sync)

### Performance Benchmarks

| Operation Type | Target Latency | Data Source | Consistency |
|----------------|----------------|-------------|-------------|
| Article Search (1000 results) | <200ms | PostgreSQL + Elasticsearch | Eventual (≤1h) |
| Article Details | <100ms | PostgreSQL (master) | Eventual (≤1h) |
| Customer Price (single) | <100ms | ERP (live query) | Strong (real-time) |
| Stock Availability (single) | <100ms | ERP (live query) | Strong (real-time) |
| Bulk Price Query (100 items) | <500ms | ERP (live query, batched) | Strong (real-time) |
| Order Creation | <200ms | ERP (live) | Strong (real-time) |
| Master Data Sync (1M articles) | <30min | Background job | N/A (incremental) |

### Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     User Request Flow                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  GET /articles?search=hammer                                     │
│       │                                                          │
│       ├─→ PostgreSQL + Elasticsearch (synced master data)        │
│       │   └─→ 1000 articles with descriptions, images (fast)     │
│       │                                                          │
│  GET /articles/12345?customerId=C001                             │
│       │                                                          │
│       ├─→ PostgreSQL (synced master data)                        │
│       │   └─→ Article 12345 details, attributes                  │
│       │                                                          │
│       ├─→ ERP Provider (live query via connection pool)          │
│       │   └─→ Customer price, stock, discount for C001           │
│       │                                                          │
│       └─→ Combine: { ...article, price, stock }                  │
│                                                                  │
│  POST /orders (create order)                                     │
│       │                                                          │
│       └─→ ERP Provider (live) → Order created in ERP             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
         ↑                                    ↑
         │                                    │
    Sync Job                          Connection Pool
   (Background)                        (Pre-warmed)
    Incremental                          <100ms
         │                                    │
         └────────────┬───────────────────────┘
                      │
              enventa Trade ERP
          (1.5M Articles, 30M Attributes)
```

### Monitoring and Performance Metrics

#### Key Performance Indicators
- **Network Latency**: P95 response time for provider calls
- **Throughput**: Operations per second per tenant
- **Error Rate**: Failed operations percentage
- **Cache Hit Rate**: >80% for frequently accessed data
- **Memory Usage**: Container memory consumption trends

#### Observability Setup
```yaml
# Prometheus metrics for ERP performance
erp_provider_requests_total{operation="GetProduct", tenant="tenant-123", status="success"} 1547
erp_provider_request_duration_seconds{operation="BulkSync", quantile="0.95"} 2.5
erp_provider_cache_hit_ratio{provider="enventa"} 0.85
```

### Deployment Models

B2X supports **two deployment models** for ERP connectors to optimize for different customer scenarios:

#### Model A: Cloud Deployment (Docker Container)

```
┌─────────────────────────────────────────────────────────────────┐
│                    B2X Cloud (Kubernetes)                  │
│  ┌─────────────────┐    ┌─────────────────────────────────────┐ │
│  │  B2X API  │    │   Windows Container                  │ │
│  │  (.NET 10)      │◄──►│   (ERP Connector .NET 4.8)          │ │
│  │  Linux          │gRPC│   Windows Server Core               │ │
│  └─────────────────┘    └──────────────┬──────────────────────┘ │
└─────────────────────────────────────────│────────────────────────┘
                                          │ VPN/Direct Connect
                                          ▼
                              ┌─────────────────────────┐
                              │  Customer ERP           │
                              │  (enventa Trade)        │
                              └─────────────────────────┘
```

**Wann verwenden:**
- Customer hat keine On-Premise IT-Infrastruktur
- ERP-System ist Cloud-basiert oder über VPN erreichbar
- Managed-Service gewünscht (B2X verwaltet Connector)

**Trade-offs:**
- ➕ Zentral gemanagt, einfaches Update-Deployment
- ➕ Einheitliche Monitoring-Infrastruktur
- ➖ Windows Container in Cloud sind teuer (~2x Linux-Preis)
- ➖ Netzwerk-Latenz zur Customer-Datenbank
- ➖ Firewall-Öffnung für ERP-Datenbankzugriff erforderlich

#### Model B: On-Premise Deployment (Windows Service)

```
┌─────────────────────────────────────────────────────────────────┐
│                    B2X Cloud (Kubernetes)                  │
│  ┌─────────────────┐                                            │
│  │  B2X API  │◄──────────────────┐                        │
│  │  (.NET 10)      │   gRPC over HTTPS │                        │
│  │  Linux          │                   │                        │
│  └─────────────────┘                   │                        │
└────────────────────────────────────────│────────────────────────┘
                                         │
                      ═══════════════════│════════════════════════
                         Internet (HTTPS only, outbound from customer)
                      ═══════════════════│════════════════════════
                                         │
┌────────────────────────────────────────│────────────────────────┐
│                    Customer On-Premise │                        │
│  ┌─────────────────────────────────────┴──────────────────────┐ │
│  │  ERP Connector Windows Service                              │ │
│  │  (.NET 4.8, TopShelf/Windows Service)                       │ │
│  │  Initiiert Verbindung zur Cloud (kein Inbound-Traffic)      │ │
│  └──────────────────────────────┬─────────────────────────────┘ │
│                                 │ Local Network                 │
│  ┌──────────────────────────────▼─────────────────────────────┐ │
│  │  enventa Trade ERP                                          │ │
│  │  (SQL Server, proprietary ORM)                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Wann verwenden:**
- enventa Trade läuft On-Premise beim Kunden (Standardfall)
- Minimale Latenz zur ERP-Datenbank erforderlich
- Keine Firewall-Öffnung gewünscht (Connector initiiert Verbindung)
- Kostenoptimierung (keine Windows-Cloud-Kosten)

**Trade-offs:**
- ➕ Direkter Zugriff auf ERP-Datenbank (minimale Latenz)
- ➕ Keine Cloud-Kosten für Windows-VMs
- ➕ Kein Inbound-Traffic erforderlich (nur HTTPS outbound)
- ➕ Daten bleiben im Kundennetzwerk bis zur Sync
- ➖ Customer muss Windows Service betreiben
- ➖ Update-Deployment komplexer (MSI/ClickOnce)
- ➖ Monitoring muss an B2X Cloud gemeldet werden

#### Deployment Decision Matrix

| Kriterium | Cloud (Docker) | On-Premise (Service) |
|-----------|----------------|----------------------|
| ERP-Standort | Cloud/VPN | On-Premise |
| IT-Betrieb beim Kunden | Minimal | Vorhanden |
| Latenz-Anforderung | Tolerant | Kritisch |
| Sicherheitsanforderung | Standard | Hoch (keine Firewall-Öffnung) |
| Kostenmodell | OpEx (Cloud) | CapEx + geringe OpEx |
| Update-Frequenz | Häufig | Selten (stabil) |
| Empfehlung | Kleinere Kunden | Enterprise-Kunden |

### Windows Service Implementation

```csharp
/// <summary>
/// ERP Connector als Windows Service mit TopShelf
/// </summary>
public class ErpConnectorService : ServiceControl
{
    private readonly IHost _host;
    
    public ErpConnectorService()
    {
        _host = Host.CreateDefaultBuilder()
            .ConfigureServices((context, services) =>
            {
                // gRPC Client für Cloud-Kommunikation
                services.AddGrpcClient<ErpSync.ErpSyncClient>(options =>
                {
                    options.Address = new Uri(context.Configuration["B2X:CloudEndpoint"]);
                });
                
                // Actor für Thread-sichere ERP-Zugriffe
                services.AddSingleton<ErpActorPool>();
                
                // Hintergrund-Sync-Dienste
                services.AddHostedService<ProductSyncWorker>();
                services.AddHostedService<OrderSyncWorker>();
                services.AddHostedService<CustomerSyncWorker>();
                
                // Health Reporting zur Cloud
                services.AddHostedService<HealthReportingWorker>();
            })
            .Build();
    }
    
    public bool Start(HostControl hostControl)
    {
        _host.Start();
        return true;
    }
    
    public bool Stop(HostControl hostControl)
    {
        _host.StopAsync().Wait();
        return true;
    }
}

// TopShelf Service-Registrierung
public class Program
{
    public static void Main()
    {
        HostFactory.Run(x =>
        {
            x.Service<ErpConnectorService>();
            x.RunAsLocalSystem();
            x.SetServiceName("B2XErpConnector");
            x.SetDisplayName("B2X ERP Connector");
            x.SetDescription("Synchronisiert enventa Trade ERP mit B2X Cloud");
            x.StartAutomatically();
            x.EnableServiceRecovery(r => r.RestartService(1)); // Restart nach 1 Minute
        });
    }
}
```

### Cloud-Side Connector Registration

On-Premise Connectors registrieren sich bei der Cloud:

```csharp
/// <summary>
/// Cloud-seitiger Service für Connector-Registrierung
/// </summary>
public class ConnectorRegistrationService : ConnectorRegistry.ConnectorRegistryBase
{
    private readonly ConcurrentDictionary<string, ConnectorInfo> _connectors = new();
    
    public override async Task<RegisterResponse> Register(
        RegisterRequest request, 
        ServerCallContext context)
    {
        var connectorInfo = new ConnectorInfo
        {
            TenantId = request.TenantId,
            ConnectorId = request.ConnectorId,
            Version = request.Version,
            Capabilities = request.Capabilities.ToList(),
            LastHeartbeat = DateTimeOffset.UtcNow,
            DeploymentModel = ConnectorDeploymentModel.OnPremise
        };
        
        _connectors.AddOrUpdate(request.ConnectorId, connectorInfo, (_, _) => connectorInfo);
        
        return new RegisterResponse
        {
            Success = true,
            CloudEndpoint = GetCloudEndpointForTenant(request.TenantId),
            HeartbeatIntervalSeconds = 30
        };
    }
    
    public override async Task Heartbeat(
        IAsyncStreamReader<HeartbeatRequest> requestStream,
        IServerStreamWriter<HeartbeatResponse> responseStream,
        ServerCallContext context)
    {
        await foreach (var heartbeat in requestStream.ReadAllAsync())
        {
            if (_connectors.TryGetValue(heartbeat.ConnectorId, out var info))
            {
                info.LastHeartbeat = DateTimeOffset.UtcNow;
                info.Status = heartbeat.Status;
                info.Metrics = heartbeat.Metrics;
            }
            
            // Sende Konfigurationsänderungen zurück
            await responseStream.WriteAsync(new HeartbeatResponse
            {
                ConfigVersion = GetLatestConfigVersion(heartbeat.TenantId)
            });
        }
    }
}
```

### Container Orchestration (Cloud Deployment)

- **Kubernetes-based deployment** with tenant namespaces
- **Docker Compose** for development environments
- **Health checks** via HTTP probes with performance thresholds
- **Auto-scaling** based on tenant usage and latency metrics

### Tenant Configuration

```json
{
  "tenantId": "tenant-123",
  "erpProvider": {
    "type": "enventa",
    "deploymentModel": "on-premise",
    "config": {
      "connectionString": "...",
      "syncBatchSize": 1000
    }
  },
  "connectorRegistration": {
    "model": "on-premise",
    "expectedConnectorId": "connector-abc-123",
    "cloudEndpoint": "https://api.B2X.cloud/erp",
    "features": ["pim", "crm", "orders"]
  }
}
```

**Alternative: Cloud Deployment Configuration**
```json
{
  "tenantId": "tenant-456",
  "erpProvider": {
    "type": "enventa",
    "deploymentModel": "cloud",
    "image": "B2X/erp-enventa:v1.2.3",
    "config": {
      "connectionString": "...",
      "syncBatchSize": 1000
    }
  },
  "crmProvider": {
    "type": "salesforce",
    "deploymentModel": "cloud",
    "image": "B2X/crm-salesforce:v2.1.0"
  }
}
```

## Consequences

### Positive

- **Flexibility**: Customer-specific ERP integrations without core system changes
- **Isolation**: Legacy systems don't impact modern architecture
- **Scalability**: Independent scaling of ERP providers
- **Maintainability**: Modular updates and testing
- **Future-proof**: Easy addition of new ERP systems
- **Performance**: Optimized batch/streaming operations reduce network overhead
- **Cost Optimization**: On-Premise deployment avoids expensive Windows Cloud VMs
- **Security**: On-Premise model requires no inbound firewall rules
- **Latency**: On-Premise connector has direct ERP database access

### Negative

- **Complexity**: Additional orchestration layer
- **Latency**: Network calls between containers (mitigated by batch operations)
- **Resource overhead**: Container management (Cloud model)
- **Development effort**: Standardized interfaces required
- **Dual deployment support**: Both Docker and Windows Service must be maintained

### Risks

- **Provider compatibility**: Ensuring interface contracts are met
- **Performance**: Bulk data synchronization efficiency (addressed via batch processing)
- **Security**: Inter-container communication security
- **Operational complexity**: Container orchestration management
- **Chatty Interfaces**: Multiple network calls causing latency (mitigated by bulk APIs)
- **.NET Framework Constraints**: Limited async patterns require compatibility layer
- **Proprietary ORM Lock-in**: enventa ORM patterns may not translate to other ERPs
- **Single-Threading Bottleneck**: Serialized ERP access limits throughput (mitigated by caching + batching)
- **On-Premise Management**: Customer must maintain Windows Service (mitigated by auto-update mechanism)

## Alternatives Considered

### 1. Direct Assembly Integration
- **Rejected**: Incompatible with .NET Framework → .NET 10 migration

### 2. Monolithic ERP Service
- **Rejected**: No customer-specific customizations, tight coupling

### 3. API Gateway Pattern
- **Rejected**: Less isolation, harder tenant separation

## Implementation Plan

### Phase 1: Foundation (2 weeks)
- Define interface contracts with batch/streaming operations
- **Validate .NET 4.8 compatibility** for all communication patterns
- **Implement Actor pattern** for thread-safe ERP access
- Create base Docker images (Windows Server Core for .NET 4.8)
- **Create Windows Service project with TopShelf**
- Implement Provider Manager skeleton with performance monitoring
- Setup gRPC infrastructure for cross-framework streaming
- Setup basic performance benchmarks

### Phase 2: enventa Integration (4 weeks)
- Develop enventa provider container (.NET 4.8 / Windows Container)
- **Develop enventa Windows Service variant**
- **Integrate with enventa's proprietary ORM** via adapter pattern
- Implement PIM/CRM/ERP interfaces with caching strategies
- **Implement Connector Registration for On-Premise deployments**
- Integration testing with B2X focusing on performance
- Optimize for "chatty" ERP operations via batch processing
- **Validate gRPC streaming** between .NET 4.8 and .NET 10

### Phase 3: Production Ready (3 weeks)
- Plugin registry system with performance metrics
- **On-Premise auto-update mechanism (MSI/ClickOnce)**
- Advanced monitoring and health checks
- **Heartbeat and status reporting for On-Premise connectors**
- Security hardening with performance impact assessment
- Documentation and performance tuning guides
- **Deployment decision guide for customers**

## Success Metrics

- **Functionality**: All ERP operations working across tenants
- **Performance**: 
  - <100ms latency for single operations
  - <500ms for bulk operations (up to 100 items)
  - <2s time-to-first-result for streaming operations
  - <30s for bulk sync (10k records)
- **Reliability**: 99.9% uptime for ERP services
- **Maintainability**: New provider integration in <2 weeks
- **Security**: Zero data leakage between tenants
- **Efficiency**: >80% cache hit rate, <5 network calls per complex operation

## Related Documents

- [ADR-022] Multi-Tenant Domain Management
- [KB-006] Wolverine Patterns
- [GL-002] Subagent Delegation
- [KB-ERP] enventa Trade ERP Technical Analysis (`.ai/knowledgebase/erp/enventa-trade-erp-analysis.md`)
- [KB-020] eGate ERP Broker Analysis

---

## Appendix: eGate Reference Implementation Analysis

Based on analysis of the NissenVelten eGate ERP Broker (see [KB-020]), the following patterns should inform our implementation:

### A.1 Connection Pooling Pattern (FSGlobalPool)

```csharp
// eGate pattern - pool per tenant identity
internal class FSGlobalPool : IDisposable
{
    private static readonly object _lock = new object();
    private readonly ConcurrentBag<IFSGlobalObjects> _globals = new();
    private readonly EventWaitHandle _globalWh;
    
    public IFSGlobalObjects GetGlobal()
    {
        if (!_globals.TryTake(out var global))
        {
            Task.Run(() => CreateGlobal());
            while (!_globals.TryTake(out global))
                _globalWh.WaitOne(-1);  // Block until available
        }
        return global;
    }
    
    public void CreateGlobal()
    {
        var global = GlobalObjectManager.CreateGlobalObject(guid.NewGuid().Value);
        lock (_lock) { global.Login(_identity); }  // Login is NOT thread-safe!
        global.Validate();
        global.EnableCaching();
        _globals.Add(global);
        _globalWh.Set();
    }
}
```

**B2X Adaptation:**
```csharp
public class ErpConnectionPool : IErpConnectionPool
{
    private readonly Channel<IErpConnection> _pool;
    private readonly SemaphoreSlim _creationLock = new(1, 1);
    
    public async ValueTask<IErpConnection> RentAsync(CancellationToken ct = default)
    {
        if (_pool.Reader.TryRead(out var conn))
            return conn;
            
        await _creationLock.WaitAsync(ct);
        try { return await CreateConnectionAsync(ct); }
        finally { _creationLock.Release(); }
    }
    
    public ValueTask ReturnAsync(IErpConnection conn)
    {
        conn.CloseActiveTransaction();
        return _pool.Writer.WriteAsync(conn);
    }
}
```

### A.2 QueryBuilder with FSQueryList

eGate uses expression-tree based query building:

```csharp
// eGate pattern
public override FSQueryList<IcECArticle> BuildConditions(FSQueryList<IcECArticle> conditions)
{
    if (_articleId.HasValue())
        conditions.Eq(x => x.sArticleId, _articleId);
        
    if (_customerArticleQuery != null)
    {
        conditions.Exists<IcECCustomerArticle>(null,
            x => x.Rel(o => o.sArticleID, i => i.sArticleId),
            _customerArticleQuery.BuildConditions
        );
    }
    return conditions;
}
```

**B2X Adaptation (gRPC-friendly):**
```csharp
public class ArticleQueryBuilder : IErpQueryBuilder<ArticleDto>
{
    private readonly List<QueryCondition> _conditions = new();
    
    public IErpQueryBuilder<ArticleDto> WhereId(string articleId)
    {
        _conditions.Add(new QueryCondition("ArticleId", "=", articleId));
        return this;
    }
    
    // Serialize to gRPC message for .NET 4.8 provider
    public QueryRequest ToGrpcRequest() => new QueryRequest
    {
        EntityType = "Article",
        Conditions = { _conditions.Select(c => c.ToProto()) }
    };
}
```

### A.3 Batch Processing Pattern

eGate batches IN clauses to avoid SQL limits:

```csharp
// eGate pattern - batch rowIds into groups of 1000
var where = rowIds.Batch(1000)
    .Select(block => $"ROWID IN ({block.Join(",")})")
    .Join(" OR ");
```

**B2X Adaptation:**
```csharp
public async IAsyncEnumerable<ArticleDto> GetByIdsAsync(
    IEnumerable<string> ids,
    [EnumeratorCancellation] CancellationToken ct = default)
{
    foreach (var batch in ids.Chunk(1000))  // .NET 6+ Chunk
    {
        var request = new BatchRequest { Ids = { batch } };
        await foreach (var item in _client.GetBatchAsync(request, ct))
        {
            yield return item;
        }
    }
}
```

### A.4 SyncRecord Pattern

eGate maintains external/internal ID mapping:

```csharp
public class SyncRecord
{
    public string ProviderId { get; set; }
    public string InternalType { get; set; }
    public int InternalId { get; set; }
    public string ExternalType { get; set; }
    public string ExternalId { get; set; }
    public DateTime? LastSync { get; set; }
}
```

**B2X Implementation:**
```csharp
public record ErpSyncMapping(
    Guid Id,
    string TenantId,
    string ProviderId,
    string EntityType,
    string B2XId,
    string ErpId,
    long ErpRowVersion,
    DateTimeOffset LastSyncUtc
);

// Store in PostgreSQL with Wolverine projections
public class SyncMappingProjection : IProjection<ErpSyncMapping>
{
    public Task Apply(SyncMappingCreated e, ErpSyncMapping? existing) => ...;
    public Task Apply(SyncMappingUpdated e, ErpSyncMapping existing) => ...;
}
```

### A.5 Critical Thread-Safety Findings

From eGate analysis:

| Component | Thread-Safety | B2X Mitigation |
|-----------|--------------|---------------------|
| `Login()` | **NOT thread-safe** | Serialize with `SemaphoreSlim` |
| `GlobalObjectManager.Create()` | Thread-safe | Can parallelize |
| `Connection.Open()` | Per-instance only | Pool per connection |
| `GetFetchNext()` | Thread-safe | Stream safely |

---

**Next Steps:**
1. @Backend: Define detailed interface contracts based on eGate patterns
2. @Backend: Implement `IErpConnectionPool` with async/await semantics
3. @DevOps: Create base Docker image templates
4. @Architect: Review and approve implementation approach
5. @QA: Define integration test strategy with eGate compatibility focus