---
docid: ADR-061
title: ADR 025 Dapper Ef Extensions Evaluation
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

# ADR-025: Dapper & EF Extensions Evaluation

**Status**: Accepted  
**Date**: 2. Januar 2026  
**Deciders**: @SARAH, @Architect, @Backend, @TechLead  
**Technical Story**: Performance-Optimierung für Bulk-Operationen und Read-Heavy Queries

## Context

Das Team evaluiert ergänzende Data-Access-Technologien für spezifische Performance-kritische Szenarien:

1. **Dapper** - Micro-ORM für schnelle Read-Queries
2. **EFCore.BulkExtensions** - Bulk-Operationen für EF Core
3. **Z.EntityFramework.Extensions** - Kommerzielle Bulk-Extension

### Aktueller Data-Access Stack

| Komponente | Technologie | Version |
|------------|-------------|---------|
| ORM | Entity Framework Core | 10.0.1 |
| Database | PostgreSQL | via Npgsql |
| Naming | EFCore.NamingConventions | 10.0.0-rc.2 |
| CQRS | Wolverine | 5.9.2 |

### Identifizierte Performance-Szenarien

| Szenario | Datenvolumen | Aktuell | Problem |
|----------|--------------|---------|---------|
| ERP Catalog Sync | 50.000+ Artikel | EF Core AddRange | Langsam (Change Tracking) |
| Search Reindexing | Alle Produkte | EF Core Query | Memory Pressure |
| Bulk Price Update | 10.000+ Preise | EF Core Loop | N+1 Updates |
| Reporting Queries | Aggregationen | EF Core LINQ | Overhead |

## Decision

### Empfehlung: Hybrid Data-Access Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                  DATA ACCESS STRATEGY                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  WRITE OPERATIONS (Commands)                                │
│  ─────────────────────────────                              │
│  → EF Core bleibt primär                                    │
│  → Change Tracking, Unit of Work, Validierung               │
│  → Domain Logic mit Entity States                           │
│                                                             │
│  BULK OPERATIONS                                            │
│  ─────────────────                                          │
│  → EFCore.BulkExtensions für Insert/Update/Delete           │
│  → Catalog Import, Price Updates, Batch Jobs                │
│                                                             │
│  READ OPERATIONS (Queries)                                  │
│  ─────────────────────────                                  │
│  → Dapper für komplexe Read-Only Queries                    │
│  → Reports, Search Projections, Aggregationen               │
│  → EF Core für Standard-Queries (Navigation Properties)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Konkrete Entscheidungen

| Technologie | Entscheidung | Begründung |
|-------------|--------------|------------|
| **Dapper** | ✅ Einführen | Read-Performance für Reports & Sync |
| **EFCore.BulkExtensions** | ✅ Einführen | Kostenlose Bulk-Operationen |
| **Z.EntityFramework.Extensions** | ❌ Ablehnen | Kostenpflichtig, BulkExtensions reicht |

## Rationale

### Warum Dapper hinzufügen?

**Performance-Vorteile:**
- 2-5x schneller als EF Core für reine Reads
- Kein Change Tracking Overhead
- Direktes SQL-Mapping
- Ideal für Wolverine Query-Handler

**Use Cases:**
```csharp
// Dapper für Read-Heavy Query (Search Reindex)
public class GetAllProductsForIndexHandler
{
    public async Task<IEnumerable<ProductIndexDto>> Handle(
        GetAllProductsForIndex query,
        IDbConnection connection)
    {
        return await connection.QueryAsync<ProductIndexDto>(
            @"SELECT id, sku, name, price, tenant_id 
              FROM products 
              WHERE tenant_id = @TenantId",
            new { query.TenantId });
    }
}

// EF Core für Domain Logic (weiterhin)
public class UpdateProductHandler
{
    public async Task Handle(UpdateProduct cmd, CatalogDbContext db)
    {
        var product = await db.Products.FindAsync(cmd.Id);
        product.UpdatePrice(cmd.NewPrice); // Domain Logic
        await db.SaveChangesAsync();
    }
}
```

### Warum EFCore.BulkExtensions?

**Performance-Vorteile:**
- BulkInsert: 10-50x schneller als AddRange
- BulkUpdate: Einzelner SQL-Statement statt N Updates
- BulkDelete: Effizient ohne Laden

**Use Cases:**
```csharp
// Bulk Insert für Catalog Import
public class ImportProductsHandler
{
    public async Task Handle(ImportProducts cmd, CatalogDbContext db)
    {
        var products = cmd.ErpProducts
            .Select(p => new Product(p.Sku, p.Name, p.Price))
            .ToList();
        
        await db.BulkInsertAsync(products);
    }
}

// Bulk Update für Price Sync
public class SyncPricesHandler
{
    public async Task Handle(SyncPrices cmd, CatalogDbContext db)
    {
        await db.Products
            .Where(p => cmd.UpdatedSkus.Contains(p.Sku))
            .BatchUpdateAsync(p => new Product { Price = cmd.GetPrice(p.Sku) });
    }
}
```

### Warum NICHT Z.EntityFramework.Extensions?

- **Kostenpflichtig**: ~$1000/Jahr für kommerzielle Lizenz
- **EFCore.BulkExtensions**: MIT License, kostenlos
- **Feature-Parität**: Für unsere Use Cases ausreichend

## Implementation Plan

### Phase 1: Package Integration

```xml
<!-- backend/Directory.Packages.props -->
<PackageVersion Include="Dapper" Version="2.1.35" />
<PackageVersion Include="EFCore.BulkExtensions" Version="8.1.3" />
```

### Phase 2: Infrastructure Setup

