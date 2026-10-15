# ADR-003: Audit Tracking Implementation

**Status:** Accepted

**Date:** 2025-01-15

**Decision Makers:** JumpStart Core Team

## Context

Modern applications require comprehensive audit trails for:

- **Compliance** - Regulatory requirements (GDPR, HIPAA, SOX, etc.)
- **Accountability** - Knowing who made what changes and when
- **Security** - Detecting unauthorized modifications
- **Debugging** - Understanding the history of data changes
- **Data Recovery** - Restoring accidentally deleted or modified data
- **Business Intelligence** - Analyzing user behavior and system usage

We needed a solution that:
- Automatically tracks creation, modification, and deletion
- Captures both timestamp and user information
- Works transparently without manual intervention
- Supports soft delete patterns
- Handles anonymous/system operations
- Integrates with ASP.NET Core Identity and custom auth systems

## Decision

We will implement **automatic audit tracking** through:

### 1. Audit Interfaces

Define separate interfaces for each audit concern following the Interface Segregation Principle:

**Creation Tracking:**
```csharp
public interface ICreatable<TKey> where TKey : struct
{
    DateTimeOffset CreatedOn { get; set; }
    TKey? CreatedById { get; set; }
}

public interface ISimpleCreatable : ICreatable<Guid>
{
}
```

**Modification Tracking:**
```csharp
public interface IModifiable<TKey> where TKey : struct
{
    DateTimeOffset ModifiedOn { get; set; }
    TKey? ModifiedById { get; set; }
}

public interface ISimpleModifiable : IModifiable<Guid>
{
}
```

**Deletion Tracking (Soft Delete):**
```csharp
public interface IDeletable<TKey> where TKey : struct
{
    DateTimeOffset? DeletedOn { get; set; }
    TKey? DeletedById { get; set; }
}

public interface ISimpleDeletable : IDeletable<Guid>
{
}
```

**Combined Audit Interface:**
```csharp
public interface IAuditable<TKey> : ICreatable<TKey>, IModifiable<TKey>, IDeletable<TKey>
    where TKey : struct
{
}

public interface ISimpleAuditable : IAuditable<Guid>, ISimpleCreatable, ISimpleModifiable, ISimpleDeletable
{
}
```

### 2. Auditable Base Classes

Provide base entity classes that implement audit interfaces:

**Advanced System:**
```csharp
public abstract class AuditableEntity<TKey> : Entity<TKey>, IAuditable<TKey>
    where TKey : struct
{
    public DateTimeOffset CreatedOn { get; set; }
    public TKey? CreatedById { get; set; }
    public DateTimeOffset ModifiedOn { get; set; }
    public TKey? ModifiedById { get; set; }
    public DateTimeOffset? DeletedOn { get; set; }
    public TKey? DeletedById { get; set; }
}
```

**Simple System:**
```csharp
public abstract class SimpleAuditableEntity : SimpleEntity, ISimpleAuditable
{
    public DateTimeOffset CreatedOn { get; set; }
    public Guid? CreatedById { get; set; }
    public DateTimeOffset ModifiedOn { get; set; }
    public Guid? ModifiedById { get; set; }
    public DateTimeOffset? DeletedOn { get; set; }
    public Guid? DeletedById { get; set; }
}
```

### 3. User Context Abstraction

Abstract user information retrieval to support different authentication systems:

```csharp
public interface ISimpleUserContext
{
    Guid? UserId { get; }
}

public interface IUserContext<TKey> where TKey : struct
{
    TKey? UserId { get; }
}
```

**Blazor Server Implementation:**
```csharp
public class BlazorUserContext : ISimpleUserContext
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public BlazorUserContext(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public Guid? UserId
    {
        get
        {
            var userIdString = _httpContextAccessor.HttpContext?.User
                .FindFirst(ClaimTypes.NameIdentifier)?.Value;
            
            return Guid.TryParse(userIdString, out var userId) ? userId : null;
        }
    }
}
```

### 4. Automatic Population in Repositories

Repository base classes automatically populate audit fields:

