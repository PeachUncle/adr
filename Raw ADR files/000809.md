---
docid: ADR-101
title: ADR Entity Localization Pattern
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR: Entity Localization Pattern - Hybrid Default + Translations

**Date:** January 1, 2026  
**Status:** Accepted  
**Owner:** @Architect  
**Stakeholders:** @Backend, @Frontend, @DatabaseSpecialist, @TechLead

## Context

B2X requires multi-language support for domain entities (Products, Categories, Brands, etc.). The solution must support:

1. **Dynamic languages** - New languages can be added without schema changes
2. **Performant admin search** - Database-indexed search on default language
3. **Simple CRUD** - Single table per entity, no complex JOINs
4. **Referential integrity** - Standard FK/CASCADE behavior
5. **Store search via Elasticsearch** - Per-language analyzers for catalog search

### Alternatives Considered

| Approach | CRUD | DB Index | Dynamic Languages | Ref. Integrity |
|----------|------|----------|-------------------|----------------|
| JSON only | ✅ Simple | ❌ No | ✅ Yes | ✅ Yes |
| Separate Translation Table | ❌ JOINs | ✅ Yes | ✅ Yes | ✅ Yes |
| Columns per Language | ⚠️ Complex | ✅ Yes | ❌ No | ✅ Yes |
| **Hybrid (chosen)** | ✅ Simple | ✅ Yes | ✅ Yes | ✅ Yes |

## Decision

**Hybrid pattern: Default value in indexed columns + Translations as JSON**

Each localizable property is represented by:
1. **Default column** - Direct column with the default language value (indexable)
2. **Translations JSON** - `LocalizedContent` Value Object containing all translations

### Data Model

```csharp
public class Product : ITenantEntity
{
    public Guid Id { get; set; }
    public Guid TenantId { get; set; }
    
    // Direct columns for default language (indexable for admin search)
    [MaxLength(255)]
    public string Name { get; set; } = string.Empty;
    
    [MaxLength(2000)]
    public string? Description { get; set; }
    
    // Translations as Owned Type (stored as JSON)
    public LocalizedContent? NameTranslations { get; set; }
    public LocalizedContent? DescriptionTranslations { get; set; }
    
    // Non-localized fields
    public string Sku { get; set; } = string.Empty;
    public decimal Price { get; set; }
}
```

### Database Schema

```sql
CREATE TABLE Products (
    Id UUID PRIMARY KEY,
    TenantId UUID NOT NULL,
    Name VARCHAR(255) NOT NULL,           -- Default language (indexed)
    Description VARCHAR(2000),            -- Default language
    NameTranslations JSONB,               -- {"de": "...", "fr": "..."}
    DescriptionTranslations JSONB,
    Sku VARCHAR(100) NOT NULL,
    Price DECIMAL(18,2) NOT NULL,
    -- ...
);

-- Index for admin search on default language
CREATE INDEX idx_products_name ON Products(Name);
CREATE INDEX idx_products_tenant_name ON Products(TenantId, Name);
```

### LocalizedContent Value Object

```csharp
public sealed class LocalizedContent : IValueObject
{
    public IReadOnlyDictionary<string, string> Translations { get; }
    
    public string? GetValue(string languageCode)
        => Translations.TryGetValue(languageCode.ToLowerInvariant(), out var v) ? v : null;
    
    public LocalizedContent WithTranslation(string languageCode, string value)
        => new(new Dictionary<string, string>(Translations) { [languageCode] = value });
}
```

### Entity Helper Methods

```csharp
public class Product
{
    // Get localized name with fallback to default
    public string GetLocalizedName(string languageCode)
        => NameTranslations?.GetValue(languageCode) ?? Name;
    
    public string GetLocalizedDescription(string languageCode)
        => DescriptionTranslations?.GetValue(languageCode) ?? Description ?? string.Empty;
}
```

### EF Core Configuration

```csharp
modelBuilder.Entity<Product>(entity =>
{
    entity.HasIndex(p => p.Name);
    entity.HasIndex(p => new { p.TenantId, p.Name });
    
    entity.OwnsOne(p => p.NameTranslations, translations =>
    {
        translations.ToJson("NameTranslations");
    });
    
    entity.OwnsOne(p => p.DescriptionTranslations, translations =>
    {
        translations.ToJson("DescriptionTranslations");
    });
});
```

### API Design

```csharp
// Admin API - Returns full entity with all translations
public class ProductAdminDto
{
    public Guid Id { get; set; }
    public string Name { get; set; }                           // Default
    public Dictionary<string, string>? NameTranslations { get; set; }
    public string? Description { get; set; }                   // Default
    public Dictionary<string, string>? DescriptionTranslations { get; set; }
}

// Store API - Returns pre-localized values
public class ProductStoreDto
{
    public Guid Id { get; set; }
    public string Name { get; set; }        // Already localized
    public string? Description { get; set; } // Already localized
}
```

## Consequences

### Positive

- ✅ **Simple CRUD** - One table per entity, standard EF Core operations
- ✅ **Admin search indexed** - Default column has database index
- ✅ **Dynamic languages** - New languages = new JSON keys, no migrations
- ✅ **Referential integrity** - Standard FK/CASCADE behavior
- ✅ **Clear API design** - Admin sees all translations, Store sees localized
- ✅ **Fallback implicit** - Default column is always populated
- ✅ **Store search via Elasticsearch** - JSON synced to search indices

### Negative

- ❌ **Two places for Name** - Column + JSON, requires sync discipline
- ❌ **Default language fixed per entity** - Changing default requires migration
- ❌ **JSON search limited** - Can't efficiently search across all translations in DB

### Mitigations

1. **Sync discipline**: Entity methods ensure consistency between default and translations
2. **Default language**: Tenant-level default language setting, entities use tenant default
3. **Translation search**: Store search uses Elasticsearch with per-language indices

## Implementation Requirements

1. **Update LocalizedContent** - Remove DefaultValue, keep only Translations dictionary
2. **Create helper extension** - `ConfigureLocalizedProperty<T>()` for EF configuration
3. **Update entities** - Product, Category, Brand with new pattern
4. **Admin API** - Return both default and translations
5. **Store API** - Return pre-localized values based on Accept-Language
6. **Elasticsearch sync** - Index each language separately

## Affected Entities

| Entity | Localized Properties |
|--------|---------------------|
| Product | Name, Description, ShortDescription, MetaDescription |
| Category | Name, Description, MetaDescription |
| Brand | Name, Description |
| ContentPage | Title, Description, Content |
| MenuItem | Label |
| FaqEntry | Question, Answer |

## Compliance

- **BITV 2.0**: Supports multiple languages for accessibility
- **GDPR**: Language preferences stored with user consent
- **Performance**: Default column indexed for admin queries

---

**Status:** ✅ Accepted - Hybrid pattern provides best balance of simplicity, performance, and flexibility for B2X's multi-language requirements.