```csharp
// Dapper Connection Factory
public interface IDapperConnectionFactory
{
    IDbConnection CreateConnection();
}

public class PostgresDapperConnectionFactory : IDapperConnectionFactory
{
    private readonly string _connectionString;
    
    public IDbConnection CreateConnection()
    {
        return new NpgsqlConnection(_connectionString);
    }
}
```

### Phase 3: Use Case Implementation

| Priority | Use Case | Technology | Sprint |
|----------|----------|------------|--------|
| P0 | Catalog Import | BulkExtensions | Current |
| P1 | Search Reindex | Dapper | Current |
| P2 | Price Sync | BulkExtensions | Next |
| P3 | Reporting | Dapper | Future |

### Phase 4: Benchmarking

```csharp
// Benchmark: EF Core vs Dapper vs BulkExtensions
[MemoryDiagnoser]
public class DataAccessBenchmarks
{
    [Benchmark(Baseline = true)]
    public async Task EfCore_Insert_10000() { /* ... */ }
    
    [Benchmark]
    public async Task BulkExtensions_Insert_10000() { /* ... */ }
    
    [Benchmark]
    public async Task Dapper_Read_10000() { /* ... */ }
    
    [Benchmark]
    public async Task EfCore_Read_10000() { /* ... */ }
}
```

## Consequences

### Positive

- **Performance**: Signifikante Verbesserung für Bulk-Operationen
- **Flexibilität**: Right tool for the job
- **Kosten**: Keine Lizenzkosten (beide MIT)
- **Wolverine Integration**: Dapper passt gut zu Query-Handler Pattern

### Negative

- **Komplexität**: Zwei Data-Access Patterns zu pflegen
- **Lernkurve**: Team muss Dapper-Syntax lernen
- **SQL-Kenntnisse**: Raw SQL für Dapper erforderlich
- **Konsistenz**: Klare Guidelines nötig wann was verwenden

### Mitigations

| Risiko | Mitigation |
|--------|------------|
| Inkonsistente Nutzung | Guidelines in Coding Standards |
| SQL Injection | Parameterized Queries enforced |
| Doppelte Logik | Klare Trennung: Commands=EF, Queries=Dapper |
| Testing | Testcontainers für beide Patterns |

## Guidelines: Wann was verwenden?

```
┌─────────────────────────────────────────────────────────────┐
│              DATA ACCESS DECISION TREE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Ist es ein WRITE (Command)?                                │
│  ├── JA → Ist es BULK (>100 Records)?                       │
│  │        ├── JA → EFCore.BulkExtensions                    │
│  │        └── NEIN → EF Core (Change Tracking)              │
│  │                                                          │
│  └── NEIN (READ/Query)                                      │
│       ├── Brauche ich Navigation Properties?                │
│       │   └── JA → EF Core                                  │
│       │                                                     │
│       ├── Ist es ein komplexer Report/Aggregation?          │
│       │   └── JA → Dapper                                   │
│       │                                                     │
│       ├── Ist es Bulk-Read (>1000 Records)?                 │
│       │   └── JA → Dapper (kein Tracking Overhead)          │
│       │                                                     │
│       └── Standard Query                                    │
│           └── EF Core (Convenience)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Alternatives Considered

### Alternative 1: Pure EF Core (Status Quo)
- **Pro**: Einfachheit, ein Pattern
- **Contra**: Performance-Probleme bei Bulk-Operationen
- **Entscheidung**: Abgelehnt - Skalierung wichtiger

### Alternative 2: Dapper Only (Replace EF Core)
- **Pro**: Maximale Performance
- **Contra**: Verlust von Change Tracking, Migrations, Navigation
- **Entscheidung**: Abgelehnt - EF Core Vorteile zu wertvoll

### Alternative 3: Z.EntityFramework.Extensions
- **Pro**: Mehr Features als BulkExtensions
- **Contra**: Kostenpflichtig (~$1000/Jahr)
- **Entscheidung**: Abgelehnt - BulkExtensions reicht

## Related Decisions

- [ADR-001](ADR-001-event-driven-architecture.md) - Wolverine CQRS (Query/Command Separation)
- [ADR-023](ADR-023-erp-plugin-architecture.md) - ERP Integration (Bulk Sync Scenarios)
- [ADR-024](ADR-024-dapr-evaluation-deferred.md) - Dapr Evaluation (Infrastructure Decisions)

## References

- [Dapper GitHub](https://github.com/DapperLib/Dapper)
- [EFCore.BulkExtensions GitHub](https://github.com/borisdj/EFCore.BulkExtensions)
- [EF Core Performance Tips](https://learn.microsoft.com/en-us/ef/core/performance/)
- [Wolverine Query Handlers](https://wolverine.netlify.app/guide/handlers.html)

---

## Sign-Off

| Role | Agent | Decision | Date | Conditions |
|------|-------|----------|------|------------|
| Coordinator | @SARAH | ✅ Approved | 2026-01-02 | - |
| Architecture | @Architect | ✅ Approved | 2026-01-02 | Decision tree as code, benchmarking priority, monitoring metrics |
| Backend | @Backend | ✅ Approved | 2026-01-02 | Transaction management, logging/metrics, coding guidelines |
| Tech Lead | @TechLead | ✅ Approved | 2026-01-02 | Team training, code review checklists, technical debt tracking |

---

## Next Steps

1. **✅ Team Review**: ADR reviewed and approved by all agents
2. **Benchmark erstellen**: EF Core vs Dapper vs BulkExtensions (Phase 4)
3. **PoC**: Catalog Import mit BulkExtensions implementieren (Phase 3)
4. **Guidelines**: Coding Standards erweitern mit Decision Tree
5. **Training**: Team-Workshop für Dapper & BulkExtensions
6. **Implementation**: Phase 1 Package Integration starten

**Implementation Start**: Immediate (Current Sprint)
**Review Deadline**: Completed 2. Januar 2026