```csharp
public abstract class Repository<TEntity, TKey>
    where TEntity : class, IEntity<TKey>
    where TKey : struct
{
    protected readonly DbContext _context;
    protected readonly DbSet<TEntity> _dbSet;
    protected readonly IUserContext<TKey>? _userContext;

    public virtual async Task<TEntity> AddAsync(TEntity entity)
    {
        // Populate creation audit fields
        if (entity is ICreatable<TKey> creatable && _userContext != null)
        {
            creatable.CreatedOn = DateTimeOffset.UtcNow;
            creatable.CreatedById = _userContext.UserId;
        }

        await _dbSet.AddAsync(entity);
        await _context.SaveChangesAsync();
        return entity;
    }

    public virtual async Task<TEntity> UpdateAsync(TEntity entity)
    {
        // Populate modification audit fields
        if (entity is IModifiable<TKey> modifiable && _userContext != null)
        {
            modifiable.ModifiedOn = DateTimeOffset.UtcNow;
            modifiable.ModifiedById = _userContext.UserId;
        }

        _dbSet.Update(entity);
        await _context.SaveChangesAsync();
        return entity;
    }

    public virtual async Task<bool> DeleteAsync(TKey id)
    {
        var entity = await GetByIdAsync(id);
        if (entity == null) return false;

        // Soft delete if entity supports it
        if (entity is IDeletable<TKey> deletable)
        {
            deletable.DeletedOn = DateTimeOffset.UtcNow;
            deletable.DeletedById = _userContext?.UserId;
            _dbSet.Update(entity);
        }
        else
        {
            // Hard delete if no soft delete support
            _dbSet.Remove(entity);
        }

        await _context.SaveChangesAsync();
        return true;
    }
}
```

### 5. Soft Delete Filtering

Automatically exclude soft-deleted entities from queries:

```csharp
protected virtual IQueryable<TEntity> GetQueryable(bool includeDeleted = false)
{
    var query = _dbSet.AsQueryable();
    
    if (!includeDeleted && typeof(IDeletable<TKey>).IsAssignableFrom(typeof(TEntity)))
    {
        var parameter = Expression.Parameter(typeof(TEntity), "e");
        var property = Expression.Property(parameter, nameof(IDeletable<TKey>.DeletedOn));
        var nullConstant = Expression.Constant(null, typeof(DateTimeOffset?));
        var equality = Expression.Equal(property, nullConstant);
        var lambda = Expression.Lambda<Func<TEntity, bool>>(equality, parameter);
        
        query = query.Where(lambda);
    }
    
    return query;
}
```

## Consequences

### Positive Consequences

- **Automatic Tracking** - No manual intervention required, audit fields populated automatically
- **Consistency** - All entities audited the same way across the application
- **Compliance Ready** - Meets common regulatory audit requirements out of the box
- **Soft Delete** - Data preserved for recovery and compliance
- **Flexible** - Implement only the interfaces you need (creation, modification, deletion, or all)
- **Type Safe** - Compile-time checking of audit field types
- **Testable** - User context can be mocked for testing
- **Authentication Agnostic** - Works with any auth system through abstraction
- **UTC Timestamps** - Consistent time zone handling with DateTimeOffset

### Negative Consequences

- **Storage Overhead** - Six additional fields per auditable entity (48 bytes for Guid, 32 for int)
- **Performance Impact** - Soft delete queries require additional WHERE clause
- **Nullable User IDs** - Must handle cases where user is unknown (system operations)
- **Data Growth** - Soft-deleted entities accumulate over time
- **Cleanup Strategy Needed** - Must implement archival/purging for old soft-deleted data
- **Index Considerations** - DeletedOn should be indexed for query performance

### Neutral Consequences

- **Optional Adoption** - Entities can opt-in by implementing interfaces
- **DateTimeOffset vs DateTime** - Using DateTimeOffset adds 8 bytes per timestamp vs DateTime
- **Navigation Properties** - Created/Modified/DeletedBy user relationships are not enforced (nullable Guid/TKey)

## Alternatives Considered

### 1. Change Tracking with DbContext ChangeTracker

Override `SaveChangesAsync` in DbContext to automatically set audit fields.

**Pros:**
- Centralized in one place
- Works for all entities automatically

**Cons:**
- Tight coupling to DbContext
- Harder to test
- Breaks separation of concerns
- User context harder to inject

