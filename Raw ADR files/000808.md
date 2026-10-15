---
docid: ADR-100
title: ADR Enhanced Localized Dto Projections
owner: @DocMaintainer
status: Active
created: 2026-01-08
---

﻿# ADR: Enhanced EF Core Localized DTO Projections Pattern

**Date:** January 1, 2026  
**Status:** Accepted  
**Owner:** @Architect  
**Stakeholders:** @TechLead, @DatabaseSpecialist, @Backend

## Context

The current EF Core Localized DTO Projections Pattern uses convention-over-configuration to automatically detect localized properties (e.g., `Name` + `NameTranslations`) and build projections. While functional, this approach has limitations in type safety and API design.

We need to enhance the pattern to provide better developer experience while maintaining the hybrid localization approach (default column + JSON translations).

### Current Pattern Limitations

1. **Convention dependency** - Relies on naming conventions (`Property` + `PropertyTranslations`)
2. **Type ambiguity** - No compile-time indication that a property is localizable
3. **API complexity** - DTOs expose both default and translation properties
4. **Maintenance burden** - Manual synchronization between default and translations

## Decision

**Adopt the Attribute-based approach with `[Localizable]` attribute** for gradual enhancement of the existing pattern.

### Rationale

After evaluating three approaches, the attribute-based solution provides the best balance of:

- **Backward compatibility** - Can be adopted incrementally without breaking changes
- **Type safety** - Compile-time validation through attributes
- **API flexibility** - Declarative configuration with minimal code changes
- **Performance** - No runtime overhead for non-localized properties
- **Maintainability** - Clear intent and centralized configuration

### Implementation

#### 1. Localizable Attribute

```csharp
[AttributeUsage(AttributeTargets.Property, AllowMultiple = false)]
public class LocalizableAttribute : Attribute
{
    public string? TranslationProperty { get; set; }
    public string? DefaultProperty { get; set; }
}
```

#### 2. Enhanced Projection Extensions

```csharp
public static class LocalizedProjectionExtensions
{
    public static IQueryable<TDto> SelectLocalized<TEntity, TDto>(
        this IQueryable<TEntity> query, 
        string locale)
        where TEntity : class, ITenantEntity
    {
        // Check for [Localizable] attributes on DTO properties
        // Build projection using attribute metadata instead of conventions
        var projection = BuildLocalizedProjection<TEntity, TDto>(locale);
        return query.Select(projection);
    }
}
```

#### 3. Usage Example

```csharp
public class ProductDto
{
    public Guid Id { get; set; }
    
    [Localizable(DefaultProperty = "Name", TranslationProperty = "NameTranslations")]
    public string Name { get; set; }
    
    [Localizable(DefaultProperty = "Description", TranslationProperty = "DescriptionTranslations")]
    public string? Description { get; set; }
    
    public decimal Price { get; set; }
}
```

## Alternatives Considered

### 1. Struct-Type: LocalizedString

**Approach:** Define localizable properties as `LocalizedString` struct containing default value and translations.

```csharp
public readonly struct LocalizedString
{
    public string DefaultValue { get; }
    public LocalizedContent? Translations { get; }
    
    public string GetLocalizedValue(string locale)
        => Translations?.GetValue(locale) ?? DefaultValue;
}
```

**Pros:**
- ✅ **Type safety** - Explicit localized type prevents misuse
- ✅ **API design** - Single property instead of property pairs
- ✅ **Encapsulation** - Localization logic contained within the type

**Cons:**
- ❌ **Backward compatibility** - Breaking change for existing DTOs
- ❌ **EF Core complexity** - Complex mapping for owned types
- ❌ **Performance** - Struct copying overhead
- ❌ **Maintainability** - Requires changes to all localized DTOs

### 2. ValueObject: LocalizedValue<T>

**Approach:** Generic value object wrapper for any localizable type.

```csharp
public class LocalizedValue<T> : IValueObject
{
    public T DefaultValue { get; }
    public LocalizedContent? Translations { get; }
    
    public T GetLocalizedValue(string locale, Func<string, T>? parser = null)
        => Translations?.GetValue(locale) is string translated 
            ? parser?.Invoke(translated) ?? (T)(object)translated 
            : DefaultValue;
}
```

**Pros:**
- ✅ **Type safety** - Generic wrapper works with any type
- ✅ **API design** - Clean, reusable abstraction
- ✅ **Flexibility** - Supports localization of any property type

**Cons:**
- ❌ **Backward compatibility** - Breaking change for existing DTOs
- ❌ **Complexity** - Generic type handling in projections
- ❌ **Serialization** - JSON serialization challenges
- ❌ **Performance** - Boxing/unboxing for value types

### 3. Attribute: [Localizable] (Chosen)

**Approach:** Declarative attribute marking localizable properties.

```csharp
[AttributeUsage(AttributeTargets.Property)]
public class LocalizableAttribute : Attribute
{
    public string? TranslationProperty { get; set; }
    public string? DefaultProperty { get; set; }
}
```

**Pros:**
- ✅ **Backward compatibility** - Can be adopted incrementally
- ✅ **Type safety** - Compile-time validation through attributes
- ✅ **API design** - Minimal changes to existing DTOs
- ✅ **Performance** - No overhead for non-localized properties
- ✅ **Maintainability** - Clear intent, centralized configuration

**Cons:**
- ❌ **Runtime reflection** - Attribute inspection at runtime
- ❌ **Convention fallback** - Still needs conventions for simple cases
- ❌ **Tooling dependency** - Requires source generators for optimal performance

## Consequences

### Positive

- ✅ **Incremental adoption** - Can enhance existing code without breaking changes
- ✅ **Developer experience** - Clear intent through attributes
- ✅ **Type safety** - Compile-time validation of localizable properties
- ✅ **Performance** - Minimal overhead, maintains current projection efficiency
- ✅ **Maintainability** - Centralized localization logic with clear contracts

### Negative

- ❌ **Attribute processing** - Runtime reflection for attribute inspection
- ❌ **Migration effort** - Gradual adoption requires dual maintenance during transition
- ❌ **Convention complexity** - Still supports conventions for backward compatibility

### Mitigations

1. **Source generator** - Generate projection code at compile-time to eliminate runtime reflection
2. **Migration tooling** - Provide automated refactoring tools for attribute adoption
3. **Dual support** - Maintain convention-based projections during transition period

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1-2)
- Create `LocalizableAttribute` class
- Update `LocalizedProjectionExtensions` to support attributes
- Add unit tests for attribute-based projections

### Phase 2: Source Generator (Week 3-4)
- Implement source generator for compile-time projection generation
- Eliminate runtime reflection overhead
- Add performance benchmarks

### Phase 3: Migration Tools (Week 5-6)
- Create automated refactoring tools
- Update documentation and examples
- Provide migration guides

### Phase 4: Entity Updates (Week 7-8)
- Apply attributes to existing DTOs
- Update API documentation
- Performance validation

## Compliance

- **BITV 2.0**: Maintains multi-language support for accessibility
- **Performance**: No degradation in query performance
- **Backward compatibility**: Zero breaking changes during transition

---

**Status:** ✅ Accepted - Attribute-based approach enables gradual enhancement while maintaining backward compatibility and improving type safety.</content>
<parameter name="filePath">/Users/holger/Documents/Projekte/B2X/.ai/decisions/ADR-enhanced-localized-dto-projections.md