**Why Rejected:** Repository pattern better encapsulates audit logic.

### 2. Entity Framework Interceptors

Use EF Core interceptors to populate audit fields.

**Pros:**
- Centralized
- Works transparently

**Cons:**
- EF Core specific
- Complex to implement
- User context injection difficult
- Less explicit

**Why Rejected:** Repository approach is clearer and more testable.

### 3. Single IAuditable Interface

One interface with all six properties instead of three separate interfaces.

**Pros:**
- Simpler API
- One interface to implement

**Cons:**
- Violates Interface Segregation Principle
- Entities must implement all audit features even if only creation tracking needed
- Harder to extend

**Why Rejected:** Flexibility to implement only needed interfaces is valuable.

### 4. Hard Delete Only

No soft delete support, always physically delete entities.

**Pros:**
- Simpler queries (no DeletedOn filtering)
- Smaller database
- No cleanup needed

**Cons:**
- Data loss
- Cannot recover accidentally deleted data
- Compliance issues
- No historical analysis

**Why Rejected:** Soft delete is essential for most business applications.

### 5. DateTime Instead of DateTimeOffset

Use `DateTime` for timestamps.

**Pros:**
- Smaller (8 bytes vs 16 bytes per timestamp)
- Simpler

**Cons:**
- Time zone issues
- Ambiguous in distributed systems
- Cannot store offset information

**Why Rejected:** DateTimeOffset is the correct choice for modern applications.

## Implementation Best Practices

### Entity Configuration

```csharp
public class ProductConfiguration : IEntityTypeConfiguration<Product>
{
    public void Configure(EntityTypeBuilder<Product> builder)
    {
        builder.HasKey(p => p.Id);
        
        // Index DeletedOn for soft delete filtering performance
        builder.HasIndex(p => p.DeletedOn);
        
        // Optional: Create foreign keys to User table for navigation properties
        // builder.HasOne(p => p.CreatedBy).WithMany().HasForeignKey(p => p.CreatedById);
        // builder.HasOne(p => p.ModifiedBy).WithMany().HasForeignKey(p => p.ModifiedById);
        // builder.HasOne(p => p.DeletedBy).WithMany().HasForeignKey(p => p.DeletedById);
    }
}
```

### Querying Including Soft-Deleted

```csharp
// Exclude soft-deleted (default)
var activeProducts = await _repository.GetAllAsync();

// Include soft-deleted (for admin views)
var allProducts = await _repository.GetAllAsync(includeDeleted: true);
```

### Manual Override (When Needed)

```csharp
public class SystemInitializationService
{
    public async Task SeedDataAsync()
    {
        var product = new Product
        {
            Name = "System Default Product",
            CreatedOn = DateTimeOffset.UtcNow,
            CreatedById = null, // System operation, no user
            ModifiedOn = DateTimeOffset.UtcNow,
            ModifiedById = null
        };
        
        await _context.Products.AddAsync(product);
        await _context.SaveChangesAsync();
    }
}
```

### Archival Strategy

```csharp
public class ArchivalService
{
    // Archive soft-deleted entities older than retention period
    public async Task ArchiveDeletedEntitiesAsync(int retentionDays = 365)
    {
        var cutoffDate = DateTimeOffset.UtcNow.AddDays(-retentionDays);
        
        var toArchive = await _context.Products
            .Where(p => p.DeletedOn != null && p.DeletedOn < cutoffDate)
            .ToListAsync();
        
        // Move to archive table or export to cold storage
        // Then hard delete from main table
    }
}
```

## References

- [ADR-001: Repository Pattern](001-repository-pattern.md)
- [ADR-002: Simple vs Advanced Entities](002-simple-advanced-entities.md)
- [Soft Delete Pattern - Microsoft Docs](https://docs.microsoft.com/en-us/ef/core/miscellaneous/nullable-reference-types)
- [Audit Logging - OWASP](https://owasp.org/www-community/Audit_Logging)

## Related Documentation

- [Getting Started: Creating Auditable Entities](../../getting-started/auditable-entities.md)
- [How-To: User Context Implementation](../../how-to/user-context.md)
- [API Reference: ISimpleAuditable](../../api/data/auditing/isimpleauditable.md)
